#!/usr/bin/env python3
"""
Token Launch Script for Swarms ACM Hackathon
Launches the DeFi Signal Agent on Swarms Marketplace via Frenzy Mode API.

Requirements:
- SWARMS_API_KEY (from swarms.world/platform/api-keys)
- Solana wallet with >= 0.04 SOL (~$6) for transaction fees

Usage:
  export SWARMS_API_KEY=your_key_here
  python launch_token.py
"""

import os
import json
import urllib.request

# ── Configuration ──────────────────────────────────────────────────────────

LAUNCH_URL = "https://swarms.world/api/token/launch"

# Load Solana private key from local wallet
def load_solana_key():
    key_path = os.path.expanduser("~/.config/solana/id.json")
    if not os.path.exists(key_path):
        print("ERROR: No Solana wallet found at ~/.config/solana/id.json")
        print("Run: solana-keygen new --outfile ~/.config/solana/id.json")
        exit(1)
    with open(key_path) as f:
        return json.load(f)

# Agent metadata
AGENT_CONFIG = {
    "name": "DeFi Signal Agent",
    "description": (
        "On-chain DeFi intelligence agent for concentrated liquidity LP monitoring. "
        "Real-time impermanent loss tracking, fee efficiency scoring, whale detection, "
        "yield opportunity scanning, and actionable rebalance recommendations. "
        "Supports LFJ (Avalanche), Uniswap V3 (Ethereum/Base), and any DexScreener pool. "
        "7 signal tools: price fetch, pool state, IL calc, recommendations, position reports, "
        "whale watch, and yield scanner."
    ),
    "ticker": "DEFI",
    "fee_selection": "frenzy",
    "quote_mint": "SOL",
}

# ── Launch ─────────────────────────────────────────────────────────────────

def main():
    api_key = os.getenv("SWARMS_API_KEY")
    if not api_key:
        print("ERROR: SWARMS_API_KEY not set")
        print("Get one from: https://swarms.world/platform/api-keys")
        print("Then run: export SWARMS_API_KEY=your_key_here")
        exit(1)

    private_key = load_solana_key()

    # Build payload
    payload = {
        **AGENT_CONFIG,
        "private_key": private_key,
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        LAUNCH_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    print("Launching DeFi Signal Agent in Frenzy Mode...")
    print(f"  Name: {AGENT_CONFIG['name']}")
    print(f"  Ticker: ${AGENT_CONFIG['ticker']}")
    print(f"  Fee mode: Frenzy (2x bonding curve fees)")
    print(f"  Quote: {AGENT_CONFIG['quote_mint']}")
    print()

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            print("✅ Token launched successfully!")
            print(f"  Agent ID: {result.get('id', '?')}")
            print(f"  Listing URL: {result.get('listing_url', '?')}")
            print(f"  Token address: {result.get('token_address', '?')}")
            print(f"  Pool address: {result.get('pool_address', '?')}")
            print()
            print("Next steps:")
            print("  1. Visit the listing URL to verify the marketplace page")
            print("  2. Record a demo video showing the agent in action")
            print("  3. Submit to the ACM Hackathon before May 27")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: HTTP {e.code}")
        try:
            err = json.loads(body)
            print(f"  {err.get('error', 'Unknown')}")
            print(f"  {err.get('message', '')}")
        except json.JSONDecodeError:
            print(f"  {body}")
        exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
