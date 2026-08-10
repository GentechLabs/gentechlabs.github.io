# Agent Kit — Built-in "Claim Evaluator" (Stack-vs-Crowd Layer)

**Source:** Jordan, Aug 10, 2026 — after doing the stack-vs-crowd exercise by hand on Tim
Warren's "crypto bottom" video. He proposed making it a **built-in Agent Kit layer** so
any kit user gets the layers + an evaluation of what they say, as a demo of our strengths.

## The product
The Agent Kit ships a **Claim Evaluator** — when an agent/user makes a market claim, the
kit runs it against its OWN data layers and returns a **"stack vs. crowd" divergence verdict**:
- what the claim says (the crowd)
- what the kit's layers say (our data)
- where they agree / diverge
- what the kit would do (action read)

This productizes the agent-sentiment / divergence index (the Layer-3 proprietary signal)
and embeds it in every kit install. It is a differentiated capability: the kit gives any
agent a built-in "second opinion" from real data layers.

## Where it fits (Agent Kit structure)
- `services/claim_evaluator.py` — MCP tool: `claim_evaluator.evaluate(claim, asset?)`
- `skills/claim-evaluation/SKILL.md` — teaches agents to use it
- Reuses existing data layers (same feeds used in the manual Aug 10 exercise):
  - Regime: `.clarity-mode-state.json` (YIELD/RANGE_BOUND/HOLD, conf 0.65)
  - Narrative rotation: `narrative-rotation.py` (DeFi warm, RWA/gaming cooling)
  - Arb basis: `.gta-arb-state.json` (LINK hottest +12.4 bps)
  - Price trend: CoinGecko 30d (BTC flat, ETH +3.3%)

## Tool shape
```
claim_evaluator.evaluate(claim="crypto bottom is in", asset="BTC")
  → pulls kit's regime / narrative / arb / price for the asset
  → diff claim vs layers
  → verdict: AGREE / DIVERGE / CONFIRMED / CONTRADICT
  → action read: HOLD / ACCUM / DEFENSIVE / TRADE
  → returns the layer values so the user SEES the stack (demo value)
```

## Example output (from the Aug 10 manual run)
```
CROWD CLAIM: "Smart money bottom signal — bottom is in" (Tim Warren)
KIT LAYERS:
  Regime: YIELD / RANGE_BOUND / HOLD, conf 0.65   → NOT a bottom-confirm
  Narrative: DeFi warm, RWA/gaming cooling          → sectoral, not market-wide
  Arb basis: LINK +12.4bps (hottest)                → rotation, not bottom
  BTC 30d: flat ($63.9k)                            → range
VERDICT: DIVERGE — macro agrees (Japan/ETF/whales real) but conclusion is ahead of our data.
ACTION: HOLD. Do NOT chase bottom-call. Watch regime flip → ACCUM, LINK as rotation lead.
```

## Build steps (when greenlit)
1. `services/claim_evaluator.py` — read the 4 feeds, diff claim, emit verdict JSON
2. Register as MCP tool in the kit server
3. `skills/claim-evaluation/SKILL.md` — usage + decision rules
4. Wire into kit version bump (0.4.0 → 0.5.0)
5. Demo it on a live claim (Tim Warren video) for the README

## Status
🅿️ PARKED — spec captured. Jordan to greenlight build.
