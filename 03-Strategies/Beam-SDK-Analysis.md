# Beam SDK (onbeam.com) — Integration Analysis
**Date:** 2026-04-21
**Author:** YoYo (Strategies)
**Status:** Research Complete → Awaiting Jordan's Direction

---

## What Beam Actually Is

**Beam** (onbeam.com) is an **Avalanche subnet** — a dedicated EVM-compatible blockchain. NOT the same as "Teleport Beams" (infrastructure agent runtimes).

### Chain Specs
| Property | Value |
|----------|-------|
| Chain ID | 4337 (0x10f1) |
| RPC | https://build.onbeam.com/rpc |
| WebSocket | wss://build.onbeam.com/ws |
| Currency | BEAM (native gas token) |
| Finality | ~1 second |
| TPS | Up to 4,500 |
| Tx Fees | Sub $0.10 |
| EVM | Fully compatible — standard Solidity/Foundry works |
| Consensus | PoA + Snowman (Avalanche protocol) |
| Testnet | Fuji available |
| Explorer | https://subnets.avax.network/beam |
| GitHub | https://github.com/BuildOnBeam/beam-docs |

### Ecosystem Focus
- Gaming (primary — 1.5M+ gamers)
- DeFi (Beam Swap, Bridge)
- AI/Compute ($40M Tactical Compute initiative with Aethir)
- Consumer apps
- NFT marketplace (Sphere)

---

## BeamSDK Architecture

The SDK has **two services** designed for different use cases:

### 1. Player Service (Self-Custodial)
For user-facing applications. Players control their own keys.
- **Users** — Connect wallet, self-custody
- **Operations** — Transaction lifecycle management
- **Sessions** — Sign once, operate without repeated approvals
- **Transactions** — Sponsored, self-paid, custom charges
- **Assets** — In-game asset management (read/write)
- **Marketplace** — List, buy, offers
- **Exchange** — Token conversion via liquidity pools
- **Webhooks** — Event notifications

### 2. Automation Service (Custodial/Backend)
For server-side automation — **most relevant to us.**
- **Profiles** — Smart contract accounts for automated asset management
  - Match profiles, Minting profiles, Treasury profiles
- **Policies** — Access control rules for what automation can do
- **Trading** — Secure asset/token transfers between profiles
- Uses Secret API key for authentication

---

## Fit With Our Current Stack

### ✅ Direct Alignment Points

| Our Component | Beam Equivalent | Integration Opportunity |
|---------------|-----------------|------------------------|
| AgentEscrow (Solidity) | EVM chain | Deploy directly — zero code changes needed |
| x402 nanopayments | Sub-$0.10 fees | Fee structure viable for micro-tx patterns |
| $TECH token economy | Beam Exchange SDK | Built-in liquidity pool token swaps |
| REP (soulbound) | NFT/asset system | Mint via Beam's asset management |
| Policy-based access | Beam Policies SDK | Declarative access control for agents |
| Automation profiles | Our agent wallets | Smart contract accounts per agent |

### 🔑 Killer Feature: Automation Service

The Automation Service is the highest-value integration:

1. **Profiles = Agent Wallets** — Each of our agents (YoYo, DMOB, Desmond) could have a Beam Profile as their on-chain identity
2. **Policies = Spending Rules** — Declarative rules like "YoYo can spend up to $X on Y per day"
3. **Trading = Agent-to-Agent Payments** — Built-in secure transfers between profiles
4. **Sponsored Transactions** — We pay gas, users don't need BEAM tokens

### 💡 Strategic Positioning

**Beam is an Avalanche subnet.** Our chain priority is Solana → AVAX → Arbitrum. This puts Beam squarely in our #2 priority lane.

**Grants available:** grants.onbeam.com — already in our Hackathon tracker under "Beam Grants — AVAX subnet — Real products get funded"

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Gaming-focused ecosystem — agentic commerce is a stretch | Medium | Position AI compute angle (Tactical Compute initiative shows intent) |
| PoA consensus — not fully decentralized yet | Low | Developer preview mode, will evolve |
| SDK is TypeScript/Unity/Unreal focused | Medium | Can use raw RPC + Foundry for smart contracts, SDK for automation layer |
| Small ecosystem compared to mainline AVAX | Medium | But grant program is specifically funding real projects |
| Beam token required for gas | Low | Sub-$0.10 fees, bridge available |

---

## Recommended Next Steps (3 Scenarios)

### Scenario A: Quick Deploy (Low Effort, 1-2 days)
Deploy existing AgentEscrow contract to Beam testnet using Foundry.
- **Pros:** Tests the waters, zero SDK dependency, proves EVM compatibility
- **Cons:** No SDK features, just another chain deployment
- **Effort:** ~2 hours (add Beam RPC to foundry.toml, deploy)

### Scenario B: SDK Integration (Medium Effort, 1 week)
Build a Beam Automation Service integration for our agents.
- **Pros:** Leverages Profile/Policy/Trading system, grant-worthy
- **Cons:** TypeScript SDK learning curve, need to test thoroughly
- **Use case:** Each agent gets a Profile, policies enforce spending limits, Trading handles agent-to-agent payments

### Scenario C: Full Beam Migration (High Effort, 2-4 weeks)
Port AgentEscrow + x402 to Beam as primary AVAX deployment.
- **Pros:** Aligns with AVAX priority, grant-eligible, built-in infra
- **Cons:** Distracts from ARC/Kite deadlines, may be premature
- **Recommendation:** Only after ARC ships (Apr 25)

---

## My Recommendation

**Go with Scenario A now → Scenario B after ARC ships.**

Rationale:
1. Deploy AgentEscrow to Beam testnet TODAY (2 hours, $0 cost, proves compatibility)
2. After ARC deadline (Apr 25), start Automation Service integration
3. Apply for Beam Grants with the working integration as proof
4. This gives us a third chain deployment (Arc + Kite + Beam) for the "build once, submit everywhere" strategy

The Beam SDK's Automation Service maps almost 1:1 to our agent wallet concept. Policies = spending guardrails, Profiles = agent identities, Trading = inter-agent payments. It's infrastructure we'd need to build anyway — Beam gives it to us for free.

---

## Key URLs
- Chain docs: https://docs.onbeam.com/chain
- SDK docs: https://docs.onbeam.com/sdk
- Automation Service: https://docs.onbeam.com/sdk/automation-service/automation-introduction
- Grants: https://grants.onbeam.com
- Explorer: https://subnets.avax.network/beam
- GitHub: https://github.com/BuildOnBeam/beam-subnet
- Discord: https://discord.gg/beamcommunity

---

#beam #avalanche #sdk #strategy #agent:yoyo
