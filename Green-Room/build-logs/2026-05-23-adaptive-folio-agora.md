# AdaptiveFolio — Agora Agents Hackathon Build Log

**Date**: May 23, 2026
**Hackathon**: Agora Agents (Canteen × Circle) — $50K prize pool
**Deadline**: May 25, 2026
**RFB**: RFB 04 — Adaptive Portfolio Manager

## What Was Built

AdaptiveFolio is an AI-powered portfolio manager that detects market regimes and automatically rebalances across multiple assets using USDC settled on Arc (Circle's stablecoin-native EVM L1).

### Architecture
- `regime.py` — Multi-signal market regime detection (momentum, trend, volume, correlation) via CoinGecko
- `portfolio.py` — Goal-based allocation (conservative/moderate/aggressive) with drift detection
- `agent.py` — AI agent orchestration (analyze → decide → rebalance cycle)
- `settlement.py` — Arc testnet USDC settlement (native value transfers, ~$0.01/tx)
- `api.py` — FastAPI dashboard with embedded HTML/CSS/JS frontend
- `docs/index.html` — Standalone static demo for GitHub Pages

### What Shipped This Session
1. **38 passing tests** — Regime detection (9), portfolio analysis (9), agent orchestration (7), settlement (7), tax-loss harvest (3), allocation profiles (6)
2. **Arc native USDC fix** — Settlement rewritten from ERC-20 transfer calls to plain value transfers (Arc makes USDC the native gas token)
3. **.env.example** — Setup documentation for reviewers
4. **GitHub Pages deployment** — Live static demo at protojay4789.github.io/adaptive-folio
5. **README polish** — Full docs with architecture, allocation tables, API endpoints

### Key Decision: Arc Native USDC
Arc testnet makes USDC the native gas token (like ETH on Ethereum). The original settlement code used ERC-20 `transfer()` calls — rewritten to use plain value transfers with `web3.eth.send_transaction()`. This is a meaningful differentiator: no token approval needed, sub-second finality.

### Live Demo
- **URL**: https://protojay4789.github.io/adaptive-folio/
- Self-contained HTML/CSS/JS, no backend needed
- Real-time CoinGecko market data
- Same regime detection logic as Python backend
- Works on mobile

## Status
- ✅ Build complete
- ✅ Tests passing (38/38)
- ✅ Live demo deployed
- ✅ README polished
- ⏳ Needs Jordan to submit (deadline May 25)

## Next Steps (Post-Submission)
- Real Arc testnet wallet integration (faucet: https://faucet.circle.com)
- Agent-to-agent payment flow (Canteen x402 pattern)
- Historical regime backtesting
- Multi-chain port (Mantle, Arbitrum)
