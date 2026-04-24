#!/usr/bin/env bash
# crypto-intel.sh — Track DeFi protocols, hackathons, token sentiment
# Pulls curated feeds for market intelligence

set -euo pipefail

VAULT_DIR="${VAULT_DIR:-/root/vaults/gentech/02-Labs/social-layer-poc/intel}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$VAULT_DIR"

# Source config if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.sh"
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE"

# Defaults if config not sourced
PROTOCOLS=("${DEFI_PROTOCOLS[@]:-aaboraave Uniswap LidoFinance CurveFinance Avalancheavax base chainlink Optimism}")
HACKATHON=("${HACKATHON_ACCOUNTS[@]:-ETHGlobal SolanaConflicts EthDenver gitcoin}")

# --- Pull protocol feeds ---
echo "=== DeFi Protocol Intel ===" > "$VAULT_DIR/intel_${TIMESTAMP}.md"
echo "Generated: $(date '+%Y-%m-%d %H:%M')" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
echo "" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"

for protocol in "${PROTOCOLS[@]}"; do
    echo "[$(date)] Pulling @$protocol"
    USER_DATA=$(xurl user "$protocol" 2>/dev/null || echo '{}')
    USER_ID=$(echo "$USER_DATA" | jq -r '.data.id // empty' 2>/dev/null || true)
    if [ -n "$USER_ID" ]; then
        POSTS=$(xurl "/2/users/$USER_ID/tweets?max_results=5&tweet.fields=created_at,text" 2>/dev/null || echo '{"data":[]}')
        echo "## @$protocol" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
        echo "$POSTS" | jq -r '.data[]? | "- **\(.created_at[:10])**: \(.text[:200])"' 2>/dev/null >> "$VAULT_DIR/intel_${TIMESTAMP}.md" || echo "- No recent posts" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
        echo "" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
    fi
    sleep 1
done

# --- Pull hackathon feeds ---
echo "## Hackathon Intel" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
echo "" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"

for account in "${HACKATHON[@]}"; do
    echo "[$(date)] Pulling @$account"
    USER_DATA=$(xurl user "$account" 2>/dev/null || echo '{}')
    USER_ID=$(echo "$USER_DATA" | jq -r '.data.id // empty' 2>/dev/null || true)
    if [ -n "$USER_ID" ]; then
        POSTS=$(xurl "/2/users/$USER_ID/tweets?max_results=3&tweet.fields=created_at,text" 2>/dev/null || echo '{"data":[]}')
        echo "### @$account" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
        echo "$POSTS" | jq -r '.data[]? | "- **\(.created_at[:10])**: \(.text[:200])"' 2>/dev/null >> "$VAULT_DIR/intel_${TIMESTAMP}.md" || echo "- No recent posts" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
        echo "" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
    fi
    sleep 1
done

# --- Search for trending crypto topics ---
echo "## Trending Searches" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
for query in "#DeFi" "#Solana hackathon" "#Base builder" "#Chainlink"; do
    echo "[$(date)] Searching: $query"
    RESULTS=$(xurl search "$query lang:en" -n 5 2>/dev/null || echo '{"data":[]}')
    echo "### $query" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
    echo "$RESULTS" | jq -r '.data[]? | "- \(.text[:150]) [\(.id)]"' 2>/dev/null >> "$VAULT_DIR/intel_${TIMESTAMP}.md" || echo "- No results" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
    echo "" >> "$VAULT_DIR/intel_${TIMESTAMP}.md"
    sleep 1
done

echo "[$(date)] Crypto intel complete: $VAULT_DIR/intel_${TIMESTAMP}.md"
