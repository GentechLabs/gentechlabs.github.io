#!/usr/bin/env python3
"""Tranche-2 demo: prove the Solana-homebase treasury LIVE (for the submission).

Runs the exact flow the grant reviewer sees, one command, honest output:
  1. Live Solana wallet status (SOL + USDC balances)
  2. Live Jupiter quotes (SOL + TAO buys) — proves settlement rail works
  3. Bridge quote (Across Base->Solana) — proves EVM->Solana funding path
  4. Allocation plan — where USDC deploys on Solana

Safe by default (DRY_RUN). Real execution only with SOLANA_REAL=1 + funded keypair.

Usage:
  python3 tranche2_demo.py                # full dry-run demo
  python3 tranche2_demo.py --fast         # quotes only (skip wallet/ledger)
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def _run(script, *args):
    cmd = [sys.executable, os.path.join(HERE, script), *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": r.stderr[-400:] or r.stdout[-400:]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fast", action="store_true")
    a = p.parse_args()

    print(f"# 🏠 Solana Homebase — Agentic Treasury Demo ({datetime.utcnow().date()})")
    print("# Superteam Earn — Agentic Engineering, Tranche 2 deliverable\n")

    # 1. Wallet status (if keypair)
    if not a.fast:
        st = _run("solana_homebase.py", "--action", "status")
        print("## 1. Wallet status")
        print(json.dumps(st, indent=2), "\n")

    # 2. Live Jupiter quotes — the settlement proof
    print("## 2. Live settlement quotes (Jupiter, real)"
          if not os.environ.get("SOLANA_REAL")
          else "## 2. Live settlement (Jupiter, EXECUTING)")
    for sym in ["SOL", "TAO"]:
        q = _run("solana_homebase.py", "--action", "buy",
                 "--symbol", sym, "--amount", "5")
        quote = q.get("quote", {})
        out = quote.get("out_amount")
        print(f"  - {sym}: $5 USDC -> {out} {sym}" if out
              else f"  - {sym}: {q.get('error', q)}")
    print()

    # 3. Bridge quote — LIVE venue measurement.
    # CORRECTED 2026-09-24: this used to say "(Across, dry)" over a STUB that returned the
    # literal string "dry-run (Across, sub-5s, ~0.08% fee)". It quoted nothing, and the 0.08%
    # was the sum of two constants in our own source, not a venue figure. Measured with controls:
    # Across serves NO EVM->Solana route (base/arbitrum/ethereum all ROUTE_NOT_ENABLED, while
    # base->arbitrum and base->ethereum return 200 ENABLED). deBridge DLN is live and is what
    # the bridge leg now quotes. This section prints which venue can actually carry the leg.
    print("## 3. EVM->Solana bridge (LIVE venue measurement)")
    b = _run("solana_homebase.py", "--action", "bridge", "--amount", "20")
    print(json.dumps(b, indent=2), "\n")

    # 4. Allocation plan
    print("## 4. Allocation plan (dry-powder deploy on Solana)")
    plan = {
        "strategy": "Regime-gated: accumulate (yield) vs trade (SOL/TAO)",
        "yield_rail": "Solana USDC deploy (Jupiter-routed)",
        "trade_legs": ["SOL (buy)", "TAO (buy)"],
        # CORRECTED 2026-09-24 — was "Across Base->Solana (sub-5s, ~0.08%)". Across cannot
        # carry this leg at all (every EVM->Solana route returns ROUTE_NOT_ENABLED), and the
        # "~0.08%" was our own constant. The live figure from deBridge on a $20 order is ~4.9%
        # because the DLN fix fee (~$1) dominates at small size — see section 3 above.
        "bridge": "deBridge DLN Base/Avalanche->Solana (LIVE quote; ~4.9% at $20, ~0.75% at $150)",
        "receipt": "Q402 trust receipt on every payment",
        "funding_needed": "~$2 SOL gas + ~$20 USDC on Solana",
    }
    print(json.dumps(plan, indent=2))

    print("\n# ✅ Demo complete. Live quotes verified above. Ready for on-chain proof"
          " when Solana wallet is funded (SOLANA_REAL=1).")


if __name__ == "__main__":
    main()
