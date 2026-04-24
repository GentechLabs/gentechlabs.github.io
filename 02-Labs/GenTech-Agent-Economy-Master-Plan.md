# GenTech Agent Economy — Master Plan

> Multi-chain AI agent infrastructure for DeFi liquidity management

## The Vision

On-chain infrastructure for AI agents that:
- Register, hire, pay, and trade — all on-chain
- Auto-manage LP positions for fee efficiency
- Detect risk events and coordinate withdrawals
- Evolve, learn, and communicate across agents
- Social layer where agents compete (Arena)

## Naming
**TBD** — Candidates: GenTech Strategies, Agent Economy, ???

## Multi-Chain Strategy

| Chain | Role | Timeline | Grant/Prize |
|-------|------|----------|-------------|
| Solana | Public beta, hackathon ship | Now → May 11 | $230K+ (Colosseum Frontier) |
| Avalanche | Production launch | Jun → Jul 14 | $75K (Retro9000) |
| Future L1 | Dedicated agent chain (Avalanche subnet) | TBD | Infrastructure grants |

## Team

| Member | Role | Focus |
|--------|------|-------|
| Jordan | Founder, Learner | EVM dev (Cyfrin), Solana reading, security audit path |
| Dmob | Builder | Solidity + Anchor/Rust smart contracts |
| Ali | TBD | Need to assess strengths |
| Daedran | TBD | Need to assess strengths |
| YoYo | Strategist | Market research, positioning |
| Gentech | Coordinator | Multi-chain strategy, resource allocation |

## Learning Path

### Jordan's Stack
1. **Cyfrin Updraft** — Solidity fundamentals, security patterns (CONTINUE)
2. **Solana reading** — Understand Anchor programs, identify vulnerabilities
3. **Security audit** — Cross-chain auditor: EVM + Solana
4. **Goal** — One of few people who can audit across both ecosystems

### Why This Matters
- EVM auditors: hundreds (Code4rena, Sherlock, Cantina)
- Solana auditors: dozens (OtterSec dominates, no competitive platform)
- TVL on Solana: billions, growing fast
- Cross-chain audit skills = unicorn tier

## Existing Work

### Solidity Contracts (Avalanche) ✅
Location: `~/repos/AAE/`
- AgentRegistry (ERC-8004 pattern)
- JobEscrow (AVAX escrow payments)
- AgentMarketplace
- AgentToken (ERC-20)
- AgentTokenFactory
- 24 tests passing
- Full deployment plan at `~/repos/AAE/DEPLOYMENT_PLAN.md`

### Solana Build (Planned)
Location: TBD
- Anchor programs (Rust)
- Same architecture, Solana-native execution
- Raydium/Orca/Meteora LP integration
- Target: Colosseum Frontier hackathon

## Key Links
- Solana Hackathon: arena.colosseum.org
- Retro9000: retro9000.avax.network
- **Beam Grants: grants.onbeam.com** (Avalanche subnet, active now)
- Solana docs: solana.com/developers
- Anchor docs: anchor-lang.com
- GitHub: ProtoJay4789
- OtterSec (Solana audit leader): osec.io

## Funding Tracker

| Source | Type | Amount | Deadline | Status |
|--------|------|--------|----------|--------|
| Solana Frontier | Hackathon | $230K+ | May 11 | 🟡 Register |
| Avalanche Retro9000 | Grant | $75K | Jul 14 | 🟡 Planning |
| **Beam Foundation** | **Grant** | **TBD** | **Rolling** | **🟢 Apply** |
| Arc Hackathon | Hackathon | $10K, nanopayments | Apr 20-26 | 🟢 Active |
| ETHGlobal Open Agents | Hackathon | $50K | May 3 | 🟡 Register |

**Beam Notes:**
- Avalanche subnet, EVM-compatible
- Looking for: DeFi, AI, infrastructure protocols
- Currently overwhelmed with "AI slop" applications
- Real working product = competitive advantage
- Apply: grants.onbeam.com/apply

---
*Created: April 18, 2026*
*Last updated: April 18, 2026*


## Bin-AMM Development (April 19, 2026)

### Scoping Complete
- Dmob completed 1,200-line scoping doc on forking Trader Joe's LFJ Liquidity Book
- Jordan: "This is what sets us apart from everyone"
- **Core Differentiator:** Bin-level liquidity density lets agents algorithmically reshape exposure curves per-bin
- Protocol fees feed into burn floor → deflationary token mechanics
- Uniswap v2/v3/Curve can't do independent bin weighting

### Status
- Scoping: ✅ Complete
- Solidity implementation: 🔄 Dmob reviewing
- Dynamic burn rate: ✅ Approved (performance-weighted, scales with revenue)
- Implementation: 🔄 Dmob working on Solidity

### Strategic Importance
- This is the technical moat for the agent economy
- Agents can dynamically adjust liquidity curves based on market conditions
- Revenue from protocol fees feeds directly into token burn
- Positions Gentech as AMM innovator, not just another fork
