# Browser-Harness Setup — 2026-04-18

## Status: ✅ OPERATIONAL

## Components
- **Chrome**: snap chromium 147.0.7727.101, headless on port 9222
- **Service**: `chromium-cdp.service` (systemd, enabled, auto-restart)
- **Daemon**: `browser-harness-daemon.service` (systemd, enabled, auto-restart)
- **Repo**: `/opt/browser-harness` (editable install via `uv tool install -e .`)
- **Socket**: `/tmp/bu-default.sock`

## Usage
```bash
cd /opt/browser-harness
uv run browser-harness <<'PY'
goto("https://example.com")
wait_for_load()
print(page_info())
PY
```

## Services
```bash
systemctl status chromium-cdp          # Chrome headless
systemctl status browser-harness-daemon # CDP bridge daemon
```

## Chrome Launch Args
`--headless --no-sandbox --disable-gpu --remote-debugging-port=9222 --disable-dev-shm-usage --disable-extensions`

## Startup Script
`/opt/browser-harness/start-daemon.sh` — auto-detects Chrome WS URL from `localhost:9222/json/version`

## Domain Skills Available
github, producthunt, tiktok, amazon, linkedin, hackernews, job-boards, news-aggregation

## Interaction Skills Available
uploads, downloads, iframes, shadow-dom, dropdowns, dialogs, tabs, screenshots, scrolling, cookies, drag-and-drop, network-requests, print-as-pdf, viewport, connection

## Verified
- ✅ Navigate to pages
- ✅ JS execution
- ✅ Screenshot capture
- ✅ Tab management (new_tab, list_tabs, switch_tab)
- ✅ page_info() extraction
- ✅ Domain skill auto-loading on goto()
