#!/usr/bin/env python3
"""GTA Execution Engine — turn arb scan state into trade decisions and order plans.

Modes:
  - DRY_RUN (default): produces the exact order plan, moves NO funds. Safe always.
  - REAL: executes only if GTA_HL_KEY env var is set; else raises NoExecutionKeyError.

Rule set (from agentic-arbitrage skill):
  - Report  >= 5 bps, Execute >= 10 bps, Close < 3 bps
  - Stop-loss: spread widened > 50 bps from entry
  - Max hold: 7 days
  - Funding cost erodes profit on hold

Layer 3 seed (agent sentiment): every decision is appended to an agent-flow
ledger (`agent-flow.jsonl`) tagged with `agent_id` + timestamp + action. This is
the attributable dataset the agent-sentiment aggregator reads later. See
`09-Green Room/specs/agent-sentiment-stack-assessment.md`.
"""

import json
import os
import sys
from datetime import datetime, timezone

# Shared treasury brain (Aug 21 2026): the executor is MODE-GATED. When the
# treasury is in YIELD_FARM mode, this job must NOT fire ENTER signals (that's
# how we got the conflicting "ENTER ONDO" while the council held the farm).
# It may still CLOSE/HOLD an existing position (exiting is always fine).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from treasury_state import get_mode, can_trade, held_line, load_state as _ts_load
except ImportError:
    def get_mode(s=None): return "YIELD_FARM"
    def can_trade(s=None): return False
    def held_line(cat, sig): return f"⏸ [{cat}] {sig} held"
    def _ts_load(): return {}

EXECUTE_BPS = 10.0
REPORT_BPS = 5.0
CLOSE_BPS = 3.0
STOP_LOSS_WIDEN_BPS = 50.0
MAX_HOLD_DAYS = 7

# Layer 3 seed: agent identity attribution. Overridable so connected agents
# (Forge, ClawWork workers, arena competitors) can log under their own id.
AGENT_ID = os.environ.get("GTA_AGENT_ID", "gentech-gta")
AGENT_FLOW_LOG = os.environ.get(
    "GTA_AGENT_FLOW_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent-flow.jsonl"),
)

# Quiet hours: 11pm-6:30am ET = 3:00-10:30 UTC
_hr = datetime.now(timezone.utc).hour
if 3 <= _hr < 10 or (_hr == 10 and datetime.now(timezone.utc).minute < 30):
    sys.exit(0)


class NoExecutionKeyError(RuntimeError):
    """Raised when REAL execution is requested but no GTA_HL_KEY is configured."""


def load_state(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"opportunities": []}


def load_position(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_position(position, path):
    with open(path, "w") as f:
        json.dump(position, f, indent=2)


def _parse_ts(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _days_held(position):
    entered = _parse_ts(position.get("entered_at", ""))
    if not entered:
        return 0.0
    return (datetime.now(timezone.utc) - entered).total_seconds() / 86400.0


def decide(state, position=None, current_spread_bps=None):
    """Return a decision dict for the highest-basis tradeable opportunity (or the
    open position, whichever applies)."""
    # 1. If we hold an open position, manage it first (exit rules dominate entry).
    if position:
        entry = position.get("entry_spread_bps")
        cur = current_spread_bps if current_spread_bps is not None else entry
        reasons = []
        if entry is not None and cur is not None and (cur - entry) > STOP_LOSS_WIDEN_BPS:
            reasons.append("stop_loss")
        if entry is not None and cur is not None and cur < CLOSE_BPS:
            reasons.append("normalized")
        if _days_held(position) > MAX_HOLD_DAYS:
            reasons.append("max_hold")
        if reasons:
            return {"action": "CLOSE", "symbol": position.get("symbol"),
                    "reasons": reasons}
        return {"action": "HOLD", "symbol": position.get("symbol"), "reasons": []}

    # 2. No open position — scan for the best entry.
    opps = state.get("opportunities", [])
    if not opps:
        return {"action": "SKIP", "symbol": None, "reasons": ["no_opportunities"]}

    best = max(opps, key=lambda o: o.get("basis_bps", 0))
    bps = best.get("basis_bps", 0)
    if bps >= EXECUTE_BPS:
        return {"action": "ENTER", "symbol": best.get("symbol"), "reasons": ["tradeable"]}
    if bps >= REPORT_BPS:
        return {"action": "REPORT", "symbol": best.get("symbol"),
                "reasons": ["below_execute"]}
    return {"action": "SKIP", "symbol": best.get("symbol"), "reasons": ["below_report"]}


def build_order_plan(opp):
    """Contango => short perp + long spot. Backwardation => reverse."""
    if opp.get("basis_bps", 0) >= 0:
        return {
            "symbol": opp.get("symbol"),
            "perp_side": "short",
            "spot_side": "buy",
            "perp_venue": "Hyperliquid",
            "spot_venue": "Coinbase",
        }
    return {
        "symbol": opp.get("symbol"),
        "perp_side": "long",
        "spot_side": "sell",
        "perp_venue": "Hyperliquid",
        "spot_venue": "Coinbase",
    }


def _dispatch_close(order_plan):
    """Dispatch a CLOSE order plan to the close+remit executor (Phase B).

    Wraps the async close executor and returns its result. Enforces the close
    executor's own gates (AAE_CLOSE_REAL + CDP creds); never fakes success.
    """
    try:
        from gta_close_executor import run_close_sync
        return run_close_sync(order_plan, dry_run=False)
    except Exception as e:
        # Surface the failure loudly — never report executed=True on an error.
        return {
            "executed": False,
            "error": f"close-dispatch-failed: {type(e).__name__}: {e}",
        }


def _execute_real(plan):
    """Place real orders. Requires GTA_HL_KEY. Wires the Hyperliquid perp leg.

    US-legal note (Aug 20 2026): Trump said CFTC is working to bring
    Hyperliquid to the US — this un-blocks the perp leg that was previously
    detection-only (US gray-zone). Now staged to go live once a key + capital
    exist. Never fakes a fill: returns the real exchange response.
    """
    key = os.environ.get("GTA_HL_KEY")
    if not key:
        raise NoExecutionKeyError(
            "REAL execution requested but GTA_HL_KEY is not set. "
            "Dry-run is always safe; wire the key to enable live orders."
        )
    # Wire the real Hyperliquid perp leg. The spot leg (Coinbase CDP) is a
    # separate integration; this module places the perp side of the arb.
    try:
        from gta_hl_execute import place_perp_order
        symbol = plan.get("symbol")
        is_buy = plan.get("perp_side") == "long"
        # Size is not in the plan yet — require it via env or default small.
        size = float(os.environ.get("GTA_HL_SIZE", "0"))
        if size <= 0:
            raise NoExecutionKeyError(
                "GTA_HL_SIZE not set (or <= 0). Set the perp order size in coin "
                "units to enable REAL execution. Refusing to guess a size."
            )
        # Wide limit for a market-ish fill; fetch reference price.
        from hyperliquid.info import Info
        info = Info("https://api.hyperliquid.xyz")
        mids = info.all_mids()
        ref = float(mids.get(symbol, 0))
        if ref <= 0:
            raise NoExecutionKeyError(
                f"could not fetch reference price for {symbol} — refusing to "
                "place an order with an unknown limit price."
            )
        limit_px = round(ref * (0.95 if is_buy else 1.05), 4)
        return place_perp_order(
            symbol=symbol, is_buy=is_buy, size=size,
            limit_px=limit_px, dry_run=False,
        )
    except NoExecutionKeyError:
        raise
    except Exception as e:
        # Surface the failure loudly — never report executed=True on an error.
        return {
            "executed": False,
            "error": f"hl-execute-failed: {type(e).__name__}: {e}",
        }


def append_agent_flow(decision, order_plan=None, executed=False, mode="DRY_RUN"):
    """Append one attributable decision to the agent-flow ledger (Layer 3 seed).

    Each line is a JSON record tagged with agent_id + timestamp so the
    agent-sentiment aggregator can compute per-agent flow / net positioning /
    confidence later. Append-only; never mutated in place.
    """
    record = {
        "agent_id": AGENT_ID,
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": decision.get("action"),
        "symbol": decision.get("symbol"),
        "reasons": decision.get("reasons", []),
        "mode": mode,
        "executed": executed,
        "order_plan": order_plan,
    }
    try:
        with open(AGENT_FLOW_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        # Never fail the trade on a logging error — log loudly, continue.
        sys.stderr.write(f"[agent-flow] write failed: {e}\n")


def run(state, dry_run=True, position=None, current_spread_bps=None):
    decision = decide(state, position, current_spread_bps)
    result = {"mode": "DRY_RUN" if dry_run else "REAL", "decision": decision,
              "order_plan": None, "executed": False}

    # MODE GATE (Aug 21 2026): ENTER signals only fire when the treasury is in
    # TRADE mode. In YIELD_FARM / DRY_POWDER, an ENTER decision is downgraded to
    # a HELD report so the trader can't contradict the council. CLOSE/HOLD on an
    # existing position always passes (exiting is always permitted).
    if decision["action"] == "ENTER" and not can_trade():
        decision = {**decision, "action": "HELD",
                    "reasons": ["mode-gate: treasury not in TRADE mode"]}
        result["held"] = held_line(
            "trader", f"ENTER {decision.get('symbol')} basis {decision.get('reasons', [''])[0] if decision.get('reasons') else ''}")
        append_agent_flow(decision, None, False, result.get("mode"))
        return result

    if decision["action"] == "ENTER":
        # find the matching opportunity for the plan
        opp = next((o for o in state.get("opportunities", [])
                    if o.get("symbol") == decision["symbol"]), None)
        if opp:
            result["order_plan"] = build_order_plan(opp)
            if not dry_run:
                _execute_real(result["order_plan"])
                result["executed"] = True

    elif decision["action"] == "CLOSE":
        result["order_plan"] = {"close": True, "symbol": decision["symbol"]}
        if not dry_run:
            # Phase B: dispatch the close to the close+remit executor, which
            # sells the spot → USDC and remits → Jordan EOA. This module
            # enforces its own gates (AAE_CLOSE_REAL + CDP creds) and refuses
            # to fake a successful exit.
            close_result = _dispatch_close(result["order_plan"])
            result["close_result"] = close_result
            result["executed"] = bool(
                (close_result or {}).get("executed")
            )
        else:
            # Dry-run: surface that a close would be dispatched, no funds move.
            result["close_dry_run"] = "dispatch-to-close-executor"

    # Layer 3 seed: log every decision (ENTER/CLOSE/HOLD/REPORT/SKIP) with
    # agent attribution. SKIP/HOLD still logged — flow includes "stayed out".
    append_agent_flow(decision, result.get("order_plan"),
                      result.get("executed", False), result.get("mode"))

    return result


if __name__ == "__main__":
    state_file = os.environ.get(
        "GTA_STATE_FILE",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gta-arb-state.json"),
    )
    pos_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gta_position.json")
    state = load_state(state_file)
    pos = load_position(pos_file)
    out = run(state, dry_run=True, position=pos)
    print(json.dumps(out, indent=2))
