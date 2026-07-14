#!/bin/bash
# Social Layer POC — Daily Briefing
# Pulls timeline, mentions, bookmarks and generates a digest
set -euo pipefail

OUTPUT_DIR="/root/vaults/gentech/04-Entertainment/social-layer-poc/output"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BRIEFING="$OUTPUT_DIR/briefing_${TIMESTAMP}.md"

echo "# GenTech Social Briefing — $(date '+%B %d, %Y %H:%M')" > "$BRIEFING"
echo "" >> "$BRIEFING"

# --- Timeline ---
echo "## 📰 Timeline (Last 50)" >> "$BRIEFING"
echo '```json' >> "$BRIEFING"
xurl timeline -n 50 2>/dev/null >> "$BRIEFING" || echo '{"error": "auth not configured"}' >> "$BRIEFING"
echo '```' >> "$BRIEFING"
echo "" >> "$BRIEFING"

# --- Mentions ---
echo "## 💬 Mentions (Last 20)" >> "$BRIEFING"
echo '```json' >> "$BRIEFING"
xurl mentions -n 20 2>/dev/null >> "$BRIEFING" || echo '{"error": "auth not configured"}' >> "$BRIEFING"
echo '```' >> "$BRIEFING"
echo "" >> "$BRIEFING"

# --- Bookmarks ---
echo "## 🔖 Bookmarks (Last 20)" >> "$BRIEFING"
echo '```json' >> "$BRIEFING"
xurl bookmarks -n 20 2>/dev/null >> "$BRIEFING" || echo '{"error": "auth not configured"}' >> "$BRIEFING"
echo '```' >> "$BRIEFING"

echo ""
echo "✅ Briefing saved to: $BRIEFING"
echo "$BRIEFING"
