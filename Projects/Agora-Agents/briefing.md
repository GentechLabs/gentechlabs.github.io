# Agora Agents — Adaptive Portfolio Manager

**Status:** 🟢 Registered, researching
**Hackathon:** Canteen × Circle × Arc
**Deadline:** May 25, 2026
**Prize:** $50K total (1st $10K, 2nd $7.5K×2, 3rd $5K×3, Standout $650-750×10-12)

## Target: RFB 04 — Adaptive Portfolio Manager

**Why:** LP Monitor is 80% of this. Regime detection + position tracking + portfolio health already built.

## Judging Criteria
- 30% Agentic Sophistication
- 30% Traction (real users, transactions, volume)
- 20% Circle tool usage
- 20% Innovation

## Tech Stack (Arc/Circle)
- Arc L1 — USDC native gas, sub-second finality, ~$0.01/tx
- CCTP — Cross-chain USDC transfers
- Gateway — Unified balance across chains, Nanopayments
- Wallets — Embedded secure wallets for agents
- Paymaster — TX fees in USDC
- App Kit — Bridge, Swap, Send, Unified Balance components

## ⚠️ Arc Gotchas
- USDC has TWO interfaces: native (18 decimals) + ERC-20 (6 decimals)
- Same underlying balance — never mix raw values
- `block.prevrandao` always 0 — no on-chain randomness
- Arc is testnet only currently
- Gas Station available, Paymaster NOT on Arc yet

## Competitive Landscape — WIDE OPEN
- Zero repos building Adaptive Portfolio Manager on Arc
- Closest competitor: RavnAgent (Zerion-based, no Arc focus)
- All hackathon repos are ★0

## Cross-Chain Reuse
| Asset | Reuse | Adaptation |
|-------|-------|------------|
| LP Monitor | RFB 04 | Strip Telegram/cron, add Circle tools |
| AgentEscrow.sol | Direct port | Solidity works on EVM |
| DeFi milestone tracker | RFB 01/05 | Add perp/arb logic |

## Getting Started
1. Install ARC CLI: `uv tool install git+https://github.com/the-canteen-dev/ARC-cli`
2. Join Canteen Discord: https://discord.gg/TGnyfKh23V
3. Join Arc builder Discord: https://discord.com/invite/buildonarc (mention "Canteen + Agora")
4. Docs: https://arc-node.thecanteenapp.com/
5. Faucet: https://faucet.circle.com
