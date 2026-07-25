#!/usr/bin/env python3
"""
Monid Social Intel — AAE Narrative Rotation Monitor
Track mention velocity, sentiment, and trends across platforms.

Usage:
    python monitor.py --scan          # Quick narrative scan
    python monitor.py --report weekly # Weekly report
    python monitor.py --watch         # Live monitoring
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

SAMPLE_DATA = {
    "period_start": (datetime.now() - timedelta(days=2)).isoformat(),
    "period_end": datetime.now().isoformat(),
    "total_mentions": 47,
    "platforms": {
        "X": {"mentions": 24, "sentiment": 3.4, "engagement": 1280, "top_posts": [
            {"url": "https://x.com/user/status/1", "text": "AAE is the next evolution of agent economies", "likes": 89},
            {"url": "https://x.com/user/status/2", "text": "x402 compliant agents are the new standard", "likes": 64},
        ]},
        "Farcaster": {"mentions": 12, "sentiment": 3.1, "engagement": 340, "top_posts": [
            {"url": "https://warpcast.com/...", "text": "building on AAE with GenTech's stack", "likes": 28},
        ]},
        "Reddit": {"mentions": 8, "sentiment": 2.8, "engagement": 190, "top_posts": [
            {"url": "https://reddit.com/r/...", "text": "Anyone using GenTech for agent payments?", "likes": 15},
        ]},
        "Lens": {"mentions": 3, "sentiment": 3.5, "engagement": 45, "top_posts": []},
    },
    "keywords": {
        "AAE": {"mentions": 22, "trend": "stable"},
        "x402": {"mentions": 18, "trend": "rising"},
        "Q402": {"mentions": 7, "trend": "new"},
        "CLARITY Act": {"mentions": 12, "trend": "rising"},
        "GenTech": {"mentions": 14, "trend": "stable"},
    },
    "co_occurrences": [
        {"topic": "x402 compliance", "mentions": 12, "signal": "publish"},
        {"topic": "agent identity", "mentions": 8, "signal": "note"},
        {"topic": "CLARITY Act regulation", "mentions": 7, "signal": "publish"},
    ],
    "daily_trend": [],
    "signals": [
        {"type": "publish", "priority": "high", "message": "x402/gateway narrative gaining — publish technical content within 4h"},
        {"type": "publish", "priority": "medium", "message": "CLARITY Act/AAE co-occurence detected — compliance angle is hot"},
        {"type": "note", "priority": "low", "message": "Reddit mentions up 40% — consider AMA or technical writeup"},
    ],
}


def generate_sample_data(days=7):
    data = json.loads(json.dumps(SAMPLE_DATA))
    now = datetime.now()
    base_mentions = 35
    for i in range(days):
        day = now - timedelta(days=days - 1 - i)
        variation = 1.0 + (i % 3 - 1) * 0.2
        data["daily_trend"].append({
            "date": day.strftime("%Y-%m-%d"),
            "mentions": int(base_mentions * variation),
            "sentiment": round(2.5 + (i % 5) * 0.2, 2),
        })
    return data


def print_scan(data):
    s = data
    tot = s["total_mentions"]
    sentiment = sum(p["sentiment"] * p["mentions"] for p in s["platforms"].values()) / tot

    print("┌─ AAE Narrative Scan ──────────────────────────────────┐")
    print(f"  Period:    {s['period_start'][:10]} → {s['period_end'][:10]}")
    print(f"  Mentions:  {tot} total")
    platforms_str = ", ".join(f"{p} ({d['mentions']})" for p, d in s["platforms"].items())
    print(f"  Platforms: {platforms_str}")
    print(f"  Sentiment: {sentiment:.1f}:1 positive")
    
    # Trend
    if s["daily_trend"]:
        prev = s["daily_trend"][-2]["mentions"] if len(s["daily_trend"]) > 1 else 0
        curr = s["daily_trend"][-1]["mentions"]
        change = ((curr - prev) / prev * 100) if prev > 0 else 0
        print(f"  Velocity:  {'+' if change >= 0 else ''}{change:.0f}% vs yesterday")

    # Top keyword trend
    rising = [k for k, v in s["keywords"].items() if v["trend"] == "rising"]
    if rising:
        print(f"  Rising:    {', '.join(rising)}")

    # Signals
    print()
    print("┌─ Signals ─────────────────────────────────────────────┐")
    for sig in s["signals"]:
        icon = {"publish": "🔴", "note": "🟡", "ignore": "⚪"}.get(sig["type"], "⚪")
        print(f"  {icon} [{sig['priority'].upper()}] {sig['message']}")

    # Platform breakdown
    print()
    print("┌─ By Platform ─────────────────────────────────────────┐")
    for p, d in sorted(s["platforms"].items(), key=lambda x: x[1]["mentions"], reverse=True):
        bar = "█" * int(max(1, d["sentiment"] * 3))
        print(f"  {p:<12} {d['mentions']:>3} mentions  ♥{bar} ({d['sentiment']:.1f})  {d['engagement']} eng.")


def print_report(data):
    """Weekly report with more detail."""
    print_scan(data)
    
    print()
    print("┌─ Co-Occurrences ──────────────────────────────────────┐")
    for co in data["co_occurrences"]:
        icon = {"publish": "🔴", "note": "🟡"}.get(co["signal"], "⚪")
        print(f"  {icon} \"{co['topic']}\" — {co['mentions']} mentions")
    
    print()
    print("┌─ Daily Trend ─────────────────────────────────────────┐")
    for d in data["daily_trend"]:
        bar = "█" * max(1, d["mentions"] // 3)
        print(f"  {d['date']}  {d['mentions']:>3} mentions  {bar}  (♥{d['sentiment']:.1f})")


def run_watch(interval=3600):
    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            data = generate_sample_data()
            print_scan(data)
            print(f"\n  🔄 Next scan in {interval}s — Ctrl+C to stop")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Stopped.")


def main():
    parser = argparse.ArgumentParser(description="Monid Social Intel — AAE Narrative Monitor")
    parser.add_argument("--scan", action="store_true", help="Quick narrative scan")
    parser.add_argument("--report", choices=["daily", "weekly"], help="Generate report")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    data = generate_sample_data(args.days)

    if args.format == "json":
        print(json.dumps(data, indent=2))
        return

    if args.watch:
        run_watch()
    elif args.report:
        print_report(data)
    else:
        print_scan(data)


if __name__ == "__main__":
    main()
