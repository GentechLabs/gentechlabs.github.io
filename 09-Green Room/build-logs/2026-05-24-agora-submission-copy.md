# AdaptiveFolio — Agora Agents Submission Copy

Ready to paste into the submission form.

---

## Problem Statement

Portfolio management requires constant rebalancing, regime detection, and cross-chain coordination — tasks that are tedious for humans and impossible to do 24/7. Most DeFi users either hold static positions (missing yield and alpha) or manually rebalance (time-consuming, emotional, error-prone). The problem is that markets shift between risk-on, risk-off, and sideways regimes, and each regime demands a different allocation strategy. Humans can't monitor this continuously, and existing tools don't adapt automatically. AdaptiveFolio solves this by using AI to detect market regimes in real-time and rebalance portfolios autonomously, settled on Arc with USDC for instant, low-cost execution.

## Project Description

AdaptiveFolio is an AI-powered adaptive portfolio manager that detects market regimes and automatically rebalances across multiple assets using USDC settled on Arc (Circle's stablecoin-native L1).

**How it works:**
- **Regime Detection:** Multi-signal analysis (momentum, trend, volume conviction, correlation) via CoinGecko data identifies whether the market is risk-on, risk-off, or sideways
- **Goal-Based Allocation:** Three portfolio profiles (conservative, moderate, aggressive) with automatic drift detection
- **Autonomous Rebalancing:** When portfolio drift exceeds threshold, the agent generates rebalance actions — no manual intervention needed
- **Arc Settlement:** All transactions settle on Arc with USDC as the native gas token — sub-second finality, ~$0.01 per tx, no token approvals required

**Tech stack:** Python (FastAPI), CoinGecko API, Arc testnet, web3.py, vanilla JS frontend

**Key differentiator:** Arc makes USDC the native gas token. This means rebalancing doesn't require separate gas tokens or token approvals — the agent can move USDC directly, making autonomous portfolio management practical at scale.

## Traction

- **38 unit tests passing** — regime detection, portfolio analysis, agent orchestration, settlement, tax-loss harvesting
- **Live demo deployed** at protojay4789.github.io/adaptive-folio — self-contained HTML/CSS/JS, works on mobile
- **Open source** on GitHub (ProtoJay4789/adaptive-folio)
- **Built in 2 days** for the Agora Agents Hackathon

*(Note: Add any social metrics here — RTs, follows, stars, Discord members, etc.)*

## Video Script Notes

The video should show:
1. Landing page with regime detection panel
2. Real-time market data updating (CoinGecko)
3. Allocation shifting between risk-on/risk-off
4. Drift detection triggering rebalance
5. Arc settlement configuration
6. Mobile demo

Target: 2:30–3:00 minutes, screen recording + voiceover
