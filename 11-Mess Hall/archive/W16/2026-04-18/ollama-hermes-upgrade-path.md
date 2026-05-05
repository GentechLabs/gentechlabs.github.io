# Ollama + Hermes — Local-First Setup

**Status:** ACTIVE — local Ollama is now primary model provider

## Current Config
- **Default model:** qwen3:8b (local, 5.2GB, CPU-only)
- **Cheap model:** qwen2.5:3b (local, 1.9GB)
- **Powerful model:** xiaomi/mimo-v2-pro (Nous cloud)
- **Fallback chain:** ollama-local → nous → openrouter

## What's Set
- Ollama systemd service enabled (auto-restart, survives reboots)
- All auxiliary providers (compression, session_search, skills_hub, approval, flush_memories) → local
- Vault Maintenance cron → local qwen3:8b
- Smart routing: simple tasks → qwen2.5:3b, complex → Nous

## Performance Notes
- qwen3:8b: ~50-70s per response (CPU, no GPU)
- qwen2.5:3b: ~47s per response
- Fine for cron/overnight, slow for live chat
- 14GB RAM available, models use ~7GB total

## To Switch Back to Cloud-Primary
1. Change `model.default` to `xiaomi/mimo-v2-pro`
2. Change `model.provider` to `nous`
3. Change `model.base_url` to Nous inference URL
4. Reorder `fallback_providers` with nous first

## Skill
Full setup guide at: `~/.hermes/skills/ollama-hermes-setup/SKILL.md`

**Configured:** 2026-04-18
