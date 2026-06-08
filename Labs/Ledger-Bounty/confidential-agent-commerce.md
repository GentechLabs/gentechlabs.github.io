# Confidential Agent Commerce — Ledger Bounty Submission

**Date:** June 4, 2026
**Status:** Approved — Delegated to Labs
**Bounty:** Ledger Agent Stack Build & Show (college.xyz)
**Reward:** $100 + 5 random win Ledger device
**Deadline:** TBD (check college.xyz)

## Concept

Two agents transact privately. No one sees what they're trading, how much, or with whom. Ledger signs both sides. Identity is public, financial activity is private.

## The Stack

- **ERC-8004** — Agent identity (public: who they are)
- **Zcash shielded addresses** — Private transactions (hidden: what they do)
- **Ledger DMK** — Hardware security (provable: they approved it)
- **x402** — Micropayments (the actual commerce)

## The Demo Flow

1. Agent A generates a Zcash shielded address (private wallet)
2. Agent B generates a Zcash shielded address (private wallet)
3. Agent A lists a service (public: "I offer market analysis")
4. Agent B requests the service (public: "I need market analysis")
5. They negotiate via x402 (public: price agreed)
6. Payment happens via Zcash shielded transaction (private: amount hidden)
7. Ledger signs both transactions (hardware proof)
8. Service is delivered (public: "Analysis complete")

## Why This Steals the Show

- Every other submission will be basic DMK demos
- We're showing **agent-to-agent private commerce** — a working prototype of the future economy
- Narrative: "Your agent's financial activity should be as private as yours"

## Why This Is Useful for AAE

- This IS the privacy layer for AAE
- Agents can transact without revealing strategies to competitors
- Hardware-backed signatures prove legitimacy without revealing details
- Sets the standard for confidential agent commerce

## Pitch

> "In the agent economy, privacy isn't optional. We built confidential agent commerce — two agents transact using Zcash shielded addresses, signed by Ledger hardware. Public identity. Private activity. Provable security."

## Technical Requirements

- Ledger DMK (TypeScript SDK)
- Ledger Wallet CLI
- Zcash signer kit (`@ledgerhq/device-signer-kit-zcash`)
- Speculos emulator (for demo/testing)
- ERC-8004 identity integration
- x402 payment flow

## Build Plan

### Phase 1: Setup (2-3 hours)
- Install Ledger DMK + Wallet CLI
- Set up Speculos emulator
- Test Zcash signing flow

### Phase 2: Agent Identity (2-3 hours)
- Integrate ERC-8004 with Ledger
- Generate shielded addresses per agent
- Agent registration flow

### Phase 3: Commerce Flow (3-4 hours)
- x402 payment negotiation
- Zcash shielded transaction
- Ledger signing on both sides

### Phase 4: Demo + Polish (2-3 hours)
- Visual dashboard
- Demo video
- Documentation

**Total estimate:** 10-13 hours

## Success Criteria

- [ ] Two agents can transact privately
- [ ] Zcash shielded addresses used
- [ ] Ledger signs both transactions
- [ ] ERC-8004 identity visible (public)
- [ ] Transaction amount hidden (private)
- [ ] Demo video showing flow
- [ ] Submitted to college.xyz
