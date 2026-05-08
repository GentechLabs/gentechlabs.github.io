# Watchdog Findings — 2026-05-07 01:00 UTC

## Fleet Status

| Agent | Gateway | Cron Jobs | Issues |
|-------|---------|-----------|--------|
| Gentech | ✅ Running (mimo-v2.5, custom endpoint) | ✅ 29 active | Nous Portal OAuth revoked (non-blocking — using custom endpoint) |
| YoYo | ✅ Running | ⚠️ defi-milestone-tracker.py had `NameError` (fixed at 00:26 UTC) | Last 3 cron runs succeeded post-fix |
| DMOB | ✅ Running | ⚠️ No cron.log present | Earlier 401 API key error (May 6) |
| Desmond | ✅ Running | ⚠️ Telegram flood control (transient) | Rate limiting from rapid messages |

## Key Findings

### 1. "No LLM provider configured" — Cron Job Provider Mismatch (11 jobs affected)
Cron jobs fail with `RuntimeError: No LLM provider configured` even though `hermes status` shows mimo-v2.5 working on custom endpoint interactively. This indicates the cron daemon execution context doesn't inherit the gateway's provider configuration.

**Affected jobs:**
- Security → Content Pipeline (fdaddce49730) — last error May 5
- Gentech X Content Extractor (5a765db9dce2) — last error May 6
- The Brain — Daily (051dcc8d3f11) — last error May 6
- Vault Manager — Nightly Sweep (fc4bead12d22) — last error May 6
- Brain Backup → GitHub (c3053df6b3d3) — last error May 7 00:00
- Provider Usage Monitor (e7e3f6147ca9) — last error May 7 00:00

**Root cause:** The cron daemon spawns jobs in a context where the custom endpoint model is not accessible. Interactive gateway loads provider config from `config.yaml` at startup; cron jobs may run in a different process context.

**Fix needed:** Pin model+provider explicitly on failing cron jobs via `cronjob(update, model={"model": "mimo-v2.5", "provider": "custom:<name>"})`.

### 2. Other Cron Job Errors (stale)
- Mess Hall — Daily Rotation: HTTP 429 quota exhausted (May 6)
- Mess Hall — Break 1: ValueError I/O operation on closed file (May 3)
- Mess Hall — Break 2: 401 API key invalid (May 3)
- Mess Hall — Break 3: ValueError I/O operation on closed file (May 3)
- Mess Hall — Pre-Shift: HTTP 429 quota exhausted (May 6)
- Weekly Skills Update Check: 401 API key invalid (May 3)

### 3. YoYo Script Bug (resolved)
- `NameError: name 'eff' is not defined` in `/root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py`
- 124 occurrences in cron.log (historical)
- Script was updated at 00:26 UTC on May 7; last 3 cron runs succeeded
- The `eff` variable was used as a function parameter name inside `within_zone(eff: float)` — not a global scope issue in current version

### 4. Auth Status
- Nous Portal: Revoked across all agents (non-blocking for Gentech which uses custom endpoint, but blocks agent runs that depend on Nous)
- All API key providers: ✗ not set in Gentech profile

### 5. Diagnostic Technique Learned
- **Cross-reference script modification time with cron.log success entries** to determine if a bug was fixed without waiting for the next cron execution
- **Check `cron.log` per-agent** for standalone script errors (separate from `gateway.log` which captures Hermes agent-level errors)

## Previous Session Pattern
This session's findings align with the ongoing systemic issues documented in:
- `references/watchdog-failure-2026-05-06.md` — credential cascades, provider outages
- `references/ongoing-issues-may-6-2026.md` — persistent auth and provider issues

The "No LLM provider configured" pattern is a NEW failure mode not previously documented, caused by the recent migration to custom endpoint models.
