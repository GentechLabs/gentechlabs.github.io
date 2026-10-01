#!/bin/bash
# chain-fee-refresh.sh — regenerate the chain-fee measurement cache the treasury report reads.
#
# WHY THIS EXISTS: agentic-treasury-report.py shows a CHAIN-measured line on every venue row, but it
# reads that from chain-fee-measurements.json rather than measuring inline — the scan takes minutes
# (24 log windows per pool) and would stall the report. A cache nobody refreshes is just a slower way
# to be wrong, and the report enforces a 12h staleness limit, so this has to actually run.
#
# Runs chain-fee-rank.py, which measures TVL from chain balances and 24h of Swap events, then writes
# the timestamped cache. Silenced unless something changed, per the silence doctrine — a refresh that
# succeeded is not news.
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

if [ ! -f "$D/chain-fee-rank.py" ]; then
  echo "❌ chain-fee-rank.py MISSING from $D — this is an ENROLLMENT failure, not a market event."
  exit 3
fi

OUT="$(python3 "$D/chain-fee-rank.py" 2>&1)"
rc=$?

if [ $rc -ne 0 ]; then
  echo "⚠️ chain-fee refresh FAILED (exit $rc)"
  echo "$OUT" | tail -15
  exit $rc
fi

CACHE="$D/chain-fee-measurements.json"
if [ ! -f "$CACHE" ]; then
  echo "⚠️ chain-fee-rank.py exited 0 but wrote NO CACHE at $CACHE"
  echo "   (a successful run that produced no output is the failure mode this guards against)"
  exit 4
fi

# The cron runs this from the PROFILE dir, so the cache lands there. But agentic-treasury-report.py
# falls back to the VAULT copy, and the vault is canonical for everything else we own — so mirror it
# back. Two copies that disagree is exactly the drift this treasury keeps catching; the rule is one
# enrolled home per artifact, and the vault is that home.
VAULT="/root/vaults/gentech/10-Labs/agent-kit-self-tracking/chain-fee-measurements.json"
if [ -d "$(dirname "$VAULT")" ] && [ "$(readlink -f "$CACHE")" != "$(readlink -f "$VAULT")" ]; then
  cp "$CACHE" "$VAULT" 2>/dev/null || echo "⚠️ could not mirror the cache to the vault"
fi

# ── QUIET ON SUCCESS (fixed 2026-09-22) ──────────────────────────────────────────────────────
# This block CLAIMED to be "quiet on success" and then printed on the success path anyway:
#     print(f"NO_NEW (chain cache refreshed: {n} pools, {age:.1f} min old)")
# A NO_NEW line delivered by a no_agent cron is still a message — so this job posted to the group
# four times a day, including 06:00 UTC, which is 2am for Jordan. "NO_NEW" is the exact thing that
# should produce no message. The intent was written down and the code disagreed with it, which is
# the same defect class as every other bug found today: a mechanism that reports while claiming
# to be silent. Exit 0 with empty stdout = silent delivery, which is what this always meant to do.
python3 - "$CACHE" <<'PY'
import json, sys, datetime as dt
try:
    d = json.load(open(sys.argv[1]))
    age = (dt.datetime.now(dt.timezone.utc)
           - dt.datetime.fromisoformat(d["measured_at"].replace("Z", "+00:00"))).total_seconds()/60
except Exception as e:
    print(f"⚠️ chain-fee cache written but unreadable: {type(e).__name__}: {e}")
    sys.exit(5)
if age > 10:
    print(f"⚠️ chain-fee cache is {age:.0f} min old immediately after a refresh — the write did not land")
    sys.exit(6)
# fresh and readable -> say NOTHING
PY
exit $?
