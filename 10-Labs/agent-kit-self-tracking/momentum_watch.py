#!/usr/bin/env python3
"""momentum_watch.py — the standing rotation monitor (Jordan's "yield trade").

THE LOOP THIS CLOSES (Jordan, 2026-09-26):

  "If we're holding while we're rising up, but then we know that we're starting to lose
   momentum. We're starting not to be able to push as high. We're starting to break off from
   our bullishness — we know we're about to land into a choppy area or there could be a
   pullback coming, right? And we want to be able to see the signs, because this also goes
   back into our intelligence."

hold_trigger.py already answers "should we HOLD or FARM?" — but only ever got ASKED from one
place: inside lfj_recenter's out-of-range branch. So the question was only put when price had
ALREADY escaped the band. Mid-range, nobody asked; momentum could stall for days in silence.
An exit-only loop: the transition was written in one direction and the other direction was a
print statement.

THIS SCRIPT ASKS ON A SCHEDULE, IN BOTH DIRECTIONS, AND WATCHES FOR THE DECAY SIGNS THAT
ARRIVE BEFORE THE BAND BREAKS.

── WHAT IT DOES NOT DO ───────────────────────────────────────────────────────────────────
NO CAPITAL. There is no wallet, no key, no tx path anywhere in this file. It reads prices,
reads the gates, writes its own sample history, and speaks. Moving capital on a verdict is a
Jordan-owned action (exit_plan.py prints the plan; the council proposes; he decides).

── THE THREE-STATE RULE ─────────────────────────────────────────────────────────────────
Verdict is HOLD / FARM / **UNKNOWN**. An unreadable feed returns UNKNOWN and SAYS SO — it
never falls back to FARM, because "could not measure" and "no signal" are different answers
with opposite actions, and a monitor that cannot measure must not read as calm.

── SILENCE DOCTRINE ─────────────────────────────────────────────────────────────────────
Silent unless the fingerprint CHANGES (verdict, or the set of decay signs). A standing known
state stays quiet; a new sign or a verdict flip speaks immediately. `--force` speaks anyway
(first run, or when a human asks). `--json` for machine consumption.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

STATE = os.path.join(HERE, ".momentum-watch-state.json")
REPORT_DIR = os.environ.get(
    "MOMENTUM_REPORT_DIR",
    "/root/vaults/gentech/01-HANDOFFS/gentech-treasury-to-gentech")

# keep the history bounded; this is a fingerprint trail, not a price archive
MAX_SAMPLES = 400

# ── decay thresholds ─────────────────────────────────────────────────────────────────────
# Each is a LEADING indicator: it can be true while price is still in range and still rising.
FAILED_HIGH_LOOKBACK = 7   # compare this window's high against the previous one


def load_state() -> dict:
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:                                                 # noqa: BLE001
        return {"samples": [], "last_fingerprint": None, "signs": []}


def save_state(st: dict) -> None:
    st["samples"] = st.get("samples", [])[-MAX_SAMPLES:]
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=2)
    os.replace(tmp, STATE)


def decay_signs(pts, ev) -> list:
    """The signs Jordan described, each computed from the series — never from vibes.

    Returns a list of {code, label, detail}. Empty list = no decay detected.
    """
    signs = []

    if ev.get("verdict") == "UNKNOWN":
        return signs           # cannot read => no signs claimed (the UNKNOWN verdict carries it)

    tm = ev.get("timeframes", {})
    m_slope = tm.get("monthly", {}).get("slope", 0.0)
    w_slope = tm.get("weekly", {}).get("slope", 0.0)

    # 1. THE FAST LEG ROLLED OVER while the slow leg is still up.
    #    "we're starting to lose momentum" — the weekly turns before the monthly does.
    if w_slope <= 0 < m_slope:
        signs.append({
            "code": "MOMENTUM_DECAY",
            "label": "the FAST leg has rolled over",
            "detail": (f"weekly slope {w_slope*100:+.3f}%/day has turned non-positive while "
                       f"the monthly is still {m_slope*100:+.3f}%/day"),
        })

    # 2. A LOWER HIGH — "we're starting not to be able to push as high".
    lb = FAILED_HIGH_LOOKBACK
    if len(pts) >= 2 * lb + 1:
        recent_hi = max(pts[-lb:])
        prior_hi = max(pts[-(2 * lb):-lb])
        if recent_hi < prior_hi:
            signs.append({
                "code": "FAILED_HIGH",
                "label": "cannot push as high",
                "detail": (f"last {lb}d high ${recent_hi:,.4f} is BELOW the prior {lb}d high "
                           f"${prior_hi:,.4f} ({(recent_hi/prior_hi-1)*100:+.2f}%)"),
            })

    # 3. THE FAST WINDOW HAS STALLED — the week stopped making progress while the month
    #    still looks good. This is "about to land into a choppy area" arriving EARLY, and it
    #    is the one sign that can be true while price is still in range and still up.
    #
    #    NOTE the shape of this test. The first cut compared the 30d strong-up/strong-down
    #    edge and fired on a +47% month (edge +2 because a high-vol BULL has plenty of big
    #    down days too) — i.e. it could not tell a healthy bull from the target state, so it
    #    would have warned permanently. A sign that always fires is not a sign. This one is
    #    anchored on a FLAT fast window underneath a STRONG slow window, which a bull in
    #    progress simply does not produce.
    FAST_NET_FLAT = 0.02      # the week netted less than this = no progress
    SLOW_STILL_STRONG = 0.10  # ...while the month is still up at least this much
    if len(pts) >= 9:
        w8 = pts[-8:]
        wmoves = [(w8[i] / w8[i - 1] - 1) for i in range(1, len(w8))]
        w_net = w8[-1] / w8[0] - 1
        w_up = sum(1 for m in wmoves if m >= 0.0010)
        w_dn = sum(1 for m in wmoves if m <= -0.0010)
        if (abs(w_net) < FAST_NET_FLAT and w_dn >= w_up
                and ev.get("net_30d", 0) > SLOW_STILL_STRONG):
            signs.append({
                "code": "FAST_WINDOW_STALLED",
                "label": "the week has stalled under a still-strong month",
                "detail": (f"last 7d net {w_net*100:+.2f}% with {w_dn} big down days vs "
                           f"{w_up} big up days, while the 30d is still "
                           f"{ev.get('net_30d',0)*100:+.2f}%"),
            })

    # 4. THE GATE THAT CARRIES THE HOLD CASE IS LOSING GROUND.
    #    Gate 3 is the binding one; when the haircut projection shrinks toward the fee core,
    #    holding stops paying for itself even if the trend has not broken.
    ratio = (ev.get("exp_haircut", 0) / ev["fee_forgone"]) if ev.get("fee_forgone") else 0
    if 0 < ratio < 2.0:
        signs.append({
            "code": "HOLD_EDGE_THINNING",
            "label": "holding is barely paying for itself",
            "detail": (f"50%-haircut projection {ev.get('exp_haircut',0)*100:+.2f}% vs fee core "
                       f"forgone {ev.get('fee_forgone',0)*100:.2f}% (ratio {ratio:.2f}x)"),
        })

    return signs


def advise(verdict: str, signs: list) -> str:
    """The action implication — stated, never taken."""
    codes = {s["code"] for s in signs}
    if verdict == "UNKNOWN":
        return "UNKNOWN — no advice on an unreadable read. Fix the feed."
    if verdict == "HOLD":
        if codes & {"MOMENTUM_DECAY", "FAILED_HIGH", "HOLD_EDGE_THINNING"}:
            return ("The bull thesis is weakening — prepare the RE-ENTRY: exit_plan.py lfj "
                    "--mode HOLD_SPLIT, then let the watchdog re-center when the tape quiets.")
        if "FAST_WINDOW_STALLED" in codes:
            return ("Still holding, but the week has stalled — momentum is flattening. Watch "
                    "for the weekly leg to roll over: that is the re-entry cue.")
        return "Hold the asset. The bull case is intact and nothing has decayed."
    if verdict == "FARM":
        if "FAST_WINDOW_STALLED" in codes:
            return ("Farming is correct — a stall is chop arriving, and chop is our weather. "
                    "This is what the fee engine is for.")
        return "Farm. The gates do not justify holding; the fee core wins."
    return "UNKNOWN — no advice on an unreadable read. Fix the feed."


def render(ev, signs, age_note, hist_n) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = []
    L.append("=" * 86)
    L.append(f"  MOMENTUM WATCH — the rotation loop    {ts}")
    L.append("=" * 86)
    if ev.get("verdict") == "UNKNOWN":
        L.append(f"  ⚠️  UNKNOWN — {ev.get('reason', 'unreadable')}")
        L.append("     Cannot measure is NOT 'nothing is happening'. No verdict claimed.")
        L.append("=" * 86)
        return "\n".join(L)

    tm = ev.get("timeframes", {})
    L.append(f"  AVAX ${ev.get('spot', 0):,.4f}   source {ev.get('source','?')} "
             f"({ev.get('points','?')} daily points)")
    L.append(f"  verdict: {ev['verdict']}   gates {ev.get('passed')}/3"
             + (f"   [{age_note}]" if age_note else ""))
    L.append("")
    for k, nice in (("monthly", "monthly (~30d)"), ("weekly", "weekly (~7d)")):
        v = tm.get(k)
        if v:
            L.append(f"    {nice:<16} {v['chg']:+7.2f}%   slope/day {v['slope']*100:+6.3f}%"
                     f"   {'BULLISH' if v['up'] else 'not bullish'}")
    L.append(f"    edge: strong-up {ev.get('strong_up')} vs strong-down {ev.get('strong_dn')}"
             f"   net 30d {ev.get('net_30d',0)*100:+.2f}%")
    L.append("")
    if signs:
        L.append("  ⚠️  DECAY SIGNS (leading — these arrive BEFORE the band breaks):")
        for s in signs:
            L.append(f"     • {s['code']} — {s['label']}")
            L.append(f"       {s['detail']}")
    else:
        L.append("  ✅ No decay signs. Nothing has rolled over.")
    L.append("")
    L.append(f"  -> {advise(ev['verdict'], signs)}")
    L.append("     READ-ONLY. No capital moves from this script.")
    L.append(f"     history: {hist_n} sample(s) on file")
    L.append("=" * 86)
    return "\n".join(L)


def main() -> int:
    js = "--json" in sys.argv
    force = "--force" in sys.argv
    nosample = "--no-sample" in sys.argv

    import hold_trigger as HT          # ONE authority for the gates

    pts, src = HT.fetch_series()
    if pts is None:
        ev = {"verdict": "UNKNOWN", "reason": src}
    else:
        ev = HT.evaluate(pts)
        ev["source"] = src
        ev["points"] = len(pts)

    signs = decay_signs(pts or [], ev)
    codes = sorted(s["code"] for s in signs)
    fingerprint = f"{ev.get('verdict')}|{','.join(codes)}"

    st = load_state()
    prev_fp = st.get("last_fingerprint")
    changed = (prev_fp != fingerprint)

    if not nosample:
        st.setdefault("samples", []).append({
            "ts": int(time.time()),
            "spot": ev.get("spot"),
            "verdict": ev.get("verdict"),
            "slope_m": ev.get("timeframes", {}).get("monthly", {}).get("slope"),
            "slope_w": ev.get("timeframes", {}).get("weekly", {}).get("slope"),
            "net_30d": ev.get("net_30d"),
            "strong_up": ev.get("strong_up"),
            "strong_dn": ev.get("strong_dn"),
            "signs": codes,
        })
        st["last_fingerprint"] = fingerprint
        st["signs"] = codes
        st["last_run"] = int(time.time())
        save_state(st)

    hist_n = len(st.get("samples", []))

    if js:
        print(json.dumps({"verdict": ev.get("verdict"), "gates": ev.get("passed"),
                          "signs": signs, "changed": changed,
                          "previous_fingerprint": prev_fp,
                          "fingerprint": fingerprint,
                          "advice": advise(ev.get("verdict", "UNKNOWN"), signs),
                          "read_only": True, "samples": hist_n}, indent=2))
        return 0

    # SILENCE DOCTRINE: speak when the fingerprint moves, or when forced.
    if not changed and not force:
        return 0

    out = render(ev, signs, None, hist_n)
    print(out)

    # Feed the intelligence layer — append a dated note, one file per day, only when it speaks.
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with open(os.path.join(REPORT_DIR, f"{day}.md"), "a") as f:
            f.write(f"\n### momentum_watch — {datetime.now(timezone.utc):%H:%M}Z\n")
            f.write(f"- verdict **{ev.get('verdict')}** (gates {ev.get('passed')}/3)"
                    f"  · fingerprint `{fingerprint}`\n")
            if signs:
                for s in signs:
                    f.write(f"- ⚠️ `{s['code']}` — {s['label']}: {s['detail']}\n")
            else:
                f.write("- no decay signs\n")
            f.write(f"- {advise(ev.get('verdict', 'UNKNOWN'), signs)}\n")
    except Exception as e:                                            # noqa: BLE001
        print(f"  (vault note not written: {type(e).__name__}: {e})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
