# 🎯 Project Audit & Hackathon Briefing
**Date:** May 11, 2026 | **Prepared by:** Gentech

---

## Executive Summary

**4 active hackathons, ~$95K+ in combined prize pools.** Kite AI is the most urgent (6 days left). Agora Agents is the newest opportunity with the strongest alignment to our stack. Here's the full picture.

---

## 1. KITE AI — 🔴 URGENT (6 days left)

**Deadline:** May 17 | **Prize:** $10K | **Track:** Agentic Commerce

### What's Done ✅
- Smart contracts: AgentEscrow.sol (238 lines) + TECHPaymentRouter.sol (161 lines)
- 52/52 tests passing (vault README claims 58 — needs correction)
- Security audit complete (4/5 stars, Medium findings fixed)
- Deploy script ready (Chain ID 2368)
- UI demo built (Tailwind + ethers.js v6)
- CI/CD via GitHub Actions

### What's NOT Done ❌
| Item | Status | Impact |
|------|--------|--------|
| Testnet deployment | ❌ No gas tokens | CRITICAL |
| Demo video | ❌ Not started | HIGH |
| Vercel UI deployment | ❌ Not done | MEDIUM |
| Brain layer MVP | ❌ Not started | HIGH (sprint plan) |
| Agent Passport (ERC-8004) | ❌ Not started | Stretch |
| x402 payment middleware | ❌ Not started | Stretch |

### Verdict
**Behind schedule but viable.** Two paths:
- **Path A (Fast):** Submit Novel Track with existing work — architecture + tests + docs, no live deployment needed. Could submit TODAY.
- **Path B (Full):** Rush deploy → UI deploy → demo video by May 17. Tight but possible if faucet cooperates.

### Blockers
- Need testnet gas from `faucet.gokite.ai`
- Test count discrepancy needs fixing (52, not 58)

---

## 2. AGORA AGENTS (Canteen × Circle on Arc) — 🟢 NEW

**Deadline:** May 25 (14 days) | **Prize:** $50K | **Format:** Online, apply to join

### Why This Matters
$50K pool, Circle backing (NYSE: CRCL), and 6 RFBs that directly match our DeFi agent stack. This is the highest-value opportunity in the pipeline.

### The 6 RFBs (Ranked by Fit)

| # | RFB | Fit Score | Notes |
|---|-----|-----------|-------|
| **04** | Adaptive Portfolio Manager | ⭐⭐⭐⭐⭐ | Regime detection, rebalancing, tax optimization — **LP Monitor is 80% of this** |
| **05** | Cross-Platform Arbitrage Agent | ⭐⭐⭐⭐⭐ | Price discrepancies, cross-chain execution — **AAE arbitrage angle** |
| **01** | Perpetual Futures Trading Agent | ⭐⭐⭐⭐ | 24/7 monitoring, leverage decisions — strong but needs perp integration |
| **02** | Prediction Market Trader Intelligence | ⭐⭐⭐ | Kelly Criterion, probability estimation — Polymarket angle |
| **06** | Social Trading Intelligence | ⭐⭐⭐ | Copy-trading with AI — could use our agent reputation system |
| **03** | Prediction Market Verticals | ⭐⭐ | Market creation — more infrastructure, less agent |

### Tech Stack
- **Arc** — Circle's EVM L1, sub-second finality, ~$0.01 USDC fees
- **CCTP** — Cross-Chain Transfer Protocol
- **Gateway** — Unified USDC balance across chains
- **Wallets** — Embedded wallets
- **USYC** — Tokenized money market fund
- **App Kit** — Bridge, Swap, Send, Unified Balance

### Judging (30/30/20/20)
1. **30% Agentic Sophistication** — How much does the AI actually decide?
2. **30% Traction** — Real users, real transactions during event window
3. **20% Circle Tool Usage** — Creative use of Circle platform
4. **20% Innovation** — Novel approaches, emergent behavior

### Awards
- 1st: $10K | 2nd: $7.5K × 2 | 3rd: $5K × 3
- Standout Teams: $7.5K (10-12 teams, ~$650-750 each)
- Easter Eggs: $2K (Discord puzzles, code-golf)

### Submission Requirements
1. Live working product demo
2. Founder pitch video
3. Public GitHub repo
4. Traction questions (users onboarded, problems solved)

### Recommendation
**RFB 04 (Adaptive Portfolio Manager) is our strongest play.** The LP Monitor already does regime detection, IL tracking, and position management. We'd be porting existing logic to Arc with Circle's stablecoin-native settlement. The CCTP integration adds cross-chain collateral movement, which is novel.

---

## 3. SWARMS ACM — 🟡 QUEUED (16 days left)

**Deadline:** May 27 | **Prize:** $30K | **Track:** Finance & Market Analysis

### Status
- Tech assessment complete ✅
- SWARMS_API_KEY ready ✅
- Build approach defined: LP Monitor → Swarms Marketplace agent
- Estimated effort: ~40 hours over 10 days (May 18-27)
- **GitHub repo creation still blocked** (needs fresh PAT)

### Plan
After Kite AI submits (May 17), pivot to Swarms build. Strip Telegram/cron dependencies, wrap with `@tool` decorators, publish to marketplace.

---

## 4. SOMNIA AGENTATHON — 🟡 QUEUED (30 days left)

**Deadline:** ~Jun 10-11 | **Prize:** $5K + Job Opportunity | **Chain:** Somnia (EVM L1)

### Key Details
- Organized by Encode Club + Somnia
- 3-week build window (May 20 – Jun 10)
- **Job opportunity:** Top builders considered for Somnia team
- **Demo Day:** Best projects featured
- **Tech:** Solidity, Hardhat/Foundry, 1M+ TPS, sub-second finality
- **Unique features:** Native Reactivity (contracts respond to events), Deterministic LLMs (on-chain AI inference), IceDB (15-100ns reads)

### Fit
- ✅ EVM-compatible — our Solidity tooling works directly
- ✅ AI agents focus
- ✅ Job opportunity is the real value (a16z + SoftBank backed)
- ⚠️ Small prize pool ($5K) but strong hiring signal

### Recommendation
Low priority for now. The job opportunity is compelling but the prize pool is small. After Agora Agents and Swarms ACM, this becomes the next focus.

---

## 5. BAGS FM — ⚪ QUEUED (21 days left)

**Deadline:** Jun 1 | **Prize:** $1M + $3M support | **Chain:** Solana

### Status
- Agent Trading Desk build planned
- 46 MCP tools for AI agents
- Solana-based memecoin launchpad

### Note
This conflicts with Somnia timing. Need to decide priority between Bags (higher prize) and Somnia (job opportunity).

---

## Pipeline Priority (Recommended)

| # | Hackathon | Deadline | Prize | Action |
|---|-----------|----------|-------|--------|
| 1 | **Kite AI** | May 17 | $10K | Submit by May 17 — Path A (Novel Track) or B (full deploy) |
| 2 | **Agora Agents** | May 25 | $50K | Apply NOW, build RFB 04 (Adaptive Portfolio Manager) |
| 3 | **Swarms ACM** | May 27 | $30K | Start build May 18, publish LP Monitor agent |
| 4 | **Somnia** | Jun 11 | $5K + job | Apply, build after Swarms |
| 5 | **Bags FM** | Jun 1 | $1M | Defer if Agora takes priority |

---

## Blockers Needing Jordan

1. **Kite AI:** Do we go Path A (submit now) or Path B (rush deploy)?
2. **Agora Agents:** Need to apply — submission link "coming soon" on site
3. **GitHub PAT:** Still expired — need fresh token for Swarms ACM repo
4. **Bags vs Somnia:** Which takes priority after Agora?

---

## Cross-Chain Reuse Opportunities

| Existing Asset | Reuse In | Adaptation Needed |
|----------------|----------|-------------------|
| LP Monitor | Agora RFB 04, Swarms ACM | Strip Telegram/cron, add Circle tools |
| AgentEscrow.sol | Somnia, Agora | Solidity works on both EVM chains |
| Agent reputation system | Agora RFB 06, Somnia | Port to Arc/Somnia agents |
| DeFi milestone tracker | Agora RFB 01, 05 | Add perp/arb logic |
