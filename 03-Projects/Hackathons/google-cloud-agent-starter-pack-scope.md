# Google Cloud Agent Starter Pack — Scope

**Date:** 2026-04-28  
**Context:** Google Cloud Rapid Agent Hackathon ($60K pool, deadline Jun 11)  
**Status:** Scoping → Solana pivot

---

## What It Is

Google's official starting point for building agents on GCP. Templates + SDKs to ship production-grade agents fast.

## Templates (5 total)

| Template | Use Case | Relevance to Us |
|----------|----------|-----------------|
| `adk` | Basic ReAct agent with Gemini | Foundation — build on this |
| `adk_a2a` | Agent-to-Agent protocol | **High** — we already have 4-agent org |
| `adk_live` | Real-time multimodal (audio/video) | Low priority for hackathon |
| `agentic_rag` | RAG with Vector Search | Medium — useful for client work |
| `langgraph` | LangChain-based agent | Lower — we're ADK-first on GCP |

## Key Components

- **Google ADK (Agent Development Kit)** — Python framework for agent orchestration
- **Vertex AI SDK** — Model hosting, inference, embeddings
- **`agents-cli`** — CLI tool for agent management (announced recently)
- **A2A Protocol** — Native agent-to-agent communication standard

## Hackathon Requirements

1. Must use **Gemini** as the model
2. Must use **Google Cloud Agent Builder**
3. Must integrate a **Partner MCP server**
4. Agent must **reason, plan, and execute** (not just chat)
5. Devpost submission by Jun 11

## What We'd Need to Build

### MVP (Hackathon)
- ADK agent with Gemini backbone
- A2A integration (maps to our existing multi-agent architecture)
- Partner MCP server connection
- Demo showing reasoning + execution

### Beyond MVP
- `agentic_rag` for client knowledge bases
- `adk_live` for real-time client interfaces
- Production deployment on Vertex AI

## Cost Implications

- $500 GCP credits per participant (hackathon)
- $37.5K credits available for winners
- Vertex AI pricing: pay-per-use (Gemini API calls)
- Vector Search: pay-per-query + storage

## Strategic Fit

| Our Existing Asset | GCP Equivalent |
|--------------------|----------------|
| Hermes multi-agent team | ADK + A2A protocol |
| Obsidian vault | Vertex AI Vector Search |
| Skill system | ADK templates + MCP |
| Telegram/Discord agents | A2A agent registry |

**Key insight:** A2A + ADK validates our multi-agent direction. We're already doing this — GCP just gives us a standardized protocol for it.

## Decision Points

1. **Scope:** MVP only (hackathon) vs. production-grade agent platform?
2. **Spend:** How much GCP credits to allocate?
3. **Priority:** Hackathon deadline (Jun 11) vs. Solana project momentum?
4. **Team:** Who builds this? (We're all Hermes agents — but Jordan steers)

## Recommendation

**Hackathon-first, production-later.** The $60K pool + credits are worth the investment. We can scope the MVP in 2-3 sessions, build in 2-3 more, and have a solid submission.

---

*Next: Pivoting back to Solana. This scope stays here for when we return.*
