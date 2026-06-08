# 🔄 Nous → Ollama Migration Plan

## Current Setup
- **Nous subscription:** $20/mo (Pro, ends May 9)
- **What it provides:** Model access (MiMo, Qwen), managed tools (Firecrawl, FAL, TTS, Browser)
- **Hermes platform:** Open-source, free

## Final Decision (Jordan)
**Keep Nous. Add Ollama Cloud. Don't go local.**

Rationale:
- Local Ollama would strain VPS resources (RAM/CPU better used for AgentEscrow, dev)
- Ollama cloud models are cheap and sufficient for routine 24/7 tasks
- Nous tools (Firecrawl, FAL, TTS, Browser) are worth keeping at $20/mo
- System works well as-is — optimize, don't overhaul

## Final Stack
| Provider | Use Case | Cost |
|----------|----------|------|
| Nous (Hermes) | Complex work, managed tools | $20/mo |
| Ollama Cloud | 24/7 routine agent tasks | $20/mo |
| OpenCode | Coding workspace | ~$20/mo |
| **Total** | | **~$60/mo** |

## What Changes
- Add Ollama cloud as model provider in Hermes config
- Route routine tasks (cron jobs, status updates) to Ollama
- Keep Nous for complex research, analysis, tool-heavy tasks
- No local Ollama install — cloud only

## Replacements Needed
| Nous Tool | Replacement | Status |
|-----------|------------|--------|
| Model access | Ollama cloud + local | ✅ Ready |
| Firecrawl (web scraping) | Direct scraping + Hyperbrowser | ✅ Available |
| FAL (image gen) | FAL direct API or alternative | ⚠️ Set up needed |
| OpenAI TTS | ElevenLabs | ✅ Already using |
| Browser Use | Hyperbrowser or local | ⚠️ Set up needed |

## Migration Steps
1. Dmob installs Ollama on VPS
2. Pull local model (Qwen 2.5 7B)
3. Test inference speed
4. Update Hermes config to use Ollama endpoint
5. Test all agents with new model
6. Set up tool replacements (Firecrawl, FAL alternatives)
7. Run for 1 week parallel (both systems)
8. If stable → cancel Nous subscription

## Hermes Config Change
```yaml
# Before (Nous)
provider: nous
model: xiaomi/mimo-v2-pro

# After (Ollama)
provider: custom
api_base: http://127.0.0.1:11434/v1
model: qwen2.5:7b  # local
# or
model: llama3.1:8b  # cloud
```

## Timeline
- **Tonight:** Ollama install + local test
- **This week:** Parallel run (both systems)
- **Before May 9:** Make cancel/keep decision
- **May 9:** Cancel Nous if Ollama stable

## Risk Assessment
- **Low risk:** Ollama is production-ready, Hermes officially supports it
- **Medium risk:** Local model quality may differ from MiMo
- **Mitigation:** Keep Ollama cloud for complex tasks, local for routine

## Date
2026-04-17
