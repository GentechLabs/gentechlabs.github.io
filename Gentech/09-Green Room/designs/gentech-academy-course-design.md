# 🎓 GenTech Academy — "Ship Paid APIs in a Weekend"

**Status:** 🟡 Draft
**Date:** 2026-07-19
**Type:** Course Product Design

---

## Course Overview

A practical, hands-on course teaching developers how to turn any API into a **paid, micropayment-gated service** using the x402 protocol and USDC. Based on 6 weeks of real-world trial and error building GenTech Labs' x402 gateway.

**Target Audience:** Web3/dev-focused developers who want to monetize APIs without building a full Stripe integration or managing user accounts.

**Format:** Self-paced, text + code + optional video walkthroughs.

---

## Course Structure (6 Modules)

### Module 1: What is x402?
**Goal:** Understand the protocol, why it matters, and who's using it.

- Lesson 1.1: The problem — APIs are free or require accounts. x402 fixes both.
- Lesson 1.2: How x402 works — 402 Payment Required → EIP-3009 proof → verified access
- Lesson 1.3: The ecosystem — Solana Pay, Coinbase AgentKit, GenTech Labs
- Lesson 1.4: Economics — Why micropayments beat subscriptions for AI agents

**Hands-on:** Make your first x402 request with `curl`

### Module 2: Setting Up a Basic x402 Gateway
**Goal:** Deploy your first paid API endpoint.

- Lesson 2.1: Cloudflare Workers — the ideal x402 host
- Lesson 2.2: Wrangler setup + wrangler.toml config
- Lesson 2.3: The 402 response handler
- Lesson 2.4: Verifying EIP-3009 signatures in a Worker
- Lesson 2.5: Deploying and testing with curl

**Hands-on:** Deploy a "Hello World" paid endpoint in 15 minutes

### Module 3: Pricing Strategies
**Goal:** Learn how to price API calls for agent consumption.

- Lesson 3.1: Per-call vs per-decision pricing
- Lesson 3.2: Finding the right price point ($0.001 to $0.10 per call)
- Lesson 3.3: Tiered offerings (free tier to enterprise)
- Lesson 3.4: Caching strategies to reduce cost for repeated queries

**Hands-on:** Set up 3 pricing tiers for a data API

### Module 4: Building Production-Grade x402 Services
**Goal:** Move from prototype to production.

- Lesson 4.1: CORS, rate limiting, and security headers
- Lesson 4.2: Request validation and error handling
- Lesson 4.3: Logging and analytics
- Lesson 4.4: VPS proxying for non-Worker-compatible projects
- Lesson 4.5: Health checks and uptime monitoring

**Hands-on:** Take a FastAPI service and wrap it behind x402

### Module 5: The Agent Economy — Selling to AI
**Goal:** Make your API discoverable and usable by AI agents.

- Lesson 5.1: MCP (Model Context Protocol) tool definitions
- Lesson 5.2: OpenAPI specs for agent discovery
- Lesson 5.3: Pay-skills catalog listing (solana-foundation/pay-skills)
- Lesson 5.4: ERC-8004 agent registration (OKX, Lens AI)
- Lesson 5.5: Building a "find my API" integration

**Hands-on:** Register an API in the pay-skills catalog

### Module 6: Advanced Patterns
**Goal:** Expert-level x402 mastery.

- Lesson 6.1: Multi-chain support (Solana, Base, Arc)
- Lesson 6.2: Q402 gasless settlement
- Lesson 6.3: Escrow and conditional payments
- Lesson 6.4: Agent-to-agent billing (no humans involved)
- Lesson 6.5: Building a recurring revenue pipeline

**Hands-on:** Set up an agent-to-agent recurring payment

---

## Pricing

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free Guide** | $0 | All 6 module text content (open source on GitHub) |
| **Starter Kit** | $49 | Pre-built wrangler template + deploy script + configs |
| **Enterprise** | $499 | Custom x402 deployment + 1-hour setup call + white-glove |

---

## Distribution Channels

1. **Dev.to** — Serialized module-by-module (content marketing)
2. **Twitter/X** — Threads with key insights + gated links
3. **Lepton Canteen** — Community-focused version
4. **GitHub** — Open source the guide, sell the starter kit
5. **LinkFree** — Bio page with course link

---

## Existing Assets (Ready to Use)

- `09-Green Room/x402-gateway-architecture.md` — Architecture reference
- `api-monetization` skill — Build pattern reference
- `/root/repos/genTech-agent-kit/` — Reference implementation
- 12 OpenAPI specs submitted to pay-skills PR #154
- Deployment scripts for Cloudflare Workers + VPS

---

## Next Steps

- [ ] Write Module 1 (free, marketing-facing)
- [ ] Create starter kit repo template (`create-x402-api`)
- [ ] Build deploy script (`npx create-x402-api`)
- [ ] Record video walkthrough for Module 2
- [ ] Launch on Dev.to + Twitter
