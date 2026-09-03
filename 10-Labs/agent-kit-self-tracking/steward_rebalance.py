#!/usr/bin/env python3
"""
Steward — Autonomous Position Rebalance Loop
=============================================
The Steward's decision layer for the Agentic Treasury. Watches the deployed LP
position, reasons about regime + shape + fee-efficiency, and re-centers the
position back into range ONLY when justified — no Jordan input for routine
maintenance.

Decision rationale (Jordan's strategy, Aug 11 2026):
  - Goal: stay IN range, keep fee efficiency HIGH, stay in the pool as long as
    gas-justified.
  - Shape by regime (from .aae-regime-state.json):
      RANGE_BOUND / ACCUMULATION / PRICE_DISCOVERY  -> CURVE (normal chop, fees)
      HIGH_VOLATILITY / BULL_TRENDING / BEAR_TRENDING-> BID_ASK (vol spikes)
  - Rebalance trigger: position OUT of range (fee efficiency < ~50-60%) AND
    gas-justified (gas cost tiny on Avalanche; re-center is effectively free).
  - Don't rebalance reflexively — only when OUT + the re-center is rational.

Modes:
  - DRY_RUN (default): reads live state, DECIDES, prints the plan. No funds move.
  - --execute: actually re-centers the position (withdraw + re-deploy curve on
    current active bin) via the SDK-corrected curve distribution. Guarded by
    --yes + funded wallet + gas check.

Refuses to fake success: REAL execution requires a funded wallet, a live
connection, and the Steward key present. If anything is missing, it says so
and holds — it never invents an executed rebalance.

Reuses: discover_positions (live LP read), deploy_lp_curve (execution leg).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# ── Paths / config ───────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
REGIME_FILE = os.environ.get(
    "AAE_REGIME_STATE_FILE", "/root/.hermes/scripts/.aae-regime-state.json")

# Execution rail (SDK-corrected curve deploy) — lives in the profile scripts dir
DEPLOY_SCRIPT = os.environ.get(
    "STEWARD_DEPLOY_SCRIPT",
    "/root/.hermes/profiles/gentech-treasury/scripts/deploy_lp_curve.py")

# Silence layer (Jordan, Sep 3 2026): alert ONCE per condition, then stay
# silent until it resolves or changes. No more re-firing the same failed
# attempt every 10 minutes.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steward_silence as silence

# Rebalance thresholds
OUT_OF_RANGE_FEE_EFF = 50.0   # fee efficiency % below this -> consider rebalance
REBALANCE_MIN_DELAY_S = 600   # don't rebalance more than once per 10 min
GAS_REFUEL_MIN_AVAX = 0.05    # need at least this much native gas to act

# Regime -> LP shape (Jordan's strategy)
REGIME_SHAPE = {
    "RANGE_BOUND": "CURVE",
    "ACCUMULATION": "CURVE",
    "PRICE_DISCOVERY": "CURVE",
    "HIGH_VOLATILITY": "BID_ASK",
    "BULL_TRENDING": "BID_ASK",
    "BEAR_TRENDING": "BID_ASK",
}

# ── Helpers ──────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str, default=None) -> Optional[Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def read_regime() -> Dict[str, Any]:
    """Regime signal from the AAE classifier. Returns {} if unavailable."""
    d = load_json(REGIME_FILE, {}) or {}
    return {
        "regime": d.get("regime", "UNKNOWN"),
        "confidence": d.get("confidence", 0.0),
        "price": d.get("price"),
        "updated_at": d.get("timestamp"),
    }


def read_position() -> Dict[str, Any]:
    """Live LP position via the generalized discover_positions reader."""
    sys.path.insert(0, HERE)
    try:
        from discover_positions import discover_positions, _is_checksum_or_valid
        cfg = load_json(os.path.join(HERE, "treasury_config.json"), {}) or {}
        wallet = cfg.get("wallet") or os.environ.get("STEWARD_WALLET")
        if not isinstance(wallet, str) or not _is_checksum_or_valid(wallet):
            return {"error": "no valid wallet in config"}
        # Discover across the configured chains; look for LFJ positions.
        data = discover_positions("avalanche", wallet)  # LFJ rail
        return data
    except Exception as e:
        return {"error": f"discovery failed: {e}"}


def fee_efficiency(position: Dict[str, Any]) -> float:
    """CONTINUOUS fee efficiency (Jordan's soft-floor rule, Sep 3 2026).

    100% = price at the exact center of our bin range (max fee capture).
    0%   = price at a range edge / out of range.
    Linear distance-from-center: eff = (1 - |frac - 0.5| * 2) * 100.

    Replaces the old binary in/out measure — "IN range" says nothing about how
    much of our curve is actually being crossed by trades.
    """
    if not position or "positions" not in position:
        return 0.0
    pos = next((p for p in position["positions"] if "error" not in p), None)
    if not pos:
        return 0.0
    if not pos.get("inRange"):
        return 0.0
    lo, hi = pos.get("rangeLow"), pos.get("rangeHigh")
    price = pos.get("livePriceUsd")
    if not (isinstance(lo, (int, float)) and isinstance(hi, (int, float))
            and isinstance(price, (int, float)) and hi > lo):
        return 100.0 if pos.get("inRange") else 0.0
    frac = max(0.0, min(1.0, (price - lo) / (hi - lo)))
    return max(0.0, 1.0 - abs(frac - 0.5) * 2.0) * 100.0


def gas_ok() -> bool:
    """Enough native gas on the Steward wallet to act (or refuel-able)."""
    try:
        from discover_positions import rpc_call
        cfg = load_json(os.path.join(HERE, "treasury_config.json"), {}) or {}
        wallet = cfg.get("wallet") or os.environ.get("STEWARD_WALLET")
        bal = int(rpc_call("avalanche", "eth_getBalance", [wallet, "latest"]), 16) / 1e18
        return bal >= GAS_REFUEL_MIN_AVAX
    except Exception:
        return False


# Minimum deployable capital (USDC) before auto-deploy triggers. Below this we
# stay as dry powder — don't burn gas opening a sub-$10 position.
DEPLOY_MIN_USDC = 10.0
DEPLOY_EXEC_SCRIPT = os.environ.get(
    "STEWARD_EXEC_SCRIPT",
    "/root/.hermes/profiles/gentech-treasury/scripts/gta_avax_lp_execute.py")


def has_deployable_capital() -> float:
    """Return deployable USDC on the Steward wallet (0 if none / error).

    This is the trigger for the auto-deploy leg: a funded wallet with no live
    position means the treasury should open a fresh curve, not sit as dry
    powder. Returns the USDC amount available to deploy.
    """
    try:
        from discover_positions import get_erc20_balance
        cfg = load_json(os.path.join(HERE, "treasury_config.json"), {}) or {}
        wallet = cfg.get("wallet") or os.environ.get("STEWARD_WALLET")
        if not isinstance(wallet, str):
            return 0.0
        # USDC on Avalanche C-Chain
        usdc_contract = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
        raw = get_erc20_balance("avalanche", usdc_contract, wallet)
        if raw is None:
            return 0.0
        return raw / 1e6
    except Exception:
        return 0.0


def get_position_after() -> str:
    """Re-read the live position after a rebalance, return a compact read string."""
    try:
        pos = read_position()
        p = next((x for x in pos.get("positions", []) if "error" not in x), None)
        if p:
            return p.get("read", "n/a")
    except Exception:
        pass
    return ""


# ── Decision ─────────────────────────────────────────────────────────────

# Jordan's soft-floor rule (Sep 3 2026): "if fee efficiency is below 60-70% for
# a while and rebalancing doesn't cost much — rebalance." In range but hovering
# near an edge = weak fee capture. Sustained weakness triggers a proactive
# re-center (gas is pennies; missed fees are not).
SOFT_FLOOR_EFF = 65.0          # below this (while in range) starts the timer
SOFT_FLOOR_PERSIST_MIN = 20    # sustained minutes below floor before acting
# 20 min = exactly 2 consecutive 10-min watchdog readings below floor (Jordan,
# Sep 3 2026: "after 20 minutes we can definitely say we need to rebalance").
SOFT_FLOOR_FILE = os.path.join(HERE, ".steward-soft-floor-state.json")


def _soft_floor_tick(eff: float) -> float:
    """Track how long fee efficiency has been below the soft floor.

    Returns minutes sustained (0 if not below floor). Writes/clears the state
    file so the timer survives across 10-min cron runs (stateful debounce).
    """
    import os as _os
    if eff >= SOFT_FLOOR_EFF:
        # Healthy — clear the timer
        try:
            if _os.path.exists(SOFT_FLOOR_FILE):
                _os.remove(SOFT_FLOOR_FILE)
        except Exception:
            pass
        return 0.0
    st = load_json(SOFT_FLOOR_FILE, {}) or {}
    first = st.get("first_seen")
    if not first:
        with open(SOFT_FLOOR_FILE, "w") as f:
            json.dump({"first_seen": _now_iso(), "eff": eff}, f)
        return 0.0
    try:
        first_dt = datetime.fromisoformat(first)
        return (datetime.now(timezone.utc) - first_dt).total_seconds() / 60.0
    except (ValueError, TypeError):
        with open(SOFT_FLOOR_FILE, "w") as f:
            json.dump({"first_seen": _now_iso(), "eff": eff}, f)
        return 0.0


def decide(position: Dict[str, Any], regime: Dict[str, str],
           last_rebalance_ts: Optional[str] = None) -> Dict[str, Any]:
    """The Steward's rebalance decision for the current state."""
    eff = fee_efficiency(position)
    regime_name = regime.get("regime", "UNKNOWN")
    shape = REGIME_SHAPE.get(regime_name, "CURVE")

    # No live position -> nothing to act on
    has_live_pos = any(
        "error" not in p for p in (position.get("positions") or []))
    if "error" in position or not has_live_pos:
        # Auto-deploy leg (Jordan, Aug 20 2026): a funded wallet with no live
        # position means the treasury should open a fresh curve, not sit as
        # dry powder. Only deploy when there's real deployable capital AND
        # enough native gas. Below the floor we stay liquid.
        deployable = has_deployable_capital()
        if deployable >= DEPLOY_MIN_USDC and gas_ok():
            return {
                "action": "deploy", "shape": shape,
                "reason": (f"funded wallet, no position — auto-deploy "
                           f"${deployable:.2f} USDC curve"), "fee_eff": eff,
            }
        return {
            "action": "hold", "shape": shape,
            "reason": "no deployable position detected", "fee_eff": eff,
        }

    # Jordan's SOFT-FLOOR rule (Sep 3 2026): in range but fee capture weak
    # (price hovering near a range edge) for a sustained stretch -> re-center.
    # Rebuke of "in range = fine": a curve with price pinned at an edge earns
    # a fraction of center-position fees, and gas costs ~nothing — so after a
    # persistence window, re-centering is rational even while technically IN.
    reason = ""
    if 0.0 < eff < SOFT_FLOOR_EFF:
        sustained_min = _soft_floor_tick(eff)
        if sustained_min < SOFT_FLOOR_PERSIST_MIN:
            return {
                "action": "hold", "shape": shape,
                "reason": (f"fee eff {eff:.0f}% below soft floor "
                           f"({SOFT_FLOOR_EFF:.0f}%) for "
                           f"{sustained_min:.0f}m (< {SOFT_FLOOR_PERSIST_MIN}m) — watching"),
                "fee_eff": eff,
            }
        reason = (f"fee eff {eff:.0f}% < {SOFT_FLOOR_EFF:.0f}% sustained "
                  f"{sustained_min:.0f}m — proactive re-center {shape}")
        # fall through to the shared frequency guard below
    elif eff >= SOFT_FLOOR_EFF:
        _soft_floor_tick(eff)  # clears the timer
        return {
            "action": "hold", "shape": shape,
            "reason": f"in range, fee eff {eff:.0f}% — stay in pool", "fee_eff": eff,
        }
    else:
        # Fully OUT of range (eff == 0) — immediate re-center, no wait.
        reason = f"OUT of range — re-center {shape} on current price"

    # Frequency guard (applies to both soft-floor and out-of-range triggers)
    if last_rebalance_ts:
        try:
            last = datetime.fromisoformat(last_rebalance_ts.replace("Z", "+00:00"))
            age_s = (datetime.now(timezone.utc) - last).total_seconds()
            if age_s < REBALANCE_MIN_DELAY_S:
                return {
                    "action": "hold", "shape": shape,
                    "reason": f"rebalanced {age_s:.0f}s ago (< {REBALANCE_MIN_DELAY_S}s) — wait",
                    "fee_eff": eff,
                }
        except (ValueError, TypeError):
            pass

    return {"action": "rebalance", "shape": shape, "reason": reason, "fee_eff": eff}


# ── Execution ────────────────────────────────────────────────────────────

def execute_rebalance(dry_run: bool = True) -> Dict[str, Any]:
    """Re-center the curve via the SDK-corrected deploy script.

    DRY_RUN (default): just report the rebalance command that WOULD run.
    REAL (--execute): run deploy_lp_curve.py on the live wallet.
    """
    if dry_run:
        return {
            "executed": False, "dry_run": True,
            "command": f"python3 {DEPLOY_SCRIPT} --execute --yes",
        }

    # REAL execution guards — refuse to fake success.
    if not os.path.exists(DEPLOY_SCRIPT):
        return {"executed": False, "dry_run": False,
                "error": "deploy_lp_curve.py not found"}
    if not gas_ok():
        return {"executed": False, "dry_run": False,
                "error": "insufficient native gas on Steward wallet — refusing"}

    import subprocess
    try:
        proc = subprocess.run(
            [sys.executable, DEPLOY_SCRIPT, "--execute", "--yes"],
            capture_output=True, text=True, timeout=180)
        ok = proc.returncode == 0 and "deployed" in proc.stdout.lower()
        return {
            "executed": ok, "dry_run": False,
            "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:],
        }
    except Exception as e:
        return {"executed": False, "dry_run": False, "error": str(e)}


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Steward — autonomous rebalance loop")
    ap.add_argument("--execute", action="store_true",
                    help="actually re-center the position (guarded)")
    ap.add_argument("--yes", action="store_true", help="confirm real execution")
    ap.add_argument("--watchdog", action="store_true",
                    help="quiet mode: print ONLY when action-worthy (OUT of range); "
                         "silent otherwise — for a cheap no_agent cron")
    ap.add_argument("--autonomous", action="store_true",
                    help="FULL AUTONOMY: detect need, execute the rebalance itself "
                         "(withdraw-redeploy via steward_execute.py), and report the "
                         "plan + result. Jordan is alerted AFTER, not asked to confirm.")
    args = ap.parse_args()

    regime = read_regime()
    position = read_position()

    # Last rebalance stamp (persist so we don't rebalance too often)
    stamp_file = os.path.join(HERE, ".steward-last-rebalance.json")
    last_ts = (load_json(stamp_file, {}) or {}).get("ts")
    decision = decide(position, regime, last_ts)

    # ── WATCHDOG mode: emit only on a real signal (silent watchdog cron) ──
    if args.watchdog:
        if decision["action"] in ("rebalance", "deploy"):
            p = next((x for x in position.get("positions", []) if "error" not in x), None)
            pos_read = p.get("read", "") if p else ""
            print(f"🛡️ Steward: {decision['action'].upper()} — {decision['shape']}")
            print(f"   {decision['reason']} (fee eff {decision['fee_eff']:.0f}%)")
            if pos_read:
                print(f"   Position: {pos_read}")
            print(f"   To act: python3 {DEPLOY_SCRIPT} --execute --yes")
        # else: silent (no output = no_agent cron sends nothing)
        return 0

    # ── AUTONOMOUS mode: detect need, execute, report (Jordan alerted AFTER) ──
    # Silence layer (Jordan, Sep 3 2026): each condition alerts ONCE, then stays
    # silent while it persists — re-alerts only on resolution->recurrence or the
    # periodic reminder window (default 6h). Resolving the condition re-arms it.
    if args.autonomous:
        if decision["action"] == "deploy":
            # Funded wallet, no position — open a fresh curve (auto-deploy).
            # SILENCE GATE: if this condition was already reported and is still
            # unresolved, stay quiet — the deploy already failed, re-announcing
            # every 10 min is noise, not monitoring.
            if silence.silenced("auto-deploy"):
                return 0
            import subprocess
            deployable = has_deployable_capital()
            deployable = max(10.0, deployable - 1.0)  # keep a little USDC + gas buffer
            print(f"🛡️ STEWARD — AUTONOMOUS DEPLOY (no position)")
            print(f"   Reason: {decision['reason']}")
            # Spread fix (Jordan, Sep 2 2026): ±11 reverts on LFJ (proven by
            # read-only eth_call simulation 2026-09-03). ±5 with 11 bins is the
            # working setting — same one auto-compound uses.
            print(f"   Plan: open {decision['shape']} curve ±5 for ${deployable:.2f}")
            proc = subprocess.run(
                [sys.executable, DEPLOY_EXEC_SCRIPT, "--amount", str(deployable),
                 "--bin-spread", "5", "--allocation", "0.5", "--execute", "--yes"],
                capture_output=True, text=True, timeout=300)
            ok = proc.returncode == 0
            print(f"   Executed: {'✅' if ok else '❌'}")
            if proc.stdout:
                print(f"   {proc.stdout[-1200:]}")
            if proc.stderr:
                print(f"   stderr: {proc.stderr[-300:]}")
            if ok:
                with open(stamp_file, "w") as f:
                    json.dump({"ts": _now_iso()}, f)
                silence.mark_success("auto-deploy")
                new_pos = get_position_after()
                if new_pos:
                    print(f"   ✅ Position live: {new_pos}")
            else:
                # Failure — suppress further attempts for 6h (one reminder after
                # that), instead of re-announcing the same failure every 10 min.
                silence.mark_failure(
                    "auto-deploy", (proc.stderr or proc.stdout or "unknown")[-300:],
                    retry_hours=6)
            return 0
        if decision["action"] != "rebalance":
            # Healthy — stay silent (no noise). The heartbeat covers the pulse.
            # Conditions RESOLVED (position live / back in range): re-arm the
            # silence keys so the NEXT occurrence alerts fresh (suppress-until-
            # resolution pattern).
            silence.mark_success("auto-deploy")
            silence.mark_success("rebalance")
            return 0
        # Rebalance leg — same silence discipline: alert ONCE per out-of-range
        # episode, stay silent while it persists, re-arm on success.
        if silence.silenced("rebalance"):
            return 0
        p = next((x for x in position.get("positions", []) if "error" not in x), None)
        pos_read = p.get("read", "") if p else ""
        print(f"🛡️ STEWARD — AUTONOMOUS REBALANCE")
        print(f"   ⚠️ OUT of range (fee eff {decision['fee_eff']:.0f}%)")
        print(f"   Reason: {decision['reason']}")
        if pos_read:
            print(f"   Before: {pos_read}")
        print(f"   Plan: withdraw + redeploy {decision['shape']} on current price")
        # Execute the full withdraw-redeploy cycle via steward_execute.py
        import subprocess
        exec_script = os.path.join(HERE, "steward_execute.py")
        shape = decision["shape"].lower()
        proc = subprocess.run(
            [sys.executable, exec_script, "--mode", "withdraw-redeploy",
             "--shape", shape, "--execute", "--yes"],
            capture_output=True, text=True, timeout=300)
        ok = proc.returncode == 0
        print(f"   Executed: {'✅' if ok else '❌'}")
        if proc.stdout:
            print(f"   {proc.stdout[-1200:]}")
        if proc.stderr:
            print(f"   stderr: {proc.stderr[-300:]}")
        if ok:
            with open(stamp_file, "w") as f:
                json.dump({"ts": _now_iso()}, f)
            silence.mark_success("rebalance")
            # Verify the new on-chain state
            new_pos = get_position_after()
            if new_pos:
                print(f"   ✅ Back at: {new_pos}")
        else:
            # Failed re-center — suppress for 2h instead of re-attempting +
            # re-announcing every 10 min (gas + noise discipline).
            silence.mark_failure(
                "rebalance", (proc.stderr or proc.stdout or "unknown")[-300:],
                retry_hours=2)
        return 0

    print("=" * 52)
    print("🛡️  STEWARD — POSITION DECISION")
    print("=" * 52)
    print(f"  Regime:     {regime.get('regime')} (conf {regime.get('confidence', 0):.0%})")
    print(f"  Shape:      {decision['shape']}")
    print(f"  Fee eff:    {decision['fee_eff']:.0f}%")
    print(f"  Action:     {decision['action'].upper()}")
    print(f"  Reason:     {decision['reason']}")

    if position.get("positions"):
        p = next((x for x in position["positions"] if "error" not in x), None)
        if p:
            print(f"  Position:   {p.get('read', 'n/a')}")

    # Execute if decided + requested
    if decision["action"] == "rebalance" and args.execute:
        if not args.yes:
            print("\n  ⚠️  --execute requires --yes (confirm). Holding.")
            return 1
        print("\n  ⚙️  Rebalancing...")
        result = execute_rebalance(dry_run=False)
        print(f"  Executed:   {result.get('executed')}")
        if result.get("error"):
            print(f"  Error:      {result['error']}")
        if result.get("stdout"):
            print(f"  {result['stdout'][-600:]}")
        if result.get("executed"):
            # Stamp the rebalance time
            with open(stamp_file, "w") as f:
                json.dump({"ts": _now_iso()}, f)
    else:
        cmd = execute_rebalance(dry_run=True)["command"]
        print(f"  (dry-run — to execute: {cmd} with --yes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
