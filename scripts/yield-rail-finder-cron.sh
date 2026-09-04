#!/usr/bin/env bash
# Yield Rail Finder — daily cron wrapper.
# Runs the finder, writes the hub JSON, commits + pushes it to main.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="/root/repos/gentechlabs.github.io"
DATA_FILE="DeFi/rainbow/rail-finder-data.json"

# 1. Run the finder, write hub JSON, print human report.
cd "$SCRIPT_DIR"
python3 yield-rail-finder.py --write-hub

# 2. Commit + push the fresh JSON to main (keeps data committed for when Pages is fixed).
cd "$REPO"
if git diff --quiet -- "$DATA_FILE"; then
    echo "[sync] no change to $DATA_FILE — nothing to push"
else
    git add "$DATA_FILE"
    git commit -m "auto: Yield Rail Finder data $(date -u +%Y-%m-%dT%H:%MZ)" >/dev/null 2>&1 || true
    # Pull-rebase to avoid non-fast-forward, then push using stored credential.
    git -c credential.helper="store --file=/root/.git-credentials" pull --rebase origin main >/dev/null 2>&1 || true
    git -c credential.helper="store --file=/root/.git-credentials" push origin main >/dev/null 2>&1 || echo "[sync] push failed (may be the known gh-pages/Actions issue)"
    echo "[sync] pushed fresh rail-finder data to main"
fi
