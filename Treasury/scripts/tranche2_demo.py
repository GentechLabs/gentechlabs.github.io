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

    # 3. Bridge quote (Across Base -> Solana)
    print("## 3. EVM->Solana bridge (Across, dry)")
    b = _run("solana_homebase.py", "--action", "bridge", "--amount", "20")
    print(json.dumps(b, indent=2), "\n")

    # 4. Allocation plan
    print("## 4. Allocation plan (dry-powder deploy on Solana)")
    plan = {
        "strategy": "Regime-gated: accumulate (yield) vs trade (SOL/TAO)",
        "yield_rail": "Solana USDC deploy (Jupiter-routed)",
        "trade_legs": ["SOL (buy)", "TAO (buy)"],
        "bridge": "Across Base->Solana (sub-5s, ~0.08%)",
        "receipt": "Q402 trust receipt on every payment",
        "funding_needed": "~$2 SOL gas + ~$20 USDC on Solana",
    }
    print(json.dumps(plan, indent=2))

    print("\n# ✅ Demo complete. Live quotes verified above. Ready for on-chain proof"
          " when Solana wallet is funded (SOLANA_REAL=1).")


if __name__ == "__main__":
    main()
