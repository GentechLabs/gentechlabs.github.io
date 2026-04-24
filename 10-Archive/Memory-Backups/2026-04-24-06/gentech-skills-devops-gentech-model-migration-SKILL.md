---
name: gentech-model-migration
description: Complete model migration guide for Gentech Agency agents — how to properly switch models via terminal config.yaml (not Telegram UI), including vision model setup, cron job bulk update, and verification.
trigger: User wants to switch agent models, update model config, change from gemma4, or asks Hermes setup model questions.
---

# Model Migration Protocol

## Critical Context
- Telegram `/model` command only changes the chat UI model. It does NOT change the backend model.
- `config.yaml` is the ONLY source of truth for model configuration.
- All 30 cron jobs are currently hardcoded to `gemma4:31b` via `ollama-cloud` provider.

## Terminal Setup Checklist

### Step 1: Run Hermes Setup
```bash
hermes setup
```

### Step 2: Model Selection
When asked for a model, choose remote/cloud option. DO NOT select local model restore (press **No**).

### Step 3: Update config.yaml for Each Agent

#### Gentech (HQ) — `/root/vaults/gentech/01-Agency/`
```yaml
model:
  default: kimi-k2.6
  provider: ollama-cloud
vision:
  model: kimi-k2.6
```

#### DMOB (Labs)
```yaml
model:
  default: qwen3-coder-next
  provider: ollama-cloud
```

#### YoYo (Strategies)
```yaml
model:
  default: kimi-k2.6
  provider: ollama-cloud
```

#### Desmond (Creative)
```yaml
model:
  default: kimi-k2.6
  provider: ollama-cloud
```

### Step 4: Update ALL 30 Cron Jobs
Cron jobs are currently all on `gemma4:31b`:
- Gentech (HQ): Watchdog, Brain Review, Brain Daily, 5x Mess Hall, Master Digest, Vault Maintenance, LLC Reminder, End of Shift, Brain Backup
- YoYo (Strategies): Crypto Watchlist+LP, Protocol DD, x402 Monitor, LayerZero DVN, Weekly Skills, Vault Nightly Sweep
- DMOB (Labs): Hermes Sync, Weekly Opportunity Scanner, PentAGI Monitor, Kite AI Check
- Desmond (Creative): Security→Content Pipeline, X Content Extractor

Update the model field in each cron job from `gemma4:31b` to the new model.

### Step 5: Verification Tests (in order)
1. Send text message → confirm response
2. Send photo/image → confirm vision works
3. Send voice message → confirm transcription works
4. Trigger a cron manually → confirm runs successfully
5. Send a long message → confirm no context compression

## Pitfalls
- **Never trust Telegram /model as source of truth** — always read the config.yaml after switching.
- **Cron jobs do NOT auto-update** when you change the main model. They must be edited individually or bulk-updated.
- **LLM field shows `gemma4:31b`** even when model is switched — check the `model.default` field, not LLM.
- **Gemma3 should NOT be used** — 4B parameter, tiny context, causes context compression after 2 messages.
- **Gemini Flash is good for speed** but weak on coding. Use `qwen3-coder-next` for Labs specifically.
- **Mistral is lightweight and great for creative work** but not for reasoning-heavy tasks.

## Current Decision (Apr 23 2026)
- HQ/Strategies/Creative: `kimi-k2.6` (multimodal + thinking + tools + swarm orchestration)
- Labs: `qwen3-coder-next` (coding-focused, multi-step reasoning)
- Vision: `kimi-k2.6` built-in (no separate auxiliary needed)
- All cron: still on `gemma4:31b` (pending Jordan's terminal update)

## Competitive Intel Context
When Jordan asks about models, he may reference this Ollama Cloud model list from Apr 23:
- kimi-42.6/42.5/42-thinking: Multi-agentic, thinking variants
- gla-5.1/4.7/4.6: Reasoning/coding agents
- qwen3.5/qwen3-coder-next: Multimodal + coding
- gemini-3-flash-preview: Fast, general purpose
- mistral-3/mistral-next/mistral-large-3: Edge/deployment/production
- deepseek-v3.1/v2.2: Hybrid/collaborative/efficiency
- open-3.5/open-3-coder-next: Open multimodal/coding
- minimax-v2.7/v3.1/v2.1: Agentic/large/software
- nemotron-3-super/nano: 70B/3B parameter
- cogita-2.1: Hybrid generative