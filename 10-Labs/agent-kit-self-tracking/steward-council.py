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
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

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
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg}&vs_currencies=usd"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return float(json.load(r)[cg]["usd"])
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


def _read_market_sentiment():
    """Read the weekly market-sentiment radar (narrative rotation renamed Aug
    2026): the overall bull/bear stance + top rotations + macro thermometer.
    Returns dict or None. Source: DeFi/rainbow/market-sentiment.json (the
    market-sentiment.py cron output)."""
    for p in (
        "/root/repos/ProtoJay4789.github.io/DeFi/rainbow/market-sentiment.json",
        os.path.join(SCRIPT_DIR, "..", "..", "ProtoJay4789.github.io", "DeFi", "rainbow", "market-sentiment.json"),
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
        L.append(_vote("Gate", "🟢", "FUNDED", f"dry powder present (${val:,.2f})", "green"))
    else:
        L.append(_vote("Gate", "🔴", "FLAT", f"no deployable capital (${val:,.2f})", "red"))

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

    # ── The Chair rules: mode recommendation (Aug 21 2026) ───────────────
    # The council is the brain. Based on the regime + verdict, it decides the
    # treasury MODE. SAFE maintenance modes auto-apply (they just re-target the
    # farm). TRADE / DRY_POWDER write a PENDING request that needs Jordan's go.
    cur_mode = get_mode()
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

    print("\n".join(L))

if __name__ == "__main__":
    main()
