---
name: genlayer-ecosystem
description: Research summary and dev reference for GenLayer Labs ecosystem
category: research
created: 2026-04-21
updated: 2026-04-23
---
# GenLayer Ecosystem Overview

## What is GenLayer?
AI research lab building \"Intelligent Contracts\" — contracts that can read real-world data and make subjective judgments. Positions itself as \"Trust Infrastructure for the AI Age.\"

- **Website:** https://genlayer.com
- **Docs:** https://docs.genlayer.com
- **GitHub:** https://github.com/genlayerlabs (76 repos, 4 people)
- **Twitter:** @GenLayer
- **Discord:** discord.gg/genlayerlabs
- **Email:** info@genlayerlabs.com

## Core Technology

### Intelligent Contracts
- Contracts that process natural language, read web data, and make AI-mediated decisions
- Run on **genvm** — a WASM-based VM (Rust)
- Adjudication via \"Optimistic Democracy\" (validator consensus)

### Transport-Agnostic Bridge Architecture
- First transport: **LayerZero** (130+ chains, 130M+ messages, zero core protocol exploits claimed)
- Can swap to Hyperlane, Axelar, IBC
- Messages, not asset transfers — attack surface is different from bridge hacks

## Key GitHub Repos

| Repo | Stack | Description |
|------|-------|-------------|
| genvm | Rust | WASM VM for Intelligent Contracts |
| genlayer-studio | Python | Interactive sandbox (120★) |
| genlayer-cli | TypeScript (MIT) | CLI tool for deploy/interact/debug |
| genlayer-js | TypeScript | JavaScript SDK |
| genlayer-py | Python | Python SDK (PyPI: genlayer-py) |
| genlayer-docs | MDX | Documentation |
| genlayer-networks | — | Network configurations |
| skills | — | AI agent plugin system |

## AI Agent Skills System (skills.genlayer.com)
Plugin marketplace for AI coding agents. Install:
```
/plugin marketplace add genlayerlabs
/plugin install genlayer-dev@genlayerlabs
```

Available skills:
- **Write Contract** — Production-quality intelligent contracts with equivalence principle guidance
- **GenVM Lint** — Safety, correctness, SDK compliance validation
- **Direct Tests** — ~30ms in-memory tests, no server required
- **Integration Tests** — Full consensus validation against live environments
- **GenLayer CLI** — Deploy, interact, debug from terminal
- **Validator Node Setup** — Interactive wizard, bare Linux → running validator in 20-45 min
- **Validator Management** — Manage validators across testnets

Source: https://github.com/genlayerlabs/skills

## Notable Projects in Ecosystem

### AutoBounty (NEW - Apr 23)
- Self-executing marketplace for GitHub contributions.
- **Mechanism:** Agents verify PRs via GenLayer consensus $\rightarrow$ Funds release from **Avalanche (@avax)** escrow.
- **Value Prop:** Eliminates human middlemen in the bounty process.

### TreasuryPilot (NEW - Apr 23)
- Autonomous grant management system.
- **Mechanism:** Org defines its mission/constitution on-chain $\rightarrow$ AI evaluates grant proposals against this constitution.
- **Value Prop:** Enforces organizational rules automatically; supports auto-approval for small grants.

### BuildersClaw (@buildersclaw)
- AI agents compete in real hackathons.
- Ship code to public repos, compete for prizes.
- Results verified onchain via Optimistic Democracy.
- Announced Apr 20, 2026.

### Apolo (@_A_polo__)
- Trustless escrow for AI agents and SLA contracts.
- Flow: x402 $\rightarrow$ Apolo escrow $\rightarrow$ GenLayer adjudicates $\rightarrow$ BNB Chain settles.
- Funds lock automatically on 402.
- AI verifies SLA condition.
- Settlement executes without human approval.
- Live on BNB Mainnet.
- Built during GenLayer Builders Hackathon.

## Staking & Passive Income (Bradbury Testnet)

### Two Roles

| Role | Min Stake | Infrastructure | Rewards |
|------|-----------|-----------------|-------------------|
| Validator | 42,000 GEN | Must run node + LLM | 10% ops fee + stake rewards |
| Delegator | 42 GEN | None | ~90% of pro-rata rewards |

### Reward Sources
- Transaction fees (variable)
- Inflation: **15% APR starting, decays to 4% over time**

### Reward Distribution (per epoch)
- 75% $\rightarrow$ Stake pool (validators + delegators proportional to shares)
- 10% $\rightarrow$ Validator owners (ops fee, taken before distribution)
- 10% $\rightarrow$ Developers
- 5% $\rightarrow$ DeepThought AI-DAO reserve

### Key Mechanics
- **Epochs = 1 day.** Stakes activate after +2 epochs (epoch 0 exceptions apply).
- **Delegated Proof of Stake (DPoS):** Delegators increase validator's total stake, share rewards minus 10% fee.
- **Validator selection weighted by:** `Weight = (0.6 × Self_Stake + 0.4 × Delegated_Stake)^0.5` — square-root damping prevents whale dominance, smaller validators get better $/GEN efficiency.
- **Unbonding period:** 7 epochs (~7 days) for both validators and delegators.
- **Slashing:** Validators and their delegators get slashed for missing execution windows or supporting fraud. 24-hour governance delay on all slashing.
- **validatorPrime():** Permissionless call required every epoch to keep validator in selection pool. Caller gets 1% of any slashed amount as incentive.
- **Max 1,000 active validators** per epoch.
- **Shares vs Stake:** Shares are fixed (ownership claim). Stake grows with rewards via exchange rate: `stake_per_share = total_stake / total_shares`. Rewards auto-compound.

### Epoch 0 (Bootstrapping)
- No minimum stake to join.
- No transactions processed.
- Stakes activate in epoch 2 (epoch 1 skipped) IF minimums met.
- No validatorPrime() needed during epoch 0.

### Risk Factors
- **Testnet only** — no real GEN token price, APR is theoretical until mainnet.
- **LLM costs** — validators pay for API calls; revenue must cover costs.
- **Inflation-funded yield** — if tx volume is low, it's dilution not real yield.
- **Shared slashing risk** — delegators penalized for validator misbehavior.
- **7-day unbonding** = not instant liquidity.

### Scenario Analysis (Delegator APR)
| Scenario | APR | Driver |
|----------|-----|------------------------------------------------------------------------|
| Bull | 12-15% | High tx volume (prediction markets, dispute resolution) |
| Base | 5-8% | Moderate adoption, inflation + some fees |
| Bear | 2-4% | Low volume, mostly inflation-funded |

### Recommended Approach
- **Entry:** Delegator with minimal stake (42 GEN) — low barrier, truly passive.
- **Later:** Validator if GEN token has significant value AND LLM costs are covered by revenue.

## Gentech Strategic Relevance
1. **x402 integration** — We use Birdeye x402 API; Apolo shows the trustless escrow pattern.
2. **Multi-agent dev** — GenLayer's skills system validates our agent-first architecture.
3. **Hackathon opportunity** — BuildersClaw + GenLayer skills = autonomous agent competition.
4. **Delegator yield** — Passive income via DPoS staking (42 GEN min, ~90% of rewards, 15% APR starting).
5. **Bounty Hunting** — AutoBounty provides a programmatic way for agents to earn income by solving GitHub issues.

## Agentic Market (agentic.market)
Coinbase's x402 marketplace — the \"App Store\" for AI agent services.

- **URL:** https://agentic.market
- **Docs:** https://docs.cdp.coinbase.com/x402/welcome
- **Daily payment volume:** ~$424K (as of Apr 21, 2026)
- **Chain:** Base
- **Install:** `npx skills add coinbase/agentic-wallet-skills`

How it works:
- Every service is payable per-request via x402 in USDC.
- No API keys, no accounts, no subscriptions.
- Install Agentic Wallet skills $\rightarrow$ authenticate with email $\rightarrow$ call any service.
- Most services under $0.05 per call.

Listing a service:
- Any API supporting x402 is **automatically discoverable**.
- No platform fees, no minimums.
- Follow x402 integration guide: https://docs.cdp.coinbase.com/x402/quickstart-for-sellers

Note: Birdeye x402 API (which Gentech uses) does NOT appear in the marketplace search — may be listed under a different name or not yet registered.

## Assumptions & Caveats
- LayerZero has had reputational concerns (bridge hacks in broader ecosystem); GenLayer claims zero core exploits but relies on L0 as first transport.
- genlayer-project-boilerplate has 10.7k stars (likely botted — doesn't reflect real adoption).
- Token is **GEN** — testnet only (Bradbury Testnet, Chain ID 4221). Mainnet token economics not yet published.
- Small team (4 people on GitHub) — early stage risk.
