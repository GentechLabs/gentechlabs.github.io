# Ollama Local Fallback Setup

Set up Ollama as a local fallback for Hermes when cloud auth (Nous) fails. Free, no subscription needed.

## When to Use
- Cloud auth expires nightly (Nous tokens ~15min, refresh token can get revoked)
- Need always-available model for cron jobs / overnight tasks
- Want to reduce cloud dependency without losing capability

## Prerequisites
- Linux VPS with 8GB+ RAM (16GB recommended)
- No GPU required — runs on CPU (slower but works)

## Setup Steps

### 1. Install Ollama
Run the official installer from ollama.com/install.sh

### 2. Pull Models (pick based on RAM)
- `qwen2.5:3b` — ~2GB, ~45-50s, fast fallback for simple tasks
- `qwen3:8b` — ~5GB, ~60-70s, better reasoning and coding
- `gemma3:4b` — ~2.5GB, ~50s, alternative lightweight

### 3. Create systemd Service (CRITICAL)
Without this, `ollama serve` dies when the terminal closes. Create a systemd unit file at `/etc/systemd/system/ollama.service` with:
- ExecStart pointing to ollama binary
- Restart=always with RestartSec=5
- Environment OLLAMA_HOST=127.0.0.1:11434

Then run: `systemctl daemon-reload && systemctl enable ollama && systemctl start ollama`

### 4. Configure Hermes Fallback Chain
In `~/.hermes/config.yaml`, add to providers section:
- `ollama-local` with api_key `ollama` and base_url `http://127.0.0.1:11434/v1`

Set fallback_providers: nous → ollama-local → openrouter

Set fallback_model: provider ollama-local, model qwen3:8b

### 5. Update Cron Jobs (if needed)
Cron jobs with hardcoded cloud models BYPASS the fallback chain. Either remove the model override or set it explicitly to local model.

## Pitfalls
1. **`ollama serve &` dies** — Use systemd, not background process
2. **Cron job model overrides bypass fallback** — Check each job's model setting
3. **CPU-only is SLOW** — 50-70s per response, fine for cron but not chat
4. **RAM usage** — qwen3:8b uses ~11GB loaded. Monitor with `free -h`
5. **No GPU** — Don't expect cloud-level speed. This is a safety net.

## No Subscription Needed
Local Ollama is 100% free. Only need subscription for Ollama Cloud models.

## Verified Setup (2026-04-18)
- VPS: 16GB RAM, 4 vCPU AMD EPYC, no GPU
- Models: qwen3:8b + qwen2.5:3b both working
- Service: systemd enabled, survives reboots
- Fallback chain configured and tested
