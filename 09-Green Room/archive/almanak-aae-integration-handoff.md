# Almanak × AAE Integration — Mess Hall Brief

**Date:** 2026-04-29
**Source:** Jordan flagged for cross-department discussion
**Status:** Open — awaiting team input

---

## Context

Almanak (github.com/almanak-co/sdk) is an open-source DeFi strategy framework:
- Python intent-based architecture (write strategies as classes with `decide()`)
- 12 chains including Avalanche, 20+ protocols (Uniswap V3, Aave V3, Morpho Blue, GMX V2, etc.)
- Non-custodial via Safe smart accounts
- Built-in backtesting engine, state management, AI agent mode
- Apache 2.0 license

Jordan sees this as the **execution layer** AAE has been missing.

## The Stack Vision

| Layer | Provider |
|-------|----------|
| Identity | Kite Passport |
| Payments | Ampersend + x402 |
| Marketplace | AAS |
| Execution | **Almanak SDK** (?) |
| Cloud | W3.CLOUD |

## Discussion Questions

### YoYo (Strategy)
1. Which existing AAE DeFi strategies could port to Almanak's framework?
2. Does their intent architecture support our D5 dynamic strategy engine vision?
3. What protocols from their 20+ catalog align with our AAE roadmap?
4. Competitive risk: does using Almanak lock us into their execution paradigm?

### DMOB (Tech)
1. Integration complexity: dependency vs fork vs wrapper?
2. How does Almanak's Safe-based custody interact with our existing AAE Solidity contracts?
3. Can we extend their intent compiler with custom AAE-specific intents?
4. What's the deployment path on Avalanche?

### Desmond (Positioning)
1. How do we message this? "Built on Almanak" vs "Powered by AAE"?
2. Does this strengthen or dilute the AAE brand narrative?
3. Content angle: "AAE agents now trade across 20+ protocols" — is this a launch moment?

## Decision Needed

Fork/customize vs build on top as dependency?
- Fork gives control but maintenance burden
- Dependency gives speed but less control

Timeline: Are we building this into the Solana Frontier submission, or is this a post-hackathon production play?

---

*Drop your analysis below. We'll consolidate and present to Jordan.*
