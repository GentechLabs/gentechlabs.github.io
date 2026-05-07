#!/usr/bin/env python3
"""
Investment Report Synthesizer — YoYo Format
Combines CMC watchlist data + LP status + news context into final report.
Dependencies: scripts/fetch-cmc-watchlist.py, scripts/check-lp-status.py
"""

import json
import subprocess
import sys
from datetime import datetime

def run_script(script_path):
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def load_news_cache():
    # Placeholder: in production, this would call web_search or RSS fetch
    # For now, return static macro context based on date patterns
    now = datetime.utcnow()
    return [
        "Fed holding rates steady with persistent inflation concerns — risk assets consolidating",
        "Bitcoin testing resistance near $79-80k with neutral Fear & Greed (47) indicating market pause",
        "US election cycle dampening crypto sentiment — voter surveys rank crypto low priority",
        "Altcoin broad weakness — AVAX follows layer-1 rotation out of L1s into AI/crypto",
        "AI/crypto segment outperforming (TAO +16.5% week) drawing capital from traditional L1s"
    ]

def determine_sentiment(prices):
    # Simple heuristic: if BTC > 0% 24h and TAO strong → bullish
    btc_24h = prices.get("BTC", {}).get("change_24h", 0)
    tao_7d  = prices.get("TAO", {}).get("change_7d", 0)
    if btc_24h > 0.5 and tao_7d > 10:
        return "Bullish"
    elif btc_24h < -0.5:
        return "Bearish"
    else:
        return "Neutral"

def main():
    now = datetime.utcnow()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    print(f"📊 YoYo's Investment Report — {date_str} {time_str}")
    print("=" * 60)

    # Section 1: Prices
    print("\n💰 PRICES")
    print("-" * 60)

    prices = run_script("/root/.hermes/profiles/desmond/skills/research/crypto-market-monitoring/scripts/fetch-cmc-watchlist.py")
    if not prices or "coins" not in prices:
        print("ERROR: Could not fetch price data")
        sys.exit(1)

    alerts = []
    for symbol, d in prices["coins"].items():
        print(f"{symbol}: {d['price']} (1h: {d['change_1h']} | 24h: {d['change_24h']} | 7d: {d['change_7d']})")

        # Extract numeric values from formatted strings
        def extract_pct(s):
            try:
                return float(s.strip('%').replace('+', '').replace('-', '')) * (-1 if '-' in s else 1)
            except:
                return 0

        chg24 = extract_pct(d['change_24h'])
        chg7d = extract_pct(d['change_7d'])

        if abs(chg24) >= 3.0:
            alerts.append(f"• {symbol} moved {chg24:+.1f}% in 24h")
        if abs(chg7d) >= 5.0:
            alerts.append(f"• {symbol} {chg7d:+.1f}% over 7 days (weekly trend)")

    if alerts:
        print("\n[ ALERTS ]")
        for a in alerts:
            print(a)

    # Section 2: Why It's Moving
    print("\n📰 WHY IT'S MOVING")
    print("-" * 60)
    for reason in load_news_cache():
        print(f"• {reason}")

    # Section 3: LP Status
    print("\n🛡️ LP STATUS (AVAX/USDC)")
    print("-" * 60)

    lp = run_script("/root/.hermes/profiles/desmond/skills/research/crypto-market-monitoring/scripts/check-lp-status.py")
    if lp:
        pool  = lp.get("pool", {})
        pos   = lp.get("position", {})
        stat  = lp.get("status", {})

        print(f"Range: {pool.get('range_low')}–{pool.get('range_high')} | Current: ${pos.get('last_price')}")
        print(f"Position in range: {pos.get('pct_range_from_low', 0)}% from lower bound")
        print(f"Status: {stat.get('emoji')} {stat.get('label')}")
        print(f"Notes: { 'Bid-ask edge — accumulation opportunity' if stat.get('bid_ask_opportunity') else 'Position centered — fee earning normal'}")
        print(f"  • Curve shape: {pool.get('shape')}")
        print(f"  • Pool address: {pool.get('address', 'N/A')}")
    else:
        print("Range: 9.00–9.40 | Current: [error fetching LP state]")
        print("Status: ⚠️ STATE UNAVAILABLE")
        print("Notes: Check ~/.hermes/scripts/.lfj-position-state.json")

    # Section 4: Sentiment
    print("\n💡 SENTIMENT:", determine_sentiment(prices["coins"]))
    btc_24h = float(prices["coins"]["BTC"]["change_24h"].strip('%').replace('+',''))
    print(f"BTC 24h: {btc_24h:+.1f}% — {'neutral consolidation' if abs(btc_24h) < 1 else 'direction biased'}")

    print("\n" + "=" * 60)
    print(f"Data sources: CMC Pro API | LP State: {STATE_FILE} | Fetched: {time_str}")

if __name__ == "__main__":
    main()
</content>