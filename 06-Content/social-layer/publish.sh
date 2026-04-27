#!/bin/bash
# Social Layer POC — Content Publisher
# Posts approved drafts via xurl
set -euo pipefail

BASE_DIR="/root/vaults/gentech/04-Entertainment/social-layer-poc"
DRAFTS_DIR="$BASE_DIR/drafts"
POSTED_DIR="$BASE_DIR/posted"
LOG_FILE="$BASE_DIR/post-log.csv"

mkdir -p "$DRAFTS_DIR" "$POSTED_DIR"

# Initialize log if needed
if [ ! -f "$LOG_FILE" ]; then
    echo "timestamp,filename,post_id,status" > "$LOG_FILE"
fi

# Find drafts (files ending in .post.md)
DRAFTS=("$DRAFTS_DIR"/*.post.md 2>/dev/null)

if [ ${#DRAFTS[@]} -eq 0 ] || [ ! -f "${DRAFTS[0]}" ]; then
    echo "📭 No drafts to publish."
    exit 0
fi

for draft in "${DRAFTS[@]}"; do
    filename=$(basename "$draft")
    echo "📤 Publishing: $filename"
    
    # Read content (strip first line if it's a title)
    CONTENT=$(cat "$draft")
    
    # Check if it's a thread (contains --- separator)
    if echo "$CONTENT" | grep -q "^---$"; then
        echo "🧵 Thread detected — posting sequentially..."
        
        # Split by --- and post each part
        POST_ID=""
        FIRST=true
        while IFS= read -r -d '' chunk; do
            chunk=$(echo "$chunk" | sed '/^$/d')
            if [ -z "$chunk" ]; then continue; fi
            
            if $FIRST; then
                RESULT=$(xurl post "$chunk" 2>&1)
                FIRST=false
            else
                # Reply to previous post to form thread
                if [ -n "$POST_ID" ]; then
                    RESULT=$(xurl reply "$POST_ID" "$chunk" 2>&1)
                fi
            fi
            
            POST_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null || echo "")
            echo "  → Posted chunk: $POST_ID"
        done < <(awk 'BEGIN{RS="\n---\n"; ORS="\0"} {print}' "$draft")
    else
        # Single post
        RESULT=$(xurl post "$CONTENT" 2>&1)
        POST_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null || echo "error")
    fi
    
    # Log and archive
    echo "$(date -Iseconds),$filename,$POST_ID,published" >> "$LOG_FILE"
    mv "$draft" "$POSTED_DIR/"
    echo "✅ Published → https://x.com/i/status/$POST_ID"
done

echo ""
echo "📋 Log: $LOG_FILE"
