#!/usr/bin/env python3
"""
Steward Council — the treasury's FOMC (Jordan, Aug 19 2026).

The Steward is the Chair. Every agent that runs a piece of the Agentic Treasury
is a Council member. When they convene, they deliberate — each gives its read,
the dissent is NAMED (doves/hawks), and minutes are written to the journal.

This is the flagship delivery: ONE meeting instead of parallel reports.

Members (live reads):
  - 🛡️ Capital Gate  -> treasury_has_capital()  (live on-chain, $25 floor)
  - 📋 Buyer          -> live CMC prices vs seasonal buy zones
  - 🔭 Scanner        -> perp-vs-spot basis from .gta-arb-state.json
  - 🌦️ Regime       -> regime from .aae-regime-state.json
  - 🛡️ Sentry        -> position watchdog / heartbeat state (if present)

Consensus: all members agree -> CONSENSUS. Any dissent -> MIXED/DISSENT, named.
Designed for no_agent cron (script=) or direct run.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
STATE_DIR = "/root/.hermes/scripts"  # shared state dir (cmc_config.json etc.)

# ── Shared treasury brain (Aug 21 2026) ─────────────────────────────────
# The council is the ONLY body that recommends changing treasury mode. But a
# council cron is no_agent — it cannot ask Jordan mid-run. So it writes a
# PENDING mode recommendation to treasury-state.json's request slot, and the
# mode only actually flips when Jordan confirms (or a maintenance sub-mode is
# clearly safe). This is the Fed-chair-as-brain pattern: the council reasons,
# Jordan ratifies the big turns.
try:
    import treasury_state as _ts
    from treasury_state import load_state, get_mode
except Exception:
    _ts = None
    def load_state(): return {}
    def get_mode(s=None): return "YIELD_FARM"

# Regime -> recommended mode (Jordan's strategy): these are the automatic
# maintenance mappings. Only these flip without Jordan (they just re-target the
# SAME farm rail, not farm<->trade). Crossing farm<->trade always asks.
REGIME_MAINTENANCE = {
    "RANGE_BOUND": "YIELD_FARM",
    "ACCUMULATION": "YIELD_FARM",
    "PRICE_DISCOVERY": "YIELD_FARM",
    "BULL_TRENDING": "TRADE",
    "BEAR_TRENDING": "TRADE",
    "HIGH_VOLATILITY": "TRADE",
}
# Modes that are "just maintenance" (safe to auto-apply from regime) vs modes
# that need Jordan's explicit go (they move capital strategy).
SAFE_MAINTENANCE = {"YIELD_FARM"}
REQUIRES_JORDAN = {"TRADE", "DRY_POWDER"}

CALENDAR_FILE = "/root/vaults/gentech/DeFi/agentic-calendar.json"
DOMINANCE_STATE_FILE = os.path.join(SCRIPT_DIR, ".btc-dominance-state.json")

def _read_dominance():
    """Read BTC dominance state (alt-season trigger)."""
    try:
        with open(DOMINANCE_STATE_FILE) as f:
            d = json.load(f)
        dom = d.get("btc_dominance")
        if dom is None:
            return None
        prev = d.get("prev_dominance")
        trend = "n/a"
        if isinstance(prev, (int, float)):
            delta = dom - prev
            trend = "▲" if delta >= 0 else "▼"
        note = ""
        if trend == "▼" and isinstance(prev, (int, float)) and (prev - dom) >= 0.5:
            note = "rollover — alts may follow"
        return {"btc": dom, "trend": trend, "note": note}
    except Exception:
        return None

def _load_agentic_calendar():
    """Load the forward calendar (Kanban-style) events for the radar."""
    for p in (CALENDAR_FILE, os.path.join(SCRIPT_DIR, "agentic-calendar.json")):
        try:
            with open(p) as f:
                return json.load(f).get("events", [])
        except Exception:
            continue
    return []

# ── Member 1: Capital Gate ───────────────────────────────────────────────
try:
    from capital_gate import treasury_has_capital, treasury_value_usd, STEWARD
except Exception:
    treasury_has_capital = lambda *a, **k: None
    treasury_value_usd = lambda *a, **k: None
    STEWARD = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"

# ── Member 2: Buy List zones (kept in sync with steward-buylist.py) ──────
BUY_ZONES = {
    "AVAX": [0, 5.50, 6.50, 8.00, 999999],   # updated 2026-08-19: floor confirmed
    "BTC":  [0, 58000, 66000, 75000, 999999], # updated 2026-08-19: no-knife standstill
}
_EMOJI = {"Deep Value": "🔥", "Accumulate": "🟢", "Watch": "🔵", "Extended": "⚪"}

def _price(symbol):
    cg = {"AVAX": "avalanche-2", "BTC": "bitcoin"}.get(symbol)
    if not cg:
        return None
    # Primary: CoinGecko. Fallback (Sep 4, 2026): CMC — CoinGecko 429s were
    # reading as "no price" votes in the council. CMC ids: BTC=1, AVAX=5805.
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg}&vs_currencies=usd"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return float(json.load(r)[cg]["usd"])
    except Exception:
        pass
    try:
        cmc_id = {"BTC": "1", "AVAX": "5805"}[symbol]
        key = ""
        try:
            with open(os.path.join(STATE_DIR, "cmc_config.json")) as f:
                key = json.load(f).get("coinmarketcap_api_key", "")
        except Exception:
            key = os.environ.get("CMC_API_KEY", "")
        if not key:
            return None
        req = urllib.request.Request(
            f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={cmc_id}&convert=USD",
            headers={"X-CMC_PRO_API_KEY": key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return float(json.load(r)["data"][cmc_id]["quote"]["USD"]["price"])
    except Exception:
        return None

def _buy_zone(coin, price):
    z = coin["zones"]
    if price < z[1]:
        return "Deep Value", "🔥"
    if price < z[2]:
        return "Accumulate", "🟢"
    if price < z[3]:
        return "Watch", "🔵"
    return "Extended", "⚪"

# ── Member 3: Scanner basis (perp vs spot) ───────────────────────────────
def _read_scanner():
    p = Path(SCRIPT_DIR) / ".gta-arb-state.json"
    try:
        if not p.exists():
            return None
        # Staleness gate (audit Aug 29): a 6-day-old scan showed as "basis live".
        # No live scan data is better than stale data wearing a live label.
        age_h = (time.time() - p.stat().st_mtime) / 3600
        if age_h > 24:
            return None
        data = json.loads(p.read_text())
        return data.get("opportunities") or []
    except Exception:
        return None

# ── Member 4: Regime ─────────────────────────────────────────────────────
def _read_regime():
    """Read the regime state file. Tries both known paths (cron vs shell HOME
    differ), and returns None if the file is missing OR stale (>6h old) so the
    council falls back to a live read rather than lagging the market."""
    candidates = [
        Path(os.path.expanduser("~/.hermes/scripts/.aae-regime-state.json")),
        Path("/root/.hermes/scripts/.aae-regime-state.json"),
        Path(SCRIPT_DIR) / ".aae-regime-state.json",
    ]
    for p in candidates:
        try:
            if not p.exists():
                continue
            data = json.loads(p.read_text())
            ts = data.get("timestamp")
            if ts:
                from datetime import datetime as _dt
                try:
                    age = (datetime.now(timezone.utc) - _dt.fromisoformat(ts)).total_seconds()
                    if age > 6 * 3600:  # stale — don't trust it
                        continue
                except Exception:
                    pass
            return data
        except Exception:
            continue
    return None

def _live_regime():
    """Live fallback: classify from current BTC momentum when the state file is stale."""
    btc = _price("BTC")
    if btc is None:
        return None
    # Standstill band from the journal thesis (2026-08-19): 58k-66k = standstill.
    if btc >= 66000:
        return {"regime": "BULL_TRENDING", "confidence": 0.6, "price": btc,
                "note": "live read — broke above standstill band"}
    if btc <= 58000:
        return {"regime": "BEAR_TRENDING", "confidence": 0.6, "price": btc,
                "note": "live read — broke below standstill band"}
    return {"regime": "RANGE_BOUND", "confidence": 0.6, "price": btc,
            "note": "live read — inside standstill band"}

_VERDICTS = []
def _vote(name, emoji, stance, note, block=None):
    """block in ('green','red','amber'). Returns the block for consensus math."""
    _VERDICTS.append({"name": name, "block": block})
    return f"{emoji} **{name}:** {stance} — {note}"


def _executive_stance(reg, sent, dom, buy_blocks):
    """The Fed-chair executive call: DOVISH / HAWKISH / CENTERED.

    Jordan's frame (Sep 7 2026): with all the member data on the table, the
    chair makes ONE executive decision on what rail / what strategy is best.
    This is the 'improve the concept' piece — the council doesn't just report
    consensus, it lands a directional stance that picks the rail.

    Inputs are the directional members (regime, sentiment, dominance) plus the
    buy-list blocks. Returns (stance, rail_call, strategy_call, rationale).
    """
    # ── Directional score: +1 risk-on, -1 risk-off, 0 neutral ──────────
    score = 0
    reasons = []

    # Regime
    r = (reg or {}).get("regime", "").upper()
    if r in ("BULL_TRENDING", "ACCUMULATION"):
        score += 1
        reasons.append(f"regime {r.replace('_',' ').title()} = risk-on")
    elif r in ("BEAR_TRENDING", "HIGH_VOLATILITY"):
        score -= 1
        reasons.append(f"regime {r.replace('_',' ').title()} = risk-off")
    else:  # RANGE_BOUND / PRICE_DISCOVERY / UNKNOWN
        reasons.append(f"regime {r.replace('_',' ').title() or 'UNKNOWN'} = neutral")

    # Sentiment
    s = (sent or {}).get("read") or (sent or {}).get("signals", {}).get("read") or ""
    s_low = s.lower()
    if "risk-on" in s_low or "bull" in s_low:
        score += 1
        reasons.append("sentiment risk-on/bull")
    elif "risk-off" in s_low or "bear" in s_low:
        score -= 1
        reasons.append("sentiment risk-off/bear")
    else:
        reasons.append("sentiment neutral/mixed")

    # Dominance (alt-season trigger): falling BTC dominance = risk-on alts
    if dom is not None:
        trend = dom.get("trend", "n/a")
        if trend == "▼":
            score += 1
            reasons.append("BTC dominance falling = alt-season risk-on")
        elif trend == "▲":
            score -= 1
            reasons.append("BTC dominance rising = flight to BTC, risk-off alts")

    # Buy-list blocks: how many coins are in accumulate/deep-value (green)
    # vs extended (red). A board heavy in accumulate zones = value = risk-on.
    greens = sum(1 for b in buy_blocks if b == "green")
    reds = sum(1 for b in buy_blocks if b == "red")
    if greens > reds:
        score += 1
        reasons.append(f"{greens} buy-list coins in value zones vs {reds} extended")
    elif reds > greens:
        score -= 1
        reasons.append(f"{reds} buy-list coins extended vs {greens} in value")

    # ── Map score to stance ─────────────────────────────────────────────
    if score >= 2:
        stance = "🕊️ DOVISH"
        rail_call = "Growth rails — AVAX LFJ farm + SOL Meteora; accumulate value zones"
        strategy_call = "FARM > trade, deploy dry powder into value, widen for upside"
    elif score <= -2:
        stance = "🦅 HAWKISH"
        rail_call = "Defensive — USDC dry powder, safe-haven HOLD (gold/BTC), reduce LP"
        strategy_call = "TRADE > farm, tighten stops, keep powder dry for the dip"
    else:
        stance = "⚖️ CENTERED"
        rail_call = "Hold current rail — stay the course, maintain the farm"
        strategy_call = "Watch — no new deploys, let the farm earn, wait for a clearer signal"

    return stance, rail_call, strategy_call, "; ".join(reasons)


def _strategy_recommendation(stance, reg, vol=None):
    """The council's deploy strategy: shape + bin count + allocation split.

    Jordan's frame (Sep 7 2026): the spread and split are INTELLIGENCE, not
    constants. The council decides how wide to be and which way to lean based
    on stance + volatility, so the treasury stays in range all day and earns
    a good amount.

    Shape semantics (shape-semantics skill): CURVE earns from chop inside a
    range; BID_ASK captures directional movement. The split is the direction
    bet — USDC-heavy (70-30) sells into strength as price climbs; WAVAX-heavy
    (30-70) buys the dip.

    Returns dict: {shape, bins, split, split_label, rationale}.
    """
    r = (reg or {}).get("regime", "").upper()
    # Volatility proxy: if we have a vol %, use it; else infer from regime.
    if vol is None:
        vol = 0.0
        if r in ("HIGH_VOLATILITY", "PRICE_DISCOVERY"):
            vol = 0.35
        elif r in ("BULL_TRENDING", "BEAR_TRENDING"):
            vol = 0.20
        else:  # RANGE_BOUND / ACCUMULATION
            vol = 0.10

    # ── Shape: directional stance → BID_ASK, neutral → CURVE ────────────
    if "DOVISH" in stance:
        shape = "BID_ASK"          # risk-on, catch the up-move
    elif "HAWKISH" in stance:
        shape = "BID_ASK"          # risk-off, catch the down-move
    else:
        shape = "CURVE"            # centered, harvest chop

    # ── Bin count: wider with volatility, tighter when calm ────────────
    # Jordan's targets: curve 11-25 bins, bid-ask a bit higher (~30).
    # Calm → tight (concentrate, earn more per bin). Choppy → wide (stay in
    # range, don't get knocked out on a small wiggle).
    if shape == "CURVE":
        if vol < 0.15:
            bins = 11          # calm — tight, max per-bin fee capture
        elif vol < 0.30:
            bins = 15          # moderate — balanced
        else:
            bins = 21          # choppy — wide, stay in range
    else:  # BID_ASK
        if vol < 0.15:
            bins = 15
        elif vol < 0.30:
            bins = 21
        else:
            bins = 25          # up to ~25 for bid-ask in high vol

    # ── Split: the direction bet ───────────────────────────────────────
    # 50-50 normal (even both sides). CORRECTED Sep 7 2026 (Jordan caught it):
    # in AVAX/USDC, tokenX=WAVAX, tokenY=USDC, price=USDC per WAVAX. When price
    # RISES, the active bin moves up and the pool converts WAVAX→USDC in the
    # bins crossed. So WAVAX-heavy (30-70 USDC) SELLS into strength (locks
    # gains as AVAX climbs); USDC-heavy (70-30) ACCUMULATES AVAX on the way up.
    if "DOVISH" in stance:
        split = 0.30            # 30-70 WAVAX-heavy — sell into the rally
        split_label = "30-70 (WAVAX-heavy — sell into strength)"
    elif "HAWKISH" in stance:
        split = 0.70            # 70-30 USDC-heavy — accumulate AVAX on the dip
        split_label = "70-30 (USDC-heavy — accumulate on the dip)"
    else:
        split = 0.50            # 50-50 normal — even both sides
        split_label = "50-50 (even — normal conditions)"

    rationale = (
        f"{shape} {bins} bins, {split_label}. "
        f"Vol proxy {vol:.0%} → {'wide to stay in range' if vol >= 0.30 else 'tight to concentrate' if vol < 0.15 else 'balanced'}."
    )
    return {
        "shape": shape, "bins": bins, "split": split,
        "split_label": split_label, "rationale": rationale,
    }


def _read_farm_vs_trade():
    """Read the buy list's farm-vs-trade signal (the source of truth).

    The buy list (steward-buylist.py) aggregates each coin's method/yield/
    strategy into a market-wide lean: FARM / TRADE / BALANCED. The council's
    rail decision consumes this directly — the 'crocodile' market-fit read
    becomes an official input, not just a hint in the report.
    """
    for p in (
        "/root/.hermes/scripts/.steward-buylist-state.json",
        "/root/.hermes/profiles/gentech-treasury/scripts/.steward-buylist-state.json",
    ):
        try:
            with open(p) as f:
                d = json.load(f)
            fvt = d.get("farm_vs_trade")
            if fvt:
                return fvt
        except Exception:
            continue
    return None


def _rail_recommendation(stance, reg, liquidity=None):
    """The council's RAIL decision: which chain/pool to farm + whether to trade.

    Jordan's frame (Sep 7 2026): the treasury should farm where liquidity is
    best and trade where the trend is. AVAX (LFJ) and SOL (Meteora) are the top
    two rails. Solana has more liquidity coming in than Avalanche — so if the
    goal is $200/day, the Solana pool may be the better farm, with AVAX traded
    (or leveraged) on the side.

    liquidity: optional dict {avax_liq, sol_liq, avax_vol, sol_vol} in USD.
    If None, uses regime + stance heuristics.

    Returns dict: {rail, farm, trade, rationale}.
    """
    r = (reg or {}).get("regime", "").upper()
    # Liquidity proxy: if not provided, infer from regime/stance.
    if liquidity is None:
        # Default: AVAX is the live rail (already funded + farming). SOL is
        # the higher-liquidity alternative (Jordan's read: more liquidity
        # coming in than AVAX).
        sol_liq = 1.0
        avax_liq = 0.8
        if r in ("BULL_TRENDING", "ACCUMULATION"):
            sol_liq = 1.2   # SOL benefits more in a bull (higher beta)
        liquidity = {"avax_liq": avax_liq, "sol_liq": sol_liq}

    sol_liq = liquidity.get("sol_liq", 0)
    avax_liq = liquidity.get("avax_liq", 0)

    # ── Farm-vs-trade signal (source of truth from the buy list) ───────
    # The 'crocodile' market-fit read: if the buy list leans TRADE, the
    # treasury should favor the trade leg; if FARM, favor the farm leg.
    fvt = _read_farm_vs_trade()
    fvt_lean = (fvt or {}).get("lean", "BALANCED")
    fvt_note = ""
    if fvt_lean == "TRADE":
        fvt_note = "buy list leans TRADE — favor the trade leg"
    elif fvt_lean == "FARM":
        fvt_note = "buy list leans FARM — favor the farm leg"

    # ── Farm rail: where liquidity is best ────────────────────────────
    # If SOL has materially more liquidity, farm SOL (Meteora) and trade AVAX.
    # Otherwise keep farming AVAX (LFJ) — it's live and proven.
    if sol_liq > avax_liq * 1.15:   # SOL >15% more liquid
        farm = "SOL (Meteora)"
        trade = "AVAX (LFJ spot/perp)"
        rail = "SOL-farm + AVAX-trade"
        rationale = (f"Solana liquidity {sol_liq:.1f} vs Avalanche {avax_liq:.1f} "
                     f"(+{(sol_liq/avax_liq-1)*100:.0f}%) — farm SOL for the "
                     f"$200/day goal, trade AVAX on the side")
    else:
        farm = "AVAX (LFJ)"
        trade = "SOL (Meteora spot/perp)"
        rail = "AVAX-farm + SOL-trade"
        rationale = (f"Avalanche liquidity {avax_liq:.1f} vs Solana {sol_liq:.1f} — "
                     f"keep farming AVAX (live + proven), trade SOL on the side")

    # ── Direction: in a bull, lean into the trade leg ─────────────────
    if "DOVISH" in stance:
        trade += " — long bias, sell into strength"
    elif "HAWKISH" in stance:
        trade += " — defensive, keep powder dry"

    # Fold the farm-vs-trade signal into the rationale
    if fvt_note:
        rationale += f" | {fvt_note}"

    return {"rail": rail, "farm": farm, "trade": trade, "rationale": rationale}


def _read_market_sentiment():
    """Read the weekly market-sentiment radar (narrative rotation renamed Aug
    2026): the overall bull/bear stance + top rotations + macro thermometer.
    Returns dict or None. Source: DeFi/rainbow/market-sentiment.json (the
    market-sentiment.py cron output)."""
    for p in (
        "/root/repos/gentechlabs.github.io/DeFi/rainbow/market-sentiment.json",  # live checkout (repos/ path was dead — audit Aug 29)
        "/root/.hermes/profiles/gentech-treasury/scripts/market-sentiment.json",
    ):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            continue
    return None


def _read_lp_position():
    """Read the live LP farm position (the Fused Command Center's layer_lp,
    folded into the council Sep 7 2026). Source: the yield-rainbow feed the
    yield-rainbow.py cron writes every 30min. Returns a dict or None."""
    for p in (
        "/var/www/gentechlabs/yield-rainbow-data.json",  # live source (audit Aug 29)
        "/root/.hermes/profiles/gentech-treasury/scripts/yield-rainbow-data.json",
    ):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            continue
    return None


def _state_path():
    """Resolve the shared treasury-state.json path."""
    return os.environ.get(
        "TREASURY_STATE_FILE",
        "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json")


def _write_mode(mode: str, by: str):
    """Apply a maintenance mode change to the shared state (safe, no Jordan)."""
    p = _state_path()
    try:
        data = json.loads(open(p).read())
    except Exception:
        data = {}
    data["mode"] = mode
    data["mode_updated_at"] = datetime.now(timezone.utc).isoformat()
    data["mode_updated_by"] = by
    data.pop("pending_mode", None)  # clear any stale pending request
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def _write_pending(mode: str, reason: str):
    """Write a PENDING mode request to the shared state — Jordan must confirm
    before the mode actually flips. Never auto-applies a farm<->trade turn."""
    p = _state_path()
    try:
        data = json.loads(open(p).read())
    except Exception:
        data = {}
    data["pending_mode"] = {
        "mode": mode,
        "reason": reason,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": "council",
    }
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = []
    L.append("🏛️ STEWARD COUNCIL — treasury meeting")
    L.append(f"   {now}")
    L.append("")

    # ── The Chair opens ──────────────────────────────────────────────────
    L.append("**The Steward opens:** 'Members, give me your reads. We decide"
             " as one, we dissent out loud, and we write it down.'")
    L.append("")

    # ── Member: Gate ─────────────────────────────────────────────────────
    cap = treasury_has_capital("avalanche", STEWARD)
    val = treasury_value_usd("avalanche", STEWARD)
    if cap is None:
        L.append(_vote("Gate", "🟡", "UNCERTAIN", "gate read failed — assume funded", "amber"))
    elif cap:
        # Fail-safe inf = on-chain read failed. Say so honestly (audit Aug 29:
        # "$inf" printed as if it were a real dollar amount).
        if val == float("inf"):
            valstr = "on-chain read failed — assumed funded"
        else:
            valstr = f"${val:,.2f}"
        L.append(_vote("Gate", "🟢", "FUNDED", f"dry powder present ({valstr})", "green"))
    else:
        L.append(_vote("Gate", "🔴", "FLAT", f"no deployable capital (${val:,.2f})", "red"))

    # ── Member: LP Position (folded from Fused Command Center, Sep 7 2026) ──
    lp = _read_lp_position()
    if lp:
        pos = lp.get("position", {})
        met = lp.get("metrics", {})
        band = lp.get("currentBand", {})
        price = pos.get("currentPrice", 0)
        eff = met.get("efficiency", 0)
        low, high = pos.get("rangeLow", 0), pos.get("rangeHigh", 0)
        in_range = "IN" if low <= price <= high else "OUT"
        band_emoji = band.get("emoji", "❓")
        pos_usd = pos.get("positionUsd", 0)
        block = "green" if in_range == "IN" and eff >= 60 else ("red" if eff == 0 else None)
        note = f"{in_range} · {eff:.0f}% eff · {band_emoji}{band.get('name','')}"
        if pos_usd:
            note += f" · ${pos_usd:.2f}"
        L.append(_vote("LP Position", "💼", f"${price:.2f}", note, block))
    else:
        L.append(_vote("LP Position", "💼", "NO DATA", "yield-rainbow feed unavailable", None))

    # ── Member: Buy List (AVAX + BTC) ────────────────────────────────────
    for sym, zones in BUY_ZONES.items():
        p = _price(sym)
        if p is None:
            L.append(_vote(f"Buy List — {sym}", "🟡", "no price", "unavailable", None))
            continue
        label, emoji = _buy_zone({"zones": zones}, p)
        block = "green" if label in ("Accumulate", "Deep Value") else ("red" if label == "Extended" else None)
        L.append(_vote(f"Buy List — {sym}", emoji, label, f"@ ${p:,.2f}", block))

    # ── Member: Scanner (basis) ─────────────────────────────────────────
    opps = _read_scanner()
    if opps:
        lines = []
        for o in opps[:3]:
            sym = o.get("symbol"); bps = o.get("basis_bps", 0)
            lines.append(f"{sym} {bps:+.1f} bps ({'backwardation' if bps<0 else 'contango'})")
        scan_block = "green" if lines else None
        L.append(_vote("Scanner", "🔭", "basis live", "; ".join(lines) or "no divergence", scan_block))
    else:
        L.append(_vote("Scanner", "🔭", "NO DATA", "scanner state unavailable", None))

    # ── Member: Regime ──────────────────────────────────────────────────
    reg = _read_regime()
    if not reg:
        reg = _live_regime()
    if reg and reg.get("regime"):
        r = reg["regime"].replace("_", " ").title()
        conf = reg.get("confidence", 0)
        note = reg.get("note", "")
        block = "green" if r in ("Accumulation", "Range Bound", "Bull Trending") else ("red" if r in ("Bear Trending", "High Volatility") else None)
        note_txt = f" — {note}" if note else ""
        L.append(_vote("Regime", "🌦️", r, f"confidence {conf:.0%}{note_txt}", block))
    else:
        L.append(_vote("Regime", "🌦️", "NO DATA", "regime state unavailable", None))

    # ── Member 5: Market Sentiment radar (the weekly bull/bear stance) ───────
    sent = _read_market_sentiment()
    if sent:
        stance = sent.get("read") or sent.get("signals", {}).get("read") or ""
        narr = sent.get("narratives", [])
        top = narr[0]["name"] if narr else "n/a"
        s_low = stance.lower()
        block = "green" if "risk-on" in s_low or "bull" in s_low else ("red" if "risk-off" in s_low or "bear" in s_low else None)
        note = f"{stance} | top: {top}" if stance else f"top rotation: {top}"
        L.append(_vote("Sentiment", "📈", stance or "radar read", note, block))
    else:
        L.append(_vote("Sentiment", "📈", "NO DATA", "market-sentiment radar unavailable", None))

    # ── Member: Dominance (alt-season trigger) ───────────────────────────────
    dom = _read_dominance()
    if dom is not None:
        trend = dom.get("trend", "n/a")
        note = dom.get("note", "")
        L.append(_vote("Dominance", "📊", f"{dom['btc']:.1f}% ({trend})", note or "alt-season trigger", None))
    else:
        L.append(_vote("Dominance", "📊", "NO DATA", "dominance state unavailable", None))

    L.append("")
    L.append("━━━ COUNCIL VERDICT ━━━")

    greens = [v for v in _VERDICTS if v["block"] == "green"]
    reds = [v for v in _VERDICTS if v["block"] == "red"]
    unknowns = [v for v in _VERDICTS if v["block"] is None]

    if reds and not greens:
        v = "🔴 DISSENT"
        msg = f"{reds[0]['name']} is the lone objector. The council hears it — nothing moves until that objection clears."
    elif reds:
        names = ", ".join(v["name"] for v in reds)
        v = "🟡 MIXED"
        msg = f"thesis largely supported, but {names} dissents. Steward holds until the dissent clears."
    elif greens and not unknowns:
        v = "🟢 CONSENSUS"
        msg = "all members agree the call is sound. Green light to proceed."
    else:
        v = "🟢 CONSENSUS (with gaps)"
        msg = "no active dissent, but some members lacked data — Steward weighs the gap."

    L.append(f"**{v}:** {msg}")
    L.append("")

    # ── The Chair's executive call: DOVISH / HAWKISH / CENTERED ─────────
    # Jordan's frame (Sep 7 2026): with all the member data on the table, the
    # chair makes ONE executive decision on what rail / what strategy is best.
    # This is the 'improve the concept' piece — the council lands a directional
    # stance, not just a consensus label.
    _buy_blocks = [v["block"] for v in _VERDICTS
                   if v["name"].startswith("Buy List")]
    _stance, _rail, _strat, _why = _executive_stance(reg, sent, dom, _buy_blocks)
    L.append("━━━ 🏛️ EXECUTIVE STANCE ━━━")
    L.append(f"**{_stance}** — the chair's call on the data")
    L.append(f"   🛤️ Rail: {_rail}")
    L.append(f"   🧭 Strategy: {_strat}")
    L.append(f"   📊 Why: {_why}")
    # ── Rail decision (Sep 7 2026): farm where liquidity is best, trade the trend ──
    try:
        _rail_rec = _rail_recommendation(_stance, reg)
        L.append(f"   🚂 Rail decision: {_rail_rec['rail']}")
        L.append(f"      Farm: {_rail_rec['farm']} | Trade: {_rail_rec['trade']}")
        L.append(f"      {_rail_rec['rationale']}")
    except Exception:
        pass
    L.append("")

    # ── The Chair rules: mode recommendation (Aug 21 2026) ───────────────
    # The council is the brain. Based on the regime + verdict, it decides the
    # treasury MODE. SAFE maintenance modes auto-apply (they just re-target the
    # farm). TRADE / DRY_POWDER write a PENDING request that needs Jordan's go.
    cur_mode = get_mode()

    # Surface any open mode request at EVERY meeting until resolved (audit Aug 29:
    # a TRADE request sat pending 3 days because later meetings read a different
    # regime, hit the "unchanged" branch, and never re-asked Jordan).
    try:
        _pend = (load_state() or {}).get("pending_mode") or {}
    except Exception:
        _pend = {}
    if _pend.get("mode") and _pend.get("mode") != cur_mode:
        try:
            _age_h = (datetime.now(timezone.utc) -
                      datetime.fromisoformat(str(_pend.get("requested_at")))).total_seconds() / 3600
        except Exception:
            _age_h = -1
        if _age_h > 168:
            try:
                _data = load_state() or {}
                _data.pop("pending_mode", None)
                with open(_ts.STATE_PATH, "w") as _f:
                    json.dump(_data, _f, indent=2)
                L.append(f"🧹 Stale mode request cleared: **{_pend['mode']}** (pending since "
                         f"{str(_pend.get('requested_at', ''))[:10]}, never confirmed).")
            except Exception:
                L.append(f"🧹 Stale mode request: **{_pend['mode']}** (pending >7d) — needs manual clear.")
        else:
            L.append(f"⏳ **PENDING MODE REQUEST: {_pend['mode']}** — awaiting Jordan since "
                     f"{str(_pend.get('requested_at', ''))[:10]} ({_pend.get('reason', '')}). "
                     f"Confirm or dismiss to clear.")
        L.append("")

    reg = _read_regime() or _live_regime() or {}
    regime_value = reg.get("regime", "UNKNOWN").upper()
    rec_mode = REGIME_MAINTENANCE.get(regime_value, "YIELD_FARM")

    if rec_mode != cur_mode:
        L.append("━━━ MODE DECISION ━━━")
        L.append(f"Regime **{regime_value.replace('_',' ').title()}** → recommended mode **{rec_mode}**")
        if rec_mode in SAFE_MAINTENANCE:
            # Same-rail maintenance — apply immediately, no Jordan needed.
            _write_mode(rec_mode, f"council auto ({regime_value})")
            L.append(f"✅ Applied: **{rec_mode}** (maintenance — no Jordan action needed)")
        elif rec_mode in REQUIRES_JORDAN:
            # Farm<->trade turn — write a pending request, ask Jordan.
            _write_pending(rec_mode, f"regime {regime_value}")
            L.append(f"🟡 **Awaiting Jordan:** recommend **{rec_mode}**. "
                     f"Mode stays **{cur_mode}** until you confirm.")
        L.append("")
    else:
        L.append(f"🟢 Mode unchanged: **{cur_mode}** (matches regime {regime_value})")
        L.append("")

    # ── Chair's close + minutes ─────────────────────────────────────────
    L.append("**The Steward closes:** 'Recorded. Minutes written so the next meeting"
             " starts from where we left off.'")
    L.append("")

    # ── Forward calendar (agentic calendar radar) ─────────────────────────
    try:
        cal = _load_agentic_calendar()
        if cal:
            L.append("📅 ON THE RADAR (next 45d)")
            today = datetime.now(timezone.utc).date()
            horizon = today + timedelta(days=45)
            upcoming = [e for e in cal if today <= datetime.fromisoformat(e["date"]).date() <= horizon]
            upcoming.sort(key=lambda e: e["date"])
            for e in upcoming[:5]:
                d = datetime.fromisoformat(e["date"]).strftime("%b %d")
                imp = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(e.get("impact", "medium"), "🟡")
                L.append(f"   {imp} {d} — {e.get('name')} ({e.get('node','—')})")
            if not upcoming:
                L.append("   (nothing in window)")
            L.append("")
    except Exception:
        pass

    L.append("📜 Minutes → `Treasury/Strategy-Journal/` (this meeting's reads + verdict)")

    # ── TRUTH LAYER (fresh-truth audit, Aug 31 2026) ────────────────────
    # The closing line CLAIMED minutes were written; nothing wrote them. A
    # council without minutes has no memory — every meeting restarted cold.
    # Also feeds the Steward decision journal, which the 4-hourly Decisions
    # Report reads (that report went 9 days silent while claiming "ok").
    minutes_path = None
    try:
        from pathlib import Path as _P
        _jdir = _P("/root/vaults/gentech/Treasury/Strategy-Journal")
        _jdir.mkdir(parents=True, exist_ok=True)
        _ts = datetime.now(timezone.utc)
        minutes_path = _jdir / f"{_ts:%Y-%m-%d}-council-{_ts:%H%M}.md"
        minutes_path.write_text(
            "# Steward Council — " + _ts.strftime("%Y-%m-%d %H:%M UTC") + "\n\n"
            + "\n".join(L) + "\n", encoding="utf-8")
        L.append(f"   ✍️ (minutes actually written this time: {minutes_path.name})")
    except Exception:
        L.append("   ⚠️ minutes write FAILED — council memory at risk")
    # Decision journal feed: every meeting is a decision point; log it so the
    # Decisions Report (4h) always has fresh material and stays provably alive.
    try:
        import subprocess as _sp
        _verdict = next((l for l in L if "CONSENSUS" in l or "MIXED" in l or "DISSENT" in l), "")
        _entry = {
            "action": "COUNCIL_MEETING",
            "symbol": "treasury",
            "rationale": (_verdict.strip() or "council met; verdict recorded")[:400],
            "data": {"minutes": str(minutes_path) if minutes_path else None},
        }
        _r = _sp.run(["python3",
                      "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/steward_decisions.py",
                      "--log", json.dumps(_entry)],
                     capture_output=True, text=True, timeout=20)
        if _r.returncode != 0:
            sys.stderr.write(f"[journal] council log failed: {_r.stderr.strip()[:200]}\n")
    except Exception:
        pass

    print("\n".join(L))

if __name__ == "__main__":
    main()
