#!/usr/bin/env python3
"""
D5 Master Cron — Consolidated report: CMC Watchlist + D5 LP Milestone
Runs 4x/day. Silent unless:
  - Any CMC token moves ≥3% in 24h
  - LP out of range OR efficiency <50% OR tier crosses
  - Monday DCA reminder
  - Compound threshold crossed

Shape-Aware DCA:
  - Center zone (70-100% efficiency, CURVE):   $50 normal DCA
  - Mid zone (50-70%):                         $30 reduced DCA
  - Low zone (30-50%):                         $20 micro-DCA + rebalance warning
  - Edge/crash zone (<30%):                    $10 micro-DCA + urgent rebalance
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

# ── CMC ───────────────────────────────────────────────────────────────────────

def load_cmc_key():
    """Load CMC API key from config file or environment"""
    # Try config file first (absolute path)
    config_path = "/root/.hermes/scripts/cmc_config.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            return config.get("coinmarketcap_api_key", "")
    # Fallback to environment variable
    return os.environ.get("CMC_API_KEY", "")

CMC_API_KEY = load_cmc_key()
CMC_THRESHOLD = 3.0

COINS = [
    {"symbol": "BTC",  "cmc_id": "1"},
    {"symbol": "SOL",  "cmc_id": "5426"},
    {"symbol": "LINK", "cmc_id": "1975"},
    {"symbol": "AVAX", "cmc_id": "5805"},
    {"symbol": "TAO",  "cmc_id": "22974"},
    {"symbol": "XAUt", "cmc_id": "5176"},
    {"symbol": "BEAM", "cmc_id": "28298"},
]

# ── LP Config ─────────────────────────────────────────────────────────────────
# ── LP Config ─────────────────────────────────────────────────────────────────
JORDAN_WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
AVAX_GAS_LOW_THRESHOLD = 0.05  # Alert if AVAX below this (for gas)

POOL = {
    "name": "AVAX/USDC",
    "chain": "avalanche",
    "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    "range_low": 9.02,
    "range_high": 9.32,
    "shape": "curve",
    "position_usd": 138.92,
    "fee_tier_bps": 5,
    "wallet": JORDAN_WALLET,
}

MILESTONES = [
    {"tier": 1, "label": "Scout",     "daily_fees": 5.0,   "unlocks": "Entry strategies (CURVE)"},
    {"tier": 2, "label": "Raider",    "daily_fees": 20.0,  "unlocks": "SPOT + BIDIRECTIONAL shapes"},
    {"tier": 3, "label": "Warlord",   "daily_fees": 55.0,  "unlocks": "Multi-pool positions"},
    {"tier": 4, "label": "Sovereign", "daily_fees": 200.0, "unlocks": "Custom strategy creation"},
]

COMPOUND_THRESHOLD = 50.0
DCA_BASE = 50

# ── State ──────────────────────────────────────────────────────────────────────

CMC_STATE = os.path.expanduser("~/.hermes/scripts/.cmc-watchlist-state.json")
LP_STATE  = os.path.expanduser("~/.hermes/scripts/.lfj-aae-state.json")

# ── Helpers ──────────────────────────────────────────────────────────────────

def now_eastern():
    return datetime.now(timezone(timedelta(hours=-4)))

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)

def fetch_cmc():
    ids = ",".join(c["cmc_id"] for c in COINS)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={ids}&convert=USD"
    req = urllib.request.Request(url, headers={
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return None

def fetch_dexscreener():
    url = f"https://api.dexscreener.com/latest/dex/pairs/{POOL['chain']}/{POOL['pool_address']}"
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

# ── On-Chain Position Fetcher ────────────────────────────────────────────────────

def fetch_wallet_position():
    """Fetch LP position data from Avalanche blockchain via DeBank API"""
    wallet = POOL.get("wallet", "")
    if not wallet:
        return {}

    # DeBank API for portfolio breakdown (free, no key needed)
    url = f"https://api.debank.com/user/addr/{wallet}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        # Returns total balance and protocol list
        return {
            "total_usd": data.get("total_usd", 0),
            "chain_list": data.get("chain_list", []),
        }
    except Exception:
        return {}

def fetch_wallet_tokens():
    """Fetch token balances for wallet via DeBank"""
    wallet = POOL.get("wallet", "")
    if not wallet:
        return []

    url = f"https://api.debank.com/user/token_list?addr={wallet}&is_all=false&chain=avax"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("token_list", [])
    except Exception:
        return []

def fetch_wallet_protocols():
    """Fetch DeFi protocol positions for wallet"""
    wallet = POOL.get("wallet", "")
    if not wallet:
        return []

    url = f"https://api.debank.com/user/protocol_list?addr={wallet}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("protocol_list", [])
    except Exception:
        return []

def calc_efficiency(price, low, high, shape):
    if price < low or price > high:
        return 0.0
    pos = (price - low) / (high - low)
    if shape == "spot":
        return 100.0
    elif shape == "bidirectional":
        return round(max(0, min(100, abs(pos - 0.5) * 2 * 100)), 1)
    else:  # curve
        return round(max(0, min(100, (1 - abs(pos - 0.5) * 2) * 100)), 1)

def est_daily_fees(volume, liq, pos_usd, fee_bps):
    if liq <= 0 or volume <= 0:
        return 0.0
    return round((volume * fee_bps / 10000) * (pos_usd / liq), 2)

def get_tier(daily_fees):
    curr = 0
    for i, m in enumerate(MILESTONES):
        if daily_fees >= m["daily_fees"]:
            curr = i
    nxt = min(curr + 1, len(MILESTONES) - 1)
    ct = MILESTONES[curr]["daily_fees"]
    nt = MILESTONES[nxt]["daily_fees"]
    pct = 0.0 if nt <= ct or daily_fees <= ct else round(((daily_fees - ct) / (nt - ct)) * 100, 1)
    return curr, MILESTONES[curr]["label"], nxt, MILESTONES[nxt]["label"], pct

def dca_by_efficiency(eff):
    """Shape-aware DCA sizing — lower efficiency = smaller, wait-and-see DCA."""
    if eff >= 70:
        return DCA_BASE, "🟢 Center zone — full $50 DCA"
    elif eff >= 50:
        return 30, "🟡 Mid zone — reduced $30 DCA (still earning, not chasing)"
    elif eff >= 30:
        return 20, "🟠 Low zone — micro-DCA $20 + watch for rebalance (price near edge)"
    else:
        return 10, "🔴 Edge/crash zone — micro-DCA $10 + urgent rebalance needed"

def bar(pct):
    blocks = int(pct / 10)
    return "▓" * blocks + "░" * (10 - blocks)

def fmt_price(p):
    if p == 0:
        return "—"
    return f"${p:,.6f}" if p < 0.01 else f"${p:,.2f}" if p > 100 else f"${p:,.4f}"

def em(change):
    return "🟢" if change >= 0 else "🔴"

# ── Wallet Balance ──────────────────────────────────────────────────────────────

def fetch_wallet_balances():
    """Fetch AVAX + USDC balances from Snowtrace"""
    balances = {"avax": 0.0, "usdc": 0.0, "avax_usd": 0.0}
    wallet = JORDAN_WALLET

    # AVAX native balance
    try:
        url = f"https://api.snowtrace.io/api?module=account&action=balance&address={wallet}&tag=latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1":
                balances["avax"] = round(int(data["result"]) / 1e18, 6)
    except Exception:
        pass

    # USDC balance (6 decimals)
    try:
        url = f"https://api.snowtrace.io/api?module=account&action=tokenbalance&contractaddress={USDC_ADDRESS}&address={wallet}&tag=latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1":
                balances["usdc"] = round(int(data["result"]) / 1e6, 2)
    except Exception:
        pass

    return balances

def wallet_alerts(balances, avax_price):
    """Check if wallet needs attention"""
    alerts = []
    if balances["avax"] < AVAX_GAS_LOW_THRESHOLD:
        alerts.append(f"⛽ Low AVAX for gas ({balances['avax']:.4f} AVAX)")
    if balances["usdc"] < 1.0:
        alerts.append(f"💸 Near-zero USDC (${balances['usdc']:.2f})")
    balances["avax_usd"] = round(balances["avax"] * avax_price, 2) if avax_price else 0
    return alerts

# ── CMC Watchlist Builder ──────────────────────────────────────────────────────

def build_watchlist(data):
    state = load_json(CMC_STATE, {})
    today = now_eastern().strftime("%Y-%m-%d")
    if state.get("date") != today:
        state = {"date": today, "last_prices": {}}

    results = []
    alerts = []
    for c in COINS:
        q = data["data"].get(c["cmc_id"], {}).get("quote", {}).get("USD", {})
        price = q.get("price", 0)
        ch = q.get("percent_change_24h", 0) or 0
        mc = q.get("market_cap", 0)
        results.append({"symbol": c["symbol"], "price": price, "ch": ch, "mc": mc})
        if abs(ch) >= CMC_THRESHOLD:
            alerts.append({"symbol": c["symbol"], "price": price, "ch": ch})
            state["last_prices"][c["symbol"]] = price

    save_json(CMC_STATE, state)
    return results, alerts

# ── LP Section Builder ──────────────────────────────────────────────────────────

def build_lp():
    data = fetch_dexscreener()
    state = load_json(LP_STATE, {})
    price = data.get("price", 0)
    vol = data.get("volume_24h", 0)
    liq = data.get("liquidity", 0)
    ch = data.get("change_24h", 0)

    eff = calc_efficiency(price, POOL["range_low"], POOL["range_high"], POOL["shape"])
    in_range = POOL["range_low"] <= price <= POOL["range_high"]
    fees = est_daily_fees(vol, liq, POOL["position_usd"], POOL["fee_tier_bps"])
    apr = round((fees * 365 / POOL["position_usd"]) * 100, 1) if POOL["position_usd"] > 0 else 0
    cum = state.get("total_fees_earned_usd", 0)
    days = state.get("total_days_in_range", 0)
    comp_ready = cum >= COMPOUND_THRESHOLD
    is_monday = now_eastern().weekday() == 0

    curr_idx, curr_lab, nxt_idx, nxt_lab, pct = get_tier(fees)
    _, dca_msg = dca_by_efficiency(eff)

    lp = {
        "price": price, "ch": ch, "vol": vol, "liq": liq,
        "eff": eff, "in_range": in_range, "fees": fees, "apr": apr,
        "cum": cum, "days": days, "curr_idx": curr_idx, "curr_lab": curr_lab,
        "nxt_lab": nxt_lab, "pct": pct, "comp_ready": comp_ready,
        "is_monday": is_monday, "dca_msg": dca_msg,
    }
    return lp

# ── Silent vs Alert Logic ──────────────────────────────────────────────────────

def should_alert(alerts, lp):
    """
    Silent rules:
    - NO alert if no CMC moves AND LP is in_range + eff>=50% + no compound + not_monday
    - ALWAYS alert if CMC moves >=3% OR out of range OR eff<50% OR compound ready
    """
    if alerts:
        return True
    if not lp["in_range"]:
        return True
    if lp["eff"] < 50:
        return True
    if lp["comp_ready"]:
        return True
    if lp["is_monday"]:
        return True
    if lp.get("wallet_alerts"):
        return True
    return False

# ── Print ──────────────────────────────────────────────────────────────────────

def print_report(results, alerts, lp):
    now = now_eastern()
    time_str = now.strftime("%I:%M %p EDT")
    date_str = now.strftime("%A, %B %d")

    lines = [f"🏆 **D5 Master Report** — {date_str} @ {time_str}"]

    # CMC Watchlist — always compact
    if alerts:
        lines.append("")
        lines.append("🚨 **Watchlist Alerts (|24h| ≥ 3%):**")
        for a in alerts:
            lines.append(f"• **{a['symbol']}**: {fmt_price(a['price'])} {em(a['ch'])} {a['ch']:+.1f}%")

    lines.append("")
    lines.append("📊 **Full Watchlist:**")
    for r in results:
        mc = f"${r['mc']/1e9:.1f}B" if r["mc"] >= 1e9 else f"${r['mc']/1e6:.0f}M"
        lines.append(f"• **{r['symbol']}**: {fmt_price(r['price'])} {em(r['ch'])} {r['ch']:+.1f}% | MC: {mc}")

    # LP Position
    lines.append("")
    lines.append(f"💰 **LP Position: {POOL['name']} ({POOL['chain'].upper()})**")
    lines.append(f"• Price: {fmt_price(lp['price'])} {em(lp['ch'])} {lp['ch']:+.2f}% (24h)")
    stat = "🟩" if lp["in_range"] else "🟥 OUT"
    lines.append(f"• Range: {fmt_price(POOL['range_low'])} — {fmt_price(POOL['range_high'])} | Status: {stat}")
    lines.append(f"• Shape: {POOL['shape'].upper()} | Efficiency: **{lp['eff']}%**")
    lines.append(f"• Pool Vol (24h): ${lp['vol']:,.0f} | TVL: ${lp['liq']:,.0f}")

    lines.append("")
    lines.append("💰 **Revenue:**")
    lines.append(f"• Est. Daily Fees: ${lp['fees']}")
    if lp["apr"] > 0:
        lines.append(f"• Implied APR: {lp['apr']}%")
    lines.append(f"• Cumulative: ${lp['cum']:.2f}")
    lines.append(f"• Days in Range: {lp['days']:.1f}")

    # D5 Ladder
    lines.append("")
    lines.append("📈 **D5 Milestone Ladder:**")
    for m in MILESTONES:
        t = m["tier"]
        lab = m["label"]
        tgt = m["daily_fees"]
        if lp["curr_idx"] + 1 == t:
            lines.append(f"    **▶ Tier {t}: {lab} — ${tgt}/day ← CURRENT**")
            if lp["pct"] < 100:
                lines.append(f"       {bar(lp['pct'])} {lp['pct']}% → Tier {lp['curr_idx']+2}: {lp['nxt_lab']}")
        elif lp["curr_idx"] + 1 > t:
            lines.append(f"    ✅ Tier {t}: {lab} — ${tgt}/day (ACHIEVED)")
        else:
            lines.append(f"    ⬜ Tier {t}: {lab} — ${tgt}/day")

    # Action Items
    lines.append("")
    lines.append("🎯 **Action Items:**")

    if lp["is_monday"]:
        lines.append(f"💰 **Monday $50 DCA** — {lp['dca_msg']}")

    if lp["comp_ready"]:
        lines.append(f"🔄 **Compound Ready** — Cumulative fees ${lp['cum']:.2f} exceed ${COMPOUND_THRESHOLD} threshold. Reinvest + DCA.")

    lines.append(f"📉 **Shape-Aware DCA**: {lp['dca_msg']}")

    if not lp["in_range"]:
        lines.append(f"🚨 **Rebalance Required** — Price out of range! Shift range to capture volatility.")
    elif lp["eff"] < 40:
        lines.append(f"⚠️ **Consider Rebalancing** — Fee efficiency low ({lp['eff']}%). A fresh range earns more.")
    elif lp["eff"] >= 70:
        lines.append(f"🏅 **Position Healthy** — Keep earning. Efficiency is strong.")

    # Daily Snapshot
    total = POOL["position_usd"] + lp["cum"]
    lines.append("")
    lines.append("📸 **Daily Snapshot:**")
    lines.append(f"• Position Value: ${POOL['position_usd']:.2f}")
    lines.append(f"• + Cumulative Fees: ${lp['cum']:.2f}")
    lines.append(f"• Total Value: ${total:.2f}")
    lines.append(f"• Next Milestone: ${MILESTONES[min(lp['curr_idx']+1, len(MILESTONES)-1)]['daily_fees']:.1f}/day")
    lines.append(f"• Next Compound: ${max(0, COMPOUND_THRESHOLD - lp['cum']):.2f} away")

    # Wallet Balances
    balances = lp.get("balances", {"avax": 0, "usdc": 0, "avax_usd": 0})
    w_alerts = lp.get("wallet_alerts", [])

    lines.append("")
    lines.append("🏦 **Wallet Balances:**")
    lines.append(f"• AVAX: {balances['avax']:.4f} (~${balances['avax_usd']:.2f})")
    lines.append(f"• USDC: ${balances['usdc']:.2f}")
    if w_alerts:
        for a in w_alerts:
            lines.append(f"⚠️ {a}")

    lines.append("")
    lines.append("💡 **Strategy**: Bear market accumulation — farm the bottom, compound rewards.")
    lines.append("📊 Data: CMC + DexScreener | D5 Engine v1")

    print("\n".join(lines))

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    cmc_data = fetch_cmc()
    if not cmc_data or "data" not in cmc_data:
        print("[SILENT] CMC API failed")
        sys.exit(0)

    results, alerts = build_watchlist(cmc_data)
    lp = build_lp()

    # Wallet balance check
    balances = fetch_wallet_balances()
    w_alerts = wallet_alerts(balances, lp.get("price", 0))
    lp["wallet_alerts"] = w_alerts
    lp["balances"] = balances

    if not should_alert(alerts, lp):
        print("[SILENT]")
        sys.exit(0)

    print_report(results, alerts, lp)

if __name__ == "__main__":
    main()
