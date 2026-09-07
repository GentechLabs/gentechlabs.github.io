#!/usr/bin/env python3
"""
Steward Buy List — Merged Intelligence Monitor
==============================================
Combines THREE layers into one report:
  1. BUY LIST   — price + buy zone + rail + method + yield + strategy per coin
  2. DEFI RAINBOW — per-coin value zone (Euphoria → Panic Farm)
  3. MARKET SENTIMENT — sector rotation ranking (hottest → coldest)

Silent unless meaningful movement (>= threshold) OR a coin enters a buy zone.
Designed for no_agent cron via script= parameter.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

# Quiet hours: skip overnight (22:00-08:00 ET)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiet_hours import is_quiet_hours
if is_quiet_hours():
    sys.exit(0)

# Config
CMC_CONFIG = "/root/.hermes/scripts/cmc_config.json"
STATE_FILE = "/root/.hermes/scripts/.steward-buylist-state.json"
MOVEMENT_THRESHOLD = 1.5  # % change to trigger report
OVERRIDES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "steward-buylist-overrides.json")


def _load_overrides():
    """Load Steward Council overrides. The council can flip a coin's strategy
    (e.g. trade -> yield-farm) after a Fed meeting or market event. Merged over
    the static BUYLIST defaults each run."""
    try:
        with open(OVERRIDES_FILE) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception:
        return {}


def _apply_overrides(coin, overrides):
    """Return a copy of the coin with council overrides applied."""
    o = overrides.get(coin["symbol"], {})
    if not o:
        return coin
    merged = dict(coin)
    for field in ("method", "yield", "strategy", "rail"):
        if field in o:
            merged[field] = o[field]
    if "zones" in o:
        merged["zones"] = o["zones"]
    return merged


def _load_cmc_key():
    try:
        with open(CMC_CONFIG) as f:
            return json.load(f).get("coinmarketcap_api_key", "")
    except Exception:
        return os.environ.get("CMC_API_KEY", "")


CMC_API_KEY = _load_cmc_key()
HEADERS = {
    "X-CMC_PRO_API_KEY": CMC_API_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# ── Steward Buy List — per-coin intelligence ──────────────────────────────
BUYLIST = [
    {
        "symbol": "BTC", "cmc_id": "1", "cg_id": "bitcoin",
        "class": "Coin · L1",
        "rail": "Coinbase spot / Hyperliquid perp",
        "method": "spot (DCA) or perp leverage",
        "yield": "no — hold or lend (Coinbase 3.5% APY)",
        "strategy": "TRADE > farm (no LP yield worth it)",
        # Zones updated 2026-08-27 (Jordan): 76K = his line of defense (accumulate
        # at/below), 84K = range top / breakout trigger. Video floor 72.5-74K.
        "zones": [0, 72000, 76000, 84000, 999999],
    },
    {
        "symbol": "SOL", "cmc_id": "5426", "cg_id": "solana",
        "class": "Coin · L1",
        "rail": "Solana (Meteora / Jupiter)",
        "method": "spot or yield-farm",
        "yield": "yes — Meteora LP, Jito staking",
        "strategy": "FARM > trade (strong LP yield)",
        "zones": [0, 40, 60, 80, 999999],
    },
    {
        "symbol": "LINK", "cmc_id": "1975", "cg_id": "chainlink",
        "class": "Coin · Oracle infra",
        "rail": "Base / Ethereum",
        "method": "spot",
        "yield": "limited — some Base pools",
        "strategy": "TRADE > farm",
        "zones": [0, 5, 8, 12, 999999],
    },
    {
        "symbol": "AVAX", "cmc_id": "5805", "cg_id": "avalanche-2",
        "class": "Coin · L1",
        "rail": "Avalanche (LFJ V2.2 / Trader Joe)",
        "method": "yield-farm (curve LP) or spot",
        "yield": "yes — LFJ V2.2 curve LP, staking 5.2%",
        "strategy": "FARM > trade (our core rail)",
        "zones": [0, 5.50, 6.50, 8.00, 999999],
    },
    {
        "symbol": "TAO", "cmc_id": "22974", "cg_id": "bittensor",
        "class": "Coin · AI infra",
        "rail": "Ethereum / Bittensor",
        "method": "spot",
        "yield": "limited",
        "strategy": "TRADE > farm",
        "zones": [0, 150, 250, 400, 999999],
    },
    {
        "symbol": "XAUt", "cmc_id": "5176", "cg_id": "tether-gold",
        "class": "RWA · Commodity (gold)",
        "rail": "Ethereum",
        "method": "spot (gold proxy)",
        "yield": "no",
        "strategy": "HOLD (safe-haven)",
        "zones": [0, 2000, 2500, 3000, 999999],
    },
    {
        "symbol": "ONDO", "cmc_id": "26754", "cg_id": "ondo-finance",
        "class": "RWA · Treasury yield",
        "rail": "Ethereum / Base",
        "method": "spot",
        "yield": "yes — ONDO RWA yield",
        "strategy": "FARM > trade (RWA yield)",
        "zones": [0, 0.50, 0.80, 1.20, 999999],
    },
    {
        "symbol": "COQ", "cmc_id": "28675", "cg_id": "coq-inu",
        "class": "Coin · Memecoin",
        "rail": "Avalanche (LFJ V2.2 / Trader Joe)",
        "method": "yield-farm (COQ/AVAX LP) or spot",
        "yield": "yes — COQ/AVAX LP on LFJ",
        "strategy": "FARM > trade (memecoin LP fees)",
        "zones": [0, 0.0000005, 0.000001, 0.000002, 999999],
    },
]

# ── Narrative scanner — sector rotation ────────────────────────────────────
NARRATIVES = {
    "AI & Data": {
        "coins": ["FET", "RENDER", "TAO", "AKT"],
        "emoji": "🤖",
        "thesis": "AI compute, data markets, decentralized inference",
    },
    "RWA (Real World Assets)": {
        "coins": ["ONDO", "PLU", "CPOOL"],
        "emoji": "🏠",
        "thesis": "Tokenized treasuries, real estate, credit",
    },
    "DeFi Blue Chips": {
        "coins": ["UNI", "AAVE", "LINK", "MKR"],
        "emoji": "🏦",
        "thesis": "Dex, lending, oracles, stablecoins",
    },
    "L1 / L2": {
        "coins": ["SOL", "AVAX", "NEAR", "ARB"],
        "emoji": "⛓️",
        "thesis": "Base layers and scaling",
    },
    "Meme / Community": {
        "coins": ["DOGE", "PEPE", "WIF", "BONK"],
        "emoji": "🐸",
        "thesis": "Community-driven, narrative plays",
    },
    "Gaming / Metaverse": {
        "coins": ["IMX", "GALA", "PYTH"],
        "emoji": "🎮",
        "thesis": "On-chain gaming, virtual worlds",
    },
}

# ── DeFi Rainbow — per-coin value zones ────────────────────────────────────
RAINBOW_BANDS = [
    {"id": "euphoria",    "name": "Euphoria",      "emoji": "🔴", "lo": 1.5, "hi": 99,
     "advice": "Take profits. Price is rich vs its recent range."},
    {"id": "peak_yield",  "name": "Peak Yield",    "emoji": "🟠", "lo": 0.8, "hi": 1.5,
     "advice": "Rich zone. Trim into strength."},
    {"id": "harvest",     "name": "Harvest Mode",  "emoji": "🟡", "lo": 0.3, "hi": 0.8,
     "advice": "Healthy. Hold / compound."},
    {"id": "accumulation", "name": "Accumulation", "emoji": "🟢", "lo": -0.3, "hi": 0.3,
     "advice": "Fair value. DCA in."},
    {"id": "bleeding",    "name": "Bleeding Edge", "emoji": "🔵", "lo": -0.8, "hi": -0.3,
     "advice": "Cheap. Micro-DCA / prepare to accumulate."},
    {"id": "panic",       "name": "Panic Farm",    "emoji": "🟣", "lo": -99, "hi": -0.8,
     "advice": "Generational entry. Be greedy when others fear."},
]

# ── Macro / Fed — FOMC + key economic data ─────────────────────────────────
FOMC_2026 = [
    {"date": "2026-09-17", "status": "upcoming", "decision": "Pending — SEP update"},
    {"date": "2026-10-28", "status": "upcoming", "decision": "Pending"},
    {"date": "2026-12-09", "status": "upcoming", "decision": "Pending — SEP update"},
]

MACRO_EVENTS = [
    {"event": "CPI (MoM)", "dates": ["2026-08-12", "2026-09-10", "2026-10-14"],
     "importance": "critical", "move": "AVAX ±3-6%"},
    {"event": "Core CPI (MoM)", "dates": ["2026-08-12", "2026-09-10", "2026-10-14"],
     "importance": "critical", "move": "AVAX ±4-7%"},
    {"event": "PPI (MoM)", "dates": ["2026-08-13", "2026-09-11", "2026-10-10"],
     "importance": "high", "move": "AVAX ±2-4%"},
    {"event": "Non-Farm Payrolls", "dates": ["2026-09-04", "2026-10-02", "2026-11-06"],
     "importance": "critical", "move": "AVAX ±3-5%"},
    {"event": "PCE Price Index (MoM)", "dates": ["2026-08-28", "2026-09-25", "2026-10-30"],
     "importance": "critical", "move": "AVAX ±3-6%"},
    {"event": "Core PCE (MoM)", "dates": ["2026-08-28", "2026-09-25", "2026-10-30"],
     "importance": "critical", "move": "AVAX ±4-7%"},
    {"event": "Fed Chair Press Conference", "dates": ["2026-09-17", "2026-10-28", "2026-12-09"],
     "importance": "critical", "move": "AVAX ±5-10%"},
]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_prices": {}, "last_run": None}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_cmc_batch(symbols):
    """Fetch price + 24h/7d/30d for a batch of symbols (CMC)."""
    results = {}
    sym_str = ",".join(symbols)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={sym_str}&convert=USD"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            for sym in symbols:
                if sym in data.get("data", {}):
                    coin = data["data"][sym]
                    q = coin.get("quote", {}).get("USD", {})
                    results[sym] = {
                        "price": q.get("price", 0),
                        "change_24h": q.get("percent_change_24h", 0),
                        "change_7d": q.get("percent_change_7d", 0),
                        "change_30d": q.get("percent_change_30d", 0),
                        # 90d is plan-dependent — kept optional, rendered only if present
                        "change_90d": q.get("percent_change_90d"),
                        "mc": q.get("market_cap", 0),
                        "vol_24h": q.get("volume_24h", 0),
                    }
    except Exception as e:
        print(f"  ⚠️ CMC fetch error: {e}", file=sys.stderr)
    return results


def format_price(symbol, price):
    if price is None:
        return "$0.00"
    if price >= 1000:
        return f"${price:,.0f}"
    elif price >= 1:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    elif price >= 0.000001:
        return f"${price:.6f}"
    else:
        return f"${price:.8f}"


def buy_zone(coin, price):
    z = coin["zones"]
    if price < z[1]:
        return "Deep Value", "🔥"
    elif price < z[2]:
        return "Accumulate", "🟢"
    elif price < z[3]:
        return "Watch", "🔵"
    else:
        return "Extended", "⚪"


def rainbow_band(metrics):
    """Compute DeFi rainbow band from 7d + 30d momentum (per-coin hint)."""
    score = 0.6 * (metrics.get("change_7d", 0) / 10.0) + 0.4 * (metrics.get("change_30d", 0) / 10.0)
    norm = max(-2.0, min(2.0, score))
    for band in RAINBOW_BANDS:
        if band["lo"] <= norm < band["hi"]:
            return band, norm
    return RAINBOW_BANDS[0], norm


def macro_events_report():
    """Build Layer 4: upcoming FOMC + macro data with day counts."""
    from datetime import date as _date
    today = _date.today()
    rows = []

    # FOMC
    fomc_hits = []
    for m in FOMC_2026:
        try:
            d = _date.fromisoformat(m["date"])
        except Exception:
            continue
        delta = (d - today).days
        if 0 <= delta <= 14:
            fomc_hits.append((delta, m))
    for delta, m in sorted(fomc_hits):
        tag = "TODAY" if delta == 0 else "TOMORROW" if delta == 1 else f"in {delta}d"
        rows.append(f"   🚨 FOMC {tag} ({m['date']}) — {m['decision']}")

    # Macro data
    for econ in MACRO_EVENTS:
        for date_str in econ["dates"]:
            try:
                d = _date.fromisoformat(date_str)
            except Exception:
                continue
            delta = (d - today).days
            if not (0 <= delta <= 7):
                continue
            emoji = "🔴" if econ["importance"] == "critical" else "🟠"
            tag = "TODAY" if delta == 0 else "TOMORROW" if delta == 1 else f"in {delta}d"
            rows.append(f"   {emoji} {econ['event']} {tag} ({date_str}) — {econ['move']}")

    if not rows:
        return None
    return rows


def _lead_call(all_data, zone_hits, movements, significant=False):
    """Lead Call (Jordan, Aug 29 2026): the judgment layer.

    Weighs the whole board and names THE ONE that matters right now —
    'hey, now is really time for Bitcoin, everything else can wait.'
    Deterministic scoring: zone weight (Deep Value 3 / Accumulate 2) +
    movement weight (|move|/5, capped at 2). One lead, honest reason.
    Movement-only reports (no zone hit) lead with the biggest mover,
    framed as watch — never dress a move up as a value signal.
    """
    scored = []
    for sym, label, emoji in zone_hits:
        zw = 3.0 if label == "Deep Value" else 2.0
        mv = movements.get(sym, 0) or 0
        mw = min(abs(mv) / 5.0, 2.0)
        scored.append((zw + mw, sym, label, mv))
    if scored:
        scored.sort(reverse=True)
        _, sym, label, mv = scored[0]
        reason = f"{label} zone"
        if abs(mv) >= MOVEMENT_THRESHOLD:
            reason += f" + {mv:+.1f}% move"
        return [f"⭐ **LEAD CALL: {sym}** — {reason}. Everything else can wait."]

    if significant:
        # No zone triggered — biggest mover gets the spotlight, as a WATCH.
        cands = [(abs((d.get("change_24h") or 0)), sym, (d.get("change_24h") or 0))
                 for sym, d in all_data.items() if d.get("price")]
        if cands:
            cands.sort(reverse=True)
            _, sym, ch = cands[0]
            return [f"⭐ **LEAD CALL: {sym}** — biggest mover on the board ({ch:+.1f}% 24h), "
                    f"no value zone triggered. Watch, don't chase."]
    return []


def _voice_lead_call(sym, label, mv, price):
    """Rainbow Opine (Jordan, Aug 29 2026): when the Lead Call fires on a real
    value zone, the rainbow OPINES in the Steve Harvey voice — a take that makes
    you think. Rate-limited (1/day global, 3-day per-symbol cooldown) so it
    stays special. Generates mp3 via steve-harvey-tts.py; cron delivers it
    natively via the MEDIA: stdout convention. Returns (line, media_path)."""
    state_p = "/root/.hermes/scripts/.steward-voice-opine-state.json"
    now = time.time()
    st = {"last_voice_day": "", "last_symbol": "", "last_ts": {}}
    try:
        with open(state_p) as f:
            st = json.load(f)
    except Exception:
        pass

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if st.get("last_voice_day") == today:
        return None  # already opined today — stays special
    last_sym_ts = (st.get("last_ts") or {}).get(sym, 0)
    if now - last_sym_ts < 3 * 86400:
        return None  # per-symbol cooldown

    verb = "dipping" if mv < 0 else "moving"
    price_s = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
    script_text = (
        f"Ladies and gentlemen, the board is speaking. {sym} is {verb} "
        f"and it just walked into the {label} zone at {price_s}. Now you can "
        f"watch it, or you can respect it. The rainbow says the value is here — "
        f"the rest can wait its turn."
    )
    import subprocess
    try:
        proc = subprocess.run(
            [sys.executable, "/root/.hermes/profiles/gentech/scripts/steve-harvey-tts.py", script_text],
            capture_output=True, text=True, timeout=180)
        media = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        if proc.returncode != 0 or not media or not os.path.exists(media):
            return None  # voice is garnish — never block the report
    except Exception:
        return None

    st["last_voice_day"] = today
    st["last_symbol"] = sym
    st.setdefault("last_ts", {})[sym] = now
    with open(state_p, "w") as f:
        json.dump(st, f, indent=2)
    return (f"🎙️ **The rainbow opines** — the Chair's take on {sym}, attached below.",
            media)


def main():
    state = load_state()
    last_prices = state.get("last_prices", {})
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d %H:%M UTC")

    # Collect all symbols we need (buy list + narratives)
    all_symbols = [c["symbol"] for c in BUYLIST]
    for narr in NARRATIVES.values():
        for s in narr["coins"]:
            if s not in all_symbols:
                all_symbols.append(s)

    # Fetch in batches of 10 (CMC limit)
    all_data = {}
    for i in range(0, len(all_symbols), 10):
        batch = all_symbols[i:i + 10]
        all_data.update(fetch_cmc_batch(batch))
        time.sleep(1)

    if not all_data:
        print(json.dumps({"error": "No price data retrieved", "time": now_str}))
        return

    # Movement since last check
    max_change = 0
    movements = {}
    for sym, data in all_data.items():
        prev = last_prices.get(sym, {}).get("price") or 0
        if prev > 0:
            pct = abs((data["price"] - prev) / prev) * 100
            movements[sym] = round(pct, 2)
            max_change = max(max_change, pct)
        else:
            movements[sym] = 0

    # Save state
    state["last_prices"] = {sym: {"price": d.get("price") or 0} for sym, d in all_data.items()}
    state["last_run"] = now_str
    # ── Farm-vs-trade signal (Sep 7 2026): the source of truth the council
    # reads. Aggregate each coin's method/yield/strategy into a market-wide
    # lean: how many coins favor FARM vs TRADE vs HOLD. The council's rail
    # decision consumes this directly.
    farm = sum(1 for c in BUYLIST if "FARM" in (c.get("strategy") or "").upper())
    trade = sum(1 for c in BUYLIST if "TRADE" in (c.get("strategy") or "").upper())
    state["farm_vs_trade"] = {
        "farm": farm, "trade": trade,
        "lean": "FARM" if farm > trade else ("TRADE" if trade > farm else "BALANCED"),
        "ts": now_str,
    }
    save_state(state)

    # Determine if we should report
    significant = max_change >= MOVEMENT_THRESHOLD
    zone_hits = []
    for coin in BUYLIST:
        if coin["symbol"] in all_data and all_data[coin["symbol"]].get("price"):
            label, emoji = buy_zone(coin, all_data[coin["symbol"]]["price"])
            if label in ("Deep Value", "Accumulate"):
                zone_hits.append((coin["symbol"], label, emoji))

    # ALWAYS report (Jordan, Sep 7 2026): "we're in a time where I need to see
    # the market. we can change the rules about needing significant movement to
    # report." The movement/zone callouts stay as highlights within the always-on
    # report — the buy list is now the market pulse, not just an alert feed.

    # ── Build report ────────────────────────────────────────────────────────
    L = []
    L.append(f"🛡️ STEWARD BUY LIST — {now_str}")
    L.append("")

    if significant:
        L.append(f"⚡ SIGNIFICANT MOVEMENT DETECTED (max {max_change:.1f}%)")
    if zone_hits:
        L.append("🎯 BUY ZONE ALERT: " + ", ".join(f"{e} {s} ({l})" for s, l, e in zone_hits))
    if significant or zone_hits:
        L.append("")

    # ── Zoom Out board (Jordan, Sep 1 2026): the trend-teller ──────────────
    # Daily change is noise; monthly change shows the reversal. Rank the buy
    # list by 30d so the board answers "how are we actually doing?" at a glance.
    L.append("━━━ 🔭 ZOOM OUT — 30d TREND ━━━")
    L.append("")
    _zoom = []
    for coin in BUYLIST:
        sym = coin["symbol"]
        d = all_data.get(sym) or {}
        if not d.get("price"):
            continue
        c30 = d.get("change_30d")
        if c30 is None:
            continue
        arrow = "🔺" if (c30 or 0) > 2 else "🔻" if (c30 or 0) < -2 else "➖"
        _zoom.append((c30, sym, arrow))
    if _zoom:
        _zoom.sort(reverse=True)
        _flips = sum(1 for c30, _s, _a in _zoom if (c30 or 0) > 0)
        L.append(f"   Monthly trend: {_flips}/{len(_zoom)} coins positive — "
                 + ("reversal CONFIRMED" if _flips >= len(_zoom) * 0.6
                    else "no reversal yet" if _flips <= len(_zoom) * 0.3
                    else "mixed recovery"))
        L.append("")
        for c30, sym, arrow in _zoom:
            L.append(f"   {arrow} **{sym}** {c30:+.1f}% (30d)")
        L.append("")
        L.append("   *Daily moves are noise. The monthly line is the truth.*")
        L.append("")

    # ── Lead Call (Jordan, Aug 29 2026): the judgment layer ────────────────
    # One line that weighs the whole board: THE one that matters right now.
    _opine_media = None
    for _lead in _lead_call(all_data, zone_hits, movements, significant):
        L.append(_lead)
        L.append("")
        # Rainbow Opine (Jordan, Aug 29 2026): when the Lead Call fires on a
        # real value zone, the chair VOICES the take (rate-limited, garnish
        # only — never blocks the report). Delivered via MEDIA: convention.
        if zone_hits:
            _sym, _label, _emoji = zone_hits[0]
            _v = _voice_lead_call(_sym, _label, movements.get(_sym, 0),
                                  (all_data.get(_sym) or {}).get("price", 0))
            if _v:
                L.append(_v[0])
                L.append("")
                _opine_media = _v[1]

    # ── Layer 1: Buy List ──────────────────────────────────────────────────
    L.append("━━━ 📋 BUY LIST ━━━")
    L.append("")
    overrides = _load_overrides()
    for i, coin in enumerate(BUYLIST):
        coin = _apply_overrides(coin, overrides)
        sym = coin["symbol"]
        if sym not in all_data or not all_data[sym].get("price"):
            continue
        d = all_data[sym]
        c24 = d.get("change_24h") or 0
        c7 = d.get("change_7d") or 0
        c30 = d.get("change_30d") or 0
        move = movements.get(sym, 0)
        e24 = "🟢" if c24 > 0 else "🔴" if c24 < 0 else "⚪"
        label, emoji = buy_zone(coin, d["price"])

        L.append(f"**{emoji} {sym} — {format_price(sym, d['price'])}**  [{label}]")
        L.append("")
        L.append(f"   🏷️ Class: {coin.get('class', 'n/a')}")
        L.append(f"   📈 1d: {e24} {c24:+.2f}%   ·   1w: {c7:+.2f}%   ·   1m: {c30:+.2f}%")
        L.append("")
        L.append(f"   🛤️ Rail: {coin['rail']}")
        L.append(f"   🧭 Method: {coin['method']}")
        L.append(f"   💰 Yield: {coin['yield']}")
        L.append(f"   🎯 Strategy: {coin['strategy']}")
        # Per-coin DeFi Rainbow hint (Jordan, Aug 23 2026): a quick value-zone
        # read on each coin. The full Rainbow section stays on Sunday.
        band, _norm = rainbow_band(d)
        L.append(f"   🌈 {band['emoji']} {band['name']}: {band['advice']}")
        L.append("")
        L.append("")

    # ── Layer 2: DeFi Rainbow ──────────────────────────────────────────────
    # MOVED to the Sunday Fed Council (Jordan, Aug 23 2026). The buy list cron
    # now focuses on the coins only — rainbow + sentiment surface weekly.

    # ── Layer 3: Market Sentiment ──────────────────────────────────────────
    # MOVED to the Sunday Fed Council. See weekly-fed-council.py.

    # ── Layer 4: Macro / Fed ───────────────────────────────────────────────
    # MOVED to the Sunday Fed Council (Jordan, Aug 23 2026). The weekly rundown
    # of FOMC + macro events now voices on Sunday. See weekly-fed-council.py.

    L.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    L.append(f"Source: CMC | Threshold: {MOVEMENT_THRESHOLD}%")

    print("\n".join(L))

    # Opine audio — native cron delivery via MEDIA: stdout convention
    if _opine_media:
        print(f"MEDIA:{_opine_media}")


if __name__ == "__main__":
    main()
