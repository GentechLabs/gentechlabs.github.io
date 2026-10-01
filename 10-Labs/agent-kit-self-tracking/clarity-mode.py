#!/usr/bin/env python3
"""
CLARITY Mode Translator — the human layer on top of the AAE regime/allocation
engine. Reads the live .aae-hybrid-signal.json and translates the engine's
regime + allocation into plain-language MODES Jordan can glance at:

  🟢 RISK-ON / GROWTH   (BULL_TRENDING / PRICE_DISCOVERY — hodl heavy)
  🟡 YIELD / LP HARVEST  (RANGE_BOUND — LP + staking heavy)
  🟣 ACCUMULATION        (ACCUMULATION — building position)
  🔴 DEFENSIVE / YIELD   (BEAR_TRENDING — staking + lending heavy)
  🟠 VOLATILITY / HEDGED (HIGH_VOLATILITY — spread out)
  ⚪ UNKNOWN

Also overlays the CLARITY Act vote status when supplied (via CLARITY_STATE_FILE),
so Jordan sees the macro catalyst alongside the mode.

Usage:
  python3 clarity-mode.py            # print current mode report
  python3 clarity-mode.py --state    # read + print persisted mode state JSON
  python3 clarity-mode.py --watch    # detect MODE CHANGE; exit 0 if changed, 1 if same

Output is Telegram-safe (<2000 chars). Writes mode state to .clarity-mode-state.json.
"""
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.expanduser("~/.hermes/scripts")
SIGNAL_FILE = os.path.join(STATE_DIR, ".aae-hybrid-signal.json")
MODE_STATE_FILE = os.path.join(SCRIPT_DIR, ".clarity-mode-state.json")
CLARITY_STATE_FILE = os.getenv("CLARITY_STATE_FILE") or os.path.join(
    SCRIPT_DIR, ".clarity-vote-state.json"
)

# regime -> (mode label, emoji, one-line posture, short name)
MODE_MAP = {
    "BULL_TRENDING":   ("RISK-ON / GROWTH",   "🟢", "hodl-heavy — long spot via CDP, ride momentum", "RISK_ON"),
    "PRICE_DISCOVERY": ("RISK-ON / GROWTH",   "🟢", "hodl-heavy — new highs, trend-ride",             "RISK_ON"),
    "RANGE_BOUND":     ("YIELD / LP HARVEST", "🟡", "LP + staking — harvest yield, low hodl",          "YIELD"),
    "ACCUMULATION":    ("ACCUMULATION",       "🟣", "building position, hodl 40%",                    "ACCUM"),
    "BEAR_TRENDING":   ("DEFENSIVE / YIELD",  "🔴", "staking + lending — shelter, low hodl",          "DEFENSIVE"),
    "HIGH_VOLATILITY": ("VOLATILITY / HEDGED","🟠", "spread across strategies, hedged",                "VOLATILE"),
    "UNKNOWN":         ("UNKNOWN",            "⚪", "no clear signal — engine default split",          "UNKNOWN"),
}

# CLARITY vote status -> macro overlay
CLARITY_MAP = {
    "PENDING":   ("⏳ CLARITY unresolved — stay flat / yield",  "risk-off"),
    "PASSED":    ("✅ CLARITY passed — risk-on catalyst live",  "risk-on"),
    "FAILED":    ("❌ CLARITY dead — volatility flush, buy dip","risk-off"),
    "MISSED":    ("⚠️ CLARITY missed recess — dead til Sept",   "risk-off"),
}


def _now():
    return datetime.now(timezone.utc).strftime("%b %d · %H:%M UTC")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


# ── Staleness guard (Sep 15 2026) ───────────────────────────────────────
# The hybrid signal is written by aae-hybrid-signal.py, which must be run on a
# schedule. When that producer falls out of cron the file sits on disk looking
# perfectly valid ("status": "ok") while describing a market that no longer
# exists. Observed: an 8-day-old read whose RANGE_BOUND/0.7 was persisted and
# reported as the current mode. A signal is only "live" if it is FRESH.
# This is the same bug family as a reverted eth_call read as zero: a value that
# is structurally valid but semantically false.
MAX_SIGNAL_AGE_S = int(os.getenv("AAE_MAX_SIGNAL_AGE_S", str(12 * 3600)))


def signal_age_seconds(sig):
    """Age of the signal in seconds, or None if the timestamp can't be parsed."""
    ts = (sig or {}).get("timestamp")
    if not ts:
        return None
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds()
    except Exception:
        return None


def translate(sig, require_fresh=True):
    """Map a raw AAE hybrid-signal dict to a mode object.

    Refuses to translate a STALE signal — a stale read is not a live signal.
    """
    if not sig or sig.get("pipeline", {}).get("regime", {}).get("status") != "ok":
        return {
            "mode": "UNKNOWN", "label": "UNKNOWN", "emoji": "⚪",
            "posture": "no live signal — engine offline", "regime": "UNKNOWN",
            "confidence": 0.0, "changed": False,
        }
    age = signal_age_seconds(sig)
    if require_fresh and age is not None and age > MAX_SIGNAL_AGE_S:
        hrs = age / 3600.0
        return {
            "mode": "STALE", "label": "STALE SIGNAL", "emoji": "⚠️",
            "posture": (f"engine signal is {hrs:.1f}h old (>{MAX_SIGNAL_AGE_S/3600:.0f}h "
                        "limit) — producer not scheduled; mode NOT trusted"),
            "regime": "STALE", "confidence": 0.0, "changed": False,
            "age_hours": round(hrs, 1),
        }
    reg = sig["pipeline"]["regime"]
    regime = reg.get("regime", "UNKNOWN")
    conf = reg.get("confidence", 0.5)
    label, emoji, posture, short = MODE_MAP.get(regime, MODE_MAP["UNKNOWN"])

    alloc = sig.get("pipeline", {}).get("allocation", {})
    action = alloc.get("action", "HOLD")
    winner = sig.get("summary", {}).get("winner", "?")
    avax = sig.get("summary", {}).get("avax_price")

    return {
        "mode": short, "label": label, "emoji": emoji, "posture": posture,
        "regime": regime, "confidence": conf, "changed": reg.get("regime_changed", False),
        "action": action, "winner": winner, "avax_price": avax,
    }


def _prev_mode():
    return _load(MODE_STATE_FILE, {}).get("mode")


def build_report(sig):
    m = translate(sig)
    L = []
    L.append(f"{m['emoji']} CLARITY MODE — {m['label']}")
    L.append(f"    {_now()}")
    L.append("")
    L.append(f"Regime: {m['regime']} ({m['confidence']:.0%})")
    L.append(f"Posture: {m['posture']}")
    L.append(f"Engine action: {m['action']} · current winner: {m['winner']}")
    if m.get("avax_price"):
        L.append(f"AVAX: ${m['avax_price']:.2f}")

    # Macro overlay
    cstate = _load(CLARITY_STATE_FILE)
    if cstate:
        vote = cstate.get("status") or cstate.get("vote_status")
        if vote in CLARITY_MAP:
            text, _ = CLARITY_MAP[vote]
            L.append(f"Macro: {text}")
    return "\n".join(L)


def persist(sig):
    m = translate(sig)
    # A STALE/UNKNOWN signal must NOT overwrite a known-good mode — persisting it
    # would launder a dead read into the "current mode" other jobs read.
    if m["mode"] in ("STALE", "UNKNOWN"):
        prev = _load(MODE_STATE_FILE, {}) or {}
        prev["signal_stale"] = True
        prev["signal_stale_note"] = m.get("posture", "")
        prev["checked_at"] = _now()
        os.makedirs(SCRIPT_DIR, exist_ok=True)
        with open(MODE_STATE_FILE, "w") as f:
            json.dump(prev, f, indent=2)
        return prev
    data = {
        "mode": m["mode"], "label": m["label"], "emoji": m["emoji"],
        "regime": m["regime"], "confidence": m["confidence"],
        "action": m["action"], "winner": m["winner"],
        "avax_price": m.get("avax_price"), "updated_at": _now(),
        "last_regime_change": m["changed"],
        "signal_stale": False,
    }
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    with open(MODE_STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return data


def main():
    sig = _load(SIGNAL_FILE)
    if sig is None:
        print("❌ CLARITY MODE: engine signal missing (aae-hybrid-signal.json not found).")
        sys.exit(1)

    if "--state" in sys.argv:
        print(json.dumps(persist(sig), indent=2))
        return

    if "--watch" in sys.argv:
        # Watch mode: report only on MODE CHANGE (for cron). Exit 0 = changed.
        # Silence doctrine: a STALE signal alerts ONCE (on the transition into
        # stale), then stays quiet until it recovers — no hourly nagging.
        m = translate(sig)
        cur = m["mode"]
        prev = _prev_mode()
        was_stale = bool((_load(MODE_STATE_FILE, {}) or {}).get("signal_stale"))
        persist(sig)
        if cur in ("STALE", "UNKNOWN"):
            if not was_stale:
                print(f"⚠️ SIGNAL PROBLEM: {cur}\n\n{build_report(sig)}")
            sys.exit(0)
        if prev is not None and prev != cur:
            print(f"🔄 MODE CHANGE: {prev} → {cur}\n\n{build_report(sig)}")
            sys.exit(0)
        # No change: silent (cron suppresses via empty stdout pattern handled by job)
        sys.exit(0)

    # Default: full report every run (daily status)
    persist(sig)
    print(build_report(sig))


if __name__ == "__main__":
    main()
