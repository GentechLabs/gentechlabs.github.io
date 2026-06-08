# AgentEscrow Architecture — Modular 5-Layer Stack

**Date:** 2026-04-18
**Source:** Jordan (voice, HQ)

## The Vision

AgentEscrow is NOT one product — it's a protocol stack. Base application with ~5 layers. Chain-specific parts get swapped per deployment (Solana ≠ AVAX). Individual layers can become standalone products.

## Architecture (Draft)

```
┌─────────────────────────────┐
│  Layer 5: UI / Frontend     │  ← can be standalone
├─────────────────────────────┤
│  Layer 4: Agent Logic       │  ← chain-agnostic brain
├─────────────────────────────┤
│  Layer 3: Escrow Engine     │  ← can be standalone
├─────────────────────────────┤
│  Layer 2: Chain Adapter     │  ← SOL / AVAX / ETH swap
├─────────────────────────────┤
│  Layer 1: Base Protocol     │  ← universal foundation
└─────────────────────────────┘
```

## Strategic Implications

1. **Build once, submit everywhere** — swap chain adapter → resubmit to different hackathon
2. **Layers become products** — individual layers can be standalone grant submissions
3. **Compounding code** — every hackathon improves the core
4. **Investor story** — "protocol stack, not single product"

## Hackathon Mapping

| Hackathon | Chain | Adapter | Deadline |
|-----------|-------|---------|----------|
| Frontier/Colosseum | Solana | SOL adapter | May 11 |
| ARC Hackathon | Avalanche | AVAX adapter | TBD |
| Kite AI | TBD | TBD | Apr 26 |
| Superteam Grant | Solana | Full platform pitch | May 4 |
| Bags Demo Day | Any (needs token) | TBD | Early next week |

## Next Steps

- [ ] Define the 5 layers precisely
- [ ] Identify which layers are chain-specific vs chain-agnostic
- [ ] Map each layer to potential standalone grant submissions
- [ ] Start with Solana adapter for Frontier
