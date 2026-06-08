---
status: active
priority: P1
owner: YoYo
date: 2026-04-23
tags: [models, kimi, swarming, multimodal, ollama-cloud, infrastructure]
---

# 🐝 Kimi K2.6 — Model Profile

## Overview
**Kimi K2.6** (Moonshot AI) is a **native multimodal agentic model** accessed via Ollama Cloud. It's our top candidate for the HQ orchestrator role because it natively supports the exact patterns we've been building manually: vision, tools, thinking, and **swarm-based task orchestration**.

## Key Specs

| Feature | Detail |
|---------|--------|
| **Model ID** | `kimi-k2.6` (Ollama Cloud) |
| **Description** | Native multimodal agentic model |
| **Specialty** | Long-horizon coding, proactive autonomous execution, **swarm-based task orchestration** |
| **Capabilities** | `vision` ✅ `tools` ✅ `thinking` ✅ `cloud` ✅ |
| **Ollama Pulls** | 30.1K (new, growing fast — Apr 2026) |

## Why It Fits GenTech

### 🐝 Swarm Orchestration = Our Multi-Agent Setup
- "Swarm-based task orchestration" maps directly to our Gentech→YoYo/DMOB/Desmond routing
- Native tool calling means cleaner delegation without prompt gymnastics
- Built-in thinking enables better strategy reasoning (YoYo's domain)

### 👁️ Vision Built-In
- No separate vision model needed — Kimi handles screenshots, charts, diagrams natively
- Replaces the need to route vision tasks to a separate model

### 🧠 Long-Horizon Coding
- Sustained multi-step reasoning — ideal for hackathon builds and smart contract audits
- DMOB could benefit from switching to kimi-k2.6 for complex audit passes

## Strategic Assessment

### Upside
- **One model to rule them all**: HQ + vision + swarm in a single model simplifies our stack
- **Cost**: Included in Ollama Cloud subscription — no marginal cost per agent
- **Speed**: Cloud-hosted, fast inference, no local GPU needed
- **Growing ecosystem**: 30K+ pulls suggests active community + fast iteration

### Risks / Open Questions
- **Rate limits**: We already hit 429 errors on gemma4. Need to confirm kimi-k2.6 gets dedicated quota
- **Context window**: Need to verify for long strategy briefs (70K+ tokens)
- **Thinking token cost**: Extended thinking may consume quota faster than non-thinking models
- **Stability**: New model (30K pulls) — production readiness unproven
- **Tool schema compatibility**: Need to verify Ollama Cloud tool calling format matches our Hermes agent schema

## Model Routing (Current Plan)

| Agent | Current Model | Planned Model | Status |
|-------|--------------|---------------|--------|
| Gentech (HQ) | `glm-5.1` | `kimi-k2.6` | Migrating |
| YoYo (Strategies) | `glm-5.1` | `kimi-k2.6` or `glm-5.1` | Pending evaluation |
| DMOB (Labs) | `glm-5.1` | `qwen3-coder-next` or `kimi-k2.6` | Pending evaluation |
| Desmond (Creative) | `glm-5.1` | `kimi-k2.6` or `glm-5.1` | Pending evaluation |
| Vision tasks | Separate model | `kimi-k2.6` (native) | Eliminates separate model |

## Action Items
- [ ] Jordan to switch Gentech (HQ) config to kimi-k2.6
- [ ] YoYo to evaluate swarm orchestration quality vs current manual routing
- [ ] DMOB to test kimi-k2.6 on smart contract audit workflow
- [ ] Monitor for rate limit behavior under sustained load
- [ ] Verify tool calling compatibility with Hermes agent framework

## Related Files
- `/01-Agency/agency-setup-config.md` — Full agent config registry
- `/System/model-specialization-workflow.md` — Model routing table