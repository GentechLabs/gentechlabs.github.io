#!/usr/bin/env python3
"""
Narrative Rotation Scanner — Weekly
Runs Sundays 3:30 PM UTC
Tracks multiple coins per narrative to spot sector rotation.
"""

import urllib.request
import json
import os
import time
import sys

def _load_cmc_key():
    """Load a working CMC API key: cmc_config.json first, then env, then empty."""
    import os as _os
    # 1. cmc_config.json (same source defi-master-cron uses, verified live)
    try:
        with open("/root/.hermes/scripts/cmc_config.json") as _f:
            _cfg = json.load(_f)
            _k = _cfg.get("coinmarketcap_api_key", "")
            if _k:
                return _k
    except Exception:
        pass
    # 2. Environment
    _k = _os.environ.get("CMC_API_KEY", "")
    if _k:
        return _k
    return ""

CMC_API_KEY = _load_cmc_key()
HEADERS = {
    "X-CMC_PRO_API_KEY": CMC_API_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Narratives with representative coins (symbol: display name)
NARRATIVES = {
    "AI & Data": {
        "coins": ["FET", "RENDER", "TAO", "AKT"],
        "emoji": "🤖",
        "thesis": "AI compute, data markets, decentralized inference"
    },
    "RWA (Real World Assets)": {
        "coins": ["ONDO", "PLU", "CPOOL"],
        "emoji": "🏠",
        "thesis": "Tokenized treasuries, real estate, credit"
    },
    "DeFi Blue Chips": {
        "coins": ["UNI", "AAVE", "LINK", "MKR"],
        "emoji": "🏦",
        "thesis": "Dex, lending, oracles, stablecoins"
    },
    "L1 / L2": {
        "coins": ["SOL", "AVAX", "NEAR", "ARB"],
        "emoji": "⛓️",
        "thesis": "Base layers and scaling"
    },
    "Meme / Community": {
        "coins": ["DOGE", "PEPE", "WIF", "BONK"],
        "emoji": "🐸",
        "thesis": "Community-driven, narrative plays"
    },
    "Gaming / Metaverse": {
        "coins": ["IMX", "GALA", "PYTH"],
        "emoji": "🎮",
        "thesis": "On-chain gaming, virtual worlds"
    }
}

def fetch_prices(symbols):
    """Fetch current prices + 7d + 30d changes for a batch of symbols."""
    results = {}
    # CMC quotes endpoint accepts comma-separated symbols
    sym_str = ",".join(symbols)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={sym_str}&convert=USD"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            for sym in symbols:
                if sym in data.get("data", {}):
                    coin = data["data"][sym]
                    quote = coin.get("quote", {}).get("USD", {})
                    results[sym] = {
                        "name": coin.get("name", sym),
                        "price": quote.get("price", 0),
                        "change_24h": quote.get("percent_change_24h", 0),
                        "change_7d": quote.get("percent_change_7d", 0),
                        "change_30d": quote.get("percent_change_30d", 0),
                        "mc": quote.get("market_cap", 0),
                        "vol_24h": quote.get("volume_24h", 0),
                    }
    except Exception as e:
        print(f"  ⚠️ Fetch error for {sym_str}: {e}")
    return results


def classify_zone(change_7d, change_30d):
    """Simple zone classification based on momentum."""
    avg = (change_7d + change_30d) / 2
    if avg > 10:
        return "🟢 Hot"
    elif avg > 0:
        return "🔵 Warm"
    elif avg > -10:
        return "🟡 Cooling"
    else:
        return "🔴 Cold"
def classify_sentiment(change_24h, change_7d, vol_24h, mc):
    """Market sentiment per narrative based on price action + volume.

    Sentiment drives yield rainbow positioning:
    - Bullish + accumulation zone = strong buy signal
    - Bearish + euphoria zone = top signal
    - Neutral = wait for confirmation
    """
    # Volume/market cap ratio (higher = more interest/urgency)
    vol_ratio = (vol_24h / mc * 100) if mc > 0 else 0

    # Composite sentiment score
    # Weight: 24h (short-term pulse) + 7d (trend) + volume (participation)
    score = change_24h * 0.3 + change_7d * 0.5

    # Volume amplifier: high volume confirms the move
    if vol_ratio > 15:
        score *= 1.3  # High conviction move
    elif vol_ratio < 3:
        score *= 0.7  # Low participation, less reliable

    if score > 5:
        sentiment = "🟢 Bullish"
        rainbow_hint = "Peak Yield / Euphoria zone — watch for tops"
    elif score > 0:
        sentiment = "🔵 Mild Bullish"
        rainbow_hint = "Harvest Mode — hold and compound"
    elif score > -5:
        sentiment = "🟡 Mild Bearish"
        rainbow_hint = "Accumulation zone — DCA opportunity"
    else:
        sentiment = "🔴 Bearish"
        rainbow_hint = "Bleeding Edge / Panic Farm — generational entry"

    return sentiment, rainbow_hint, round(score, 1), round(vol_ratio, 1)




def narrative_score(coin_data):
    """Simple momentum score for a coin: weighted 7d + 30d."""
    if not coin_data:
        return 0
    return (coin_data.get("change_7d", 0) * 0.6) + (coin_data.get("change_30d", 0) * 0.4)


def format_mc(mc):
    if mc >= 1e9:
        return f"${mc/1e9:.1f}B"
    elif mc >= 1e6:
        return f"${mc/1e6:.0f}M"
    else:
        return f"${mc:,.0f}"


def fetch_macro_indicators():
    """Fetch the macro liquidity thermometer: BTC dominance + stablecoin market
    caps (USDT, USDC). Jordan (Aug 21 2026): these are the signals that tell us
    where the narrative rotation is bullish or bearish — on-chain dollar supply
    (stablecoins) + BTC dominance are the bull/bear backdrop for every narrative.

    Returns dict with btc_dominance, stablecoin_mcap, btc_dom_trend, notes.
    """
    out = {
        "btc_dominance": None,
        "usdt_mcap": None,
        "usdc_mcap": None,
        "stablecoin_mcap_total": None,
        "stablecoin_delta_7d": None,
        "signals": [],
        "stance": None,  # 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    }

    # 1. BTC dominance + total mcap (CoinGecko global)
    try:
        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/global",
            headers={"User-Agent": "Mozilla/5.0 (Steward/1.0)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            g = json.loads(r.read().decode())
        d = g.get("data", {})
        out["btc_dominance"] = d.get("market_cap_percentage", {}).get("btc")
        out["total_mcap_usd"] = d.get("total_market_cap", {}).get("usd")
    except Exception:
        pass

    # 2. Stablecoin market caps (CMC — same key the scanner already uses)
    stable_syms = {"USDT": "tether", "USDC": "usd-coin"}
    try:
        sym_str = ",".join(stable_syms.keys())
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={sym_str}&convert=USD"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        usdt_mc = data.get("data", {}).get("USDT", {}).get("quote", {}).get("USD", {}).get("market_cap")
        usdc_mc = data.get("data", {}).get("USDC", {}).get("quote", {}).get("USD", {}).get("market_cap")
        out["usdt_mcap"] = usdt_mc
        out["usdc_mcap"] = usdc_mc
        total = (usdt_mc or 0) + (usdc_mc or 0)
        out["stablecoin_mcap_total"] = total
    except Exception:
        pass

    # 3. Read the persisted BTC dominance trend (from the daily monitor state)
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".btc-dominance-state.json")) as f:
            dom_state = json.load(f)
        prev = dom_state.get("prev_dominance")
        if out["btc_dominance"] is not None and prev is not None:
            out["btc_dom_delta"] = out["btc_dominance"] - prev
    except Exception:
        pass

    # 4. Interpret the thermometer
    # Stablecoin supply is the "dry powder" — rising = fuel for upside.
    if out["stablecoin_mcap_total"]:
        # Cross-reference with previous reading for a delta trend.
        # (Simple threshold: >$200B combined = strong on-chain liquidity.)
        if out["stablecoin_mcap_total"] >= 250e9:
            out["signals"].append(f"💵 Stablecoin liquidity HIGH — ${out['stablecoin_mcap_total']/1e9:.0f}B combined USDT+USDC (>$250B). On-chain dollars ready to deploy.")
            out["read"] = "BULLISH" if out.get("btc_dom_delta", 0) is not None and out.get("btc_dom_delta", 0) < 0 else "BULLISH"
        else:
            out["signals"].append(f"💵 Stablecoin liquidity: ${out['stablecoin_mcap_total']/1e9:.0f}B combined")
    if out["btc_dominance"] is not None:
        dom_txt = f"BTC dominance: {out['btc_dominance']:.1f}%"
        if out.get("btc_dom_delta") is not None and out["btc_dom_delta"] <= -0.5:
            dom_txt += " ▼ (rollover — money rotating to alts)"
        out["signals"].insert(0, f"🐻🐂 {dom_txt}")

    # Net stance
    btc_dom_delta = out.get("btc_dom_delta")
    # Simplification: stablecoin supply > $250B + dominance falling = risk-on.
    if out["stablecoin_mcap_total"] and out["stablecoin_mcap_total"] >= 250e9 and btc_dom_delta is not None and btc_dom_delta < 0:
        out["read"] = "🟢 RISK-ON — stablecoin liquidity high + BTC dominance rolling over"
    elif out["stablecoin_mcap_total"] and out["stablecoin_mcap_total"] < 220e9:
        out["read"] = "🔴 RISK-OFF — on-chain dollar supply contracting"
    else:
        out["read"] = "🟡 NEUTRAL — liquidity stable, dominance steady"

    return out


def print_macro_section(macro):
    """Print the macro thermometer block in the narrative rotation report."""
    lines = ["", "=" * 55, "🌡️ MACRO LIQUIDITY THERMOMETER", "=" * 55]
    if macro.get("btc_dominance") is not None:
        lines.append(f"  BTC dominance: {macro['btc_dominance']:.1f}%")
        if macro.get("btc_dom_delta") is not None:
            lines.append(f"  vs last read:  {macro['btc_dom_delta']:+.1f} pp")
    if macro.get("usdt_mcap") is not None:
        lines.append(f"  USDT market cap: {format_mc(macro['usdt_mcap'])}")
    if macro.get("usdc_mcap") is not None:
        lines.append(f"  USDC market cap: {format_mc(macro['usdc_mcap'])}")
    if macro.get("stablecoin_mcap_total") is not None:
        lines.append(f"  Stablecoin supply: {format_mc(macro['stablecoin_mcap_total'])}")
    for s in macro.get("signals", []):
        lines.append(f"  {s}")
    lines.append(f"  → {macro.get('read', 'n/a')}")
    print("\n".join(lines))


def main():
    print("🔄 NARRATIVE ROTATION SCANNER")
    print(f"{'='*55}")
    
    # Fetch BTC for context
    btc_data = fetch_prices(["BTC"])
    btc = btc_data.get("BTC", {})
    btc_price = btc.get("price", 0)
    btc_7d = btc.get("change_7d", 0)
    print(f"\n🧭 BTC CONTEXT: ${btc_price:,.2f} | 7d: {btc_7d:+.1f}%")

    # Macro liquidity thermometer (BTC dominance + stablecoin supply) — the
    # bull/bear backdrop for the narratives (Jordan, Aug 21 2026).
    print_macro_section(fetch_macro_indicators())
    
    # Collect all symbols we need
    all_symbols = []
    for narr in NARRATIVES.values():
        all_symbols.extend(narr["coins"])
    
    # Fetch in batches of 10 (CMC limit)
    all_data = {}
    for i in range(0, len(all_symbols), 10):
        batch = all_symbols[i:i+10]
        all_data.update(fetch_prices(batch))
        time.sleep(1)  # Rate limit
    
    # Score each narrative
    narrative_scores = {}
    for name, narr in NARRATIVES.items():
        scores = []
        for coin in narr["coins"]:
            if coin in all_data:
                scores.append(narrative_score(all_data[coin]))
        avg_score = sum(scores) / len(scores) if scores else 0
        narrative_scores[name] = avg_score
    
    # Sort narratives by score (hottest first)
    sorted_narratives = sorted(narrative_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'='*55}")
    print("📊 NARRATIVE RANKING (by momentum score)")
    print(f"{'='*55}")
    
    for rank, (name, score) in enumerate(sorted_narratives, 1):
        narr = NARRATIVES[name]
        emoji = narr["emoji"]
        zone = classify_zone(
            sum(all_data.get(c, {}).get("change_7d", 0) for c in narr["coins"]) / len(narr["coins"]),
            sum(all_data.get(c, {}).get("change_30d", 0) for c in narr["coins"]) / len(narr["coins"])
        )
        # Calculate narrative-level sentiment
        avg_24h = sum(all_data.get(c, {}).get("change_24h", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_7d = sum(all_data.get(c, {}).get("change_7d", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_vol = sum(all_data.get(c, {}).get("vol_24h", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_mc = sum(all_data.get(c, {}).get("mc", 0) for c in narr["coins"]) / len(narr["coins"])
        sentiment, rainbow_hint, sent_score, vol_ratio = classify_sentiment(avg_24h, avg_7d, avg_vol, avg_mc)

        print(f"\n{rank}. {emoji} {name} — {zone} (score: {score:+.1f})")
        print(f"   Sentiment: {sentiment} | Vol/MCap: {vol_ratio}%")
        print(f"   🌈 Rainbow: {rainbow_hint}")
        print(f"   Thesis: {narr['thesis']}")
        
        for coin in narr["coins"]:
            if coin in all_data:
                d = all_data[coin]
                chg_7d = d["change_7d"]
                chg_30d = d["change_30d"]
                arrow_7 = "🔺" if chg_7d > 0 else "🔻"
                arrow_30 = "🔺" if chg_30d > 0 else "🔻"
                print(f"   {coin}: ${d['price']:.4f} | 7d: {arrow_7}{abs(chg_7d):.1f}% | 30d: {arrow_30}{abs(chg_30d):.1f}% | MCap: {format_mc(d['mc'])}")
    
    # Rotation signals
    print(f"\n{'='*55}")
    print("🧭 ROTATION SIGNALS")
    print(f"{'='*55}")
    
    if len(sorted_narratives) >= 2:
        hot = sorted_narratives[0]
        cold = sorted_narratives[-1]
        print(f"\n🔥 Hottest: {NARRATIVES[hot[0]]['emoji']} {hot[0]} (score: {hot[1]:+.1f})")
        print(f"❄️ Coldest: {NARRATIVES[cold[0]]['emoji']} {cold[0]} (score: {cold[1]:+.1f})")
        
        # Check for potential rotation signals
        if hot[1] > 5 and cold[1] < -5:
            print(f"\n⚡ ROTATION ALERT: Strong momentum divergence")
            print(f"   Money may be rotating FROM {cold[0]} → {hot[0]}")
        
        # Check BTC context
        if btc_7d < -5:
            print(f"\n⚠️ BTC WEAKNESS: -{abs(btc_7d):.1f}% 7d — risk-off environment")
            print(f"   Defensive narratives (RWA, stablecoins) may outperform")
        elif btc_7d > 5:
            print(f"\n🚀 BTC STRENGTH: +{btc_7d:.1f}% 7d — risk-on environment")
            print(f"   Beta narratives (meme, gaming) may outperform")
    
    print(f"\n{'='*55}")
    print("📋 ACTIONABLE TAKEAWAYS")
    print(f"{'='*55}")
    
    # Generate simple recommendations
    top_narr = sorted_narratives[0][0]
    bottom_narr = sorted_narratives[-1][0]
    
    print(f"\n1. OVERWEIGHT: {NARRATIVES[top_narr]['emoji']} {top_narr}")
    print(f"   → Strongest momentum, consider adding exposure")
    print(f"\n2. UNDERWEIGHT: {NARRATIVES[bottom_narr]['emoji']} {bottom_narr}")
    print(f"   → Weakest momentum, trim or avoid new positions")
    print(f"\n3. WATCH: Narrative divergence — if AI stays hot while DeFi cools,")
    print(f"   it signals a rotation into infrastructure/ compute plays")
    
    print(f"\n{'='*55}")
    print("📊 Source: CoinMarketCap | Weekly Narrative Rotation")
    print(f"{'='*55}")

    # === Write JSON for dashboard ===
    json_output = {
        "lastUpdated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "btc": {
            "price": btc_price,
            "change_7d": btc_7d
        },
        "narratives": [],
        "signals": {}
    }

    for rank, (name, score) in enumerate(sorted_narratives, 1):
        narr = NARRATIVES[name]
        zone = classify_zone(
            sum(all_data.get(c, {}).get("change_7d", 0) for c in narr["coins"]) / len(narr["coins"]),
            sum(all_data.get(c, {}).get("change_30d", 0) for c in narr["coins"]) / len(narr["coins"])
        )
        # Hub expects coins as comma-separated string
        coin_list = []
        for coin in narr["coins"]:
            if coin in all_data:
                d = all_data[coin]
                chg = d["change_7d"]
                arrow = "↑" if chg >= 0 else "↓"
                coin_list.append(f"{coin} {arrow}{abs(chg):.0f}%")
            else:
                coin_list.append(coin)

        # Sentiment data for JSON
        avg_24h_j = sum(all_data.get(c, {}).get("change_24h", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_7d_j = sum(all_data.get(c, {}).get("change_7d", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_vol_j = sum(all_data.get(c, {}).get("vol_24h", 0) for c in narr["coins"]) / len(narr["coins"])
        avg_mc_j = sum(all_data.get(c, {}).get("mc", 0) for c in narr["coins"]) / len(narr["coins"])
        sent, hint, s_score, v_ratio = classify_sentiment(avg_24h_j, avg_7d_j, avg_vol_j, avg_mc_j)

        json_output["narratives"].append({
            "rank": rank,
            "name": name,
            "emoji": narr["emoji"],
            "thesis": narr["thesis"],
            "score": round(score, 1),
            "zone": zone,
            "coins": ", ".join(coin_list),
            "sentiment": sent,
            "rainbow_hint": hint,
            "sentiment_score": s_score,
            "vol_cap_ratio": v_ratio
        })

    if sorted_narratives:
        json_output["signals"] = {
            "hottest": {"name": sorted_narratives[0][0], "emoji": NARRATIVES[sorted_narratives[0][0]]["emoji"], "score": round(sorted_narratives[0][1], 1)},
            "coldest": {"name": sorted_narratives[-1][0], "emoji": NARRATIVES[sorted_narratives[-1][0]]["emoji"], "score": round(sorted_narratives[-1][1], 1)}
        }

    json_path = "/root/repos/ProtoJay4789.github.io/DeFi/rainbow/rotation-data.json"
    try:
        with open(json_path, "w") as f:
            json.dump(json_output, f, indent=2)
        print(f"\n✅ Dashboard JSON written to {json_path}")
    except Exception as e:
        print(f"\n⚠️ Failed to write JSON: {e}")


if __name__ == "__main__":
    main()
