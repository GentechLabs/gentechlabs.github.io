#!/usr/bin/env python3
"""
D5 Milestone Summary — Daily consolidated report for Jordan.
One-per-day report covering ALL LP positions against the D5 milestone ladder:
  Scout ($5/day) → Raider ($20/day) → Warlord ($55/day) → Sovereign ($200/day)
  → Freedom ($??)

Integrates:
  - Live pool data (DexScreener)
  - D5 tier progression
  - Micro-DCA triggers (efficiency-based)
  - Compound threshold tracking
  - Cumulative fee + P&L summary
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

# ── Config ──────────────────────────────────────────────────────────────────

POOLS = [
    {
        "name": "AVAX/USDC",
        "chain": "avalanche",
        "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
"range_low": 9.75,
        "range_high": 10.01,
        "shape": "curve",
        "position_usd": 83.92,
        "token0_symbol": "AVAX",
        "token1_symbol": "USDC",
        "fee_tier_bps": 5,
    }
]

MILESTONES = [
    {"tier": 1, "label": "Scout",    "daily_fees": 5.0,    "unlocks": "Entry strategies (CURVE)"},
    {"tier": 2, "label": "Raider",   "daily_fees": 20.0,   "unlocks": "SPOT + BIDIRECTIONAL shapes"},
    {"tier": 3, "label": "Warlord",  "daily_fees": 55.0,   "unlocks": "Multi-pool positions"},
    {"tier": 4, "label": "Sovereign","daily_fees": 200.0,  "unlocks": "Custom strategy creation"},
]

COMPOUND_THRESHOLD = 50.0
DCA_AMOUNT = 50
MICRO_DCA_LOW = 10
MICRO_DCA_HIGH = 20

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-aae-state.json")

# ── Helpers ─────────────────────────────────────────────────────────────────

def now_eastern():
    return datetime.now(timezone(timedelta(hours=-4)))

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def fetch_dexscreener(pool_address: str, chain: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
        return {
            "price": float(pair.get("priceNative", 0)),
            "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
            "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
            "change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
        }
    except Exception:
        return {}

def calc_efficiency(price: float, range_low: float, range_high: float, shape: str) -> float:
    if price < range_low or price > range_high:
        return 0.0
    position = (price - range_low) / (range_high - range_low)
    if shape == "spot":
        return 100.0
    elif shape == "bidirectional":
        return round(max(0, min(100, abs(position - 0.5) * 2 * 100)), 1)
    else:  # curve
        return round(max(0, min(100, (1 - abs(position - 0.5) * 2) * 100)), 1)

def estimate_daily_fees(volume_24h: float, liquidity: float, position_usd: float, fee_bps: int) -> float:
    if liquidity <= 0 or volume_24h <= 0:
        return 0.0
    fee_rate = fee_bps / 10000
    return round((volume_24h * fee_rate) * (position_usd / liquidity), 2)

def get_current_tier(est_fees: float) -> tuple:
    """Returns (current_idx, current_label, next_idx, next_label, progress_pct)."""
    # Find the highest milestone that has been reached or surpassed
    current_idx = -1
    for i, m in enumerate(MILESTONES):
        if est_fees >= m["daily_fees"]:
            current_idx = i
        else:
            break  # Found first milestone not reached

    # If no milestone reached (current_idx = -1), we are before the first milestone
    if current_idx == -1:
        next_idx = 0
        progress_pct = round((est_fees / MILESTONES[0]["daily_fees"]) * 100, 1)
        return -1, "Unranked", next_idx, MILESTONES[next_idx]["label"], progress_pct

    # If we've reached the highest milestone, pct = 100
    if current_idx == len(MILESTONES) - 1:
        return current_idx, MILESTONES[current_idx]["label"], current_idx, MILESTONES[current_idx]["label"], 100.0

    next_idx = current_idx + 1
    current_target = MILESTONES[current_idx]["daily_fees"]
    next_target = MILESTONES[next_idx]["daily_fees"]
    progress_pct = round(((est_fees - current_target) / (next_target - current_target)) * 100, 1)
    return current_idx, MILESTONES[current_idx]["label"], next_idx, MILESTONES[next_idx]["label"], progress_pct

def micro_dca_action(efficiency: float) -> dict:
    """Returns (trigger_level, bonus_amount, action_text)."""
    if efficiency < 30:
        return ("🔴 CRITICAL", MICRO_DCA_HIGH, "Rebalance + deploy $20 bonus DCA into fresh range")
    elif efficiency < 40:
        return ("🔴 Red", MICRO_DCA_HIGH, "Strongly consider rebalancing + $20 bonus DCA into fresh range")
    elif efficiency < 50:
        return ("🟠 Orange", MICRO_DCA_LOW, "Deploy $10 bonus DCA + monitor for rebalance")
    elif efficiency < 60:
        return ("🟡 Yellow", 0, "Watch only — no bonus DCA, still earning")
    else:
        return ("🟢 Green", 0, "None — position is healthy")

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    now = now_eastern()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p EDT")
    state = load_state()

    cumulative_fees = state.get("total_fees_earned_usd", 0)
    days_in_range = state.get("total_days_in_range", 0)
    compound_ready = cumulative_fees >= COMPOUND_THRESHOLD
    is_monday = now.weekday() == 0

    lines = [
        f"🏆 **D5 Milestone Report** — {date_str}",
        f"",
    ]

    global_micro_dca = 0
    global_efficiency = None

    for pool in POOLS:
        # Dynamic position USD from state or tracker, so DCA additions are reflected
        position_usd = state.get("position_usd", pool["position_usd"])
        data = fetch_dexscreener(pool["pool_address"], pool["chain"])
        price = data.get("price", 0)
        volume = data.get("volume_24h", 0)
        liquidity = data.get("liquidity", 0)
        change_24h = data.get("change_24h", 0)

        in_range = pool["range_low"] <= price <= pool["range_high"]
        efficiency = calc_efficiency(price, pool["range_low"], pool["range_high"], pool["shape"])
        est_fees = estimate_daily_fees(volume, liquidity, position_usd, pool["fee_tier_bps"])

        global_efficiency = efficiency
        current_idx, current_label, next_idx, next_label, progress_pct = get_current_tier(est_fees)
        _, micro_bonus, micro_action = micro_dca_action(efficiency)
        global_micro_dca = micro_bonus

        # ── Header ────────────────────────────────────────────
        range_status = "🟩 In Range" if in_range else "🟥 OUT OF RANGE"
        price_emoji = "🟢" if change_24h >= 0 else "🔴"
        lines.append(f"**{pool['name']} — {pool['chain'].upper()}**")
        lines.append(f"• Price: ${price:.4f} {price_emoji} {change_24h:+.2f}% (24h)")
        lines.append(f"• Range: ${pool['range_low']} — ${pool['range_high']} | Status: {range_status}")
        lines.append(f"• Shape: {pool['shape'].upper()} | Efficiency: {efficiency}%")
        lines.append(f"• Pool Vol (24h): ${volume:,.0f} | TVL: ${liquidity:,.0f}")
        lines.append("")

        # ── Revenue ───────────────────────────────────────────
        lines.append(f"💰 **Revenue Summary**")
        lines.append(f"• Est. Daily Fees: ${est_fees}")
        if est_fees > 0:
            apr = round((est_fees * 365 / pool["position_usd"]) * 100, 1)
            lines.append(f"• Implied APR: {apr}%")
        lines.append(f"• Cumulative Fees: ${cumulative_fees:.2f}")
        lines.append(f"• Days in Range: {days_in_range:.1f}")
        lines.append("")

        # ── D5 Milestone Ladder ───────────────────────────────
        lines.append(f"📈 **D5 Milestone Ladder**")
        for m in MILESTONES:
            tier_num = m["tier"]
            label = m["label"]
            target = m["daily_fees"]
            unlocks = m["unlocks"]
            if current_idx + 1 == tier_num:
                lines.append(f"    **▶ Tier {tier_num}: {label} — ${target}/day ← CURRENT**")
                if progress_pct < 100:
                    bar = "▓" * (int(progress_pct / 10)) + "░" * (10 - int(progress_pct / 10))
                    lines.append(f"       {bar} {progress_pct}% → Tier {next_idx + 1}: {next_label}")
            elif current_idx + 1 > tier_num:
                lines.append(f"    ✅ Tier {tier_num}: {label} — ${target}/day (ACHIEVED)")
            else:
                lines.append(f"    ⬜ Tier {tier_num}: {label} — ${target}/day")
        lines.append(f"    Unlocks: {unlocks_for(current_label)}")
        lines.append("")

        # ── Action Items ──────────────────────────────────────
        lines.append(f"🎯 **Action Items**")

        if is_monday:
            lines.append(f"💰 **$50 Monday DCA** — Ready to deploy!")
        
        if compound_ready:
            lines.append(f"🔄 **Compound Ready** — Cumulative fees (${cumulative_fees:.2f}) exceed ${COMPOUND_THRESHOLD} threshold.")
        
        if micro_bonus > 0:
            lines.append(f"📉 **Micro-DCA Trigger ({micro_action.split('—')[0].strip()})** — ${micro_bonus} bonus DCA flagged")
            lines.append(f"   {micro_action}")
        else:
            lines.append(f"✅ **No Micro-DCA** — {micro_action.split('—')[1].strip() if '—' in micro_action else micro_action}")

        if not in_range:
            lines.append(f"🚨 **Rebalance Required** — Price out of range! Shift range to current price level.")
        elif efficiency < 40:
            lines.append(f"⚠️ **Consider Rebalancing** — Fee efficiency low ({efficiency}%). A fresh range will earn more.")
        elif efficiency >= 70:
            lines.append(f"🏅 **Position Healthy** — Keep earning. Efficiency is strong.")

        lines.append("")

        # ── Daily Snapshot ────────────────────────────────────
        lines.append(f"📸 **Daily Snapshot**")
        total_position = position_usd + cumulative_fees
        lines.append(f"• Position Value: ${position_usd:.2f}")
        lines.append(f"• + Cumulative Fees: ${cumulative_fees:.2f}")
        lines.append(f"• Total Value: ${total_position:.2f}")
        lines.append(f"• Next Milestone: ${MILESTONES[min(current_idx + 1, len(MILESTONES)-1)]['daily_fees']:.1f}/day")
        lines.append(f"• Next Compound: ${max(0, COMPOUND_THRESHOLD - cumulative_fees):.2f} away")
        if is_monday:
            lines.append(f"• Today: DCA Day (+${DCA_AMOUNT})")
        lines.append("")

    # ── Strategy Note ─────────────────────────────────────────
    lines.append("💡 **Strategy**: Bear market accumulation — farm the bottom, compound rewards.")
    lines.append(f"   Data: DexScreener | Generated: {time_str}")

    print("\n".join(lines))

def unlocks_for(label: str) -> str:
    for m in MILESTONES:
        if m["label"] == label:
            return m["unlocks"]
    return "—"

if __name__ == "__main__":
    main()
