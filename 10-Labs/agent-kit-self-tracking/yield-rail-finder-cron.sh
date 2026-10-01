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

    # 3. DEPLOY to the web root. Committing is NOT publishing: this site is served by nginx from
    #    /var/www/gentechlabs, not by GitHub Pages. Without this step the cron writes, commits, exits
    #    0 and reports success on schedule -- while the page a reader actually loads stays frozen.
    #    That is exactly what happened: rail-finder-data.json was served 8 days stale (2026-09-16)
    #    while the repo copy was current (2026-09-23). Same false-value family as the rest of the
    #    treasury: a mechanism reporting SUCCESS while doing NOTHING.
    WEBROOT="/var/www/gentechlabs/DeFi/rainbow"
    if [ -d "$WEBROOT" ]; then
    cp -p "$DATA_FILE" "$WEBROOT/" 2>/dev/null
    _r=$(md5sum "$DATA_FILE" 2>/dev/null | cut -c1-8)
    _w=$(md5sum "$WEBROOT/$(basename "$DATA_FILE")" 2>/dev/null | cut -c1-8)
    if [ -n "$_r" ] && [ "$_r" = "$_w" ]; then
        echo "[sync] deployed to web root (md5 $_r)"
    else
        echo "[sync] DEPLOY FAILED — repo=$_r webroot=$_w (the page is serving stale data)"
    fi
    else
    echo "[sync] WARNING: web root $WEBROOT missing — data committed but NOT published"
    fi
