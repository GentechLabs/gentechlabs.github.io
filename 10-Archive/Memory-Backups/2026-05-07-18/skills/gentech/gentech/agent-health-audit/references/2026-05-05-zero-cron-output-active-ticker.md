# 2026-05-05 — Zero Cron Output Despite Active Ticker

**Skill context**: `agent-health-audit` — Phase 3 Cron Execution Verification

## Symptom

All four agents (Gentech, YoYo, DMOB, Desmond) showed evidence of a **living cron scheduler thread** but produced **zero job output files**:

- `.tick.lock` files updated within the last 2 minutes (ticker alive)
- `gateway.log` contained `Cron ticker started (interval=60s)` with no corresponding `Cron ticker stopped`
- **Output directory** (`/root/.hermes/profiles/<agent>/cron/output/`) was **completely empty** (0 files) for Gentech, YoYo, DMOB; Desmond had 1 ancient file from April 28
- No session files prefixed `session_cron_` created in the past 24 hours
- Despite active Telegram message responsiveness from the gateways themselves

## Diagnostic timeline

| Step | Command | Finding |
|---|---|---|
| 1. Ticker liveness | `ls -lat ~/profiles/*/cron/.tick.lock` | All mtimes within 2 min → ticker threads alive |
| 2. Output evidence | `find ~/profiles/*/cron/output -type f` | Zero output files (except Desmond's stale single file) |
| 3. Job registry | `cat */cron/jobs.json \| jq '.jobs | length'` | Gentech: 31 jobs, YoYo: 29, DMOB: 8, Desmond: 6 — jobs exist and are `enabled: true` |
| 4. Agent log scan | `grep -E '\[cron_[a-f0-9]+\]' logs/agent.log` | Gentech: 1338 gateway-triggered markers; YoYo: 3273; DMOB: 96; Desmond: 86 — **but note**: These markers reflect *gateway-internal* cron executions; their absence from recent timestamps indicates recent jobs are failing before dispatch |
| 5. Error log scan | `grep -i 'ERROR cron' logs/errors.log \| tail -20` | Fleet-wide pattern: `RuntimeError: Refresh session has been revoked` + `No LLM provider configured` + `Model ... 404 not found` |

## Root causes (compound)

The zero-output condition resulted from **three simultaneous failures**:

1. **Nous OAuth tokens invalid** (`Refresh session has been revoked`) — Every profile's `auth.json` had expired or revoked refresh tokens. The cron runner aborts job initialization when it cannot obtain an access token.
2. **Model namespace misconfiguration** (`Model 'nousresearch/trinity-large-thinking' not found`) — The configured model ID used the wrong OpenRouter namespace prefix (`nousresearch/` instead of `arcee-ai/`). This returned 404 even if auth succeeded.
3. **Cron dispatcher blocked at provider initialization** — Because both errors occur during the *pre-execution* phase (before any job logic runs), no output file is ever created. The ticker marks a tick, attempts to dispatch, hits provider-level failure, logs an ERROR, and moves on — leaving no output artifact.

### Why output files were missing

Hermes cron's execution flow:
```
tick → acquire job → initialize session (LLM provider) → execute job → write output
```
Failure at **initialize session** aborts before output file open. The ticker continues; no output files appear.

## Detection recipe

```bash
#!/bin/bash
# Check for "alive ticker, dead output" pattern
for agent in gentech yoyo dmob desmond; do
  lock="/root/.hermes/profiles/$agent/cron/.tick.lock"
  outdir="/root/.hermes/profiles/$agent/cron/output"

  if [ ! -d "$outdir" ]; then
    echo "$agent: output directory missing — cron never configured"
    continue
  fi

  lock_age=$(( $(date +%s) - $(stat -c %Y "$lock") ))
  out_count=$(find "$outdir" -type f -mmin -30 | wc -l)

  if [ $lock_age -lt 120 ] && [ $out_count -eq 0 ]; then
    echo "🚨 $agent: ticker fresh ($lock_age s) but output empty (0 files in 30 min)"
  else
    echo "$agent: OK (output count=$out_count, lock age=${lock_age}s)"
  fi
done
```

## Recovery sequence

Step 1 — Re-authenticate all agents with Nous:
```bash
for agent in gentech yoyo dmob desmond; do
  sudo -u $agent hermes model  # interactive OAuth device code flow
done
```

Step 2 — Fix model ID namespace in each `config.yaml`:
```bash
for agent in gentech yoyo dmob desmond; do
  sed -i 's|nousresearch/trinity-large-thinking|arcee-ai/trinity-large-thinking|' \
    /root/.hermes/profiles/$agent/config.yaml
done
```

Step 3 — Restart all gateways to pick up config+credential changes:
```bash
pkill -f hermes.*gateway
# or per-agent:
for agent in gentech yoyo dmob desmond; do
  /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile $agent gateway run --replace &
done
```

Step 4 — Verify output production:
```bash
# Wait 5–10 minutes, then check output directories
find /root/.hermes/profiles/*/cron/output -type f -mmin -10 | wc -l  # should be >0
```

## Distinguishing from other silent-cron patterns

| Pattern | Ticker alive? | Output files | Key differentiator |
|---|---|---|---|
| Zero output due to auth block | ✅ Yes (lock fresh) | ❌ Zero | `errors.log` full of 401/403/refresh-revoked; job registry intact |
| Cron daemon crashed | ❌ No (lock stale) | ❌ Zero | `.tick.lock` mtime old; gateway.log lacks recent "Cron ticker started" |
| Job registry empty | ✅ or ❌ | ❌ Zero | `jobs.json` `jobs` array length = 0 or file malformed |
| Output dir permission denied | ✅ Yes | ❌ Zero | `errors.log` shows `PermissionError` or `OSError: [Errno 5]` |

## Related skill sections

- **Phase 3 — Cron Execution Verification** — Primary methodology for cron health
- **Pattern: Auth Revocation Cascade Detection** — OAuth revocation identification
- **Pattern: Model Provider Deprecation Cascade** — Model 404 misconfiguration detection
- **Pattern: Agent Silence Detection via Session Analysis** — Complementary: check for sessions with only user messages

## Follow-up observations

Even after fixing auth + model IDs, allow **2–3 ticks** (2–6 minutes) for cron outputs to appear. The ticker runs every 60 seconds; jobs may be staggered across the minute.

If output files appear but remain empty (0 bytes), check job script for early exits or missing dependencies.
