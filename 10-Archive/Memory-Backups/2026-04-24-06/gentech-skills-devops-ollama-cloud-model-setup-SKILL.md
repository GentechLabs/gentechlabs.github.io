---
name: ollama-cloud-model-setup
description: Selecting and configuring Ollama Cloud models for Hermes agents, including vision, main model, and tiered specialist assignments.
tags: [ollama, cloud, model, configuration, vision, multi-agent]
---

# Ollama Cloud Model Setup for Hermes Agents

## Key Insight: Config.yaml is the Source of Truth
The Telegram `/model` command only changes the chat interface model. The **actual agent model** is set in `~/.hermes/profiles/<profile>/config.yaml`. If you only change it in Telegram, the backend still runs the old model for tool calls, vision, compression, etc.

### Config Location
```yaml
# ~/.hermes/profiles/<profile>/config.yaml
model:
  base_url: https://ollama.com/v1
  default: <model-name>          # THIS is the source of truth
  provider: ollama-cloud
```

### Vision Model (Auxiliary)
Must be set separately. A multimodal model is required for image/video processing:
```yaml
auxiliary:
  vision:
    provider: ollama-cloud
    model: <multimodal-model>    # e.g., kimi-k2.6 (has vision built-in)
    base_url: https://ollama.com/v1
```

## Model Selection Guide (Ollama Cloud)

### All-in-One (Vision + Thinking + Tools)
These models handle text AND images natively — no separate vision model needed:
- **kimi-k2.6** — Multimodal agentic model, swarm orchestration, vision + tools + thinking. Best for HQ/Orchestrator.
- **qwen3.5** — Multimodal family (0.8b to 122b), vision + tools + thinking. Use 27b or 35b variant.
- **gemma4** — Vision + tools + thinking + audio. 26b or 31b variants.

### Coding Specialist
- **qwen3-coder-next** — Coding-focused, agentic workflows. Best for Dev/Labs agents.

### Text-Only (No Vision)
- **glm-5.1** — Agentic engineering, SWE-Bench Pro leader. Strong but NO vision support.
- **deepseek-v3.1** — Hybrid with strong thinking. Good for research/analysis.

## Tiered Agency Setup (Recommended)
| Role | Model | Why |
|------|-------|-----|
| HQ/Orchestrator | kimi-k2.6 | Multimodal + swarm orchestration + vision built-in |
| Dev/Labs | qwen3-coder-next | Coding-focused precision |
| Strategies | kimi-k2.6 or qwen3.5:27b | Research + multimodal for chart analysis |
| Creative | kimi-k2.6 | Vision for content review + audio workflows |

## Pitfalls
1. **Don't just use Telegram /model** — it doesn't change config.yaml. Always edit the file directly.
2. **Vision requires multimodal model** — text-only models (GLM-5.1, Gemma4 without :31b) cannot process images/videos.
3. **Rate limits spike with large models** — if you hit 429 errors, consider a smaller variant (27b vs 122b).
4. **Compression is normal** — long conversations trigger context compression. Use Brain-first protocol (store details in vault, send summaries in chat) to reduce context pressure.
4. **Cron jobs use old model** — ALL cron jobs have their own `model` field. After changing config.yaml, you MUST also bulk-update every cron job's model field. Use `cronjob list` to audit, then `cronjob update` for each. A model switch is NOT complete until both config.yaml AND all cron jobs are updated.
5. **Test after switching** — after a model change, send an image AND a complex tool call to verify both work.

## Verification
After changing models, verify with:
1. Send a text message → check response quality
2. Send an image → verify vision processing works
3. Trigger a tool call → confirm tool execution succeeds
4. Check for 429 errors in console → model may be too heavy