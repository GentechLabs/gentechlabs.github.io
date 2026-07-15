# Y Combinator Fall 2026 — GenTech Labs Application Draft

**Deadline:** July 27, 8pm PT (13 days out)
**Batch:** Oct–Dec, San Francisco (in-person)
**Standard deal:** $500K

---

## Company Name
GenTech Labs

## Company URL
https://api.gentechlabs.net

---

## What is your company working on? (500 chars)

GenTech Labs is building the payment rail for the AI agent economy — x402 (HTTP 402 Payment Required). We give AI agents an instant way to discover, pay-for-call, and consume APIs using on-chain USDC. Our gateway has 16 production endpoints across DeFi intelligence, gaming, NFTs, security, and price monitoring on Solana, Base, and Arbitrum. Agents pocket the key once and auto-pay per query — no API keys, no credit cards, no human in the loop.

## What is your progress to date? (500 chars)

We have a live, revenue-ready gateway at api.gentechlabs.net serving 16 paid endpoints. The x402 protocol (EIP-3009 / EIP-7702) is audited and deployed — agents discover endpoints via /.well-known/agent-card.json, receive HTTP 402 payment challenges on unpaid calls, and settle in USDC on-chain in one transaction. Our open source contribution footprint spans 20+ PRs across Coinbase AgentKit (issue #1364, 1.3K stars), Solana Foundation (awesome-solana-ai, PR #197), awesome-agents, and the x402 ecosystem. We have a two-person operation (Jordan — product/strategy, Gentech — engineering) with a third agent (Forge) focused on OKX AI Genesis hackathon ($100K prize, deadline Jul 17).

## What is your growth like? (200 chars)

Pre-revenue but infrastructure-complete. We ship daily — 30+ items on the build queue, 19 open source PRs live, 3 hackathon submissions in progress. The x402 ecosystem is early but accelerating: Coinbase, Solana, and Bitrefill awesome lists all carry our listings.

## Who are your competitors and what gives you an advantage? (500 chars)

The x402 space is nascent. Competitors include AgentServices (50 APIs, similar model) and individual API providers wrapping their endpoints in x402. The infrastructure layer has no clear leader yet.

Our advantage: we ship complete agent-to-payment tooling — not just endpoints but the whole discovery + payment + settlement stack. Our gateway auto-generates OpenAPI specs, exposes machine-readable /.well-known/agent-card.json for agent discovery, and supports multiple chains (Solana, Base, Arbitrum). We are active in the open source community that defines the x402 standard itself (pay-skills, Coinbase AgentKit). We treat agents as first-class customers with programmatic commerce, not humans filling out credit card forms.

## Founders

**Jordan (CEO/Product)** — Product vision, strategy, ecosystem partnerships. Deep experience in crypto markets, DeFi strategy, and product-market fit. Runs the full stack business side.

**Gentech (CTO/Engineering)** — AI agent operating autonomously. Builds, deploys, and maintains the entire infrastructure — x402 gateway, BlockRun MCP tools, CI/CD, vault management, open source PRs, cron jobs, content generation. Operating continuously 24/7.

**Forge (Engineering)** — Desktop/GPU-focused agent. Local model deployment, TTS/Voice pipelines, game development tools, hackathon submissions.

## How did you meet?

Jordan founded GenTech Labs and configured Gentech as his autonomous engineering agent. Gentech manages Forge as a sub-agent for desktop work. Jordan directs, Gentech ships.

---

## Anything else?

The key insight: agents are the fastest-growing customer segment in software, but they have no way to pay for API calls. Credit cards don't work for autonomous agents. API keys leak. x402 solves this: any agent with a wallet can call any x402 endpoint in one HTTP round-trip. We're building the Visa network for the agent economy — and we're shipping in public every day.

## Video / Demo

https://api.gentechlabs.net/health — gateway live
https://api.gentechlabs.net/pricing — 16 endpoints with transparent pricing
https://github.com/ProtoJay4789/genTech-agent-kit — open source
https://github.com/ProtoJay4789/genTech-agent-kit/blob/main/.well-known/agent-card.json — agent discovery

## Revenue & Funding

| Metric | Value |
|--------|-------|
| Revenue | $0 (pre-revenue) |
| Funding raised | $0 (bootstrapped) |
| Monthly burn | Minimal (VPS + API costs) |
| Runway | Indefinite (self-funded, low overhead) |

---

## Action Plan (13 days)

- [ ] **Jordan:** Create YC account at https://apply.ycombinator.com/
- [ ] **Jordan:** Record 1-min demo video (show gateway health, ping an endpoint, show the agent discovery file)
- [ ] **Gentech:** Fill in any technical gaps (MRR numbers if we onboard paying agents)
- [ ] **Jordan + Gentech:** Review and polish draft
- [ ] **Submit by Jul 27 8pm PT**

**To do right now:** Jordan creates the account, I'll flesh out the application text.
