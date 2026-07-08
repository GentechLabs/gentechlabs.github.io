#!/bin/bash
# detect-tunnel.sh — finds the current Cloudflare tunnel URL and writes it to a file
# Called by the bridge server on startup

TRIES=0
MAX_TRIES=30

while [ $TRIES -lt $MAX_TRIES ]; do
    URL=$(journalctl -u gentech-tunnel --no-pager -n 50 2>/dev/null | grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1)
    if [ -n "$URL" ]; then
        echo "$URL" > /tmp/gentech-tunnel-url
        export GENTECH_TUNNEL_URL="$URL"
        echo "Tunnel detected: $URL"
        exit 0
    fi
    sleep 1
    TRIES=$((TRIES + 1))
done

echo "Failed to detect tunnel URL"
exit 1
