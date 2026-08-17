# Handoff → Treasury: Decision Guidance Layer (AgentLayer borrow)

**Date:** 2026-08-15
**From:** Gentech (HQ)
**To:** Treasury group

## What shipped
Patched the **Decision Guidance Layer** into the `defi-operations` skill (borrowed from
AgentLayer's Uniswap Liquidity skill, Aug 15). Every low-efficiency, out-of-range, or
rebalance recommendation must now include a plain-language "why" — the width/efficiency
trade-off, the narrow-range risk, and the fee-vs-IL framing BEFORE the move.

## Why it matters to Treasury
Turns LP alerts from "here's a number" into "here's the trade-off, here's why" — so the
Steward (autonomous mode) and Jordan (hybrid mode) decide with the reasoning visible,
not just the metric. This is the explain-before-decide layer that separates a guided
workflow from a raw alert.

## Borrow vs spit out
- **BORROW:** the explain-before-decide mechanism (fee-tier / range-width / capital-efficiency / IL framing)
- **SPIT OUT:** the tool itself — AgentLayer is Uniswap V3/V4; we're on Trader Joe/LFJ (Avalanche)

## Next
- LP monitor alerts should now carry the decision-guidance block.
- Verify on next low-efficiency / out-of-range trigger that the "why" renders correctly.
