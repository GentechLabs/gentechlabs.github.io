#!/bin/bash
# mix-audio.sh
# Concatenate TTS stems into a single audio file with gaps and normalization
# Usage: ./mix-audio.sh --stems-dir "stems/" --output "conversation.mp3"

set -e

STEMS_DIR="stems"
OUTPUT="conversation.mp3"
GAP=0.7  # seconds of silence between speakers

while [[ $# -gt 0 ]]; do
  case $1 in
    --stems-dir) STEMS_DIR="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --gap) GAP="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Create silent padding audio
silence_file=$(mktemp --suffix=.mp3)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t "$GAP" -q:a 9 -acodec libmp3lame "$silence_file" > /dev/null 2>&1

# Sort stems lexicographically (assumes timestamp-based filenames)
# Build a file list with silence between each stem
file_list=$(mktemp)
first=true
ls -1 "${STEMS_DIR}"/*.mp3 | sort > "$file_list"

# Generate concatenation script for ffmpeg's concat demuxer
concat_file=$(mktemp --suffix=.txt)
> "$concat_file"
while IFS= read -r stem; do
  if [[ "$first" == true ]]; then
    first=false
  else
    echo "file '$silence_file'" >> "$concat_file"
  fi
  echo "file '$stem'" >> "$concat_file"
done < "$file_list"

# Concatenate with silences
ffmpeg -y -f concat -safe 0 -i "$concat_file" -c copy "${OUTPUT}.raw.mp3" > /dev/null 2>&1

# Normalize loudness (EBU R128)
ffmpeg -y -i "${OUTPUT}.raw.mp3" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -acodec libmp3lame -q:a 2 "$OUTPUT" > /dev/null 2>&1

# Cleanup
rm -f "$silence_file" "$file_list" "$concat_file" "${OUTPUT}.raw.mp3"

echo "Mixed audio saved to: $OUTPUT"
