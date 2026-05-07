#!/bin/bash
# validate-conversation.sh
# Pre-flight check before mixing/distributing TTS conversation
# Usage: ./validate-conversation.sh --script "script.md" --stems-dir "stems/"

set -e

SCRIPT=""
STEMS_DIR="stems"
VALID=true

while [[ $# -gt 0 ]]; do
  case $1 in
    --script) SCRIPT="$2"; shift 2 ;;
    --stems-dir) STEMS_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$SCRIPT" ]]; then
  echo "Error: --script required"
  exit 1
fi

echo "=== Validating conversation ==="

# 1. Check all agents in script have voice mapping
echo "• Checking agent voice assignments..."
# Simple parser: lines starting with **Agent:** pattern
agents=$(grep -oE '^\*\*[^*]+\*\*:' "$SCRIPT" 2>/dev/null | sed 's/^**//;s/**://' | sort -u)
if [[ -z "$agents" ]]; then
  echo "  ⚠️  No speaker lines found in script"
  VALID=false
else
  echo "  Found agents: $agents"
  # Check against known assignment table (would come from vault in real run)
  known_agents=("Desmond" "DMOB" "YoYo" "Gentech")
  for agent in $agents; do
    if ! printf '%s\n' "${known_agents[@]}" | grep -qx "$agent"; then
      echo "  ❌ Agent '$agent' not in known voice assignment table"
      VALID=false
    fi
  done
fi

# 2. Check stem files exist for all script lines
echo "• Checking stem coverage..."
line_count=$(grep -cE '^\*\*.*\*\*:' "$SCRIPT" 2>/dev/null || echo 0)
stem_count=$(find "$STEMS_DIR" -name '*.mp3' 2>/dev/null | wc -l)
echo "  Script lines: $line_count, Stems found: $stem_count"
if [[ $stem_count -lt $line_count ]]; then
  echo "  ❌ Missing stems (expected $line_count, got $stem_count)"
  VALID=false
fi

# 3. Check for malformed script entries
echo "• Checking script formatting..."
malformed=$(grep -vE '^\*\*.*\*\*:\s*".*"$' "$SCRIPT" 2>/dev/null | grep -c '^\s*\*\*' || echo 0)
if [[ $malformed -gt 0 ]]; then
  echo "  ⚠️  $malformed lines may be malformed (check quotation marks)"
fi

# 4. Check stems are valid audio files (quick header check)
echo "• Checking stem audio validity..."
bad_stems=0
for stem in "$STEMS_DIR"/*.mp3; do
  if [[ -f "$stem" ]]; then
    # Check MP3 header magic bytes
    if ! head -c 3 "$stem" | grep -q 'ID3'; then
      echo "  ⚠️  $stem may not be a valid MP3"
      ((bad_stems++))
    fi
  fi
done
if [[ $bad_stems -gt 0 ]]; then
  VALID=false
fi

# Final verdict
echo ""
if [[ "$VALID" == true ]]; then
  echo "✅ Validation passed. Ready to mix."
  exit 0
else
  echo "❌ Validation failed. Fix errors above before mixing."
  exit 1
fi
