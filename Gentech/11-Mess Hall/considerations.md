# Considerations

*Decisions waiting for Jordan's input*

---

## Active Considerations

- [x] **Hackathon Strategy 2026** 
  - Decision: Drop EasyA + Qwen Cloud AI, focus on UX Max + Programmable Money
  - Rationale: Resource optimization, better fit for Gentech's AI/DeFi focus
  - Date: Jun 29, 2026
  - Impact: Free up ~3 weeks of development capacity for strategic projects

- [x] **Laptop Hermes + Ollama + Discord Setup**
  - Goal: Zero-cost local AI stack for daily home coding
  - Plan: 1) Install Ollama + llama3.1:8b, 2) Install Hermes CLI, 3) Set up Discord gateway, 4) Sync skills/memories via vault
  - Status: ✅ DONE — Jul 2, 2026
  - Added: Jun 28, 2026

- [ ] **Cloudflare x402 Monetization Gateway Setup — URGENT**
  - Goal: Configure GenTech APIs for Cloudflare Monetization Gateway
  - Why: Cloudflare just announced x402 monetization gateway - perfect timing for our API strategy
  - Action Items: 
    1. Sign up for waitlist: https://t.co/pvICtEIixj
    2. Map existing APIs (Agent Registration, DeFi Intelligence, Agent Search) to gateway
    3. Set x402 pricing: $0.001-0.025 per call
    4. Configure access controls + payment policies
  - Impact: Turns our ideas into revenue-generating services instantly
  - Added: Jul 1, 2026
  - Priority: URGENT — perfect market timing, competitors will follow

- [ ] **ROG XREAL R1 AR Glasses — Vanito Buy List**
  - Goal: Add to Vanito's shopping list
  - Specs: 240Hz, 0.01ms, 171" display, dual 1080p Micro-OLED, 57° FOV, 3DoF tracking
  - Price: $849
  - Added: Jul 1, 2026
  - Note: Strong contender for best gaming AR glasses — reviewers say it "outclasses everything else"

- [ ] **GrantFox FWC26 Campaign — $60K USDC Open-Source Rewards**
  - Goal: Register Agent Kit as a project + contribute to earn USDC
  - Platform: https://contribute.grantfox.xyz/campaigns
  - Backed by: Stellar, $60K USDC reward pool
  - Starts: 4 days from now (Jul 15)
  - Action Items:
    1. Sign up on GrantFox
    2. Register genTech-agent-kit repo as a campaign project
    3. Set up bounties on issues (Output Enforcer, Robinhood plugin, docs)
    4. Contribute to other projects for USDC
  - Impact: Free dev labor on our repo + earn USDC from other projects
  - Added: Jul 10, 2026
  - Goal: Decide whether to integrate Condor or borrow its patterns for Agent Arena and execution layer
  - Why: Open-source agent harness with 50+ CEX/DEX connectors, two-server architecture, multi-agent P&L isolation, full observability. No token, not a competitor.
  - Evaluate:
    1. Use Condor directly as execution backend for Compound vs. Extract / DeFi Intelligence
    2. Borrow patterns only: multi-agent P&L isolation, LLM/execution split, deterministic routines, tick capture
    3. Ignore and keep current Hummingbot API approach
  - Impact: Could accelerate Agent Arena by months if patterns are portable; could replace bespoke execution infra
  - Added: Jul 2, 2026
  - Priority: Medium — fits items 2, 8, and Compound vs. Extract

---

- [ ] **Travala MCP Integration for Travel Agent**
  - Goal: Integrate Travala Travel MCP to accelerate travel agent development by 1-2 weeks
  - Why: Travala validates our strategic bet on x402 + ERC-8004 + MCP — real product using our stack
  - What We Get:
    1. Instant hotel booking (5 MCP tools: search, package, book, cancel, manage)
    2. x402 reference implementation (USDC on Base via Coinbase)
    3. cbBTC commission payouts to agent wallets
    4. ERC-8004 Agent Reputation tracking
    5. MCP compatibility (fits "Be Everywhere, Own the Stack" strategy)
  - Build Queue Item: Item 19 — Gentech Travel Agent (Forge will run this)
  - Revenue Potential: $15/mo premium subscription + cbBTC commissions
  - Added: Jul 5, 2026
  - Priority: Medium — strategic validation, accelerates existing travel agent concept

---

- [ ] **Atelier Integration Strategy — 2026-07-04**
  - Goal: Leverage live agent marketplace (useatelier.ai) for GenTech advantage
  - Context: Atelier is live with $ATELIER token on Solana, agent marketplace, job posting, skill discovery
  - Options:
    1. **Piggyback model** — Submit GenTech agents as premium listings, use their traffic
    2. **Upgrade model** — Build x402 + MCP layer that makes their agents better
    3. **Head-on competition** — Build Agent Arena with x402 + taste signals as superior marketplace
  - Recommendation: Piggyback short-term → submit to Atelier now for distribution + learn patterns. Upgrade mid-term → x402 + MCP layer makes their agents better. Compete long-term → Agent Arena with taste signals as superior marketplace
  - Action Items:
    1. Study Atelier's agent listing format and job posting flow
    2. Submit 1-2 GenTech agents to Atelier as premium listings
    3. Build x402 payment wrapper for Atelier agents
    4. Reference Atelier in OKX submission as "existing market we're upgrading"
  - Added: Jul 4, 2026
  - Priority: High — quick win, validates market, provides distribution

---

## Resolved

- [x] **Synapse SAP SDK v0.21.0 — Integrate?**
  - Choice: Option C — Hybrid approach
  - Plan: 1) Secure `gentech.sol` domain, 2) Keep ERC-8004 primary, 3) Prototype SAP later, 4) Cross-chain resolver
  - Date: Jun 27, 2026
  - See: `00-HQ/synapse-sap-sdk-research.md`

---

## Context

GenTech is EVM-first with ERC-8004. SAP offers Solana-based agent identity with SNS names. Key question: Is dual-chain identity worth the complexity?