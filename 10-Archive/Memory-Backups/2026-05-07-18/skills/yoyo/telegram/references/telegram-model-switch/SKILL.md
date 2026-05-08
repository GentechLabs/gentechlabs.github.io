---

## Name
telegram-model-switch

## Description
Switch the Hermes agent's language model from Telegram chat. Uses `/model` and `/models` commands.

## Author
Gentech Agent Council

## Version
1.0.0

## Triggers
- `/model` — show current model or switch to a new one
- `/models` — list available providers and models

## Instructions

### /models — List available models

When user says `/models` or "what models are available":

1. Read the agent's config.yaml to see which providers are configured
2. Query the provider's available models if possible (or show common ones)
3. Return a formatted list:

**Example output:**
```
Available models:

nous:
  • xiaomi/mimo-v2-pro (current)
  • atem/atem-v1

openrouter:
  • qwen/qwen-3.6-chat
  • anthropic/claude-sonnet-4
  • google/gemini-2.5-pro

openai-codex:
  • o3

Usage: /model <provider>/<model>
       e.g. /model openrouter/qwen/qwen-3.6-chat
```

### /model — Switch model

When user says `/model <provider>/<model>` or "switch to <model>":

1. **Validate format** — must be `provider/model` or `provider/model/version`
2. **Check authorization** — only allow if sender is Jordan (user ID from config or memory)
3. **Show preview** — "Switch from xiaomi/mimo-v2-pro to qwen/qwen-3.6-chat? (yes/no)"
4. On confirmation:
   - Update `config.yaml`:
     ```yaml
     model:
       provider: <provider>
       default: <model>
     ```
   - If `base_url` differs per provider, update that too
5. **Restart gateway** — restart the Hermes gateway to apply changes
6. **Confirm** — "✓ Switched to qwen/qwen-3.6-chat. Gateway restarted."

### Error handling

- Unknown provider → "Provider not configured. Add it to config.yaml first."
- Invalid model format → "Usage: /model provider/model-name"
- Unauthorized user → "❌ Only Jordan can switch models."
- Config write error → "Failed to update config. Check file permissions."

### Notes

- This skill edits `/root/.hermes/profiles/default/config.yaml` (or current agent's profile if running as sub-agent)
- Gateway restart takes ~5 seconds, messages will be buffered
- Keep a backup of the previous model in memory so we can roll back if needed
