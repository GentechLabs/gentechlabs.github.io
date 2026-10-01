#!/bin/bash
# lfj-fee-snapshot.sh — hourly snapshot of our LFJ claim, so a real 24h fee rate can exist.
# Silent on success: it writes a data point, it does not need to speak. The MEASUREMENT
# reports; the snapshot just accumulates history. (Silence doctrine.)
# FIXED 2026-09-22 — `2>/dev/null` + `2>&1` used to be `/dev/null`, so the cron record could only
# ever say "exit 1" and threw the CAUSE away with it. On 2026-09-22 api.avax.network returned
# Cloudflare 1015 (source rate-limit); the snapshot lost its point and the log said nothing about
# why. A silent success and a silent failure must not be the same artifact.
#   - stdout stays suppressed (a successful snapshot is not news)
#   - stderr is KEPT and forwarded on failure, so the cause reaches the cron record
#   - a real failure says so on stdout, so it cannot hide inside "silent"
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
ERR="$(mktemp)"
OUT="$(mktemp)"
trap 'rm -f "$ERR" "$OUT"' EXIT

if python3 "$D/lfj_fee_measure.py" --snapshot >"$OUT" 2>"$ERR"; then
  exit 0
else
  rc=$?          # capture INSIDE the else: after `fi`, $? is the if-statement's own status (0)
fi
echo "⚠️ LFJ fee snapshot FAILED (exit $rc) — no data point written"
# FIXED 2026-09-22 (v2) — keeping stderr was necessary but NOT sufficient, because the underlying
# reader prints its failure cause to STDOUT (a `print`, not `file=sys.stderr`). With stdout at
# /dev/null the preserved stderr was EMPTY and the record still said "cause is missing upstream" —
# preserving a stream that carries nothing. Now BOTH are captured: the cause is surfaced whichever
# stream it lands on. This is the same defect as the swallowed cause, one layer down.
if [ -s "$ERR" ]; then tail -20 "$ERR"; fi
if [ -s "$OUT" ]; then tail -5 "$OUT"; fi
if [ ! -s "$ERR" ] && [ ! -s "$OUT" ]; then echo "   (no output on either stream — cause missing upstream)"; fi
exit "$rc"
