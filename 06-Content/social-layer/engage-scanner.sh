#!/bin/bash
# Social Layer POC — Engagement Scanner
# Searches for relevant conversations to engage with
set -euo pipefail

OUTPUT_DIR="/root/vaults/gentech/04-Entertainment/social-layer-poc/output"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT="$OUTPUT_DIR/engage_${TIMESTAMP}.md"

# GenTech-relevant search queries
QUERIES=(
    "#hackathon blockchain"
    "#BuildOnBase smart contracts"
    "#Solana developer"
    "AI agents crypto"
    "Code4rena audit"
    "escrow smart contract"
    "x402 protocol"
    "LayerZero bridge security"
)

echo "# Engagement Opportunities — $(date '+%B %d, %Y %H:%M')" > "$REPORT"
echo "" >> "$REPORT"

for query in "${QUERIES[@]}"; do
    echo "## 🔍 Query: \`$query\`" >> "$REPORT"
    echo '```json' >> "$REPORT"
    xurl search "$query" -n 10 2>/dev/null >> "$REPORT" || echo '{"error": "auth not configured"}' >> "$REPORT"
    echo '```' >> "$REPORT"
    echo "" >> "$REPORT"
done

echo "✅ Engagement scan saved to: $REPORT"
echo "$REPORT"
