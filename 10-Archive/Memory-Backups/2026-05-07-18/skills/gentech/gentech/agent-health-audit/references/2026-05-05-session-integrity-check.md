# May 5, 2026 — Fleet Health Check: Session Integrity Failure Pattern

## Executive Summary

All four agents (YoYo, DMOB, Desmond, Gentech) exhibited a **systemic session write corruption** pattern: 0% session completion rate across 2-hour window despite active gateway processes and Telegram connectivity. This established a new higher-order health indicator: **session completeness ratio**.

## Evidence

| Agent | Sessions (2h) | Complete | Incomplete | Completion Rate |
|-------|---------------|----------|------------|-----------------|
| YoYo   | 44            | 0        | 44         | 0%              |
| DMOB   | 6             | 0        | 6          | 0%              |
| Desmond| 6             | 0        | 6          | 0%              |
| Gentech| 36            | 0        | 36         | 0%              |

## Technical Details

**Detection method**:
```bash
python3 -c "
import json, glob, os, time
cutoff = time.time() - 7200
for agent in ['yoyo','dmob','desmond','gentech']:
  d = f'/root/.hermes/profiles/{agent}/sessions'
  comp = inc = 0
  for f in glob.glob(d+'/*.json'):
    if os.path.getmtime(f) < cutoff: continue
    try:
      with open(f) as fh:
        s = json.load(fh)
      if 'status' in s and 'created_at' in s: comp += 1
      else: inc += 1
    except: inc += 1
  print(f'{agent.upper()}: {comp} complete, {inc} incomplete')
"
```

**Session file structure**: Complete sessions contain top-level keys: `session_id`, `status`, `created_at`, `last_updated`, `system_prompt`, `messages`. Incomplete files often have only `session_id`, `model`, `platform`, `session_start`, `last_updated`, `system_prompt`, `tools`, `message_count`, and **lack** `status` and `created_at`. This indicates the session was never properly finalized/committed.

## Root-cause hypotheses (ranked by likelihood)

1. **Coordinated ungraceful shutdown**: Multiple `gateway drain timed out` events across all agents around 02:26 UTC; running processes may have been killed during session write, truncating JSON.
2. **Disk I/O pressure**: Even though disk usage was healthy (~33%), brief I/O stalls could abort JSON serialization.
3. **In-memory corruption spill**: Earlier bytecode corruption or DB corruption affecting session serialization path.

## Correlation with other error patterns

- YoYo and Gentech logs showed repeated `404 Model 'nousresearch/trinity-large-thinking' not found` → model misconfiguration
- DMOB logs showed `401 ElevenLabs quota_exceeded`, `400 invalid model`, `No LLM provider configured` → credential cascade
- Desmond logs showed `401 ElevenLabs quota_exceeded`, `402 insufficient balance`, `No LLM provider configured` → same
- All agents logged `Auxiliary auto-detect: using main provider nous (arcee-ai/trinity-large-thinking)` but then failed on actual LLM calls → provider auto-detection working at probe time but request-time failure

**Key insight**: High session-incomplete rate + active Telegram gateway + model 404 errors = **fleet-wide provider initialization failure** with Telegram still responsive for user-triggered messages (auxiliary client may be separate from main LLM path).

## Health determination rules (derived)

1. **Session completion rate** is a **leading health indicator**: if <80% over last 20 sessions → flag as degraded; <50% → critical; 0% → agents not producing results despite process liveness
2. Always cross-check session completeness **before** concluding "alive = healthy"
3. When all agents show 0% completion simultaneously → look for fleet-wide trigger (OAuth revocation, model withdrawal, coordinated restart, disk event)
4. Telegram flood-control retries (seen in DMOB/Desmond/Gentech) can coexist with healthy sessions; they don't cause incompleteness

## Remediation tracking

This reference documents the May 5, 2026 incident state; remediation steps were not executed during the watchdog run. Subsequent recovery actions should be appended here.

## Related session IDs

- `session_cron_9ecfada01952_20260505_032519` (YoYo)
- `session_20260505_024829_865eda` (DMOB)
- `session_20260505_024850_f222b3` (Desmond)
- `session_cron_9ecfada01952_20260505_032537` (Gentech)

All show `status` and `created_at` fields missing from their JSON structures, confirming incomplete writes.

## Follow-up checks

After remediation (model fix, credential rotation, gateway restart), re-run session completeness audit. Expect immediate jump to 100% completion within 1–2 cron cycles. If incomplete rate persists, investigate disk write path (profile directory permissions, disk errors, ENOSPC).