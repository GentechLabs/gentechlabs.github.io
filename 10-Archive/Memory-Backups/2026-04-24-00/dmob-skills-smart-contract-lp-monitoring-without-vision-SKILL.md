---
name: lp-monitoring-without-vision
description: Workflow for monitoring Liquidity Provider (LP) positions and ranges when the vision_analyze tool is unstable or unavailable.
---

# LP Monitoring Without Vision

## Trigger
When the `vision_analyze` tool fails (e.g., 404 model not found) or when monitoring LP positions for a cron job where accuracy and reliability are prioritized over UI screenshots.

## Workflow

### 1. Data Extraction
Instead of relying on screenshots, extract the following critical identifiers from the user's provided images or text:
- **Pool Address**: The contract address of the LP pool (e.g., `0x864...16EA`).
- **Token Pair**: The assets involved (e.g., AVAX/USDC).
- **Pool Version**: The version of the DEX (e.g., TraderJoe v2.2, PancakeSwap v3).
- **Target Range**: The specific Min/Max price boundaries requested by the user.

### 2. API Transition
Shift the monitoring logic from "Visual Analysis" $\rightarrow$ "API Retrieval":
- **DexScreener API**: Use for real-time price, volume, and liquidity checks.
- **DEX-Specific APIs (LFI/TraderJoe/Uniswap)**: Use for position-specific data (if available) or to verify pool technicals.
- **On-Chain Calls**: Use `cast` or a Python script to query the pool contract for `slot0` (current price) and `liquidity`.

### 3. Cron Integration
Update the monitoring script (e.g., `crypto-watchlist.py`) to include:
- **Price Tracking**: Compare the live price against the target range.
- **Yield Calculation**: Estimate daily rewards based on pool volume and position size to track against the user's daily income goal (e.g., $500/day).
- **Status Alerts**: Trigger a notification if the price exits the target range.

## Pitfalls
- **Blind Spots**: Without vision, you cannot see "UI-only" data (like specific reward accumulation if not available via API). Request a text dump or CSV export from the user as a fallback.
- **Model Failures**: Do not repeatedly call `vision_analyze` if it returns a 404; immediately pivot to the API-first approach.

## Verification
- Verify the pool address matches the screenshot.
- Ensure the API-reported price matches the "Current Price" listed in the last known screenshot.
