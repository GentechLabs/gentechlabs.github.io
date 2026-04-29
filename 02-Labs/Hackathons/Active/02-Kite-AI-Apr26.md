# 🏆 Kite AI Global Hackathon

**Status:** ✅ BUILDING  
**Deadline:** May 17, 2026 (extended from May 11)  
**Prize:** $10,000  
**Chain:** Kite AI  
**Theme:** Agentic Commerce — the **agent labor market** landing on Kite AI

## What We're Submitting

The AAE Economy on Kite AI — trained agents earning REP, getting hired via AAS, and settling on Kite AI via x402 + USDC.

**"Everyone else sells you a hammer. We sell you the carpenter."**

### One agent lifecycle (the demo):
1. Agent trains in AAE simulation → earns REP
2. Client discovers agent via Agent Portal (AG)
3. Client hires agent via Agent as a Service (AAS)
4. Agent executes task, settles on Kite AI (x402)
5. REP updated on-chain, fee flows to $TECH buyback

### Why Kite AI wins by hosting this:
Kite becomes the **settlement layer for the agent labor market**. Not just another chain running escrow — the chain where AI labor gets paid.

## Key Deliverables

| Item | Status | Notes |
|------|--------|-------|
| AgentEscrow.sol (238 lines) | ✅ Deploy-ready | ReentrancyGuard + CEI fixes applied |
| TECHPaymentRouter.sol (161 lines) | ✅ Deploy-ready | Dual burn/treasury router |
| MockTECH.sol (19 lines) | ✅ Testnet token | Unrestricted mint for testing |
| Deploy.s.sol | ✅ Kite testnet | Chain ID 2368 |
| foundry.toml | ✅ Configured | Kite RPC + explorer |
| Security audit | ✅ M-1, M-2 fixed | DMOB audit: 4/5 rating |
| Tests | ✅ 58/58 passing | AgentEscrow + TECHPaymentRouter + MockTECH |
| Submission README | ✅ Created | Full hackathon writeup |
| Kite Passport deep dive | ✅ Updated | Strategic context added |

## Remaining

- [ ] Deploy to Kite testnet (DMOB)
- [ ] Record demo video (DMOB)
- [ ] Social media thread (Desmond)
- [ ] Final submission polish

## AAS + AG: The Unfair Advantage

> "Everyone else sells you a hammer. We sell you the carpenter."

- AAS = Deployed agents as a service (rep → performance fee)
- AG = Live social feed (copy traders, see real-time P&L)
- Built on top of the AAE progression layer (learn → simulate → earn REP → deploy)
- This is an actual labor market — not just automation, but *skill-based delegation*
- No competition has this layer — it's the exit ramp from learning to earning

## Tokenomics (Draft)

- Gateway Fee (10%) → $TECH burn
- Performance Fee (20%) → $TECH mixed
- Subscriptions ($5-$20/mo) → $TECH utility
- Copy Fee (2%) → $TECH burn
- Data Licensing → $TECH utility

## Unique Market Position

- We're the only platform where agents earn **reputation** in simulation, then **real capital** in production
- Network effects in the leaderboard → users join to emulate top agents
- Rep as a barrier to entry — we inherit gamified onboarding

## GitHub

- ProtoJay4789/kite-agent-commerce (canonical)

## Strategic Context

**Why Kite AI is the right play:**
- Avalanche has NO competition in AI payments — Kite is the first L1 purpose-built for agentic commerce
  - No other chain has native agent identity + settlement primitives
  - First-mover advantage on AVAX = massive ecosystem leverage
- Kite Passport (identity layer) maps directly to our AgentEscrow scope model
- x402 + USDC on Kite = the standard for how agents pay for services
- **"Everyone else sells you a hammer. We sell you the carpenter."** — Kite is where carpenters get paid

**See also:**
- `[[Kite-Passport-Technical-Deep-Dive]]` — hackathon-focused identity layer breakdown
- `[[ai-agent-payments-landscape]]` — competitive landscape (Solana vs Avalanche)
- `[[Audit-KiteAI-kite-agent-commerce-2026-04-28]]` — security audit results

## Notes

- 19 days from Apr 28
- Dmob owns the code
- YoYo owns research/strategy
