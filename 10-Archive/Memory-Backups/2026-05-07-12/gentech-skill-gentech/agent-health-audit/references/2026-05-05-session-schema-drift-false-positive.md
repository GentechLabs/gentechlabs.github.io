# Session Schema Drift — False Positive Discovery (May 5, 2026 ~13:55 UTC)

## What Happened
Watchdog cron ran a fleet health check. Session integrity audit reported 0% completion across all 78 recent sessions (YoYo 23, DMOB 11, Desmond 9, Gentech 35). Initial diagnosis flagged this as fleet-wide session corruption.

## Root Cause
The session file schema has evolved. The `check_session_integrity.py` script and inline SKILL.md checks used `REQUIRED_KEYS = {'status', 'created_at'}`, but current Hermes sessions use a completely different structure:

**Old format (pre-May 2026):**
```json
{
  "status": "...",
  "created_at": "...",
  "messages": [...]
}
```

**Current format (May 2026+):**
```json
{
  "session_id": "...",
  "model": "...",
  "base_url": "...",
  "platform": "telegram",
  "session_start": "...",
  "last_updated": "...",
  "system_prompt": "...",
  "tools": [...],
  "message_count": 42,
  "messages": [...]
}
```

Neither `status` nor `created_at` exist in the current format. The completeness check was checking for keys that don't exist, producing a permanent 0% false positive fleet-wide.

## Schema Probe (discovery command)
```python
import json, os, glob
d = '/root/.hermes/profiles/gentech/sessions'
files = sorted(glob.glob(d+'/*.json'), key=os.path.getmtime, reverse=True)
with open(files[0]) as f:
    data = json.load(f)
print('Keys:', list(data.keys())[:15])
# Output: ['session_id', 'model', 'base_url', 'platform', 'session_start', 'last_updated', 'system_prompt', 'tools', 'message_count', 'messages']
```

## What Was Updated
1. `scripts/check_session_integrity.py`: `REQUIRED_KEYS` changed from `{'status', 'created_at'}` to `{'session_start', 'last_updated', 'messages'}`
2. SKILL.md Phase 1.5: Added schema evolution warning, schema probe command, and corrected detection commands
3. SKILL.md FATAL patterns: Changed session completeness from unconditional FATAL to schema-validated (must confirm keys match first)
4. SKILL.md Pitfalls: Added #17 (cron output is .md not .json) and #18 (`execute_code` requires explicit `terminal` import)

## Additional Discoveries This Session
- **Cron output files are `.md` format**, not `.json`. Filenames: `YYYY-MM-DD_HH-MM-SS.md`
- **`execute_code` tool** requires `from hermes_tools import terminal` — `terminal()` is not available by default in the sandboxed interpreter
- **DMOB LP monitor script path mismatch**: Cron expects `/root/.hermes/profiles/dmob/scripts/lp-aae-signal-monitor.py` but it lives at `/root/.hermes/profiles/dmob/home/.hermes/scripts/lp-aae-signal-monitor.py`
- **Desmond still missing skills**: `cmc-watchlist-scraper` and `crypto-monitoring-cron` absent from skill registry

## Implication
Any future watchdog run that checks session integrity MUST first verify the schema probe confirms the expected keys exist. A 0% rate without schema validation is meaningless.
