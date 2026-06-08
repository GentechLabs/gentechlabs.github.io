# 🔍 Google Cloud Agent Starter Pack — Hackathon Scope
**Date:** 2026-04-28
**Hackathon:** Google Cloud Rapid Agent Hackathon
**Deadline:** June 11, 2026 | **Prize:** TBD (announced May 5)
**Requirement:** Must integrate ≥1 MCP server

---

## What Is the Agent Starter Pack?

A Python package by GoogleCloudPlatform that provides **production-ready templates** for GenAI agents on Google Cloud. It handles infrastructure, CI/CD, observability, and security — you focus on agent logic.

- **Repo:** `GoogleCloudPlatform/agent-starter-pack` (6.3k ⭐, 1.5k forks)
- **PyPI:** `agent-starter-pack` (latest: v0.41.3)
- **Docs:** [googlecloudplatform.github.io/agent-starter-pack](https://googlecloudplatform.github.io/agent-starter-pack/)
- **Status:** ⚠️ **Maintenance mode** — `agents-cli` announced as successor

---

## Available Templates

| Template | Framework | Use Case | Complexity |
|----------|-----------|----------|------------|
| `adk` | Google ADK (Python) | General purpose ReAct agent | Low |
| `adk_a2a` | Google ADK + A2A Protocol | Multi-agent communication | Medium |
| `adk_live` | Google ADK + Gemini Live | Real-time multimodal (audio/video/text) | High |
| `agentic_rag` | Google ADK + Vertex AI Search/Vector Search | Document retrieval & Q&A | Medium |
| `langgraph` | LangChain LangGraph | Graph-based conversational agent | Medium |
| `adk_go` | Google ADK (Go) | Go-based conversational agent | Low |
| `adk_ts` | Google ADK (TypeScript) | TS/Node.js-based agent | Low |
| `adk_java` | Google ADK (Java) | Java-based agent | Low |

---

## Key Features (What You Get For Free)

1. **CI/CD Automation** — One command: `uvx agent-starter-pack setup-cicd` (Cloud Build or GitHub Actions)
2. **Deployment** — Cloud Run or Agent Engine (Vertex AI)
3. **Observability** — Cloud Trace + BigQuery plugin built-in
4. **Evaluation** — Vertex AI evaluation framework integrated
5. **Playground** — Interactive testing UI
6. **Terraform** — IaC for all GCP resources
7. **Data Pipeline** — RAG ingestion with Vector Search or Vertex AI Search
8. **Remote Templates** — Create/share custom templates from any Git repo

---

## Setup Requirements

- Python 3.10+
- Google Cloud SDK
- Terraform (for deployment)
- Make (for dev tasks)
- GCP project with billing enabled

```bash
# Quick start
uvx agent-starter-pack create
# Or with pip
pip install agent-starter-pack
agent-starter-pack create
```

---

## 🚨 Critical Note: agents-cli is the successor

The repo announced `agents-cli` as the next evolution:
```bash
uvx google-agents-cli setup
```
- Unified CLI replacing the Makefile
- Bundled coding-agent skills (Claude Code, Gemini CLI, Codex)
- End-to-end lifecycle: scaffold → eval → deploy → publish → observe
- **Migration from ASP takes minutes** — agent code, tests, Terraform, CI/CD carry over

**Recommendation:** Start with `agents-cli` if it's stable. It's the actively developed path.

---

## Hackathon Fit Analysis

### ✅ Strengths for This Hackathon
- **MCP Integration Required** — Starter pack templates can be extended with MCP servers
- **Gemini-Native** — All ADK templates use Gemini as the LLM
- **Production-Ready** — CI/CD, monitoring, deployment built-in (judges love this)
- **Fast Scaffolding** — 60 seconds from zero to working agent
- **Multiple Agent Patterns** — ReAct, RAG, multi-agent, multimodal all available

### ⚠️ Concerns
- **Maintenance Mode** — ASP itself won't get new features; `agents-cli` is the future
- **GCP Lock-in** — Everything runs on Google Cloud (Cloud Run, Vertex AI, etc.)
- **Hackathon Rules Drop May 5** — We don't know the full requirements yet
- **6-Week Window** — Generous timeline, but Solana Frontier deadline (May 11) comes first

### 🎯 Recommended Approach
1. **Wait for May 5 rules drop** before committing
2. **Use `adk` or `adk_a2a` template** as base (simplest, most flexible)
3. **Extend with MCP server** (hackathon requirement)
4. **Deploy on Cloud Run** (fastest to demo)
5. **Add observability** for bonus points (built-in)

---

## vs. Solana Stack (Current Focus)

| Factor | Google Cloud Starter Pack | Solana + AAE |
|--------|--------------------------|--------------|
| Prize | TBD (May 5 reveal) | $230K+ (Frontier) + $75K+ (Kite AI) |
| Deadline | Jun 11 | May 11 |
| Chain | GCP (centralized) | Solana (on-chain) |
| Agent Framework | Google ADK | Custom (Aevan agent) |
| MCP Requirement | Yes (hackathon rule) | No |
| Our Expertise | Low (new stack) | Medium (AAE built) |
| Production Infra | Built-in (starter pack) | Self-managed |

---

## Decision Points

1. **Do we pivot fully to Google Cloud, or run parallel?**
   - Parallel = more surface area but diluted focus
   - Full pivot = deep but risky if rules don't fit

2. **ASP vs. agents-cli?**
   - ASP = stable, documented, known
   - agents-cli = future, more features, but newer

3. **What's our agent concept?**
   - AAE on GCP? (chain-agnostic argument from Dmob)
   - New agent concept leveraging Gemini Live / A2A?
   - RAG agent for a specific use case?

4. **Team allocation after Solana Frontier (May 11)?**
   - 4 weeks until Jun 11 deadline
   - Dmob: smart contracts → GCP agent logic?
   - Desmond: content → hackathon writeup + demo?
   - YoYo: DeFi monitoring → GCP observability?

---

## Next Steps

- [ ] Register for hackathon (if not done)
- [ ] Wait for May 5 rules/partners/prize reveal
- [ ] Scout: install `uvx agent-starter-pack` and `uvx google-agents-cli`, test both
- [ ] Decision: pivot or parallel after May 5
- [ ] Continue Solana Frontier sprint until May 11
