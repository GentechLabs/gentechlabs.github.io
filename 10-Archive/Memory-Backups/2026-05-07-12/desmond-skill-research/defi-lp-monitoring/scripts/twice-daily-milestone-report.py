#!/usr/bin/env python3
"""
Twice-Daily DeFi Milestone Report — Jordan's Preferred Format
Runs: 08:30 AM and 09:00 PM daily via cron "30 8,21 * * *"

Source: d5-master-cron.py + milestone ladder from config.
Output: Human-readable Telegram message with milestone progress.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# Paths
VAULT_DIR = "/root/vaults/gentech"
CONFIG_PATH = f"{VAULT_DIR}/00-HQ/config/defi-lp-config.env"
STATE_PATH = os.path.expanduser("~/.hermes/scripts/.lfj-aae-state.json")

# Wallet
JORDAN_WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"


def load_config():
    """Load milestone ladder and range from config (.env-style or JSON)."""
    config = {}
    # Try JSON first (new format)
    json_path = f"{VAULT_DIR}/00-HQ/config/.lfj-aae-config.json"
    if os.path.exists(json_path):
        with open(json_path) as f:
            cfg = json.load(f)
        config["range_low"] = cfg.get("position", {}).get("range_low")
        config["range_high"] = cfg.get("position", {}).get("range_high")
        config["milestones"] = cfg.get("milestones", [])
    else:
        # Fallback to .env parsing
        with open(CONFIG_PATH) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    config[k.lower()] = v
    return config


def load_state():
    """Load latest LP state (efficiency, fees earned, in_range flag)."""
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH) as f:
        return json.load(f)


def fetch_current_price():
    """Fetch AVAX/USDC price from DexScreener (quick, no auth)."""
    import urllib.request
    pool_addr = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{pool_addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech/2.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    pair = data.get("pair", data.get("pairs", [{}])[0])
    return float(pair.get("priceNative", 0))


def calc_fee_efficiency(price, range_low, range_high, shape="curve"):
    """Rough efficiency estimate based on position width."""
    width_ratio = (range_high - range_low) / range_low
    if shape == "curve":
        if width_ratio <= 0.05:
            base_efficiency = 90
        elif width_ratio <= 0.10:
            base_efficiency = 75
        else:
            base_efficiency = 60
    else:
        base_efficiency = 85 if width_ratio <= 0.05 else 65
    center = (range_low + range_high) / 2
    distance = abs(price - center) / (range_high - range_low) * 100
    return max(0, base_efficiency - distance * 2)


def format_milestone_report(config, state, price, in_range, efficiency):
    """Build Telegram-friendly milestone progress message."""
    milestones = config.get("milestones", [
        {"tier": 1, "label": "Scout",     "daily_fees": 5.0},
        {"tier": 2, "label": "Raider",    "daily_fees": 20.0},
        {"tier": 3, "label": "Warlord",   "daily_fees": 55.0},
        {"tier": 4, "label": "Sovereign", "daily_fees": 200.0},
    ])

    fees_today = state.get("fees_earned", 0.0)
    current_tier = None
    next_tier = None
    for i, m in enumerate(milestones):
        if fees_today >= m["daily_fees"]:
            current_tier = m
        elif not next_tier:
            next_tier = m

    eastern = timezone(timedelta(hours=-4))
    now = datetime.now(eastern)
    time_str = now.strftime("%I:%M %p").lstrip("0")

    lines = [
        "📊 **DeFi Milestone Check-in**",
        f"🕐 {now.strftime('%B %d, %Y')} — {time_str} EDT",
        "",
        f"💰 **Current Fees Today:** ${fees_today:.2f}",
    ]

    if current_tier:
        lines.append(f"🏆 **Current Tier:** {current_tier['label']} (Tier {current_tier['tier']})")
        if next_tier:
            gap = next_tier["daily_fees"] - fees_today
            lines.append(f"🎯 **Next:** {next_tier['label']} — need ${gap:.2f} more")
        else:
            lines.append("🚀 **Max tier reached!** All shapes unlocked.")
    else:
        gap = next_tier["daily_fees"] - fees_today if next_tier else 0
        lines.append(f"📈 **Target:** {next_tier['label'] if next_tier else 'Sovereign'} (${gap:.2f} to go)")

    lines.extend([
        "",
        f"📍 **Price:** ${price:.4f} | {'IN RANGE' if in_range else 'OUT OF RANGE'}",
        f"⚡ **Efficiency:** {efficiency:.1f}%",
    ])

    if not in_range:
        lines.append("⚠️ **Action needed:** Rebalance soon to avoid fee loss")

    lines.extend([
        "",
        "---",
        f"Wallet: `{JORDAN_WALLET[:6]}...{JORDAN_WALLET[-4:]}`",
    ])

    return "\n".join(lines)


def main():
    try:
        config = load_config()
        state = load_state()
        price = fetch_current_price()

        range_low = config.get("range_low")
        range_high = config.get("range_high")
        if not range_low or not range_high:
            print("ERROR: Missing range in config", file=sys.stderr)
            sys.exit(1)

        in_range = range_low <= price <= range_high
        efficiency = calc_fee_efficiency(price, range_low, range_high,
                                          config.get("shape", "curve"))

        report = format_milestone_report(config, state, price, in_range, efficiency)
        print(report)

        # Exit code for cron alert escalation
        if not in_range:
            sys.exit(1)   # warning
        elif efficiency < 50:
            sys.exit(2)   # red alert
        else:
            sys.exit(0)   # OK

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
