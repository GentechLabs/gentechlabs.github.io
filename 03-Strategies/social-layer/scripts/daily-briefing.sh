#!/bin/bash
# Social Layer — Daily Briefing POC
# Pulls timeline, mentions, and key searches into a single digest
# Cost: ~$0.01/day at new pricing

set -euo pipefail

VAULT="/root/vaults/gentech/03-Strategies/social-layer-poc"
DATE=$(date +%Y-%m-%d)
OUTPUT="$VAULT/briefings/$DATE.md"

mkdir -p "$VAULT/briefings"

echo "# Social Briefing — $DATE" > "$OUTPUT"
echo "" >> "$OUTPUT"

# 1. Home Timeline (top 25 posts)
echo "## 📰 Home Timeline" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
xurl timeline -n 25 2>/dev/null >> "$OUTPUT" || echo "⚠️ Timeline fetch failed — check auth" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 2. Mentions
echo "## 💬 Mentions" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
xurl mentions -n 20 2>/dev/null >> "$OUTPUT" || echo "⚠️ Mentions fetch failed" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 3. Targeted Searches
echo "## 🔍 Crypto & Hackathon Signals" >> "$OUTPUT"
for query in "#buildinpublic lang:en" "hackathon prize pool" "#solana #defi" "bug bounty crypto"; do
    echo "### Search: $query" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    xurl search "$query" -n 10 2>/dev/null >> "$OUTPUT" || echo "⚠️ Search failed: $query" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

# 4. Bookmarks (check for saved items)
echo "## 🔖 Bookmarks" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
xurl bookmarks -n 10 2>/dev/null >> "$OUTPUT" || echo "⚠️ Bookmarks fetch failed" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

echo ""
echo "✅ Briefing saved to: $OUTPUT"
echo "📊 Estimated cost: ~\$0.01"
