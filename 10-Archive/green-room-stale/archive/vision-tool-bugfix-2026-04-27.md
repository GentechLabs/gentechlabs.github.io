# Vision Tool Bugfix
**Date:** 2026-04-27
**Reported by:** Jordan
**Routed to:** DMOB (Labs)
**Provider:** Ollama Cloud (not Nous)

## Symptoms
- `vision_analyze` → "unauthorized"
- `browser_navigate` → `/usr/bin/env: 'node': No such file or directory`
- System: Node.js not installed locally
- Env says `AUXILIARY_APPROVAL_PROVIDER=nous` but primary provider is Ollama Cloud

## Root Cause Diagnosis

### Issue 1: Browser Tools
- `browser_navigate` depends on local Node.js + Puppeteer/Playwright
- **Node is not installed on this machine**
- Fix: `apt-get install nodejs` or install via nvm

### Issue 2: Vision Analyze
- `vision_analyze` likely routing to Nous provider (per env vars) but we're on Ollama Cloud
- OR: trying to use a non-vision model for vision tasks
- Fix: Check Hermes vision model config; ensure it uses Ollama Cloud vision model (e.g., `llava`, `llava-phi3`, `gemma3:4b-it` if vision-capable)

## Fix Required
- [ ] Install Node.js locally (`apt update && apt install -y nodejs npm`)
- [ ] Verify which model `vision_analyze` is actually calling (Hermes config check)
- [ ] If routing to Nous: validate Nous API key in `.env`
- [ ] If should route to Ollama Cloud: update Hermes config to use Ollama vision model
- [ ] Post-fix test: `vision_analyze` on cached image
