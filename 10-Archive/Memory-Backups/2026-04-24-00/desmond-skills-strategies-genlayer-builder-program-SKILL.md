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

## Action Checklist
- [ ] Sign up at portal.genlayer.foundation (Jordan — when home)
- [ ] Get Vanito and Dadrian referral links (10% points forever)
- [ ] Submit IResolver spec as first contribution
- [ ] Deploy AgentEscrow-nu equivalent with superior architecture
- [ ] Write differentiation blog post

## Existing Specs Location
- IResolver Interface: `/root/vaults/gentech/09-Green Room/IResolver-interface-spec.md`
- IResolver Solidity: `/root/vaults/gentech/09-Green Room/IResolver.sol`
- AgentEscrow Vision: `/root/vaults/gentech/03-Strategies/AgentEscrow-Product-Vision.md`
- AgentEscrow README: `/root/vaults/gentech/06-Content/AgentEscrow-README.md`

## Pitfalls
- **Don't submit emark's work as ours** — their "Agent Escrow" Honorable Mention is a different project. Ours is "AgentEscrow" (one word, different architecture).
- **Points system is iterating** — the portal warns "YMMV" and bugs are expected. Submit early, submit often.
- **Contribution reviews are delayed** — all submissions are recorded but review takes time. Don't wait for approval before submitting more.