#!/bin/bash
# Social Layer — Influencer Scout
# Maps key accounts in crypto/hackathon space for engagement strategy
# Run once to build baseline, then weekly to track changes

set -euo pipefail

VAULT="/root/vaults/gentech/03-Strategies/social-layer-poc"
OUTPUT="$VAULT/influencers/scout-$(date +%Y-%m-%d).md"

mkdir -p "$VAULT/influencers"

echo "# Influencer Scout — $(date +%Y-%m-%d)" > "$OUTPUT"
echo "" >> "$OUTPUT"

# Look up key accounts
ACCOUNTS=("solana" "base" "buildathon" "cyfrinupdraft" "code4rena" "sherlockdefi")

for acct in "${ACCOUNTS[@]}"; do
    echo "## @$acct" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    xurl user "$acct" 2>/dev/null >> "$OUTPUT" || echo "⚠️ Not found" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    
    # Their recent posts
    echo "### Recent Posts" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    xurl search "from:$acct" -n 5 2>/dev/null >> "$OUTPUT" || echo "⚠️ Search failed" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

echo "✅ Influencer scout saved to: $OUTPUT"
