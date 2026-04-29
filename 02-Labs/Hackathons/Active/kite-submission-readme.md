# 🏆 Kite AI Global Hackathon — Submission

**Team:** GenTech  
**Project:** Agent Commerce Economy  
**Track:** Agentic Commerce  
**Deadline:** May 17, 2026  
**Repo:** [ProtoJay4789/kite-agent-commerce](https://github.com/ProtoJay4789/kite-agent-commerce)  
**Tests:** 58/58 ✅

---

## One-Liner

> **"Everyone else sells you a hammer. We sell you the carpenter."**

We built the agent labor market — trained agents earning reputation, getting hired via Agent-as-a-Service, and settling payments on Kite AI via x402 + USDC.

---

## What We Built

### The Problem

AI agents are already booking flights, spinning up compute, and executing API calls — but traditional auth systems are built for humans. There's no identity layer purpose-built for autonomous agents, and no settlement infrastructure for agent-to-agent commerce.

### The Solution

A full-stack agent economy on Kite AI:

1. **Agent Training** → Agents train in AAE simulation, earn REP (reputation score)
2. **Discovery** → Clients find agents via Agent Portal (live social feed, real-time P&L)
3. **Hiring** → Agent-as-a-Service (AAS) — rep-based pricing, performance fees
4. **Settlement** → x402 per-task payments on Kite AI (USDC)
5. **Tokenomics** → Fees flow to $TECH buyback + burn

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GEN TECH AGENT ECONOMY                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │   AAE    │───▶│   AAS    │───▶│    AG    │             │
│  │ Academy  │    │  Service │    │  Portal  │             │
│  │(Training)│    │ (Hiring) │    │ (Social) │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│       │              │               │                      │
│       ▼              ▼               ▼                      │
│  ┌──────────────────────────────────────────┐             │
│  │           KITE AI SETTLEMENT             │             │
│  │   AgentEscrow + x402 + USDC              │             │
│  └──────────────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Three-Layer Identity Model (Kite Passport)

| Layer | What It Is | Authority |
|-------|-----------|-----------|
| **User** | Wallet (root) | Never transacts directly — derives agent keys |
| **Agent** | Per-agent keypair | Executes within delegated scope |
| **Task** | Scoped credentials | Time-limited, service-specific |

This maps directly to our AgentEscrow architecture — escrow = User layer, agent key = Agent layer, x402 settlements = Task layer.

---

## Smart Contracts

### AgentEscrow.sol (238 lines)

AI-validated escrow for agent-to-service payments.

- **USDC + EIP-712 signatures** for secure, gasless approvals
- **AI_VALIDATOR** role — only authorized validators can release funds
- **Deadline support** — time-limited escrows with automatic refund
- **ReentrancyGuard** on all external calls
- **SafeERC20** for all token transfers

### TECHPaymentRouter.sol (161 lines)

Dual-payment router — splits $TECH between burn and treasury.

- **Configurable burn ratio** (default 50%)
- **Volume discounts** — tiered pricing based on usage
- **Treasury management** — owner can update recipient
- **Audit fixes applied** — ReentrancyGuard + CEI pattern

### MockTECH.sol (19 lines)

Testnet $TECH token with unrestricted mint for testing.

---

## Security Audit

**Auditor:** DMOB (Labs)  
**Rating:** ⭐⭐⭐⭐ (4/5)  
**Status:** All medium findings fixed

| Finding | Severity | Status |
|---------|----------|--------|
| M-1: ReentrancyGuard missing | MEDIUM | ✅ Fixed |
| M-2: CEI violation | MEDIUM | ✅ Fixed |
| L-1: No emergency pause | LOW | Accepted (hackathon scope) |
| L-2: No per-user limits | LOW | Accepted (hackathon scope) |
| L-3: Inconsistent errors | LOW | Accepted (hackathon scope) |

---

## Test Coverage

**Total:** 58/58 tests passing ✅

| Contract | Tests | Coverage |
|----------|-------|----------|
| AgentEscrow | 23 | All core functions |
| TECHPaymentRouter | 32 | All functions + fuzz |
| MockTECH | 3 | Mint + transfer |

---

## Why Kite AI?

### Zero Competition on Avalanche

While Solana's agent payments space is crowded (MCPay, Latinum, Corbits), Avalanche has **no competition**. Kite is the first L1 purpose-built for agentic commerce.

### Strategic Advantage

1. **Native identity primitives** — Kite Passport formalizes what we're building
2. **x402 settlement** — per-task payments without accounts
3. **First-mover leverage** — whoever ships best agent infrastructure on AVAX first captures the ecosystem
4. **Audit trail** — three-layer identity makes agent activity traceable

### Our Edge

| What We Have | What They Don't |
|--------------|-----------------|
| 58/58 tests passing | Most are demos/prototypes |
| Multi-agent coordination | Single-agent focus |
| REP + $TECH dual token | Just payments |
| Education layer (PGE Academy) | No learning path |
| Cross-chain (Solana + EVM + Kite) | Single chain |

---

## Demo Flow (5 minutes)

1. **Agent Training** → Watch agent learn in AAE simulation, earn REP
2. **Discovery** → Client browses Agent Portal, sees live P&L
3. **Hiring** → Client hires agent via AAS (REP-based pricing)
4. **Execution** → Agent completes task, triggers x402 settlement
5. **Settlement** → USDC flows through AgentEscrow, $TECH burns

---

## Tokenomics

| Fee | Rate | Flow |
|-----|------|------|
| Gateway Fee | 10% | $TECH burn |
| Performance Fee | 20% | $TECH mixed |
| Subscriptions | $5-$20/mo | $TECH utility |
| Copy Fee | 2% | $TECH burn |
| Data Licensing | — | $TECH utility |

---

## What's Next

- [ ] Deploy to Kite testnet (Chain ID 2368)
- [ ] Record demo video
- [ ] Finalize submission docs
- [ ] Social media thread on launch

---

## Links

- **GitHub:** [ProtoJay4789/kite-agent-commerce](https://github.com/ProtoJay4789/kite-agent-commerce)
- **Kite AI:** [kite.ai](https://kite.ai)
- **Avalanche Builder Hub:** [builders.avax.network](https://builders.avax.network)

---

*Built with ❤️ by GenTech — where AI agents earn, learn, and get hired.*

**"Everyone else sells you a hammer. We sell you the carpenter."**
