---
name: genlayer-builder-program
description: Strategy for participating in GenLayer's Incentivized Builder Program — earning points, differentiating AgentEscrow, and leveraging existing specs for contributions.
version: 1.0
---

# GenLayer Incentivized Builder Program

## Portal
- **URL:** https://portal.genlayer.foundation/
- **How it works:** Submit contributions (builds, content, community) → earn Builder Points (BP)
- **Referral:** 10% of referred friends' points FOREVER — get collaborators signed up under your link ASAP
- **Stats:** 12.6K builders, 16.8K contributions, 932K total points (as of Apr 2026)

## Competition Landscape
- Someone named **emark** already won 🏅 Honorable Mention with "Agent Escrow" at the Bradbury Hackathon
- Their version is at https://agentescrow-nu.vercel.app/
- This VALIDATES the concept — our version is architecturally superior

## Key Differentiators vs. emark's Agent Escrow

| Feature | emark's Version | **Our AgentEscrow** |
|---------|-----------------|---------------------|
| Architecture | Likely monolithic | **IResolver interface — swappable, composable** |
| Dispute Resolution | Single-tier | **Two-tier escalation: Human → GenLayer AI consensus** |
| Payment | Standard escrow | **x402 native (HTTP 402 "Payment Required")** |
| Multi-chain | Single chain | **Solana primary, Avalanche secondary, modular bridge** |
| Agent Intelligence | Static contract | **Multi-agent handoff chain** (Risk → LP → Vault Agent) |
| Revenue Model | Flat fee | **Dual pricing: USDC base + $TECH AI upgrades** |
| Social Layer | None | **Arena — compete, showcase, verify agent performance** |

## Pitch Tagline
**"Swap the chain, keep the agent."**

## Contribution Strategy (What to Submit)

### Immediate (Low-hanging fruit)
1. **IResolver Interface Spec** — Already written, in `09-Green Room/IResolver-interface-spec.md`. This is a *reference implementation* for GenLayer integration patterns. Submit as a Developer Docs contribution.
2. **GenLayerOracleResolver Spec** — Tier 2 resolver that posts disputes to GenLayer's Intelligent Contract. Submit as a Smart Contract contribution.
3. **Escalation Model** — Human → AI consensus escalation. This is a GenLayer showcase use case.

### Short-term (Build out)
4. **Deploy AgentEscrow to GenLayer testnet** — Working demo with our IResolver pattern
5. **Comparison blog post** — "Why AgentEscrow's IResolver Makes It the GenLayer Standard"
6. **Arena concept on GenLayer** — Subjective consensus for agent performance verification

### Team Contributions (Multi-department)
- **DMOB**: Smart contract code, IResolver implementation, GenLayer integration
- **YoYo**: Research papers, tokenomics models, competitive analysis
- **Desmond**: Blog posts, social content, documentation, video walkthroughs

## 5. Passive Income / Delegation (Apr 2026 Update)

| Metric | Value |
|--------|-------|
| Minimum stake | 42 GEN |
| Base APR | ~15% (inflation-based) |
| APR trajectory | Declining to ~4% over time |
| Validator cut | 10% |
| **Effective APR** | **~13.5%** |
| Unbonding period | 7 epochs (~7 days) |
| Risk | Slashing if validator misbehaves |
| Infrastructure | None required |
| Compound | Auto-compounding (set-and-forget) |

### Validator Path
| Metric | Value |
|--------|-------|
| Minimum | 42,000 GEN |
| Reward premium | 10% |
| Infrastructure | Must run own node |

## 6. Cross-Department Gentech Operations (Jordan Directive)

### Investment (YoYo)
- Target 42 GEN delegation for baseline passive yield.
- Farm Builder Points on testnet for speculative airdrop.
- Monitor 42k GEN threshold for eventual validator scaling.

### Development (DMOB)
- **Primary showcase:** Deploy AgentEscrow as builder-leaderboard vehicle.
- Optimize Intelligent Contract performance on Bradbury testnet.
- Integrate AI Oracle into GenLayer contracts for differentiation.

### Creative (Desmond)
- **Narrative:** "Premier GenLayer Builder" via case studies (AgentEscrow + AI Oracle synergy).
- Content series: "Intelligent Contracts" → socials for ecosystem attention.
- Hackathon submission drafts where GenLayer is the protocol sponsor.

## Action Checklist
- [ ] Sign up at portal.genlayer.foundation (Jordan — when home)
- [ ] Get Vanito and Dadrian referral links (10% points forever)
- [ ] Submit IResolver spec as first contribution
- [ ] Deploy AgentEscrow-nu equivalent with superior architecture
- [ ] Write differentiation blog post
- [ ] Confirm 42 GEN delegation amount + wallet setup (YoYo)
- [ ] Deploy first Intelligent Contract on Bradbury (DMOB)
- [ ] Draft "Gentech x GenLayer" brand narrative (Desmond)
- [ ] Sync builder points dashboard to weekly digest (YoYo)

## Existing Specs Location
- IResolver Interface: `/root/vaults/gentech/09-Green Room/IResolver-interface-spec.md`
- IResolver Solidity: `/root/vaults/gentech/09-Green Room/IResolver.sol`
- AgentEscrow Vision: `/root/vaults/gentech/03-Strategies/AgentEscrow-Product-Vision.md`
- AgentEscrow README: `/root/vaults/gentech/06-Content/AgentEscrow-README.md`

## Pitfalls
- **Don't submit emark's work as ours** — their "Agent Escrow" Honorable Mention is a different project. Ours is "AgentEscrow" (one word, different architecture).
- **Points system is iterating** — the portal warns "YMMV" and bugs are expected. Submit early, submit often.
- **Contribution reviews are delayed** — all submissions are recorded but review takes time. Don't wait for approval before submitting more.