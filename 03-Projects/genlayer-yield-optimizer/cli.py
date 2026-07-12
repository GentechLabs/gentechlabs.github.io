#!/usr/bin/env python3
"""
DeFi Yield Optimizer — CLI Client
==================================
Interact with the YieldOptimizer GenLayer contract from the command line.

Usage:
    python cli.py scan [--protocol FILTER]
    python cli.py recommend [--protocol aave] [--pool POOL_ID] [--chain ethereum] [--apy 3.5] [--value 10000]
    python cli.py rebalance --from PROTOCOL --to PROTOCOL --from-pool POOL --to-pool POOL --amount AMOUNT [--reason "text"]
    python cli.py gas-status
    python cli.py deposit AMOUNT_ETH
    python cli.py history
    python cli.py stats
    python cli.py compare

Part of GenLayer Builder Program — Intelligent Contract Templates.
Built by GenTech Labs.
"""

import argparse
import json
import sys
import os
from datetime import datetime

try:
    from genlayer_js import GenLayerClient
    HAS_SDK = True
except ImportError:
    HAS_SDK = False


# ─── Contract Address (set after deployment) ────────────────────────────────
CONTRACT_ADDRESS = os.environ.get("YIELD_OPTIMIZER_ADDRESS", "")


def format_wei(wei: int) -> str:
    """Format wei to human-readable ETH."""
    eth = wei / 10**18
    if eth < 0.001:
        return f"{wei} wei"
    elif eth < 1:
        return f"{eth:.6f} ETH"
    else:
        return f"{eth:.4f} ETH"


def format_usd(value: float) -> str:
    """Format USD value."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"


def print_json(data: dict, indent: int = 2):
    """Pretty-print JSON output."""
    print(json.dumps(data, indent=indent, default=str))


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_table(headers: list, rows: list):
    """Print a simple table."""
    if not rows:
        print("  No data available.")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Print header
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(f"  {header_line}")
    print(f"  {'─' * len(header_line)}")

    # Print rows
    for row in rows:
        line = "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        print(f"  {line}")


# ─── Commands ───────────────────────────────────────────────────────────────

def cmd_scan(args):
    """Fetch and display current yield data."""
    print_header("📊 Yield Scan — DeFi Llama")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Running in demo mode.")
        print("  Install: pip install genlayer-js")
        print()
        # Demo: fetch directly from DeFi Llama
        import urllib.request
        url = "https://yields.llama.fi/pools"
        print(f"  Fetching from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GenLayer-YieldOptimizer/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"  ❌ API error: {e}")
            return

        pools = data.get("data", [])

        # Filter
        if args.protocol:
            pools = [p for p in pools if args.protocol.lower() in p.get("project", "").lower()]

        pools = [p for p in pools if p.get("tvlUsd", 0) > 100_000 and 0 < p.get("apy", 0) < 1000]
        pools.sort(key=lambda x: x.get("apy", 0), reverse=True)

        print(f"\n  Found {len(pools)} qualifying pools")
        if args.protocol:
            print(f"  Filter: {args.protocol}")
        print()

        headers = ["Protocol", "Symbol", "Chain", "APY", "TVL", "Stablecoin"]
        rows = []
        for p in pools[:15]:
            rows.append([
                p.get("project", "?")[:20],
                p.get("symbol", "?")[:15],
                p.get("chain", "?")[:10],
                f"{p.get('apy', 0):.2f}%",
                format_usd(p.get("tvlUsd", 0)),
                "✓" if p.get("stablecoin") else "",
            ])

        print_table(headers, rows)
        return

    # Live contract call
    client = GenLayerClient()
    result = client.call_contract(
        CONTRACT_ADDRESS,
        "scan_yields",
        args=[args.protocol or ""]
    )

    print(f"  Pools fetched: {result['pools_fetched']}")
    print(f"  Pools cached:  {result['pools_cached']}")
    print(f"  Filter:        {result['protocol_filter']}")
    print()

    headers = ["Protocol", "Symbol", "Chain", "APY", "TVL", "Stablecoin"]
    rows = []
    for p in result.get("top_yields", []):
        rows.append([
            p["protocol"][:20],
            p["symbol"][:15],
            p["chain"][:10],
            f"{p['apy']:.2f}%",
            format_usd(p["tvl_usd"]),
            "✓" if p.get("stablecoin") else "",
        ])

    print_table(headers, rows)


def cmd_recommend(args):
    """Get LLM-powered yield recommendation."""
    print_header("🧠 Yield Recommendation")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio for live recommendations.")
        print("  Set YIELD_OPTIMIZER_ADDRESS env var after deployment.")
        return

    client = GenLayerClient()
    result = client.call_contract(
        CONTRACT_ADDRESS,
        "get_recommendation",
        args=[
            args.protocol or "",
            args.pool or "",
            args.chain or "",
            args.apy or 0.0,
            args.value or 0.0,
        ]
    )

    print(f"  Status:    {result.get('status', 'unknown')}")
    print(f"  Analysis:  {result.get('analysis_type', 'unknown')}")
    print()
    print(f"  Current APY:    {result.get('current_yield', 0):.2f}%")
    print(f"  Best APY:       {result.get('best_yield', 0):.2f}%")
    print(f"  Improvement:    {result.get('improvement_pct', 0):.2f}%")
    print(f"  Worthwhile:     {'✅ Yes' if result.get('rebalance_worthwhile') else '❌ No'}")
    print(f"  Gas Status:     {result.get('gas_status', 'unknown')}")
    print()

    if result.get("recommendation"):
        print(f"  💡 Recommendation:")
        print(f"     {result['recommendation']}")
        print()

    if result.get("risk_assessment"):
        print(f"  ⚠️  Risk Assessment:")
        print(f"     {result['risk_assessment']}")
        print()

    if result.get("top_opportunities"):
        print(f"  🎯 Top Opportunities:")
        for i, opp in enumerate(result["top_opportunities"][:3], 1):
            print(f"     {i}. {opp.get('protocol', '?')} — {opp.get('symbol', '?')} on {opp.get('chain', '?')}")
            print(f"        APY: {opp.get('apy', 0):.2f}% | TVL: {format_usd(opp.get('tvl_usd', 0))} | Risk: {opp.get('risk_level', '?')}")
            if opp.get("reason"):
                print(f"        {opp['reason']}")
        print()


def cmd_rebalance(args):
    """Execute a rebalance action."""
    print_header("🔄 Execute Rebalance")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    # Confirmation
    print(f"  From:  {args.from_protocol} ({args.from_pool})")
    print(f"  To:    {args.to_protocol} ({args.to_pool})")
    print(f"  Amount: {args.amount}")
    if args.reason:
        print(f"  Reason: {args.reason}")
    print()

    confirm = input("  Confirm rebalance? [y/N]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    client = GenLayerClient()
    result = client.call_contract(
        CONTRACT_ADDRESS,
        "execute_rebalance",
        args=[
            args.from_protocol,
            args.to_protocol,
            args.from_pool,
            args.to_pool,
            int(args.amount),
            args.reason or "",
        ]
    )

    if result.get("status") == "success":
        print(f"  ✅ Rebalance #{result['rebalance_id']} executed!")
        print(f"     APY: {result['apy_before']:.2f}% → {result['apy_after']:.2f}%")
        print(f"     Gas cost: {format_wei(result['gas_cost'])}")
        print(f"     Gas remaining: {format_wei(result['gas_remaining'])}")
        if result.get("needs_gas_topup"):
            print(f"     ⚠️  {result['message']}")
        else:
            print(f"     ✅ {result['message']}")
    else:
        print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
        if result.get("message"):
            print(f"     {result['message']}")


def cmd_gas_status(args):
    """Check gas escrow status."""
    print_header("⛽ Gas Escrow Status")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    client = GenLayerClient()
    result = client.call_contract(CONTRACT_ADDRESS, "get_gas_status")

    if not result.get("has_vault"):
        print(f"  {result['message']}")
        return

    print(f"  Balance:           {result['gas_balance_eth']:.6f} ETH")
    print(f"  Threshold:         {result['gas_threshold_eth']:.6f} ETH")
    print(f"  Cost per rebalance: {result['gas_cost_per_rebalance_eth']:.6f} ETH")
    print(f"  Remaining actions: {result['remaining_rebalances']}")
    print(f"  Total deposited:   {result['total_deposited_eth']:.6f} ETH")
    print(f"  Total spent:       {result['total_spent_eth']:.6f} ETH")
    print(f"  Rebalance count:   {result['rebalance_count']}")
    print()
    print(f"  Status: {result['status']}")


def cmd_deposit(args):
    """Deposit gas to escrow."""
    print_header("💰 Deposit Gas")

    amount_eth = float(args.amount)
    amount_wei = int(amount_eth * 10**18)

    print(f"  Depositing {amount_eth:.6f} ETH to gas escrow...")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    client = GenLayerClient()
    result = client.call_contract(
        CONTRACT_ADDRESS,
        "deposit_gas_escrow",
        value=amount_wei
    )

    if result.get("status") == "success":
        print(f"  ✅ {result['message']}")
    else:
        print(f"  ❌ Error: {result.get('error', 'Unknown')}")


def cmd_history(args):
    """View rebalance history."""
    print_header("📜 Rebalance History")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    client = GenLayerClient()
    result = client.call_contract(CONTRACT_ADDRESS, "get_user_history")

    if result.get("rebalance_count", 0) == 0:
        print("  No rebalances yet.")
        return

    print(f"  Total rebalances: {result['rebalance_count']}")
    print(f"  Total gas spent:  {format_wei(result['total_gas_spent'])}")
    print()

    headers = ["#", "From", "To", "APY Before", "APY After", "Gas Cost"]
    rows = []
    for i, h in enumerate(result.get("history", []), 1):
        rows.append([
            i,
            h["from_protocol"][:15],
            h["to_protocol"][:15],
            f"{h['apy_before']:.2f}%",
            f"{h['apy_after']:.2f}%",
            format_wei(h["gas_cost"]),
        ])

    print_table(headers, rows)


def cmd_stats(args):
    """View global contract statistics."""
    print_header("📈 Contract Statistics")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    client = GenLayerClient()
    result = client.call_contract(CONTRACT_ADDRESS, "get_total_stats")

    print(f"  Total rebalances:     {result['total_rebalances']}")
    print(f"  Gas deposited:        {result['total_gas_deposited_eth']:.6f} ETH")
    print(f"  Gas spent:            {result['total_gas_spent_eth']:.6f} ETH")
    print(f"  Active vaults:        {result['active_vaults']}")
    print(f"  Cached pools:         {result['cached_pools']}")
    if result.get("last_yield_scan"):
        scan_time = datetime.fromtimestamp(result["last_yield_scan"])
        print(f"  Last yield scan:      {scan_time.strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_compare(args):
    """View yield comparison across protocols."""
    print_header("⚖️  Protocol Yield Comparison")

    if not HAS_SDK:
        print("  ⚠️  GenLayer SDK not installed. Connect to GenLayer Studio.")
        return

    client = GenLayerClient()
    result = client.call_contract(CONTRACT_ADDRESS, "get_yield_comparison")

    if result.get("cached_pools", 0) == 0:
        print(f"  {result.get('message', 'No data. Run scan_yields() first.')}")
        return

    print(f"  Cached pools: {result['cached_pools']} across {result['protocol_count']} protocols")
    print()

    headers = ["Protocol", "Pools", "Best APY", "Avg APY", "Total TVL", "Risk"]
    rows = []
    for p in result.get("protocols", []):
        rows.append([
            p["protocol"][:20],
            p["pool_count"],
            f"{p['best_apy']:.2f}%",
            f"{p['avg_apy']:.2f}%",
            format_usd(p["total_tvl"]),
            p["risk_score"],
        ])

    print_table(headers, rows)


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DeFi Yield Optimizer — CLI Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py scan                          # Scan all yields
  python cli.py scan --protocol aave          # Scan Aave only
  python cli.py recommend                     # Get recommendation (no position)
  python cli.py recommend --protocol aave --apy 3.5 --value 10000
  python cli.py deposit 0.01                  # Deposit 0.01 ETH gas
  python cli.py gas-status                    # Check gas balance
  python cli.py rebalance --from aave --to curve --from-pool 1 --to-pool 2 --amount 1000
  python cli.py history                       # View past rebalances
  python cli.py stats                         # Global stats
  python cli.py compare                       # Protocol comparison
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # scan
    scan_p = subparsers.add_parser("scan", help="Fetch current yields from DeFi Llama")
    scan_p.set_defaults(func=cmd_scan)
    scan_p.add_argument("--protocol", help="Filter by protocol name")

    # recommend
    rec_p = subparsers.add_parser("recommend", help="Get LLM yield recommendation")
    rec_p.set_defaults(func=cmd_recommend)
    rec_p.add_argument("--protocol", help="Your current protocol")
    rec_p.add_argument("--pool", help="Your current pool ID")
    rec_p.add_argument("--chain", help="Your current chain")
    rec_p.add_argument("--apy", type=float, help="Your current APY")
    rec_p.add_argument("--value", type=float, help="Position value in USD")

    # rebalance
    reb_p = subparsers.add_parser("rebalance", help="Execute a rebalance")
    reb_p.set_defaults(func=cmd_rebalance)
    reb_p.add_argument("--from", dest="from_protocol", required=True, help="Source protocol")
    reb_p.add_argument("--to", dest="to_protocol", required=True, help="Target protocol")
    reb_p.add_argument("--from-pool", required=True, help="Source pool ID")
    reb_p.add_argument("--to-pool", required=True, help="Target pool ID")
    reb_p.add_argument("--amount", required=True, help="Amount to rebalance")
    reb_p.add_argument("--reason", help="Reason for rebalance")

    # gas-status
    gas_p = subparsers.add_parser("gas-status", help="Check gas escrow status")
    gas_p.set_defaults(func=cmd_gas_status)

    # deposit
    dep_p = subparsers.add_parser("deposit", help="Deposit gas to escrow")
    dep_p.set_defaults(func=cmd_deposit)
    dep_p.add_argument("amount", help="Amount in ETH")

    # history
    hist_p = subparsers.add_parser("history", help="View rebalance history")
    hist_p.set_defaults(func=cmd_history)

    # stats
    stats_p = subparsers.add_parser("stats", help="Global contract statistics")
    stats_p.set_defaults(func=cmd_stats)

    # compare
    comp_p = subparsers.add_parser("compare", help="Protocol yield comparison")
    comp_p.set_defaults(func=cmd_compare)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
