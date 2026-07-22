#!/usr/bin/env python3
"""
DeFi Rebalance Suggestion Engine
Fetches live AVAX price, calculates rebalance signals, updates dashboard data.
Designed for cron: 1:00pm + 8:30pm EST daily.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

# === CONFIG ===
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
VAULT_PATH = "/root/vaults/gentech"
HUB_PATH = f"{VAULT_PATH}/hub.html"
DATA_PATH = f"{VAULT_PATH}/defi-data.json"

# Position constants (sync with hub.html)
RANGE_LOW = 6.70
RANGE_HIGH = 6.88
SHAPE = "bid-ask"
AVAX_HELD = 3.812
USDC_HELD = 18.73
DAILY_FEES = 0.364  # estimated from last known

# Milestones
MILESTONES = {
    "Scout": 5,
    "Raider": 20,
    "Warlord": 55,
    "Fisher": 100,
    "Sovereign": 200,
}


def fetch_price():
    """Fetch live AVAX price from DexScreener."""
    import urllib.request
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL_ADDRESS}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GenTech/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pair = data.get("pairs", [{}])[0]
            return {
                "price": float(pair.get("priceNative", 0)),
                "change24h": float(pair.get("priceChange", {}).get("h24", 0)),
                "volume24h": float(pair.get("volume", {}).get("h24", 0)),
                "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
            }
    except Exception as e:
        print(f"ERROR: Price fetch failed: {e}", file=sys.stderr)
        return None


def calc_efficiency(price, low, high, shape):
    """Shape-aware fee efficiency calculation."""
    if price < low or price > high:
        return 0.0
    mid = (low + high) / 2
    width = high - low
    normalized = (price - low) / width  # 0 to 1

    if shape == "bid-ask":
        # U-shape: edges = high efficiency, center = low
        efficiency = 2 * abs(normalized - 0.5) * 100
    elif shape == "curve":
        # Bell: center = high, edges = low
        efficiency = (1 - 2 * abs(normalized - 0.5)) * 100
    else:  # spot
        efficiency = 100 if abs(normalized - 0.5) < 0.1 else 50

    return min(100, max(0, efficiency))


def calc_dca_suggestion(eff, price, range_low, range_high):
    """Generate DCA/rebalance suggestion based on efficiency and price position."""
    mid = (range_low + range_high) / 2
    dist_from_mid = abs(price - mid) / mid * 100
    near_low = price < range_low + (range_high - range_low) * 0.2
    near_high = price > range_high - (range_high - range_low) * 0.2

    if price < range_low:
        return {
            "action": "⚠️ REBALANCE NOW",
            "detail": f"Price ${price:.2f} is BELOW range (${range_low:.2f}–${range_high:.2f}). Add AVAX to rebalance.",
            "risk": "High",
            "dca": "Full rebalance — price out of range",
        }
    elif price > range_high:
        return {
            "action": "⚠️ REBALANCE NOW",
            "detail": f"Price ${price:.2f} is ABOVE range (${range_low:.2f}–${range_high:.2f}). Add USDC to rebalance.",
            "risk": "High",
            "dca": "Full rebalance — price out of range",
        }
    elif near_low:
        return {
            "action": "🟠 Micro-DCA + Watch",
            "detail": f"Price ${price:.2f} near lower edge. DCA $10 AVAX to widen range down.",
            "risk": "Medium",
            "dca": "$10 AVAX — edge zone",
        }
    elif near_high:
        return {
            "action": "🟠 Micro-DCA + Watch",
            "detail": f"Price ${price:.2f} near upper edge. Consider taking profits or widening range up.",
            "risk": "Medium",
            "dca": "$10 USDC — edge zone",
        }
    elif eff >= 70:
        return {
            "action": "🟢 Hold & Earn",
            "detail": f"Price ${price:.2f} in sweet spot. Full $50 DCA if adding.",
            "risk": "Low",
            "dca": "$50 — center zone (70%+ efficiency)",
        }
    elif eff >= 50:
        return {
            "action": "🟡 Hold — Reduced DCA",
            "detail": f"Price ${price:.2f} mid-zone. $30 DCA if adding.",
            "risk": "Low",
            "dca": "$30 — mid zone (50–70%)",
        }
    else:
        return {
            "action": "🟠 Watch — Low Efficiency",
            "detail": f"Price ${price:.2f} in low-efficiency zone ({eff:.0f}%). Micro-DCA $20.",
            "risk": "Medium",
            "dca": "$20 — low zone (<50%)",
        }


def update_defi_data(market, efficiency, suggestion):
    """Update defi-data.json with fresh market data."""
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "lastUpdated": now,
        "pool": "AVAX/USDC",
        "chain": "Avalanche",
        "dex": "LFJ",
        "currentPrice": market["price"],
        "priceChange24h": market["change24h"],
        "volume24h": market["volume24h"],
        "liquidity": market["liquidity"],
        "lpPosition": {
            "shape": SHAPE,
            "rangeLow": RANGE_LOW,
            "rangeHigh": RANGE_HIGH,
            "totalBalance": AVAX_HELD * market["price"] + USDC_HELD,
            "avaxAmount": AVAX_HELD,
            "avaxValue": AVAX_HELD * market["price"],
            "usdcAmount": USDC_HELD,
            "usdcValue": USDC_HELD,
        },
        "fees": {
            "dailyFees": DAILY_FEES,
            "cumulativeFees": DAILY_FEES,
            "feeCurrency": "USD",
        },
        "efficiency": round(efficiency, 1),
        "rebalance": suggestion,
        "milestones": MILESTONES,
    }
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return data


def update_hub_timestamp():
    """Update the 'Last updated' timestamp in hub.html."""
    now_str = datetime.now().strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    try:
        with open(HUB_PATH, "r") as f:
            content = f.read()
        # Replace last updated timestamp
        content = re.sub(
            r"Last updated:.*?<",
            f"Last updated: {now_str}<",
            content,
            count=1,
        )
        with open(HUB_PATH, "w") as f:
            f.write(content)
        print(f"✓ Dashboard timestamp updated: {now_str}")
    except Exception as e:
        print(f"⚠ Timestamp update failed: {e}", file=sys.stderr)


def git_push():
    """Commit and push changes to GitHub."""
    cmds = [
        f"cd {VAULT_PATH} && git add defi-data.json hub.html",
        f"cd {VAULT_PATH} && git commit -m 'auto: rebalance update $(date +%H:%M)'",
        f"cd {VAULT_PATH} && git push",
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"⚠ Git: {result.stderr.strip()}", file=sys.stderr)
    print("✓ Pushed to GitHub")


def main():
    now = datetime.now()
    print(f"🔄 DeFi Rebalance Check — {now.strftime('%I:%M %p ET')}")

    # 1. Fetch live price
    market = fetch_price()
    if not market or market["price"] == 0:
        print("❌ Could not fetch price. Aborting.")
        sys.exit(1)

    price = market["price"]
    print(f"📈 AVAX: ${price:.4f} ({market['change24h']:+.2f}%)")
    print(f"📊 24h Vol: ${market['volume24h']:,.0f} | TVL: ${market['liquidity']:,.0f}")

    # 2. Calculate efficiency
    in_range = RANGE_LOW <= price <= RANGE_HIGH
    efficiency = calc_efficiency(price, RANGE_LOW, RANGE_HIGH, SHAPE)
    print(f"⚙️  Efficiency: {efficiency:.1f}% ({'In Range' if in_range else 'OUT OF RANGE'})")

    # 3. Generate suggestion
    suggestion = calc_dca_suggestion(efficiency, price, RANGE_LOW, RANGE_HIGH)
    print(f"💡 {suggestion['action']}")
    print(f"   {suggestion['detail']}")
    print(f"   DCA: {suggestion['dca']}")

    # 4. Update data file
    update_defi_data(market, efficiency, suggestion)
    print(f"✅ defi-data.json updated")

    # 5. Update dashboard timestamp
    update_hub_timestamp()

    # 6. Push to GitHub
    git_push()

    # 7. Print summary for cron delivery
    print(f"\n{'='*40}")
    print(f"🔄 REBALANCE CHECK — {now.strftime('%I:%M %p ET')}")
    print(f"{'='*40}")
    print(f"AVAX: ${price:.4f} ({market['change24h']:+.2f}%)")
    print(f"Range: ${RANGE_LOW:.2f}–${RANGE_HIGH:.2f} | {'🟢 In Range' if in_range else '🔴 OUT'}")
    print(f"Efficiency: {efficiency:.1f}%")
    print(f"Position: ${AVAX_HELD * price + USDC_HELD:.2f} ({AVAX_HELD} AVAX + {USDC_HELD} USDC)")
    print(f"Daily Fees: ~${DAILY_FEES:.3f}")
    print(f"")
    print(f"💡 {suggestion['action']}")
    print(f"{suggestion['detail']}")
    print(f"DCA: {suggestion['dca']}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
