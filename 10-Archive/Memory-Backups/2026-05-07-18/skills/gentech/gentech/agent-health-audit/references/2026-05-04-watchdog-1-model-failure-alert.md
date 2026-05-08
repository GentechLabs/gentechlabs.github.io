# Fleet-Wide Model Failure — May 4, 2026

**Trigger:** Watchdog cron across YoYo, DMOB, Desmond, Gentech — immediate alert

**Root cause:** All agents configured with invalid model ID `nousresearch/trinity-large-thinking` (404). Provider maintains model under `arcee-ai/trinity-large-thinking` prefix.

**Errors detected:** May 4, 2026:
```
2026-05-04 19:35:06,425 ERROR root: Non-retryable client error: Error code: 404 - Model 'nousresearch/trinity-large-thinking' not found.
2026-05-04 19:35:06,430 ERROR cron.scheduler: Job 'Gentech Watchdog' failed: RuntimeError: Error code: 404 ...
```

Same pattern across DMOB, Desmond, Gentech. Also gateway `Primary provider auth failed: Hermes is not logged into Nous Portal` (likely secondary; primary blocker is model ID).

**Impact:** Repeated cron job failures across entire fleet since Apr 27 (per existing errors). Agents alive but functionally dead; LLM-dependent tasks blocked.

**Correction:** Edit each agent's `config.yaml` to set:
```yaml
model:
  default: arcee-ai/trinity-large-thinking
```
or run `hermes model` per profile to select a valid model from catalog.

Then restart all gateways.

**Relation to existing patterns:** Mirrors `references/2026-05-04-model-deprecation-fleet-failure.md` but here the model is not withdrawn; it is mis-prefixed. Treat as *namespace confusion* variant of model misconfiguration cascade.

**Validation steps:**
1. Query OpenRouter models API to confirm exact model ID exists
2. Check each agent's `config.yaml` for `model.default`
3. After correction, trigger test cron or direct message to confirm 200 responses

**Prevention:** Maintain a `references/model-catalog-snapshot.md` with known-good IDs per provider; enforce prefix checks during agent configuration.