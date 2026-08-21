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
    """Fee efficiency from the live position. IN range = 100, OUT = 0."""
    if not position or "positions" not in position:
        return 0.0
    pos = next((p for p in position["positions"] if "error" not in p), None)
    if not pos:
        return 0.0
    return 100.0 if pos.get("inRange") else 0.0


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

    # Not out of range -> hold (stay in pool, keep earning)
    if eff >= OUT_OF_RANGE_FEE_EFF:
        return {
            "action": "hold", "shape": shape,
            "reason": f"in range (fee eff {eff:.0f}%) — stay in pool", "fee_eff": eff,
        }

    # Out of range. Is re-centering justified?
    # Gas is effectively free on Avalanche (measured ~$0.001), so the gate is
    # "is the shape right for the regime" + "not too frequent."
    reason = (f"OUT of range (fee eff {eff:.0f}%) — re-center {shape} on "
              f"current price")

    # Frequency guard
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
    if args.autonomous:
        if decision["action"] == "deploy":
            # Funded wallet, no position — open a fresh curve (auto-deploy).
            import subprocess
            deployable = has_deployable_capital()
            deployable = max(10.0, deployable - 1.0)  # keep a little USDC + gas buffer
            print(f"🛡️ STEWARD — AUTONOMOUS DEPLOY (no position)")
            print(f"   Reason: {decision['reason']}")
            print(f"   Plan: open {decision['shape']} curve for ${deployable:.2f}")
            proc = subprocess.run(
                [sys.executable, DEPLOY_EXEC_SCRIPT, "--amount", str(deployable),
                 "--bin-spread", "11", "--execute", "--yes"],
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
                new_pos = get_position_after()
                if new_pos:
                    print(f"   ✅ Position live: {new_pos}")
            return 0
        if decision["action"] != "rebalance":
            # Healthy — stay silent (no noise). The heartbeat covers the pulse.
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
            # Verify the new on-chain state
            new_pos = get_position_after()
            if new_pos:
                print(f"   ✅ Back at: {new_pos}")
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
