# Agentic Treasury — Yield Farm Command Center

## Vision
A unified dashboard + alert system that tracks every DeFi position across protocols and chains in one place. Same pattern as the LP monitor, but scaled.

**Core thesis:** ARC as home base. Everything in USDC — gas, LP deposits, fees, rebalances. One currency, one pool of capital, the AI agent handles all the chain math.

## ARC Home Base — Single-Currency Operations

The fundamental insight: **gas tokens are friction**. Every chain has its own native token for fees (AVAX, SOL, ETH, BNB). Every time you want to move capital, you need to swap into the right gas token first. That's mental overhead and failed transactions.

**ARC fixes this:**
- Deposit USDC once → that's your gas budget, LP capital, and fee pool
- ARC bridges to Avalanche, Solana, Base, wherever the yield is
- No token swapping for fees — the single biggest UX friction in DeFi, eliminated
- The AI agent calculates everything: "To deploy $X into this pool, we need $Y for the position and $Z for gas, all in USDC"

**The agent's job:**
1. Know your total USDC pool across all chains
2. Before any deployment, calculate exact amounts: position size + gas + buffer
3. Simulate the transaction on-chain before you sign
4. Execute with the corrected parameters
5. Report: "Deployed $X into LFJ AVAX/USDC. Gas cost: $0.02. Remaining USDC: $W."

## Architecture

### 1. Unified Config (`agentic-treasury.json`)
Single source of truth for all positions. Each entry has:
- Protocol, chain, pool/contract address
- Shape (for LP), strategy label
- Entry price / APY target
- Alert thresholds

### 2. On-Chain Readers (one per protocol)
| Protocol | Status | What it reads |
|----------|--------|---------------|
| LFJ V2.2 | ✅ Done | Range, bins, active price, balances |
| Uniswap V3 | 📝 Template | NFT manager → tick range, liquidity |
| Aave / Morpho | 📝 Planned | supply balance, APY, borrow rate |
| Balancer | 📝 Planned | pool ID, weights, LP value |

### 3. LP Monitor (existing, proven)
- Reads config → fetches live data → calculates efficiency, IL, fees
- Debounce rules: 2x/hour normal, immediate on out-of-range or low efficiency
- Quiet hours: 11 PM – 6 AM ET

### 4. Command Center Dashboard
- GitHub Pages frontend (same pattern as existing hub)
- One card per position: range, efficiency, APY, IL, next action
- Cron updates data every cycle

### 5. Alerts (same debounce pattern)
- Out of range → immediate
- APY drops below target → alert
- Compound ready → notification
- DCA day → notification

## Next Steps
1. Build the unified config file
2. Add Aave/Morpho reader
3. Wire into the existing LP monitor cron
4. Build the dashboard frontend
