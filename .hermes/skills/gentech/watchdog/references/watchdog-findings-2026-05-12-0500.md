# Watchdog Findings — 2026-05-12 05:00 UTC

## Status: OK — All systems nominal

### OK Items
- Gateway process: running (PID 627656 since May 9) ✓
- Cron jobs: 20 active — ALL showing `ok` status ✓
- Sessions: 40 sessions in last 24h ✓
- Disk: 66% used (67G free) ✓
- Memory: 4.9Gi/15Gi used ✓
- gateway.log: 0 errors in last hour ✓
- errors.log: MCP JSONRPC parse errors continuing (known ampersend proxy noise, non-blocking) ✓
- Vault: accessible, git working, files present ✓

### Known/Ongoing (no change)
- Nous Portal auth: not logged in (interactive sessions using OpenCode Go provider, unaffected)
- MCP JSONRPC parse errors: continuing (known ampersend proxy stdout pollution, non-blocking)
- Vault git: diverged from origin, staged changes present — not blocking operations

### Changes from Previous Run (04:30)
- No meaningful changes — all systems stable
