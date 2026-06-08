# Arc Hackathon — Agent Escrow & x402 Plan

## Overview
- **Event**: Arc (ongoing program, not time-boxed hackathon)
- **Focus**: x402 payment protocol, escrow, ERC-8004 agent identity
- **Repo**: `~/repos/arc-hackathon/`
- **Status**: AgentEscrow.sol written, needs expansion

## AAE Layer: Foundation — Agent Marketplace + Escrow

### What It Does
The economic foundation for the agent economy:
- Agent-to-agent payments via escrow
- x402 HTTP payment protocol integration
- ERC-8004 agent identity standard
- Dispute resolution and reputation

### Why Arc
- x402 = HTTP 402 "Payment Required" → machine-native payments
- ERC-8004 = on-chain agent identity (what AAE AgentRegistry already implements)
- Escrow is the trust layer — no agent economy without it

---

## Architecture

```
┌─────────────────────────────────────────────┐
│          AgentEscrow.sol (existing)          │
│  create() / accept() / complete() / dispute()│
│  AVAX-native escrow payments                 │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          x402PaymentHandler.sol (new)        │
│  HTTP 402 payment verification               │
│  Sign → verify → release                     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          AgentRegistry.sol (existing, AAE)   │
│  ERC-8004 identity + reputation              │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          DisputeResolver.sol (new)           │
│  Arbitration logic for contested jobs        │
└─────────────────────────────────────────────┘
```

---

## Contract Status

| Contract | Status | Action Needed |
|---|---|---|
| `AgentEscrow.sol` | ✅ Written | Audit + expand lifecycle |
| `x402PaymentHandler.sol` | ❌ Not started | New — HTTP 402 payment flow |
| `DisputeResolver.sol` | ❌ Not started | New — arbitration logic |

---

## Timeline

### Phase 1: Audit Existing (Apr 19-25)
- [ ] Security audit of AgentEscrow.sol
- [ ] Test suite expansion
- [ ] Document current state

### Phase 2: x402 Integration (Apr 26 - May 15)
- [ ] Research x402 protocol spec
- [ ] x402PaymentHandler.sol — sign/verify/release
- [ ] Integration tests

### Phase 3: Dispute Resolution (May 16-31)
- [ ] DisputeResolver.sol
- [ ] Multi-sig arbitration pattern
- [ ] Reputation-weighted voting

### Phase 4: Polish (Jun 1-15)
- [ ] End-to-end integration
- [ ] Deploy to Avalanche C-Chain
- [ ] Documentation

---

## Connection to AAE
This is the **economic bedrock** — every other layer depends on escrow:
- Layer 1 (LP): agents earn fees → escrowed until performance confirmed
- Layer 2 (Risk): risk alerts → trigger escrow actions (pause/release)
- Layer 3 (Brain): learned outcomes → reputation updates in escrow
- Layer 4 (Social): reputation scores → dispute resolution weighting
- Layer 5 (Coord): agents hiring agents → escrow between agents

---

## Tags
#Arc #x402 #ERC8004 #escrow #hackathon #plan #AAE-foundation
