# LayerZero DVN Security Analysis

**Date**: 2026-04-21  \
**Status**: In Progress  \
**Trigger**: KelpDAO exploit linked to DVN misconfiguration

---

## Context
LayerZero's security model is **configurable** — each OApp/ONFT chooses its own DVN (Decentralized Verifier Network) setup. This is a double-edged sword: flexibility for apps, but also a massive footgun.

## Key Concern: 47% 1-of-1 DVN
- Dune analytics showed ~47% of cross-chain messages use a **1-of-1 DVN** configuration
- 1-of-1 = single point of failure. If that one verifier is compromised, messages can be forged
- KelpDAO exploit confirmed tied to their DVN config

## Risk Assessment

| DVN Config | Security Level | Use Case |
|-----------|---------------|----------|
| 1-of-1 | ⛔ Dangerous | Dev/test only |
| 2-of-3 | ⚠️ Moderate | Low-value transfers |
| 3-of-5+ | ✅ Good | Production DeFi |
| LayerZero default (with Chainlink) | ✅ Strong | Recommended baseline |

## Chainlink as DVN
- LayerZero can use **Chainlink as a DVN** alongside other verifiers
- This is the strongest configuration available
- Aligns with Jordan's Chainlink preference + Cyfrin coursework
- Chainlink CCIP is an **alternative** to LayerZero entirely — evaluate both

## Action Items
- [ ] Map which GenTech contracts use LayerZero (if any)
- [ ] Check DVN config for any deployed OApps
- [ ] Determine if Chainlink CCIP is sufficient for our cross-chain needs
- [ ] Review KelpDAO post-mortem for exact exploit vector
- [ ] Document Chainlink vs LayerZero decision framework

## References
- KelpDAO exploit post-mortem (TBD — find primary source)
- LayerZero DVN docs: https://docs.layerzero.network/v2/concepts
- Chainlink CCIP: https://docs.chain.link/ccip
