#!/bin/bash
# security-sentinel-watch.sh — surface only NEW attacks relevant to OUR treasury.
#
# Jordan Sep 11 2026: "a cron job specifically supposed to look out for new
# attacks out in the space. Anytime it's relevant to us it helps us find how it
# happened and upgrading our treasury. We need some type of security layer that
# is also a part of self-healing."
#
# Silence doctrine: the sentinel fingerprints the set of relevant incidents and
# speaks ONLY when a NEW one appears. A standing feed of "attacks exist" would
# train everyone to ignore it.
set -uo pipefail
SC="/root/.hermes/profiles/gentech-treasury/scripts"
cd "$SC" || exit 0

OUT=$(timeout 280 python3 security_sentinel.py 2>/dev/null)
RC=$?

# Non-zero/timeout: say so once rather than failing silently forever.
if [ $RC -ne 0 ] && [ -z "$OUT" ]; then
  echo "⚠️  Security sentinel could not complete (exit $RC). Feed sources may be unreachable."
  exit 0
fi

if [ -n "$OUT" ]; then
  printf '%s\n' "$OUT"
fi
exit 0
