#!/usr/bin/env python3
"""
GenTech Receipts — x402 Spending Tracker
Track per-agent spend, per-endpoint revenue, daily totals, and receipt verification.

Usage:
    python tracker.py --summary daily       # Daily revenue summary
    python tracker.py --verify --tx 0x...   # Verify a receipt
    python tracker.py --export data.json    # Export to JSON
    python tracker.py --watch               # Live monitoring mode
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_DAYS = 7

SAMPLE_DATA = {
    "summary": {
        "total_volume_usdc": 847.50,
        "total_calls": 1247,
        "unique_callers": 23,
        "avg_payment_usdc": 0.68,
        "period_start": (datetime.now() - timedelta(days=7)).isoformat(),
        "period_end": datetime.now().isoformat(),
    },
    "by_endpoint": [
        {"endpoint": "/api/analyze", "calls": 412, "volume": 289.40, "price": 0.70},
        {"endpoint": "/api/scan", "calls": 298, "volume": 208.60, "price": 0.70},
        {"endpoint": "/api/credit-score", "calls": 187, "volume": 93.50, "price": 0.50},
        {"endpoint": "/api/compliance-check", "calls": 156, "volume": 109.20, "price": 0.70},
        {"endpoint": "/api/treasury/balance", "calls": 98, "volume": 49.00, "price": 0.50},
        {"endpoint": "/api/predict", "calls": 52, "volume": 52.00, "price": 1.00},
        {"endpoint": "/api/trade/signal", "calls": 44, "volume": 45.80, "price": 1.04},
    ],
    "by_chain": [
        {"chain": "Base", "calls": 612, "volume": 416.50},
        {"chain": "Polygon", "calls": 389, "volume": 264.52},
        {"chain": "Arbitrum", "calls": 246, "volume": 166.48},
    ],
    "daily_totals": [],
    "top_callers": [
        {"address": "0x742d...4a29", "calls": 187, "volume": 127.16},
        {"address": "0x8f3e...b721", "calls": 143, "volume": 97.24},
        {"address": "0x1abc...9de4", "calls": 112, "volume": 76.16},
        {"address": "0x5def...3c18", "calls": 98, "volume": 66.64},
        {"address": "0x3f7a...e502", "calls": 76, "volume": 51.68},
    ],
    "recent_transactions": [],
}


def generate_sample_data(days=DEFAULT_DAYS):
    """Generate realistic sample data for the demo."""
    data = json.loads(json.dumps(SAMPLE_DATA))  # deep copy

    # Daily totals with realistic variation
    now = datetime.now()
    base_volume = 120  # base daily volume
    for i in range(days):
        day = now - timedelta(days=days - 1 - i)
        variation = 1.0 + (i % 5 - 2) * 0.15  # vary by ±30%
        daily_vol = round(base_volume * variation, 2)
        daily_calls = int(180 * variation)
        data["daily_totals"].append({
            "date": day.strftime("%Y-%m-%d"),
            "volume_usdc": daily_vol,
            "calls": daily_calls,
        })

    # Recent transactions
    chains = ["Base", "Polygon", "Arbitrum"]
    endpoints = [e["endpoint"] for e in data["by_endpoint"]]
    for i in range(20):
        ts = now - timedelta(minutes=i * 12 + (i % 3) * 5)
        data["recent_transactions"].append({
            "tx_hash": f"0x{os.urandom(16).hex()}",
            "chain": chains[i % 3],
            "endpoint": endpoints[i % len(endpoints)],
            "caller": data["top_callers"][i % 5]["address"],
            "amount_usdc": round(0.50 + (i % 5) * 0.25, 2),
            "timestamp": ts.isoformat(),
            "verified": i > 2,  # first 3 unverified
        })

    return data


def print_summary(data, fmt="text"):
    """Print a summary report."""
    s = data["summary"]

    if fmt == "json":
        print(json.dumps(data, indent=2))
        return

    print("╔══════════════════════════════════════════════════════════╗")
    print("║              GenTech Receipts — Summary                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"  Period:     {s['period_start'][:10]} → {s['period_end'][:10]}")
    print(f"  Total Volume: ${s['total_volume_usdc']:.2f} USDC")
    print(f"  Total Calls:  {s['total_calls']}")
    print(f"  Unique Callers: {s['unique_callers']}")
    print(f"  Avg Payment:  ${s['avg_payment_usdc']:.2f}")
    print()

    # By endpoint
    print("┌─ By Endpoint ──────────────────────────────────────────┐")
    print(f"  {'Endpoint':<25} {'Calls':>8} {'Volume':>10}")
    print(f"  {'─'*25} {'─'*8} {'─'*10}")
    for ep in sorted(data["by_endpoint"], key=lambda x: x["volume"], reverse=True):
        print(f"  {ep['endpoint']:<25} {ep['calls']:>8} ${ep['volume']:>7.2f}")
    print()

    # By chain
    print("┌─ By Chain ─────────────────────────────────────────────┐")
    for ch in data["by_chain"]:
        pct = ch["volume"] / s["total_volume_usdc"] * 100
        print(f"  {ch['chain']:<12} ${ch['volume']:>7.2f}  ({pct:>5.1f}%)  {ch['calls']} calls")

    # Daily trend
    print()
    print("┌─ Daily Trend ─────────────────────────────────────────┐")
    for d in data["daily_totals"]:
        bar = "█" * max(1, int(d["volume_usdc"] / 10))
        print(f"  {d['date']}  ${d['volume_usdc']:>6.2f}  {bar}")


def run_watch(interval=30, days=DEFAULT_DAYS):
    """Live monitoring mode — refresh every N seconds."""
    try:
        while True:
            data = generate_sample_data(days)
            os.system("clear" if os.name == "posix" else "cls")
            print_summary(data)
            print(f"\n  🔄 Auto-refresh every {interval}s — Ctrl+C to stop")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Stopped.")


def export_data(data, path):
    """Export data to JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Exported to {path}")


def verify_receipt(tx_hash, chain="base", data_path=None):
    """Verify a receipt. In production, queries the chain. Here, checks sample data or uses the verification algorithm."""
    # Check sample data first
    if data_path:
        try:
            with open(data_path) as f:
                data = json.load(f)
            for tx in data.get("recent_transactions", []):
                if tx["tx_hash"] == tx_hash:
                    status = "✅ Verified" if tx["verified"] else "❌ Invalid"
                    print(f"  Receipt: {tx_hash}")
                    print(f"  Status:  {status}")
                    print(f"  Chain:   {tx['chain']}")
                    print(f"  Endpoint: {tx['endpoint']}")
                    print(f"  Amount:  ${tx['amount_usdc']:.2f}")
                    print(f"  Time:    {tx['timestamp']}")
                    return tx["verified"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    # Algorithmic verification (used when no local data)
    print(f"  🔍 Verifying receipt {tx_hash} on {chain}...")
    print(f"  ⚠️  No local data found for this hash.")
    print(f"  In production, this would query {chain.upper()} for:")
    print(f"    - Transaction receipt")
    print(f"    - Event logs (x402.PaymentSent or similar)")
    print(f"    - Sender/recipient/amount matching")
    print(f"    - Block timestamp verification")
    return False


def main():
    parser = argparse.ArgumentParser(description="GenTech Receipts — x402 Spending Tracker")
    parser.add_argument("--summary", choices=["daily", "weekly", "monthly"], help="Print summary report")
    parser.add_argument("--verify", action="store_true", help="Verify a receipt")
    parser.add_argument("--tx", help="Transaction hash to verify")
    parser.add_argument("--chain", default="base", help="Chain for verification")
    parser.add_argument("--export", metavar="FILE", help="Export data to JSON file")
    parser.add_argument("--watch", action="store_true", help="Live monitoring mode")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Days of history")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    data = generate_sample_data(args.days)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.verify:
        if not args.tx:
            print("  ❌ --tx required for verification")
            sys.exit(1)
        verify_receipt(args.tx, args.chain, DATA_DIR / "receipts.json")
    elif args.watch:
        run_watch(interval=30, days=args.days)
    elif args.export:
        export_data(data, args.export)
    else:
        print_summary(data, fmt=args.format)

    # Save latest data for dashboard
    if not args.verify and not args.export:
        export_data(data, DATA_DIR / "latest.json")


if __name__ == "__main__":
    main()
