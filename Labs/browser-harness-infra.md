# Browser-Harness Infrastructure Files

Reference for disaster recovery. If services need rebuilding, use these exact files.

## `/opt/browser-harness/start-daemon.sh`
```bash
#!/bin/bash
# Auto-detect Chrome WS URL and start browser-harness daemon
set -e

WS_URL=$(curl -s http://localhost:9222/json/version | python3 -c "import sys,json; print(json.load(sys.stdin)['webSocketDebuggerUrl'])")

if [ -z "$WS_URL" ]; then
    echo "ERROR: Chrome not responding on port 9222"
    exit 1
fi

cd /opt/browser-harness
export BU_CDP_WS="$WS_URL"
export PATH="/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Clean stale socket
rm -f /tmp/bu-default.sock

echo "Starting daemon with WS: $WS_URL"
exec /root/.local/bin/uv run python daemon.py
```

## `/etc/systemd/system/chromium-cdp.service`
```ini
[Unit]
Description=Headless Chromium with CDP remote debugging
After=network.target

[Service]
Type=simple
ExecStart=/snap/bin/chromium --headless --no-sandbox --disable-gpu --remote-debugging-port=9222 --disable-dev-shm-usage --disable-extensions about:blank
Restart=always
RestartSec=5
Environment=HOME=/root

[Install]
WantedBy=multi-user.target
```

## `/etc/systemd/system/browser-harness-daemon.service`
```ini
[Unit]
Description=Browser Harness Daemon (CDP bridge)
After=chromium-cdp.service
Requires=chromium-cdp.service

[Service]
Type=simple
ExecStartPre=/bin/sleep 3
ExecStart=/opt/browser-harness/start-daemon.sh
Restart=always
RestartSec=5
WorkingDirectory=/opt/browser-harness
Environment=HOME=/root

[Install]
WantedBy=multi-user.target
```
