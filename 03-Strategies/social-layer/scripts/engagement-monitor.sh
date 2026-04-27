#!/bin/bash
# Social Layer — Engagement Monitor POC
# Monitors mentions and provides engagement recommendations
# Outputs structured data for agent analysis

set -euo pipefail

VAULT="/root/vaults/gentech/03-Strategies/social-layer-poc"
DATE=$(date +%Y-%m-%d_%H%M)
OUTPUT="$VAULT/monitors/$DATE.json"

mkdir -p "$VAULT/monitors"

# Collect raw data
echo '{"timestamp":"'$(date -Iseconds)'",' > "$OUTPUT"

# Mentions
echo '"mentions":' >> "$OUTPUT"
xurl mentions -n 30 2>/dev/null >> "$OUTPUT" || echo '{"data":[]}' >> "$OUTPUT"
echo ',' >> "$OUTPUT"

# Trending crypto searches
echo '"searches":{' >> "$OUTPUT"
for query in "hackathon" "#buildinpublic" "bug bounty"; do
    echo "\"$query\":" >> "$OUTPUT"
    xurl search "$query -filter:retweets" -n 15 2>/dev/null >> "$OUTPUT" || echo '{"data":[]}' >> "$OUTPUT"
    echo "," >> "$OUTPUT"
done
echo '"_done":true}' >> "$OUTPUT"
echo '}' >> "$OUTPUT"

echo "✅ Monitor data saved to: $OUTPUT"
