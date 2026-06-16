#!/bin/bash
# On-Chain Position Reader — Cron wrapper
# Reads live LFJ LP position, writes to DeFi/defi-data.json, pushes to GitHub
set -e

WALLET="${1:-0x7ebff188f2Eba16518C02864589b1403a5d1296a}"
SHAPE="${SHAPE:-bid-ask}"

cd /root/projects/lp-reader

echo "🔄 $(date '+%Y-%m-%d %H:%M:%S') — Running on-chain position reader"
node reader.mjs --wallet "$WALLET" --shape "$SHAPE" 2>&1

# Sync to GitHub Pages
REPO="/root/ProtoJay4789.github.io"
cd "$REPO"
git add DeFi/defi-data.json
if ! git diff --cached --quiet; then
    git commit -m "auto: on-chain position update $(date +%H:%M)" 2>&1
    # Retry push once if remote moved (another cron tick or manual update)
    if ! git push 2>&1; then
        echo "⚠️ Push rejected, rebasing and retrying..."
        git pull --rebase 2>&1
        git push 2>&1
    fi
fi

echo "✅ Done at $(date '+%Y-%m-%d %H:%M:%S')"
