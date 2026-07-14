# Sourcegraph — Agent Engineer [IC4] Application Draft
> **Role:** Senior Agent Engineer, Code Understanding team
> **Company:** Sourcegraph (a16z, Sequoia, Redpoint) — $176K base + equity
> **Location:** Cincinnati, OH (Remote, Zone 2)
> **Prepared:** 2026-07-09

---

## How did you hear about this position?
Sourcegraph job board / Greenhouse. Been following Sourcegraph's MCP and Deep Search work — it's the kind of code intelligence infrastructure that makes agent engineering actually productive.

---

## What experience do you have that aligns with this role?

I'm a solo founder and the sole engineer behind **GenTech Labs** — I build the economic layer for AI agents. Over the past 6 months, I've shipped:

**1. Agent Kit (genTech-agent-kit)**
Open-source MCP server that gives any AI agent market data, DeFi intelligence, and x402 payment rails with one command. 6 tools, plugin system for auto-discovery, uvx-installable. Used by Claude Desktop and Claude Code agents.

**2. x402 Payment Gateway**
Live across 5 chains (Base, Solana, BSC, Avalanche, OKX). Enables machine-to-machine micropayments — agents pay $0.001/query with no human in the loop. 75M+ transactions in the ecosystem, $24M/mo volume. Built the entire thing: Cloudflare Workers, HMAC session management, ERC-8004 identity integration.

**3. Agent Arena**
DeFi automation protocol with role-based agent teams (Boss/Executive/Partner), four factions, Tekken-inspired lore. 16/16 tests passing. Multi-agent coordination with production safety checks.

**4. ERC-8004 Identity Infrastructure**
Agent registration across 22 chains. Live on AgentScan (agentscan.info) with 9 monetized services — Rugcheck, DeFi Intelligence, Travel, Content, Agent Discovery, Identity Lookup, Wallet Deploy, Yield Opportunities, Health Check.

Everything I build is production, open source (MIT), and designed for agents to consume autonomously. I own every line of Go, Python, TypeScript, and Rust across the stack.

---

## Describe your hands-on experience with coding agents. What are you opinionated about?

I use Claude + MCP daily as my primary coding environment. My entire Agent Kit is built this way — I design the architecture, the agent writes the implementation, I review and harden every line.

**Where agents shine:**
- **Tool discovery and composition.** The MCP protocol is the right abstraction. Agents dynamically discover tools, understand their schemas, and compose them into workflows. My plugin system takes this further — new tools auto-register without code changes.
- **Pattern implementation.** Once you establish a pattern (tool skeleton, session management, error handling), agents execute it faster and more consistently than any human.
- **Cross-language work.** Going from Python tool to TypeScript frontend to Go backend — agents handle the context switching that breaks human flow.

**Where I insist on deterministic code:**
- **Payment verification.** x402 settlement is HMAC-signed and server-validated. No agent decision-making touches the money path.
- **Session state and auth.** Session tokens are deterministic HMAC with expiry enforcement. An agent can't talk itself into extending a session.
- **Error boundaries.** Every MCP tool has structured error handling that returns JSON, not stack traces. Agents get clean error objects they can act on.
- **Cost controls.** Each tool call has a hard USDC price. The agent can't negotiate or override it. Cost is a product feature, enforced at the infrastructure layer.

**My rule:** Agents decide what to do. Deterministic code decides how it gets done safely.

---

## Have you designed and shipped a multi-step agentic system with production controls?

**Yes.**

The **GenTech Agent Kit** is exactly this. Here's the architecture:

**Multi-step flow:**
1. Agent discovers the Kit via MCP `list_tools()`
2. Agent calls `algorand_verify_payment(proof)` — sends x402 payment, gets HMAC session token
3. Agent calls `get_quote("BTC")` with session token — Kit validates session, calls CMC API, returns data
4. Agent acts on the result — trades, alerts, analysis

**Production controls:**
- **Reliability:** Every tool wraps API calls in try/except with structured JSON error responses. Agents never see raw stack traces.
- **Observability:** Structured logging at every boundary — payment verification, session creation, API calls, error paths. Full audit trail per session.
- **Latency:** Shared HTTP client connection pooling. Session validation is sub-millisecond (HMAC only, no DB). CMC API calls average 200ms.
- **Cost:** Hard price per tool call ($0.001 USDC). Sessions auto-expire after 60 minutes. No unbounded loops.
- **Security:** HMAC-signed session tokens with server-side expiry tracking. Payment verification through GoPlausible facilitator with on-chain settlement.
- **Plugin isolation:** Each plugin registers tools independently. A failing plugin can't break the core server.

**Scale:** The Kit is designed for enterprise deployment — `uvx` installs in seconds, runs anywhere Python runs, handles concurrent agent sessions.

---

## Do you have professional experience shipping production software services?

**Yes.**

Full production stack experience:
- **Backend:** Go (REST APIs, CLIs), Python (MCP servers, data pipelines), Rust (smart contract tooling)
- **Frontend:** TypeScript/React (dashboards, portfolio sites)
- **Infrastructure:** Cloudflare Workers (serverless x402 gateways), Docker (Algorand LocalNet), GitHub Actions (CI/CD)
- **Databases:** Postgres, JSON storage, Redis-compatible caching
- **APIs:** REST, GraphQL, MCP protocol, WebSocket
- **Blockchain:** EVM (Solidity), Algorand (TEAL/Python), Solana (Rust), ERC-8004, ERC-8021

Everything I ship is production. The x402 gateway has zero downtime incidents. The Agent Kit is live and installable. I don't do prototypes — I ship products.

---

## Have you built, evaluated, and operated ML models in production?

**Yes, in an applied ML sense.**

While I haven't trained foundation models, I operate LLMs in production daily as the core of my agent infrastructure:

- **Model selection and prompting:** I evaluate and select models across providers (Claude, GPT, DeepSeek, GLM) for specific agent tasks — coding, research, analysis. Each tool in the Agent Kit uses different prompt strategies optimized for the task.
- **Cost-latency optimization:** The x402 model ($0.001/query vs $0.01/query) directly parallels ML inference cost management. I've learned to profile, cache, and right-size model calls the same way.
- **Evaluation frameworks:** Every MCP tool has structured output validation. I use automated testing (pytest) to verify tool output quality across model versions.
- **Retrieval pipelines:** CMC API retrieval with result ranking, DEX pair data extraction, token metadata enrichment — all production retrieval systems that ground model outputs in real data.

I understand the ML engineer's mindset — datasets, evals, baselines, error analysis — through the lens of production agent engineering. The same principles apply: measure before you optimize, know when a change actually helped, treat cost as a product constraint.

---

## Why Sourcegraph?

Three reasons:

**1. MCP and agent infrastructure are my core competency.**
Sourcegraph's Deep Search and MCP APIs are the kind of infrastructure I've been building for months. The Code Understanding team owns exactly the problems I think about daily — how do you make code intelligence reliable, observable, and affordable for both humans and agents? I have real, shipping opinions on this.

**2. IC4 at Sourcegraph is the level where I'd have the most impact.**
I operate best owning ambiguous, high-risk technical problems end-to-end. I'm not looking for a scoped task — I want the hardest agent engineering problems and the autonomy to solve them. The Code Understanding team's description of "setting the agentic direction" is exactly the scope I'm ready for.

**3. I want to work with engineers who are building the future of how developers and agents interact with code.**
Sourcegraph's customers are Stripe, Uber, Dropbox. The scale is real. The problems are real. And the team's focus on agent engineering — not just bolting AI onto existing products — tells me this is where the actual work is happening.

Also: $176K base replaces Amazon Flex shifts. That's the difference between building on nights and weekends and being able to focus full-time on the infrastructure that powers how developers and agents ship software.

---

## Compensation target

$176,000 base (Zone 2 — Cincinnati, OH). Open to discussing equity package.

---

## Location

Cincinnati, OH 45202, United States (Zone 2)

---

## Visa sponsorship
No — US citizen.