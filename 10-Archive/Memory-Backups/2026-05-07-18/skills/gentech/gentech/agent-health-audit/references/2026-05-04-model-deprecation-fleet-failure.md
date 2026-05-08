# Model ID Misconfiguration Fleet Failure — 2026-05-04

**Watchdog run**: May 4, 2026 18:00 UTC  
**Agents affected**: YoYo, DMOB, Desmond (all non-Gentech agents)  
**Severity**: Critical — all scheduled jobs failing  
**Duration**: Ongoing from first detection; requires manual config correction  
**Status**: OPEN (unresolved as of report time)

---

## What Happened

All three operational agents (YoYo, DMOB, Desmond) simultaneously began failing with the same error in their cron jobs and direct LLM calls:

```
RuntimeError: Error code: 404 - {'status': 404, 'message': "Model 'nousresearch/trinity-large-thinking' not found. The requested model does not exist in our configuration or OpenRouter catalog."}
```

Despite possessing valid OPENROUTER_API_KEY credentials, the agents could not initialize the LLM client because the configured model ID was incorrect.

**Configured (wrong)**: `nousresearch/trinity-large-thinking`  
**Actual catalog ID**: `arcee-ai/trinity-large-thinking` (confirmed present on OpenRouter)

The error manifested as a 404 from OpenRouter's model endpoint, which could be misread as auth failure or provider outage, but was in fact a simple namespace/prefix mismatch.

---

## Root Cause

Each agent's profile `config.yaml` contained:

```yaml
model:
  default: nousresearch/trinity-large-thinking
  provider: nous
```

The `nousresearch/` prefix is **wrong** for this model on OpenRouter. Trinity models are published under the `arcee-ai/` organization on OpenRouter, not `nousresearch/`. The Nous Research organization hosts different models (e.g., `nousresearch/hermes-4-70b`), not Trinity.

The misconfiguration likely originated from:
- Copying a model ID from another provider's catalog where Trinity *is* listed under Nous (e.g., Nous Portal direct API uses a different namespace)
- Incorrect assumption that organization name in the error or model branding matches the OpenRouter organization ID

---

## Impact

- YoYo: Defi Milestone Tracker cron (every 10 min) completely failing
- DMOB: LP Position Monitor Hourly cron failing; wallet monitor script may also depend on LLM
- Desmond: Memory & Profile Backup cron failing; CMC watchlist script failing
- All direct LLM queries through these agents also returning 404
- No fallback engagement because fallback providers (openai, ollama) lacked credentials/configuration in these profiles

Gentech (CEO profile) was unaffected because it uses a different model configuration (stepfun/step-3.5-flash via xiaomi provider).

---

## Detection Sequence

1. Watchdog health check on 2026-05-04 18:10 UTC noticed repeated `Model.*not found` 404 errors in agent logs
2. Cross-referenced all three agent logs — identical error pattern within same time window
3. Verified OPENROUTER_API_KEY present in `.env` but not actually used due to model init failure
4. Queried OpenRouter `/api/v1/models` with the API key; confirmed model exists as `arcee-ai/trinity-large-thinking`
5. Inspected agent config files — all had `nousresearch/` prefix

---

## Recovery Steps (Needed)

Per agent (YoYo, DMOB, Desmond):

1. Edit config: `/root/.hermes/profiles/<agent>/config.yaml`
2. Change:
   ```yaml
   model:
     default: arcee-ai/trinity-large-thinking
   ```
3. Save and restart agent gateway:
   ```bash
   pkill -f "hermes.*<agent>.*gateway"
   /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace
   ```
4. Validate:
   - Check agent log for successful LLM client init: `tail -50 /root/.hermes/profiles/<agent>/logs/agent.log | grep -i "auxiliary.*using main provider"`
   - Trigger next cron execution or send direct message; expect 200 responses, no 404 model errors
   - Run `hermes model` for that agent to confirm model is recognized

Batch automation available via `scripts/fix-model-id-misconfiguration.py` in the `agent-health-audit` skill directory.

---

## Prevention

- **Verify model IDs via API** before committing to config: `curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models | jq '.data[] | select(.id | contains("trinity")) | .id'`
- Document known-good model IDs per provider in the reference section of `agent-health-audit` skill (snapshot approach)
- Add config validation step to agent onboarding: run `hermes model list` and confirm configured model appears

---

## Key Insight

Model 404 errors can indicate **misconfiguration** (wrong ID) even when the intended model *does* exist on the platform — always verify the exact ID string, not just the model name. Provider catalogs use organization-scoped IDs: the same model may appear under different prefixes on different platforms.

---

**Related patterns in `agent-health-audit`**:
- Pattern: Model Provider Deprecation Cascade (updated 2026-05-04 to include misconfiguration detection)
- Pattern: Process environment vs .env file validation
- Pattern: Alive But Degraded
