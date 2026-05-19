# GenLayer Recon

## Overview
Research into GenLayer SDK, Intelligent Contracts, and potential integration with AgentEscrow/Kite layers.

## Key Resources
- **Docs**: https://docs.genlayer.com/
- **Studio**: https://studio.genlayer.com/contracts
- **GitHub**: https://github.com/genlayerlabs
- **Boilerplate**: genlayer-project-boilerplate (10.7k stars)

## SDK Stack
| Repo | Language | Stars | Purpose |
|------|----------|-------|---------|
| genlayer-js | TypeScript | 50 | Frontend/DApp interaction |
| genlayer-py | Python | 32 | Server-side SDK |
| genlayer-studio | Python | 120 | Local testing sandbox |
| genvm | Rust | 16 | WASM-based VM for contracts |
| genlayer-docs | MDX | 35 | Documentation |

## Key Findings
- Contracts written in Python, run on GenVM (WASM)
- Native LLM integration + web access (no oracles needed)
- Consensus: Optimistic Democracy with AI validators
- **No "agent skills marketplace" for revenue sharing**
- Revenue model: deploy contracts → earn fees OR run validator → earn staking rewards
- Studio limitations (as of Apr 2026): no token transfers, no contract-to-contract, no gas

## Related Research
- Beams (Push Protocol) — also investigated as infra play

## Strategy: Modular Hackathon System

We pick the best SDK/platform for each layer — no single-vendor lock-in. Hackathon submissions are modular composites:

| Kite Layer | Best Tool | Why |
|---|---|---|
| **L5 Marketplace + Escrow** | GenLayer (Python) | On-chain settlement, native AI dispute resolution |
| **L4 Enforcement/SLAs** | GenLayer (Python) | Subjective consensus — "did the agent deliver?" |
| **L3 Brain/Memory** | Beam Cloud | Stateful bots, fast GPU, real-time learning |
| **L2 Risk Intel** | Beam Cloud | Fast inference, sandboxed execution |
| **L1 Fee/LP** | AVAX (Solidity) | Chain ownership, x402, ERC-8004 agent identity |

**Hackathon approach:** Build L4+L5 on GenLayer (fastest demo path), wire L3+L2 to Beam, frame L1 as future roadmap. Each hackathon gets a different modular combo — we adapt to the sponsor's stack.

## Status
- [x] Initial SDK recon (YoYo)
- [x] Dmob brief drafted + routed to Labs (Apr 19)
- [x] SDK comparison created — "eat the meat, spit the bones"
- [x] GenLayer vs Beam layer mapping complete
- [x] Modular strategy approved: best tool per layer, adapt per hackathon
- [x] Dmob action plan routed (Apr 19)
- [ ] Dmob scaffolds Python contract (L4/L5 on GenLayer)
- [ ] Deploy to Bradbury testnet
- [ ] Grant application drafted
- [ ] Beam SDK recon for L3/L2 layers

## Notes
- Beams (Push Protocol) also in scope — separate infra play (notifications vs. consensus)
- GenLayer × Kite fit: L5 (escrow/dispute) = strongest, L4 (SLAs) = strong
