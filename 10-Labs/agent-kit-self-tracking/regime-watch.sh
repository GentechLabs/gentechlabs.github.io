#!/bin/bash
# regime-watch.sh — run the regime classifier on the Blackhole pool, write state,
# and print ONLY when the regime actually changes (silence doctrine: no noise when
# nothing changed). The classifier always prints JSON; this wrapper suppresses the
# steady-state output so the cron delivers nothing unless the regime shifts.
cd "$(dirname "$0")"
# Classify the LFJ WAVAX/USDC pool. This used to pass the BLACKHOLE pool
# (0x41100c6d...) with a comment saying "we're on Blackhole, not LFJ" — true when it
# was written, false since we moved to LFJ. The classifier's own default was already
# the correct LFJ pair; this override was dragging it back to the old venue.
OUT=$(python3 regime_classifier.py 0x864d4e5ee7318e97483db7eb0912e09f161516ea 2>/dev/null)
# The classifier writes .aae-regime-state.json itself. Read the change flag.
CHANGED=$(echo "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('regime_changed', False))" 2>/dev/null)
if [ "$CHANGED" = "True" ]; then
    echo "$OUT"
fi

# ── AAE hybrid-signal producer (SEP 15 2026 fix) ────────────────────────
# clarity-mode.py reads ~/.hermes/scripts/.aae-hybrid-signal.json, but the ONLY
# producer (Treasury/scripts/aae-hybrid-signal.py) was referenced by NO cron job.
# The file sat 8 days old while looking valid ("status":"ok"), and the mode watch
# laundered it into a live RANGE_BOUND 0.7. Producer now rides the same tick as
# the classifier that feeds it. clarity-mode.py also gained a 12h staleness guard.
python3 aae-hybrid-signal.py --json >/dev/null 2>&1 || true
exit 0
