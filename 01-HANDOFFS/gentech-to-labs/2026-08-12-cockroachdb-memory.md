# Handoff — CockroachDB × AWS "Build with Agentic Memory" (Devpost)
*Prepared 2026-08-12 · Deadline **Aug 18, 2026 @ 5:00pm EDT** (6 days) · $8,750*

## What it is
Build an **agentic application that uses CockroachDB as its persistent memory layer, deployed on AWS.** Agents that think, act, and remember reliably at scale.

**Prizes:** $8,750 total — 1st $5,000 · 2nd $2,500 · 3rd $1,250.

## Hard requirements (from official rules)
- **CockroachDB = the agent's persistent memory** (conversation history, user context, task state, embeddings, or structured transactional data — at real scale, not toy queries)
- **Use ≥2 of these 4 CockroachDB tools:**
  1. **Cloud Managed MCP Server** (`cockroachlabs.cloud/mcp`) — connect agents directly, read-only default, audit logging
  2. **Distributed Vector Indexing** — embeddings + semantic search at scale, no separate vector store
  3. **ccloud CLI (Agent-Ready)** — provision clusters, JSON output, service-account RBAC
  4. **Agent Skills Repo (open source)** — machine-executable skills, MCP-compatible
- **Use ≥1 AWS service** — Bedrock, Lambda, ECS/EKS, S3, SageMaker, Bedrock Agents, or other
- **Submission:** public open-source repo (LICENSE at root!), functional demo URL, **<3-min video on YouTube/Vimeo (public)**, identify which CockroachDB + AWS tools used

## Why this is OUR lane — we already built this
This is literally our **session-memory / vault system** translated to CockroachDB. We already have:
- Persistent agent memory (vault, session search, persistent profile)
- Cross-session context management
- Agent fleet with shared state

We're not building from scratch — we're **re-homing our existing memory system onto CockroachDB as the storage layer** and deploying on AWS.

## Recommended build
**"GenTech Agent Memory"** — take our vault/session-memory architecture, back it with CockroachDB (managed MCP server + distributed vector indexing for embeddings = 2 tools), deploy agent execution on AWS Lambda or Bedrock Agents.

## For Labs — what to prep
- [ ] Stand up a CockroachDB Cloud cluster + managed MCP server (free tier)
- [ ] Wire the managed MCP server to an agent (Claude Code / Cursor native support)
- [ ] Implement distributed vector indexing for agent embeddings (semantic retrieval)
- [ ] Deploy one agent execution path on AWS (Lambda or Bedrock)
- [ ] Public GitHub repo + LICENSE (Apache 2.0 at root — detectible in About)
- [ ] 2-3 min demo video showing the memory layer working

## Judging criteria (screen for these)
- **Agentic Memory Design** — CockroachDB is a real production-grade memory layer, not toy queries
- **Technical Implementation** — quality + correct/safe tool use
- **Real-World Impact** — meaningful use case
- **Production Readiness** — secure, observable, scalable, resilient
- **Creativity** — genuinely new agentic application

## Notes / blockers
- Deadline Aug 18 (6 days). Doable — we're re-homing existing tech, not greenfield
- Repo MUST be public with a detectible LICENSE (the #1 miss across all our submissions)
- Video <3 min, must be PUBLIC on YouTube/Vimeo

**Status:** Jordan registering Aug 12. Build brief ready. Awaiting greenlight to start.
