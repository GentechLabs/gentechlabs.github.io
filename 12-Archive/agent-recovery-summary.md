# Agent Recovery Report — 2026-04-22

## Status
- **YoYo**: Gateway running, LLM auth expired (Nous OAuth revoked)
- **DMOB**: Gateway running, LLM auth expired (Nous OAuth)
- **Desmond**: Gateway running, LLM auth expired (Nous OAuth)

## Actions Taken

### 1. Stopped all gateway processes
Cleaned stale PID and lock files.

### 2. Fixed provider misconfiguration
Changed each agent's `config.yaml`:
- `provider: stepfun` → `provider: nous`
- `base_url` → `https://inference-api.nousresearch.com/v1`
- `default: step/step-3.5-chat` → `openai/gpt-5.3-chat`

### 3. Repaired profile symlinks
Ensured all agent `home/.hermes` symlinks point to `/root/.hermes`:
- YoYo: was a directory → replaced with symlink
- DMOB: was a directory → replaced with symlink
- Desmond: was missing → created symlink

### 4. Restored `auxiliary_client.py`
Copied clean version from hermes-agent source:
- Source: `/root/.hermes/hermes-agent/agent/auxiliary_client.py`
- Replaced corrupted files in YoYo and Desmond profiles

### 5. Restarted all gateways
All 3 agent gateway processes now live.

## Outstanding Blocker
**All three agents have expired Nous OAuth tokens** (`expires_at: 2026-04-21`).  
They can import Python modules and connect to Telegram, but cannot call LLM inference until creds refreshed.

**LLM keys currently available in environment:**
- Stepfun: none
- OpenAI: none
- OpenRouter: not set (placeholder in .env)
- Anthropic: none
- Nous OAuth: tokens present but revoked

## Next Steps

Choose ONE path:

### Path A — Re-authenticate Nous OAuth (recommended if you have valid Nous account)
Run for each agent (live Hermes access may interfere; may need manual):
```bash
export HERMES_HOME=/root/.hermes/profiles/yoyo
hermes model --portal-url https://inference-api.nousresearch.com
```
Repeat for dmob, desmond. This will open a browser for OAuth consent.

### Path B — Switch to alternative provider
Supply a valid API key for another provider (Stepfun, OpenAI, OpenRouter, etc.) and update agent configs accordingly.

Example using OpenRouter:
```yaml
provider: openrouter
base_url: https://openrouter.ai/api/v1
default: openai/gpt-4o
```
Then set `OPENROUTER_API_KEY` in the environment or each agent's `auth.json`.

### Path C — Use local LLM (Ollama)
Install and run Ollama, set `provider: local` and `default: llama3`.

---
End of report.
