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

# Pre-flight: recover from any previous failed rebase
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    echo "⚠️ Aborting stale rebase..."
    git rebase --abort 2>/dev/null || true
fi

# Ensure we're on a real branch
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ -z "$CURRENT_BRANCH" ]; then
    echo "⚠️ Detached HEAD detected, switching to main..."
    git checkout main 2>/dev/null || git checkout -b main origin/main 2>/dev/null
fi

git add DeFi/defi-data.json
if ! git diff --cached --quiet; then
    git commit -m "auto: on-chain position update $(date +%H:%M)" 2>&1
    # Retry push once if remote moved (another cron tick or manual update)
    if ! git push 2>&1; then
        echo "⚠️ Push rejected, pulling and retrying..."
        git pull --rebase origin main 2>&1 || git pull --no-rebase origin main 2>&1
        git push 2>&1
    fi
fi

echo "✅ Done at $(date '+%Y-%m-%d %H:%M:%S')"
