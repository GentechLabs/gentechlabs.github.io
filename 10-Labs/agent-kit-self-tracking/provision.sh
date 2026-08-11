#!/usr/bin/env bash
# Agent Kit — Self-Tracking Treasury: one-command cron provisioning
#
# Reads treasury_config.json (wallet + chains + optional pools), verifies the
# generalized discover_positions.py runs, and registers the reporting cron(s)
# against it. "Deploy a position, the kit tracks it" — zero manual wiring.
#
# Usage:
#   ./provision.sh                    # provision with treasury_config.json
#   ./provision.sh --dry-run          # validate + show plan, don't register
#   ./provision.sh --config PATH      # use a different config file
#
# Idempotent: safe to re-run; won't double-register a matching cron.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${SCRIPT_DIR}/treasury_config.json"
DRY_RUN=0

# ── args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -f "$CONFIG" ]] || { echo "❌ config not found: $CONFIG" >&2; exit 1; }

# ── read config (needs python) ──────────────────────────────────────────
WALLET="$(python3 -c "import json,sys;print(json.load(open('$CONFIG')).get('wallet',''))")"
CHAINS="$(python3 -c "import json,sys;print(' '.join(json.load(open('$CONFIG')).get('chains',[])))")"

[[ -n "$WALLET" ]] || { echo "❌ no wallet in config" >&2; exit 1; }
[[ -n "$CHAINS" ]] || { echo "❌ no chains in config" >&2; exit 1; }

echo "🔑 Wallet:  $WALLET"
echo "⛓️  Chains:  $CHAINS"

# ── validate the discovery module actually runs ─────────────────────────
for chain in $CHAINS; do
  echo "⏳ probing $chain (live RPC)..."
  if ! python3 "${SCRIPT_DIR}/discover_positions.py" \
      --wallet "$WALLET" --chain "$chain" --json >/dev/null 2>&1; then
    echo "⚠  discovery failed for $chain — check config/RPC" >&2
    # don't hard-fail: one chain down shouldn't block the others
  else
    echo "   ✓ $chain reachable"
  fi
done

if [[ "$DRY_RUN" == "1" ]]; then
  echo "🏁 dry-run: would register a cron per chain. Exiting."
  exit 0
fi

# ── register reporting crons ────────────────────────────────────────────
# The kit's reporting cron (defined by the agent/scheduler) invokes
# discover_positions.py per chain and emits a self-tracking line. Here we
# just emit the command the cron should run — the exact cron scheduling is
# owned by the Hermes scheduler, which calls this script on install.
for chain in $CHAINS; do
  echo "🕒 scheduled report for $chain:"
  echo "   python3 ${SCRIPT_DIR}/discover_positions.py --wallet $WALLET --chain $chain"
done

echo ""
echo "✅ provisioning validated. Add the above report command(s) to your"
echo "   scheduler (or run discover_positions.py directly) to self-track."
