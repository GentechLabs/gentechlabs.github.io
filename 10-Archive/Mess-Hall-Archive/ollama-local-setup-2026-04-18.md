# Ollama Local-First Setup — 2026-04-18

## Config Changes Made
- Default model → `qwen3:8b` (local Ollama)
- Smart routing → qwen2.5:3b for simple, Nous for complex
- Fallback chain → ollama-local → nous → openrouter
- All auxiliary providers → local Ollama
  - Compression: qwen3:8b
  - Session search: qwen2.5:3b
  - Skills hub: qwen2.5:3b
  - Approval: qwen2.5:3b
  - Flush memories: qwen2.5:3b

## Cron Jobs Updated
- Vault Maintenance → local qwen3:8b (was cloud)
- Others use default chain (local first, fallback to cloud)

## Systemd Service
- `ollama.service` enabled, auto-restarts on reboot
- API at http://127.0.0.1:11434/v1

## Performance Notes
- CPU only (no GPU), 16GB RAM, 4 vCPU AMD EPYC
- qwen2.5:3b: ~47s for short reply
- qwen3:8b: ~70s for 50 tokens
- Good for overnight/cron, slow for live chat

## To Switch Back to Cloud
Edit `~/.hermes/config.yaml`:
- Change `model.default` to `xiaomi/mimo-v2-pro`
- Change `model.provider` to `nous`
- Change `model.base_url` to `https://inference-api.nousresearch.com/v1`
- Restart gateway
