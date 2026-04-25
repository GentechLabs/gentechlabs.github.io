# AAE Layer → Hackathon Master Plan

> 5 layers, 4 hackathons, 1 full stack by May 11
> **Updated 2026-04-19:** Mapped to new 8-layer Kite architecture. Old layer names below map as:
> Escrow → Foundation, Marketplace → L5, Brain → L1+L3, Social/Arena → L5, Enforcement → L6.
> New L7 (Transaction) and L8 (Lifecycle) are Phase 3 additions post-hackathons.

## The Stack

```
┌─────────────────────────────────────────────┐
│            AAE Premium Application           │
├─────────────────────────────────────────────┤
│  Social/Arena Layer ←── Frontier (May 11)   │
│  Brain Layer ←────────── Dev3pack (May 8)   │
│  Agent Marketplace ←──── Kite AI (Apr 26)   │
│  Escrow Layer ←────────── ARC (Apr 20)      │
│  Enforcement Layer ←──── Woven through ALL  │
└─────────────────────────────────────────────┘
         │              │
    Swap for EVM    Swap for Solana
   (Kite/Arbitrum)  (Dev3pack/Frontier)
```

## Timeline

| Date | Event | Layer | Prize | Owner |
|------|-------|-------|-------|-------|
| Apr 20-26 | ARC | Escrow | $10K | Dmob + Jordan |
| May 11 | Kite AI | Marketplace | — | Dmob + Jordan |
| ~~May 3~~ | ~~ETHGlobal Open Agents~~ | ~~L2+L3+L4+L5~~ | ~~$50K~~ | ~~DROPPED~~ |
| ~~May 8-10~~ | ~~Dev3pack~~ | ~~Brain~~ | ~~TBA~~ | ~~SKIPPED per Jordan directive~~ |
| May 11 | **Kite AI** | **Marketplace** | **—** | **Dmob + Jordan** |
| May 11 | Solana Frontier (main) | All layers | $230K+ | Full team |
| Jul 14 | Retro9000 | Full stack (AVAX) | $75K | Full team |

## Enforcement Layer — Cross-Cutting

Not a standalone submission. Embedded in every hackathon:
- **ARC:** Validator checks before releasing escrow funds
- **Kite AI:** Marketplace reputation slashing, quality disputes
- **Dev3pack:** Brain-layer risk detection, bad decision filtering
- **Frontier:** Arena performance penalties, auto-exit triggers

## Code Reuse

| Component | Solidity (EVM) | Anchor (Solana) |
|-----------|---------------|-----------------|
| Escrow | ✅ AgentEscrow.sol | 🔜 Rewrite |
| Registry | ✅ AgentRegistry.sol | 🔜 Rewrite |
| Marketplace | ✅ AgentMarketplace.sol | 🔜 Rewrite |
| Token | ✅ AgentToken.sol | 🔜 Rewrite |
| Brain | N/A (off-chain) | 🔜 New |
| Arena | N/A (off-chain) | 🔜 New |

## Funding Stack (if we win)

| Source | Amount | Probability |
|--------|--------|-------------|
| ARC | $10K | High (home game) |
| ETHGlobal Open Agents | $50K | Medium (good fit) |
| **Superteam Earn Sidetracks** | **$680K+** | **Medium (multiple submissions)** |
| Solana Frontier (main) | $230K+ | Medium (competition) |
| Frontier Accelerator | $250K pre-seed | If we win Frontier |
| Retro9000 | $75K | Medium (working product) |
| Beam Foundation | TBD | Medium (subnet play) |
| **Total potential** | **$1.285M+** | |

## Status Board

- [x] ARC — signed up, repo exists
- [x] Kite AI — registered, multi-SDK strategy (GenLayer L4+L5, Beam L3)
- [x] Dev3pack — SKIPPED per Jordan directive
- [ ] Surge Ignition Race — sign up, submit proof of work
- [ ] Solana Frontier — register
- [ ] Retro9000 — planning phase

## Modular Architecture Decision (Apr 19)

**Kite is NOT "pick one platform."** It's multi-SDK:

| Layer | SDK | Rationale |
|-------|-----|-----------|
| L1 AgentFi | Custom | DeFi routing — our core IP |
| L2 Risk Intel | Beam Cloud | Fast inference, real-time scoring |
| L3 Brain | Beam Cloud | Stateful memory, fast GPU |
| L4 Enforcement | GenLayer | Subjective AI consensus |
| L5 Escrow | GenLayer | On-chain settlement + disputes |
| L6 Orchestration | Beam Cloud | Multi-agent workflows |
| L7 Governance | Custom | Voting, treasury |

**Build each layer once. Assemble per hackathon like LEGO.**

---
*Created: Apr 18, 2026*
*Updated: Apr 18, 2026*
