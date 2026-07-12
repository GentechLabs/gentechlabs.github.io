#!/usr/bin/env python3
"""
DeFi Yield Optimizer — Monitoring Agent
========================================
Standalone monitoring script that scans yields, detects opportunities,
and alerts when rebalancing would be beneficial.

Designed to run as a cron job or background process.

Usage:
    python monitor.py                    # Single scan
    python monitor.py --loop             # Continuous monitoring
    python monitor.py --interval 3600    # Hourly checks
    python monitor.py --threshold 1.0    # Alert if APY improvement > 1%
    python monitor.py --min-tvl 500000   # Only pools with > $500K TVL
    python monitor.py --notify tg        # Send alerts to Telegram
    python monitor.py --output report.json  # Save report to file

Environment:
    YIELD_OPTIMIZER_ADDRESS  — Contract address (for on-chain actions)
    TELEGRAM_BOT_TOKEN       — For Telegram notifications
    TELEGRAM_CHAT_ID         — Target chat for alerts

Part of GenLayer Builder Program — Intelligent Contract Templates.
Built by GenTech Labs.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ─────────────────────────────────────────────────────────────────

DEFAULT_MIN_TVL = 100_000        # $100K minimum TVL
DEFAULT_MIN_APY = 0.5            # Minimum APY to consider
DEFAULT_ALERT_IMPROVEMENT = 1.0  # Alert if APY improvement > 1%
DEFAULT_INTERVAL = 3600          # 1 hour between scans
MAX_POOLS_FETCHED = 500          # Max pools to process

PROTOCOL_RISK = {
    "aave": 85, "compound": 85, "curve": 80, "uniswap": 80,
    "convex": 75, "yearn": 70, "beefy": 70, "pendle": 65,
    "gmx": 60, "default": 50,
}

# ─── Data Fetching ──────────────────────────────────────────────────────────

import urllib.request
import urllib.error

DEFILLAMA_YIELDS_URL = "https://yields.llama.fi/pools"


def fetch_yields(protocol_filter: str = "", min_tvl: float = DEFAULT_MIN_TVL) -> list:
    """Fetch yield data from DeFi Llama API."""
    print(f"  📡 Fetching yields from DeFi Llama...")
    try:
        req = urllib.request.Request(
            DEFILLAMA_YIELDS_URL,
            headers={"User-Agent": "GenLayer-YieldOptimizer/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return []

    pools = data.get("data", [])

    # Filter
    if protocol_filter:
        pools = [p for p in pools if protocol_filter.lower() in p.get("project", "").lower()]

    pools = [
        p for p in pools
        if p.get("tvlUsd", 0) > min_tvl
        and 0 < p.get("apy", 0) < 1000
    ]

    pools.sort(key=lambda x: x.get("apy", 0), reverse=True)
    return pools[:MAX_POOLS_FETCHED]


def get_risk_score(protocol: str) -> int:
    """Get deterministic risk score for a protocol."""
    protocol_lower = protocol.lower()
    for key, score in PROTOCOL_RISK.items():
        if key in protocol_lower:
            return score
    return PROTOCOL_RISK["default"]


def score_pool(pool: dict) -> float:
    """Score a pool for risk-adjusted yield."""
    apy = pool.get("apy", 0)
    tvl = pool.get("tvlUsd", 0)
    protocol = pool.get("project", "default")
    risk = get_risk_score(protocol) / 100.0
    tvl_factor = min(1.0, tvl / 10_000_000)
    stablecoin_bonus = 1.2 if pool.get("stablecoin", False) else 1.0
    return apy * risk * tvl_factor * stablecoin_bonus


# ─── Analysis ───────────────────────────────────────────────────────────────

def analyze_yields(pools: list, current_protocol: str = "", current_apy: float = 0.0,
                   alert_threshold: float = DEFAULT_ALERT_IMPROVEMENT) -> dict:
    """Analyze yields and find opportunities."""
    if not pools:
        return {
            "opportunities": [],
            "best_score": 0,
            "best_pool": None,
            "improvement": 0,
            "alert": False,
        }

    # Score and rank
    scored = []
    for p in pools:
        s = score_pool(p)
        scored.append({
            "pool": p,
            "score": s,
            "risk_score": get_risk_score(p.get("project", "default")),
            "risk_level": "LOW" if get_risk_score(p.get("project", "default")) >= 80 else
                         "MEDIUM" if get_risk_score(p.get("project", "default")) >= 60 else "HIGH"
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    best = scored[0]
    best_apy = best["pool"].get("apy", 0)

    # Calculate improvement
    improvement = best_apy - current_apy if current_apy > 0 else best_apy

    # Top opportunities
    opportunities = []
    for s in scored[:5]:
        p = s["pool"]
        opportunities.append({
            "protocol": p.get("project", "unknown"),
            "symbol": p.get("symbol", "???"),
            "chain": p.get("chain", "unknown"),
            "apy": round(p.get("apy", 0), 2),
            "tvl_usd": round(p.get("tvlUsd", 0)),
            "risk_level": s["risk_level"],
            "risk_score": s["risk_score"],
            "score": round(s["score"], 2),
            "stablecoin": p.get("stablecoin", False),
            "pool_id": p.get("pool", ""),
        })

    return {
        "opportunities": opportunities,
        "best_score": round(best["score"], 2),
        "best_pool": best["pool"].get("pool", ""),
        "best_protocol": best["pool"].get("project", ""),
        "best_apy": round(best_apy, 2),
        "improvement": round(improvement, 2),
        "alert": improvement >= alert_threshold,
        "total_pools": len(pools),
    }


def generate_report(pools: list, analysis: dict, protocol_filter: str = "") -> dict:
    """Generate a monitoring report."""
    now = datetime.now(timezone.utc)

    # Protocol breakdown
    protocols = {}
    for p in pools:
        proto = p.get("project", "unknown")
        if proto not in protocols:
            protocols[proto] = {"count": 0, "best_apy": 0, "total_tvl": 0}
        protocols[proto]["count"] += 1
        protocols[proto]["best_apy"] = max(protocols[proto]["best_apy"], p.get("apy", 0))
        protocols[proto]["total_tvl"] += p.get("tvlUsd", 0)

    # Stablecoin vs volatile
    stable_pools = [p for p in pools if p.get("stablecoin")]
    volatile_pools = [p for p in pools if not p.get("stablecoin")]

    report = {
        "timestamp": now.isoformat(),
        "scan_summary": {
            "total_pools": len(pools),
            "protocol_filter": protocol_filter or "all",
            "protocols_tracked": len(protocols),
            "stablecoin_pools": len(stable_pools),
            "volatile_pools": len(volatile_pools),
        },
        "top_10": [{
            "protocol": p.get("project", "unknown"),
            "symbol": p.get("symbol", "???"),
            "chain": p.get("chain", "unknown"),
            "apy": round(p.get("apy", 0), 2),
            "tvl_usd": round(p.get("tvlUsd", 0)),
            "stablecoin": p.get("stablecoin", False),
        } for p in pools[:10]],
        "analysis": analysis,
        "protocol_summary": {
            proto: {
                "pools": info["count"],
                "best_apy": round(info["best_apy"], 2),
                "total_tvl": round(info["total_tvl"]),
            }
            for proto, info in sorted(protocols.items(), key=lambda x: x[1]["best_apy"], reverse=True)[:20]
        },
    }

    return report


# ─── Notifications ──────────────────────────────────────────────────────────

def send_telegram_alert(message: str, token: str = "", chat_id: str = ""):
    """Send alert to Telegram."""
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("  ⚠️  Telegram credentials not set. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print("  📱 Telegram alert sent!")
                return True
            else:
                print(f"  ❌ Telegram error: {result}")
                return False
    except Exception as e:
        print(f"  ❌ Telegram send failed: {e}")
        return False


def format_alert(analysis: dict, report: dict) -> str:
    """Format analysis into a Telegram-friendly alert message."""
    lines = []
    lines.append("📊 *Yield Optimizer Alert*")
    lines.append(f"_{report['scan_summary']['total_pools']} pools scanned across {report['scan_summary']['protocols_tracked']} protocols_")
    lines.append("")

    if analysis.get("alert"):
        lines.append("🚨 *OPPORTUNITY DETECTED*")
        lines.append(f"Best: *{analysis['best_protocol']}* — {analysis['best_apy']}% APY")
        lines.append(f"Improvement: *+{analysis['improvement']}%*")
        lines.append("")
    else:
        lines.append(f"Best yield: {analysis.get('best_protocol', 'N/A')} at {analysis.get('best_apy', 0)}%")

    lines.append("*Top 5 Opportunities:*")
    for i, opp in enumerate(analysis.get("opportunities", [])[:5], 1):
        stable = " 🪙" if opp.get("stablecoin") else ""
        lines.append(
            f"{i}. `{opp['protocol']}` — {opp['symbol']} ({opp['chain']})"
            f"\n   {opp['apy']}% APY | TVL: ${opp['tvl_usd']:,} | Risk: {opp['risk_level']}{stable}"
        )

    lines.append(f"\n_Scan at {report['timestamp'][:19]}Z_")
    return "\n".join(lines)


# ─── Main Loop ──────────────────────────────────────────────────────────────

def run_scan(args) -> dict:
    """Run a single scan cycle."""
    print(f"\n{'='*60}")
    print(f"  🔍 Yield Scan — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}")

    # Fetch
    pools = fetch_yields(args.protocol, args.min_tvl)
    if not pools:
        print("  No pools found.")
        return {}

    print(f"  ✅ {len(pools)} qualifying pools found")

    # Analyze
    analysis = analyze_yields(pools, args.current_protocol, args.current_apy, args.threshold)

    # Report
    report = generate_report(pools, analysis, args.protocol)

    # Display
    print(f"\n  📈 Top 10 Yields:")
    for i, p in enumerate(report["top_10"], 1):
        stable = " 🪙" if p["stablecoin"] else ""
        print(f"  {i:2d}. {p['protocol'][:15]:15s} {p['symbol'][:12]:12s} {p['chain'][:10]:10s} "
              f"{p['apy']:8.2f}%  ${p['tvl_usd']:>12,.0f}{stable}")

    print(f"\n  🎯 Best Opportunity:")
    print(f"     Protocol:  {analysis.get('best_protocol', 'N/A')}")
    print(f"     APY:       {analysis.get('best_apy', 0):.2f}%")
    print(f"     Score:     {analysis.get('best_score', 0)}")
    if args.current_apy > 0:
        print(f"     Improvement: +{analysis.get('improvement', 0):.2f}%")

    if analysis.get("alert"):
        print(f"\n  🚨 ALERT: Significant yield improvement detected!")

        # Send notification
        if args.notify:
            alert_msg = format_alert(analysis, report)
            if args.notify == "tg":
                send_telegram_alert(alert_msg)

    # Save report
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n  💾 Report saved to {args.output}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="DeFi Yield Optimizer — Monitoring Agent"
    )
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Seconds between scans (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--protocol", default="", help="Filter by protocol")
    parser.add_argument("--min-tvl", type=float, default=DEFAULT_MIN_TVL,
                        help=f"Minimum TVL in USD (default: {DEFAULT_MIN_TVL})")
    parser.add_argument("--threshold", type=float, default=DEFAULT_ALERT_IMPROVEMENT,
                        help=f"Alert threshold for APY improvement (default: {DEFAULT_ALERT_IMPROVEMENT}%)")
    parser.add_argument("--current-protocol", default="", help="Your current protocol")
    parser.add_argument("--current-apy", type=float, default=0.0, help="Your current APY")
    parser.add_argument("--notify", choices=["tg", "none"], default="none",
                        help="Notification method")
    parser.add_argument("--output", default="", help="Save report to JSON file")

    args = parser.parse_args()

    if args.loop:
        print(f"  🔄 Starting continuous monitoring (interval: {args.interval}s)")
        while True:
            try:
                run_scan(args)
            except KeyboardInterrupt:
                print("\n  ⏹  Monitoring stopped.")
                break
            except Exception as e:
                print(f"\n  ❌ Error: {e}")

            print(f"\n  ⏳ Next scan in {args.interval}s...")
            time.sleep(args.interval)
    else:
        run_scan(args)


if __name__ == "__main__":
    main()
