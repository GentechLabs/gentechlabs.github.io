#!/bin/bash
# On-Chain Position Reader — Cron wrapper
# Reads live LFJ LP position and writes to defi-data.json
# Usage: ./run-reader.sh [WALLET_ADDRESS]

set -e

WALLET="${1:-0x7ebff188f2Eba16518C02864589b1403a5d1296a}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="/root/projects/lp-reader"
OUTPUT="/root/vaults/gentech/defi-data.json"

echo "🔄 $(date '+%Y-%m-%d %H:%M:%S') — Running on-chain position reader"

cd "$PROJECT_DIR"
node reader.mjs --wallet "$WALLET" --output "$OUTPUT" 2>&1

echo "✅ Done at $(date '+%Y-%m-%d %H:%M:%S')"
