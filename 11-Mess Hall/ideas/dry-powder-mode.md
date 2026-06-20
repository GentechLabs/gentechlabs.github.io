# Dry Powder Mode — AAE Stop-Loss Feature

**Date:** 2026-06-19
**Source:** Jordan (voice message)
**Category:** AAE Feature / DeFi

## The Idea

When a major crash is detected (geopolitical event, market-wide selloff, etc.), the AAE agent should automatically:

1. **Detect the crash signal** — price dropping X% in Y minutes, or external trigger (Iran headlines, etc.)
2. **Pull liquidity from yield farms** — withdraw from LFJ/Trader Joe/etc. before impermanent loss gets worse
3. **Convert to stablecoins** — swap everything to USDC/USDT and enter "dry powder mode"
4. **Wait for recovery signal** — sit in stables until conditions improve, then redeploy

## Why This Matters

- Currently: Jordan manually rebalances during crashes (like today's Iran dump)
- Problem: Can't watch markets during 12hr Amazon shifts
- Solution: Agent auto-protects capital when Jordan can't

## Implementation Notes

- Could be a toggle in the AAE config: `"dry_powder_mode": true/false`
- Agent monitors price action + external signals (news sentiment, funding rates)
- When triggered: auto-withdraw → swap to stables → log action → notify Jordan
- Recovery: agent watches for bottom signals (RSI oversold, volume spike, news cooldown) before re-entering

## Prior Art

- We discussed stop-loss agent in the brain before (pre-June 2026)
- This is the "Co-Pilot Principle" in action — agent auto-executes when configured, user decides when in advisory mode
