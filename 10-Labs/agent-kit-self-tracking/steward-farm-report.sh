#!/bin/bash
# steward-farm-report.sh — cron wrapper for the chain-fed farm report.
# Single source of truth lives in the vault (no copy divergence).
#
# ── MADE PER-TENANT 2026-09-28 ──────────────────────────────────────────────────────────────────
# This wrapper used to be a single `exec python3 steward_farm_report.py`. That script resolves its
# wallet via steward_identity.wallet(), which with no STEWARD_TENANT set falls to the configured
# DEFAULT — jordan. So the report described ONE book and was silently blind to every other: with
# two ACTIVE tenants, dadrian's farm was never reported at all, and nothing said so.
#
# Jordan: "he's focusing on yield farming command center." This is the job that faces that work, so
# a single-book farm report is exactly the separation fault.
#
# Each tenant now runs as its OWN process with its OWN wallet and its OWN state files, so one book's
# failure or state can never become another's number. Same shape as steward-watchdog.sh, deliberately.
#
# NOTE ON ORDER: per-tenant sections are printed in registry order and each is labelled. Output is
# NOT merged — a merged total would describe neither book, which is the fault we are fixing.
set -uo pipefail

REGISTRY="${REGISTRY:-/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json}"
REPORT="/root/vaults/gentech/10-Labs/agent-kit-self-tracking/steward_farm_report.py"

# ── A REGISTRY WE CANNOT READ IS NOT AN EMPTY REGISTRY ─────────────────────────────────────────
# (house rule, hardened in steward-watchdog.sh 2026-09-23 after a Sr audit.)
# If this file is unreadable, the old failure mode is ZERO tenants -> "nobody active, say nothing",
# which looks exactly like a legitimately empty registry. Every book silently unreported, no error.
# Distinguish "no one is active" from "I cannot see who is active" explicitly.
REG_OUT="$(python3 - "$REGISTRY" <<'PY'
import json, sys
try:
    reg = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"REGISTRY_UNREADABLE\t{type(e).__name__}: {e}")
    raise SystemExit(0)
for n, t in (reg.get("tenants") or {}).items():
    if t.get("status") == "ACTIVE" and t.get("wallet"):
        print(f"{n}\t{t['wallet']}")
PY
)"

if printf '%s' "$REG_OUT" | grep -q '^REGISTRY_UNREADABLE'; then
    echo "⚠️  FARM REPORT OUT OF ACTION — the tenant registry cannot be read; NO book is reported."
    echo "    $(printf '%s' "$REG_OUT" | grep '^REGISTRY_UNREADABLE' | cut -f2-)"
    echo "    ($REGISTRY)"
    exit 1        # non-zero: this is an error, not a quiet no-op
fi

mapfile -t ROWS <<< "$REG_OUT"
# a VALID, empty registry — nobody active, say nothing (and that is correct, not blind)
[ "${#ROWS[@]}" -eq 0 ] && exit 0

MULTI=0
[ "${#ROWS[@]}" -gt 1 ] && MULTI=1

RC=0
for row in "${ROWS[@]}"; do
    TENANT="${row%%$'\t'*}"
    WALLET="${row##*$'\t'}"
    [ -z "$TENANT" ] && continue

    # Label each section ONLY when there is more than one book, so a single-tenant box keeps its
    # clean output and never shows a tenant header that means nothing.
    if [ "$MULTI" -eq 1 ]; then
        echo "════════════════════════════════════════════════════════════════"
        echo "  ${TENANT^^}  ·  ${WALLET}"
        echo "════════════════════════════════════════════════════════════════"
    fi

    # STEWARD_TENANT resolves the registry wallet inside steward_identity._from_env(), and
    # STEWARD_WALLET is exported too so nothing falls through to the configured default.
    out="$(STEWARD_TENANT="$TENANT" STEWARD_WALLET="$WALLET" \
           timeout 300 python3 "$REPORT" 2>&1)"
    rc=$?
    printf '%s\n' "$out"

    if [ "$rc" -ne 0 ]; then
        # Name the failure against the tenant. A blank section with no explanation reads as
        # "nothing to report", which is a different and much worse claim.
        echo "  ⚠️  ${TENANT}: farm report exited rc=$rc — the section above is incomplete or empty."
        RC="$rc"
    fi
    [ "$MULTI" -eq 1 ] && echo
done

exit "$RC"
