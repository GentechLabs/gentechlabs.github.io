#!/usr/bin/env python3
"""
Multi-Wallet Treasury Manager
Manage multiple wallets with per-wallet strategies and automatic rebalancing.

Usage:
    python treasury_manager.py --wallets         # List wallets
    python treasury_manager.py --wallet <id>     # Check wallet
    python treasury_manager.py --report          # Unified balance report
    python treasury_manager.py --rebalance       # Execute rebalance
    python treasury_manager.py --watch           # Live monitoring
"""

import json
import os
import sys
import time
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# Sample wallet configurations
SAMPLE_WALLETS = [
    {
        "id": "hot-base",
        "name": "Hot Wallet — Base",
        "chain": "base",
        "type": "hot",
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
        "balance_usdc": 4820.50,
        "target_pct": 0.15,
        "min_balance": 1000,
        "max_balance": 10000,
        "strategy": "liquidity",
        "current_apy": 0.08,
        "gas_spent_30d": 12.40,
        "last_rebalance": (datetime.now() - timedelta(days=1)).isoformat(),
    },
    {
        "id": "yield-base",
        "name": "Yield Wallet — Base",
        "chain": "base",
        "type": "yield",
        "address": "0x8f3E8A2e9C0F1b3e5Dc9A2b8F4e7D1c5A6b3E2f1",
        "balance_usdc": 18500.00,
        "target_pct": 0.20,
        "min_balance": 10000,
        "max_balance": 30000,
        "strategy": "aero-lp",
        "current_apy": 0.12,
        "gas_spent_30d": 8.75,
        "last_rebalance": (datetime.now() - timedelta(days=7)).isoformat(),
    },
    {
        "id": "yield-avax",
        "name": "Yield Wallet — Avalanche",
        "chain": "avax",
        "type": "yield",
        "address": "0x1aBc3dEf4G5h6I7j8K9l0MnOpQrStUvWxYz1234",
        "balance_usdc": 12500.00,
        "target_pct": 0.15,
        "min_balance": 5000,
        "max_balance": 20000,
        "strategy": "lfj-lp",
        "current_apy": 0.18,
        "gas_spent_30d": 15.20,
        "last_rebalance": (datetime.now() - timedelta(days=3)).isoformat(),
    },
    {
        "id": "cold",
        "name": "Cold Wallet",
        "chain": "base",
        "type": "cold",
        "address": "0x5dEf7A3bC1D2e4F5g6H7i8J9k0L1mN2oP3qR4sT5",
        "balance_usdc": 45000.00,
        "target_pct": 0.35,
        "min_balance": 30000,
        "max_balance": 60000,
        "strategy": "hold",
        "current_apy": 0.0,
        "gas_spent_30d": 0,
        "last_rebalance": (datetime.now() - timedelta(days=60)).isoformat(),
    },
    {
        "id": "operational",
        "name": "Operational Wallet",
        "chain": "base",
        "type": "operational",
        "address": "0x3f7a4B2c8D9e0F1a2B3c4D5e6F7a8B9c0D1e2F3",
        "balance_usdc": 3200.00,
        "target_pct": 0.10,
        "min_balance": 2000,
        "max_balance": 8000,
        "strategy": "gas-reserve",
        "current_apy": 0.0,
        "gas_spent_30d": 45.30,
        "last_rebalance": (datetime.now() - timedelta(days=5)).isoformat(),
    },
    {
        "id": "reserve",
        "name": "Reserve Wallet",
        "chain": "base",
        "type": "reserve",
        "address": "0x9aB8c7D6e5F4g3H2i1J0kL9mN8oP7qR6sT5uV4w",
        "balance_usdc": 8000.00,
        "target_pct": 0.05,
        "min_balance": 5000,
        "max_balance": 15000,
        "strategy": "emergency",
        "current_apy": 0.0,
        "gas_spent_30d": 0,
        "last_rebalance": (datetime.now() - timedelta(days=90)).isoformat(),
    },
]

TOTAL_AUM = sum(w["balance_usdc"] for w in SAMPLE_WALLETS)
TARGET_ALLOCATIONS = {w["id"]: w["target_pct"] for w in SAMPLE_WALLETS}


def print_wallets(wallets):
    """Print all wallets in a table."""
    print("┌─ Multi-Wallet Treasury ─────────────────────────────────────────────────────┐")
    print(f"  {'ID':<18} {'Chain':<8} {'Type':<14} {'Balance':>10} {'Target':>8} {'APY':>6} {'Strategy':<16}")
    print(f"  {'─'*18} {'─'*8} {'─'*14} {'─'*10} {'─'*8} {'─'*6} {'─'*16}")
    for w in sorted(wallets, key=lambda x: x["balance_usdc"], reverse=True):
        apy_str = f"{w['current_apy']*100:.0f}%" if w['current_apy'] > 0 else "—"
        target_pct = w["target_pct"] * 100
        print(f"  {w['id']:<18} {w['chain']:<8} {w['type']:<14} ${w['balance_usdc']:>8.2f} {target_pct:>6.0f}% {apy_str:>6} {w['strategy']:<16}")
    print(f"\n  Total AUM: ${TOTAL_AUM:,.2f}")
    print(f"  Wallets:   {len(wallets)}")
    print(f"  Chains:    {', '.join(set(w['chain'] for w in wallets))}")


def print_wallet(w):
    """Print detailed wallet info."""
    print(f"┌─ Wallet: {w['id']} ───────────────────────────────────────────┐")
    print(f"  Name:      {w['name']}")
    print(f"  Chain:     {w['chain']}")
    print(f"  Type:      {w['type']}")
    print(f"  Address:   {w['address'][:10]}...{w['address'][-6:]}")
    print(f"  Balance:   ${w['balance_usdc']:,.2f}")
    print(f"  Target:    {w['target_pct']*100:.0f}% (${TOTAL_AUM * w['target_pct']:,.2f})")
    actual_pct = w['balance_usdc'] / TOTAL_AUM * 100
    drift = actual_pct - w['target_pct'] * 100
    drift_str = f"{'+' if drift > 0 else ''}{drift:.1f}%"
    print(f"  Actual:    {actual_pct:.1f}% ({drift_str} drift)")
    print(f"  Range:     ${w['min_balance']:,} – ${w['max_balance']:,}")
    print(f"  APY:       {w['current_apy']*100:.0f}%" if w['current_apy'] > 0 else "  APY:       —")
    print(f"  Gas (30d): ${w['gas_spent_30d']:.2f}")
    print(f"  Strategy:  {w['strategy']}")
    print(f"  Last Rebal: {w['last_rebalance'][:10]}")
    
    # Status assessment
    if w['balance_usdc'] < w['min_balance']:
        print(f"  Status:    ❌ UNDERFUNDED (${w['min_balance'] - w['balance_usdc']:,.2f} short)")
    elif w['balance_usdc'] > w['max_balance']:
        print(f"  Status:    ⚠️  OVERFUNDED (${w['balance_usdc'] - w['max_balance']:,.2f} excess)")
    else:
        print(f"  Status:    ✅ In range")


def print_report(wallets):
    """Unified balance report."""
    total = sum(w["balance_usdc"] for w in wallets)
    
    print("┌─ Treasury Report ────────────────────────────────────────────────┐")
    print(f"  Total AUM:     ${total:,.2f}")
    print(f"  Wallet Count:  {len(wallets)}")
    
    # Allocation breakdown
    print()
    print("┌─ Allocation ─────────────────────────────────────────────────────┐")
    for w in sorted(wallets, key=lambda x: x["balance_usdc"], reverse=True):
        actual = w["balance_usdc"] / total * 100
        target = w["target_pct"] * 100
        drift = actual - target
        bar = "█" * max(1, int(actual / 2))
        drift_icon = "🔴" if abs(drift) > 5 else ("🟡" if abs(drift) > 2 else "✅")
        print(f"  {drift_icon} {w['id']:<18} {actual:>5.1f}% (target {target:.0f}%) {bar}")
    
    # Rebalance opportunities
    opportunities = []
    for w in wallets:
        if w["balance_usdc"] < w["min_balance"]:
            opportunities.append(f"  🔴 {w['id']}: ${w['min_balance'] - w['balance_usdc']:,.0f} short")
        elif w["balance_usdc"] > w["max_balance"]:
            opportunities.append(f"  ⚠️  {w['id']}: ${w['balance_usdc'] - w['max_balance']:,.0f} excess")
    
    if opportunities:
        print()
        print("┌─ Rebalance Needed ──────────────────────────────────────────────┐")
        for opp in opportunities:
            print(opp)
    else:
        print()
        print("┌─ Rebalance ─────────────────────────────────────────────────────┐")
        print("  ✅ All wallets within range")


def check_rebalance(wallets, dry_run=True):
    """Check what rebalances are needed."""
    total = sum(w["balance_usdc"] for w in wallets)
    actions = []
    
    for w in wallets:
        target = total * w["target_pct"]
        actual = w["balance_usdc"]
        delta = actual - target
        
        if abs(delta) / target > 0.05:  # 5% threshold
            if delta > 0:
                actions.append({
                    "wallet": w["id"],
                    "action": "withdraw",
                    "amount": round(delta, 2),
                    "reason": f"Over target by ${delta:,.0f}"
                })
            else:
                actions.append({
                    "wallet": w["id"],
                    "action": "deposit",
                    "amount": round(-delta, 2),
                    "reason": f"Under target by ${-delta:,.0f}"
                })
    
    if not actions:
        print("  ✅ No rebalance needed — all wallets within 5% of target")
        return
    
    print(f"  {'Action':<10} {'Wallet':<20} {'Amount':>12} {'Reason'}")
    print(f"  {'─'*10} {'─'*20} {'─'*12} {'─'*30}")
    total_moved = 0
    for a in actions:
        icon = "📤" if a["action"] == "withdraw" else "📥"
        print(f"  {icon} {a['action']:<8} {a['wallet']:<20} ${a['amount']:>9.2f}  {a['reason']}")
        total_moved += a["amount"]
    
    print(f"\n  Total to rebalance: ${total_moved:,.2f}")
    if dry_run:
        print("  🟡 DRY RUN — no transactions executed")
    else:
        print("  🔴 EXECUTING rebalance...")


def run_watch(interval=3600):
    """Continuous monitoring mode."""
    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print_report(SAMPLE_WALLETS)
            print(f"\n  🔄 Refresh every {interval}s — Ctrl+C to stop")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Stopped.")


def main():
    parser = argparse.ArgumentParser(description="Multi-Wallet Treasury Manager")
    parser.add_argument("--wallets", action="store_true", help="List all wallets")
    parser.add_argument("--wallet", help="Check a specific wallet by ID")
    parser.add_argument("--report", action="store_true", help="Unified balance report")
    parser.add_argument("--rebalance", action="store_true", help="Check/execute rebalance")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no transactions)")
    parser.add_argument("--watch", action="store_true", help="Live monitoring mode")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    wallets = json.loads(json.dumps(SAMPLE_WALLETS))
    total_aum = sum(w["balance_usdc"] for w in wallets)

    if args.wallet:
        found = [w for w in wallets if w["id"] == args.wallet]
        if found:
            print_wallet(found[0])
        else:
            print(f"  ❌ Wallet '{args.wallet}' not found")
            print(f"  Available: {', '.join(w['id'] for w in wallets)}")
    elif args.report:
        print_report(wallets)
    elif args.rebalance:
        check_rebalance(wallets, dry_run=args.dry_run)
    elif args.watch:
        run_watch()
    elif args.format == "json":
        data = {"aum": total_aum, "wallets": wallets, "timestamp": datetime.now().isoformat()}
        print(json.dumps(data, indent=2))
    else:
        print_wallets(wallets)


if __name__ == "__main__":
    main()
