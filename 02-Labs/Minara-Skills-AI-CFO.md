# Minara Skills — AI CFO for Agents
**Date:** 2026-04-25
**Source:** https://x.com/i/status/2047753073506877863 → https://github.com/Minara-AI/skills
**Author:** Tom Dörr (@tom_doerr) / Minara AI
**License:** MIT
**Stars:** 220 | **Forks:** 24 | **Commits:** 89
**Updated:** 2026-04-25 (re-shared in HQ)

## What It Is
Minara Skills turns your AI agent into a **personal AI CFO**. It provides a unified skill set for analyzing and trading crypto, US stocks, commodities, forex, and more. Supports on-chain transactions, wallet management, and real-time market intelligence.

## Key Data
| Metric | Value |
|--------|-------|
| Stars | 219 |
| Forks | 24 |
| Commits | 89 |
| License | MIT |
| Benchmark | 88/100 (crypto-skill-bench v3.0.2, Claude Sonnet 4.6) |
| Safety gate | PASS |

## Supported Networks
Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, **Solana**, BSC, Berachain, Blast, Manta, Mode, Sonic, Conflux, Merlin, Monad, Polymarket, XLayer, and **Hyperliquid** (perps).

## Core Features
| Feature | Description |
|---------|-------------|
| Spot Trading | Buy, sell, swap, convert, transfer by ticker/token/contract |
| Perpetual Futures | Open/close positions, leverage, multi-wallet, trade history, AI autopilot (Hyperliquid) |
| Limit Orders | Create, list, cancel spot and perps limit orders |
| Wallet & Funds | Built-in wallet, balance, portfolio, deposit, withdrawals, MoonPay on-ramp |
| AI Insights | Real-time on-chain data, fundamentals, whale flows, trending tokens/stocks, equity research, commodities, forex |
| x402 Payment | Pay x402-enabled HTTP APIs directly from Minara wallet |
| Premium | Plans, credits, subscription management |

## Agent Support
| Platform | Status | Setup Script |
|----------|--------|--------------|
| Claude Code | ✅ Supported | `scripts/claudecode-minara-skill-setup.sh` |
| OpenClaw | ✅ Supported | `scripts/openclaw-minara-skill-setup.sh` |
| **Hermes** | ✅ Supported | `scripts/hermes-minara-skill-setup.sh` |

Recent commit: *"Implementing Hermes Agents support"* (2 weeks ago)

## Benchmark Breakdown
| Dimension | Score |
|-----------|-------|
| Safety | 91 |
| Coverage | 86 |
| Robustness | 88 |
| Routing | 88 |
| UX | 86 |
| **Total** | **88/100** |

66 passed, 10 partial, 0 failed. Safety gate: PASS.

## Relevance to GenTech
- **Direct Hermes integration:** They explicitly support Hermes agents — we should test this immediately
- **Our chains:** Base + Solana are core supported networks
- **Trading infrastructure:** Spot, perps, limit orders, AI autopilot — exactly YoYo's domain
- **x402 payments:** Aligned with our payment router thesis
- **MIT license:** Can fork, extend, or integrate freely
- **Competitive positioning:** Early mover in AI CFO space; 219 stars and growing

## Action Items
- [ ] Test Hermes setup script for compatibility
- [ ] Evaluate trading capabilities vs. YoYo's current LP/strategy stack
- [ ] Assess x402 integration with our $TECH payment router
- [ ] Determine if we should integrate, fork, or compete
- [ ] Check tokenomics / incentive model (if any)

## Tags
#ai-cfo #trading #hermes #crypto-skills #solana #base #hyperliquid #x402 #agent-integration
