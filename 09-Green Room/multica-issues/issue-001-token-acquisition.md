# Multica Issue #1: AAE Token Acquisition Agent
**Assignee:** Desmond (Strategist)
**Priority:** P1
**Deadline:** May 30, 2026

## Objective
Build an automated token acquisition agent for Agent Arena (AAE) that manages:
- Daily DCA purchases of AVAX ($50/day)
- Limit orders for SOL when price drops below threshold
- USDC yield farming optimization

## Requirements
1. **DCA Engine**
   - Execute $50 AVAX purchase daily at 9:00 AM UTC
   - Use DexScreen or similar for price feeds
   - Log all transactions to vault

2. **Limit Orders**
   - Monitor SOL price
   - Trigger buy when SOL drops 10% from 7-day average
   - Maximum $500 per order

3. **Yield Farming**
   - Track USDC pools on Aave, Compound
   - Auto-rebalance for best APY
   - Minimum 5% APY threshold

## Skills Required
- crypto-price-fetch
- defi
- solana
- base

## Acceptance Criteria
- [ ] DCA engine executes daily without manual intervention
- [ ] Limit orders trigger within 5 minutes of price threshold
- [ ] Yield farming rebalances weekly
- [ ] All transactions logged to `02-Agent-Arena/token-acquisition-log.md`

## Notes
- Use OpenClaw Cash as primary wallet
- No mainnet integration without audit (per security rules)
- Start with testnet for first week
