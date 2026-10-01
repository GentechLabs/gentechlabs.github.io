#!/bin/bash
# gated-run.sh — run a capital-dependent script ONLY when the treasury has capital.
#
# The "smart" layer (Jordan, Aug 17 2026): when the treasury is flat (no LP,
# no meaningful balance), capital-dependent cron jobs go SILENT and save tokens.
# When funded, the underlying script runs normally.
#
# Usage: gated-run.sh <script> [args...]
#   <script> is resolved relative to this scripts dir (like the cron `script` field).
#
# For no_agent cron jobs: empty stdout = silent delivery. So when flat, this
# wrapper prints nothing and exits 0 — the job delivers nothing and burns no
# tokens. When funded, it execs the underlying script.

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$SCRIPTS_DIR/capital_gate.py"

# ── A BROKEN GATE IS NOT A FLAT TREASURY (fixed 2026-09-23, Sr audit) ──────────────────────
# This read was `python3 "$GATE" --check 2>/dev/null | grep -q "TRUE"` — so a CRASHING
# capital_gate.py produced no output, no match, and `exit 0`: indistinguishable from a
# legitimately flat treasury, with the traceback swallowed. ANY gate error silently blinded every
# gated job. The failure direction matters too, and it is not symmetric: running a funded job when
# the treasury is flat merely costs tokens, but NOT running a needed job when the money is out of
# the pool costs money — that is exactly how a flat book was left unrecovered all night. So an
# unreadable gate FAILS OPEN (run the job) and says so, in the log and on stderr.
GATE_RC=0
GATE_OUT="$(python3 "$GATE" --check 2>&1)" || GATE_RC=$?
if [ "$GATE_RC" -ne 0 ]; then
    echo "gated-run: capital_gate.py failed (exit $GATE_RC) — FAILING OPEN, running the job."
    echo "$GATE_OUT" | tail -3
    echo "$GATE_OUT" >&2
elif ! printf '%s' "$GATE_OUT" | grep -q "TRUE"; then
    # A genuine FALSE: the treasury is flat. Stay silent, save tokens.
    exit 0
fi

# Funded — run the underlying script.
TARGET="$1"
shift
if [[ "$TARGET" == *.sh ]]; then
    exec bash "$SCRIPTS_DIR/$TARGET" "$@"
else
    exec python3 "$SCRIPTS_DIR/$TARGET" "$@"
fi
