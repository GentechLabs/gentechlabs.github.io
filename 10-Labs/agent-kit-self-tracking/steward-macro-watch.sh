#!/bin/bash
# steward-macro-watch.sh — MACRO POSTURE as its own job (Jordan, 2026-09-20).
#
# Split out of the position heartbeat. Macro is a different question on a different clock:
# CPI/FOMC/NFP windows govern whether we should be positioned for volatility at all, whereas
# the heartbeat governs a position that already exists. Mixing them meant a 10-day-old macro
# stand-down printed on every heartbeat - and it printed "stand-down CURVE" while we were IN a
# curve, which is advice pointing the wrong way.
#
# Prints the current macro posture, and says plainly when an action has EXPIRED rather than
# repeating it forever as though it were live.
# ── REFRESH THE ECONOMIC CALENDAR FIRST (added 2026-09-27) ───────────────────────────────────
# THIS SCRIPT IS THE ONLY PLACE THE CALENDAR CAN BE KEPT CURRENT, and until today NOTHING did it.
# The file sat 245 hours (10 days) old while its events still read time:"TODAY", so posture's
# protection layer asserted a high-impact event on EVERY run, forced FARM_BIDASK, and the market
# and regime never got a vote on the shape. fed-event-tracker.py had TWO ways to stay silent on a
# quiet day (an early `return  # empty = SILENT` and an `if hub_events:` guard on the writer), so
# its output was only ever rewritten when an event was NEAR — and then never again.
#
# Both are fixed in the tracker; this call is what makes the fix reach the live file. It runs
# before the posture read so the same pass sees a current calendar. Bounded and non-fatal: a
# failed refresh must not stop the macro report from printing.
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPTS_DIR/fed-event-tracker.py" ]; then
    timeout 120 python3 "$SCRIPTS_DIR/fed-event-tracker.py" >/dev/null 2>&1 || true
    if [ -f /root/repos/gentechlabs.github.io/DeFi/economic-calendar.json ]; then
        cp -f /root/repos/gentechlabs.github.io/DeFi/economic-calendar.json \
              /var/www/gentechlabs/DeFi/economic-calendar.json 2>/dev/null || true
    fi
fi

python3 - << 'PY'
import os, sys, json
from datetime import datetime, timezone
HERE="/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
sys.path.insert(0, HERE)
try:
    import steward_state as S
except Exception as e:
    print(f"⚠️ macro watch: cannot load the planner ({type(e).__name__})"); raise SystemExit(0)
try:
    a = S.macro_next_action()
except Exception as e:
    print(f"⚠️ macro watch: planner raised {type(e).__name__}: {str(e)[:80]}"); raise SystemExit(0)
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
print("📅 STEWARD MACRO WATCH")
print(f"   {now}")
print()
if not a:
    print("   No reposition scheduled. The planner enforces only when a CPI/FOMC/NFP")
    print("   is inside 36h, so an empty result means no macro window is near.")
    raise SystemExit(0)
# a scheduled action must be CHECKED FOR EXPIRY, not repeated forever
st = os.path.join(os.path.dirname(S.MACRO_SCHEDULED_STATE), ".steward-macro-scheduled.json")
expired = False
try:
    d = json.load(open(S.MACRO_SCHEDULED_STATE))
    when = d.get("when") or d.get("scheduled") or d.get("timestamp")
    if when:
        t = datetime.fromisoformat(str(when).replace("Z", "+00:00"))
        if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - t).total_seconds()/3600
        if age_h > 36:
            expired = True
            print(f"   ⏹ EXPIRED — this action was scheduled {age_h:.0f}h ago and is {age_h/24:.1f} days old.")
            print(f"     It is NOT live advice. Repeating it every run makes a stale decision look current.")
            print()
except Exception:
    pass
print(f"   {'(STALE) ' if expired else ''}{a}")
PY
