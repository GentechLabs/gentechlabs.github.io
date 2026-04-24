---
status: active
priority: P1
owner: YoYo
last_updated: 2026-04-23
tags: [models, workflow, infrastructure, agents]
---

# 🤖 Model Specialization Workflow

## Default Model (All Agents)
**GLM-5.1 via Ollama Cloud** — Upgraded from gemma4:31b on Apr 23, 2026 to resolve 429 rate limit errors.

## Ollama Cloud Available Models (Apr 23, 2026)

### Models by Capability
| Model | Vision | Tools | Thinking | Audio | Best For |
|:---|:---|:---|:---|:---|:---|
| **kimi-k2.6** | ✅ | ✅ | ✅ | — | Multimodal agentic, long-horizon coding, swarm orchestration |
| **glm-5.1** | — | ✅ | ✅ | — | Agentic engineering, SWE-Bench leader (CURRENT DEFAULT) |
| **gemma4** | ✅ | ✅ | ✅ | ✅ | Frontier reasoning, multimodal, multiple sizes (e2b/e4b/26b/31b) |
| **qwen3.5** | ✅ | ✅ | ✅ | — | Multimodal, 0.8b–122b range, best utility |
| **qwen3-coder-next** | — | ✅ | — | — | Agentic coding workflows |
| **devstral-small-2** | ✅ | ✅ | — | — | Codebase exploration, multi-file editing (24b) |
| **nemotron-3-super** | — | ✅ | ✅ | — | 120B MoE, multi-agent apps, 12B active params |
| **minimax-m2.7** | — | ✅ | — | — | Coding, agentic workflows, productivity |
| **ministral-3** | ✅ | ✅ | — | — | Edge deployment, lightweight (3b/8b/14b) |

## Specialized Model Routing
For best-quality work, specific job types can activate specialized models on top of the GLM-5.1 default:

| Job Type | Preferred Model | Why |
|:---|:---|:---|
| Vision (images/screenshots) | **kimi-k2.6** | Native multimodal + thinking + tools |
| High-Level Strategy | **gemma4:31b** | Frontier reasoning + audio + vision |
| Smart Contracts & Coding | **qwen3-coder-next** | Code-specialized, agentic workflows |
| Creative Content & Writing | **glm-5.1** (default) | Strong generalist |
| Vault Maintenance & Cron Jobs | **ministral-3:8b** | Lightweight, vision-capable, massive throughput |
| Codebase Exploration | **devstral-small-2** | Multi-file editing, codebase search |

## Rule
- **Default**: All agents run GLM-5.1 unless the job matches a specialization above.
- **Override**: Jordan can manually specify any model for any task.
- **Escalation**: If an agent hits repeated failures on GLM-5.1, escalate to the specialized model for that job type.

## Cron Job Model Assignment
- Watchlist/LP Monitor: GLM-5.1 (default)
- Vault Nightly Sweep: `gemmas-3-flash-preview` (lightweight)
- Omni-Summary Master Brief: `kink-42-thinking` (high reasoning)

## Sync Protocol
When Jordan says "Update the Brain," also push this config to the private GitHub backup repo.