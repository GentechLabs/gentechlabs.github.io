#!/bin/bash
# generate-tts-batch.sh
# Generate TTS audio stems from a dialogue script for multiple agents
# Requires: elevenlabs-tts-integration skill or edge-tts installed
# Usage: ./generate-tts-batch.sh --script "path/to/script.md" --output-dir "stems/"

set -e

SCRIPT=""
OUTPUT_DIR="stems"
PROVIDER="elevenlabs"  # or "edge"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --script) SCRIPT="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$SCRIPT" ]]; then
  echo "Error: --script required"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Load voice assignment table (copied from references/voice-assignment-table.md)
# In practice, this would source from a generated table or skill output
declare -A VOICE_MAP
VOICE_MAP["Desmond"]="FGY2WhTYpPnrIDTdsKH5"
VOICE_MAP["DMOB"]="IKne3meq5aSn9XLyUdCD"
VOICE_MAP["YoYo"]="EXAVITQu4vr4xnSDxMaL"
VOICE_MAP["Gentech"]="JBFqnCBsd6RMkjVDRZzb"

# Parse script lines: **Agent:** "text"
grep -E '^\*\*.*\*\*:' "$SCRIPT" | while IFS= read -r line; do
  # Extract agent name between ** **
  agent=$(echo "$line" | grep -o '^\*\*[^*]*\*\*' | tr -d '*')
  # Extract text after the colon and quotes
  text=$(echo "$line" | sed -E 's/^\*\*[^*]*\*\*:\s*"//;s/"$//')

  if [[ -z "$agent" || -z "$text" ]]; then
    echo "Skipping malformed line: $line"
    continue
  fi

  voice_id="${VOICE_MAP[$agent]}"
  if [[ -z "$voice_id" ]]; then
    echo "Warning: No voice mapping for agent '$agent'. Skipping line."
    continue
  fi

  timestamp=$(date +%s%N)
  output_file="${OUTPUT_DIR}/${agent}_${timestamp}.mp3"

  if [[ "$PROVIDER" == "elevenlabs" ]]; then
    if [[ -z "$ELEVENLABS_API_KEY" ]]; then
      echo "Error: ELEVENLABS_API_KEY not set"
      exit 1
    fi
    curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/${voice_id}" \
      -H "xi-api-key: $ELEVENLABS_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"text":"'"${text}"'","model_id":"eleven_multilingual_v2"}' \
      --output "$output_file"
  else
    # Edge TTS fallback
    echo "$text" | edge-tts --voice "en-US-ChristopherNeural" --write "$output_file" > /dev/null
  fi

  echo "Generated: $output_file (agent: $agent)"
done

echo "Batch generation complete. Stems in $OUTPUT_DIR/"
