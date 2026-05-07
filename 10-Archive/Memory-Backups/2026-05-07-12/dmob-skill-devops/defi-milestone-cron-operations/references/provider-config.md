# Provider Config Reference

## Current Setup (as of May 5, 2026)

### Primary Provider: XiaomiMega
- **Config section:** `custom_providers:` in config.yaml
- **Name:** `XiaomiMega`
- **Type:** OpenAI-compatible
- **Base URL:** `https://token-plan-sgp.xiaomimimo.com/v1`
- **Model:** `mimo-v2.5`
- **Cron format:** `{"provider": "custom:XiaomiMega", "model": "mimo-v2.5"}`

### Legacy/Dead Providers
- **Nous OAuth:** Dead (401 — "API key invalid, blocked or out of funds")
  - Portal: https://portal.nousresearch.com
  - Was used as fallback; no longer functional
- **GitHub Copilot:** ghp_* tokens not supported; needs gho_* or fine-grained PAT

## Provider Naming Rules (Hermes Cron)

1. **Named custom providers:** Always `custom:<name>` — e.g. `custom:XiaomiMega`
2. **Bare `custom`:** NOT valid for cron job model overrides — will fail silently or resolve to wrong provider
3. **Built-in providers:** Just the name — e.g. `anthropic`, `openrouter`, `ollama`
4. **Model field:** Must match exactly — `mimo-v2.5` works, `mimo-2.5-pro` does NOT (400 error)

## Config File Locations
- Global: `/root/.hermes/config.yaml`
- Per-profile: `/root/.hermes/profiles/<name>/config.yaml`
- Both have `custom_providers:` and `model:` sections

## Provider Resolution Chain (when model is null)
1. Check job-level `model` + `provider` fields
2. Fall back to profile `model:` section
3. Fall back to global `model:` section
4. Try `fallback_providers:` list
5. Fail with "No LLM provider configured"

**Key insight:** Steps 2-4 may resolve to dead providers (Nous OAuth). Always pin explicitly.
