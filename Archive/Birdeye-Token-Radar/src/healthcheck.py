"""
Quick API health check — verifies Birdeye connectivity and counts toward BIP min 50 calls.
Run: python src/healthcheck.py
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from radar import BirdeyeClient, SafetyScorer, format_alert
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "config" / ".env")


def main():
    api_key = os.getenv("BIRDEYE_API_KEY", "")
    if not api_key:
        print("❌ BIRDEYE_API_KEY not set")
        print("   Get one at https://bds.birdeye.so")
        sys.exit(1)

    client = BirdeyeClient(api_key)

    print("🔍 Testing Birdeye API connectivity...\n")

    # 1. New listings
    print("1️⃣  Fetching new listings...")
    listings = client.get_new_listings(limit=5)
    if listings:
        print(f"   ✅ Got {len(listings)} new tokens")
        for t in listings[:3]:
            print(f"      • {t.get('name', '?')} (${t.get('symbol', '?')}) — {t.get('address', '?')[:16]}...")
    else:
        print("   ⚠️  No listings returned (may need API key or different chain)")

    # 2. Security check on first token
    if listings:
        addr = listings[0].get("address", "")
        print(f"\n2️⃣  Security check on {listings[0].get('name', '?')}...")
        time.sleep(0.5)
        security = client.get_token_security(addr)
        if security:
            score = SafetyScorer.score(security, listings[0].get("liquidityAddedAt"))
            print(f"   ✅ Safety score: {score['total']}/100 {score['grade']}")
            if score["flags"]:
                for f in score["flags"]:
                    print(f"      {f}")
        else:
            print("   ⚠️  No security data returned")

        # 3. Overview
        print(f"\n3️⃣  Token overview...")
        time.sleep(0.5)
        overview = client.get_token_overview(addr)
        if overview:
            price = overview.get("priceUsd") or overview.get("value")
            mcap = overview.get("mc")
            print(f"   ✅ Price: ${price}" if price else "   ⚠️  No price")
            print(f"   ✅ MCap: ${mcap:,.0f}" if mcap else "   ⚠️  No mcap")
        else:
            print("   ⚠️  No overview data")

    print(f"\n📊 Total API calls made: {client.call_count}")
    print("   (Need 50+ for BIP competition — run radar.py --watch to accumulate)")

    # 4. Sample formatted alert
    if listings and security:
        print("\n📱 Sample Telegram alert:")
        print("─" * 40)
        print(format_alert(listings[0], security, score, overview))

    print("\n✅ Health check complete!")


if __name__ == "__main__":
    main()
