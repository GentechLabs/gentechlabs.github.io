# Agora Agents — Adaptive Portfolio Manager

**RFB 04** | Agora Agents Hackathon (Canteen × Circle × Arc)
**Deadline:** May 25, 2026
**Prize:** $50K total — 1st $10K, 2nd $7.5K × 2, 3rd $5K × 3

## What We're Building

An AI-driven portfolio manager that autonomously rebalances positions based on market regime detection. The agent monitors on-chain data, classifies market conditions (bull/bear/range/volatile), and executes rebalancing trades on Arc using Circle's USDC infrastructure.

**Core loop:**
1. Monitor → On-chain price/volume data from DEX pools
2. Classify → Regime detection (6 regimes: bull, bear, range, volatile, accumulation, discovery)
3. Decide → AI agent determines optimal allocation per regime
4. Execute → Rebalance via Circle Gateway + CCTP for cross-chain USDC

## Tech Stack

| Layer | Tech | Why |
|-------|------|-----|
| Chain | Arc (Circle L1) | Sub-second finality, $0.01 tx fees in USDC |
| Settlement | USDC native | No volatile gas, instant settlement |
| Cross-chain | CCTP | Move USDC across chains for multi-venue arb |
| Wallets | Circle Wallets | Embedded secure wallets for agents |
| Fees | Paymaster | TX fees in USDC (no ETH/AVAX needed) |
| Yield | USYC | Tokenized money market fund on idle capital |
| Agent | Python + OpenRouter | Regime classification + portfolio decisions |
| UI | Next.js | Dashboard + portfolio overview |

## Project Structure

```
Agora-Agents/
├── contracts/          # Solidity (Foundry)
│   ├── src/
│   │   ├── PortfolioManager.sol    # Core portfolio contract
│   │   ├── RegimeOracle.sol        # On-chain regime feed
│   │   └── Rebalancer.sol          # Automated rebalancing logic
│   ├── test/
│   └── script/
├── agent/              # Python AI agent
│   ├── regime_classifier.py        # Ported from LP Monitor
│   ├── portfolio_optimizer.py      # Allocation engine
│   ├── circle_client.py            # Circle SDK wrapper
│   └── main.py                     # Agent entry point
├── ui/                 # Next.js dashboard
└── docs/               # Submission writeup, demo script
```

## Existing Assets (Reused)

| Asset | Source | Adaptation |
|-------|--------|------------|
| Regime classifier | LP Monitor (`regime_classifier.py`) | Generalize from AVAX to multi-asset |
| Position health logic | LP Monitor (`lp-aae-signal-monitor.py`) | Extend to portfolio-level |
| AgentEscrow pattern | Kite AI deployment | Port Solidity to Arc |
| x402 payments | Canteen workshop reference | Agent-to-agent settlement |

## Circle Tools Usage (20% judging weight)

- **Gateway**: Unified USDC balance for agent treasury
- **CCTP**: Cross-chain USDC moves for multi-venue positioning
- **Wallets**: Secure embedded wallet for autonomous agent
- **Paymaster**: USDC-denominated tx fees
- **USYC**: Yield on idle stablecoin allocation

## Judging Criteria Alignment

| Criterion | Weight | Our Angle |
|-----------|--------|-----------|
| Agentic Sophistication | 30% | AI decides allocation, timing, regime response — not just rebalance on schedule |
| Traction | 30% | Real on-chain positions, demo with live USDC on Arc |
| Circle Tool Usage | 20% | 5/6 Circle tools integrated (Gateway, CCTP, Wallets, Paymaster, USYC) |
| Innovation | 20% | Regime-adaptive strategy that evolves with market conditions |

## Getting Started

```bash
# Install Arc CLI
uv tool install git+https://github.com/the-canteen-dev/ARC-cli

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Setup contracts
cd contracts
forge install

# Setup agent
cd ../agent
pip install -r requirements.txt

# Setup UI
cd ../ui
npm install
```

## Quick Links

- [Agora Agents Hub](https://agora.thecanteenapp.com/)
- [Arc Docs](https://docs.arc.network)
- [Circle Developer Platform](https://developers.circle.com)
- [Canteen Discord](https://discord.gg/TGnyfKh23V)
- [Arc Builder Discord](https://discord.com/invite/buildonarc)
