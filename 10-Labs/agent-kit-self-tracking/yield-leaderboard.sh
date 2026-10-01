#!/usr/bin/env bash
# yield-leaderboard.sh — the fleet yield board, delivered on the old heartbeat slot.
#
# WHY THIS REPLACED THE HEARTBEAT (Jordan, 2026-09-22: "we can clean up and consolidate yield
# farm cron jobs to add him like a yield leader board. Following the same rules I have")
#
# The heartbeat reported ONE tenant's position twice an hour. The leaderboard reports EVERY
# active tenant, ranked by how hard the capital is working, against the same two baselines
# Jordan is held to (average staker, and simply holding). So this is not a new job bolted on
# beside the old one - it is the old job's slot carrying a fleet-wide answer. Same cadence,
# same group, one less report to read, and Dadrian is on it from day one.
#
# Every tenant is valued in its OWN process (yield_leaderboard.py) so a row can never be
# another tenant's numbers wearing a different name.
#
# NOT silent-if-flat: a leaderboard with no rows is itself the finding.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

OUT="$(timeout 420 python3 "$DIR/yield_leaderboard.py" 2>&1)"
RC=$?

if [ $RC -ne 0 ] || [ -z "$OUT" ]; then
    echo "⚠️  YIELD LEADERBOARD FAILED (rc=$RC)"
    echo "$OUT" | tail -12
    exit 0
fi

# Suppress the noise line that names the registry path on every run.
echo "$OUT" | grep -v "^\s*$"

# ── HUB REFRESH MOVED OUT (condensed 2026-09-28) ─────────────────────────────────────────────
# This slot used to also run `defi_hub_data.py` to keep the per-person DeFi pages current. But the
# dedicated "DeFi Hub Refresh" job (dcb074a180d3, */10) ALREADY does exactly that — every ten
# minutes, three times as often. So the hub was being rebuilt up to 48 extra times a day for no
# gain, each build spawning a subprocess per tenant against live RPC.
#
# Jordan, 2026-09-28: "if we could also condense them, that'd also be great. Just make everything
# just kind of easy and redistrict to the point." So the refresh now lives in ONE place (the job
# whose entire purpose is that), and this job does one thing: the leaderboard.
#
# Nothing is lost — dcb074a180d3 owns the hub, runs more often, and is already silent on success.
# One job, one responsibility, and no duplicated RPC load.
