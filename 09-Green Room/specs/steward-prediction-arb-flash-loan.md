# The Steward — Prediction-Arb Rail + Agentic Flash-Loan Layer

**Date:** 2026-08-22
**Status:** 🟢 Jordan GREEN LIGHT. Phase 1 (prediction rail) building now. Phase 2 (flash-loan executor) deferred until funded + Phase 1 proves an edge.
**Naming:** "The Steward" (Agentic Treasury). GTA = earlier working name.

## The thesis — "The One Paperclip, for agents"
Kyle MacDonald traded a red paperclip up to a house. The Steward trades a mispriced signal up to a treasury. Agents don't get bored, emotional, or quit on drawdown — they keep finding the next edge and compounding the spread every cycle. **Start from a few dollars of edge, reinvest the spread, let the loop run.**

## Why this fits the Steward
- The Steward is undercapitalized today — flash loans let it **start from nothing** and arbitrage without standing capital.
- Prediction markets price the SAME event on different venues. If Polymarket and Kalshi disagree on e.g. "Bitcoin above $70K," that's an atomic arb: borrow → buy cheap side → sell expensive side → repay → keep the spread.
- This is the machine-money loop: **consume intelligence → route to a prediction-market rail → execute autonomously → auto-settle.**

## Agentic flash loans — NOT how devs do it
Not a hand-written Uniswap flash-loan contract. This is the **agentic** version (from the Agent Arena scored-leverage spec, Aug 4):
- Agent opens a **credit line** underwritten by its credit score (`agent-credit-score`, 0-850, 22/22 tests).
- **Borrow → trade (arb) → repay**, atomic.
- **Revenue Router** (borrowed from Krexa, Aug 4): every PnL services debt automatically (fixed % first), agent keeps the rest, score rises with good repayment → more credit → the loop feeds itself.

## Phased sequencing
### Phase 1 — Prediction rail (BUILD NOW, dry-run, no live orders)
- `steward_prediction.py`: pulls Polymarket (Gamma + CLOB) + Kalshi (trade-api) market data.
- Cross-venue arb edge detector: same event priced differently across Polymarket/Kalshi → flag the spread.
- Writes state file (`.steward-prediction.json`) → feeds the fused Steward report as a "🎯 Prediction" producer block.
- **Data is keyless** (Gamma 200, Kalshi markets 200) — build + test with zero capital.

### Phase 2 — Agentic arb + flash-loan executor (DEFERRED, armed once funded)
- Execute the detected edge atomically via flash-loan borrow → trade → repay.
- Wired into the Steward's existing decision layer (not a separate cron).
- Requires: funded Polymarket wallet + EVM private key (never main wallet) + Kalshi trading auth.

## The arbitration edge (Jordan: "I like the arbitration idea")
Cross-venue same-event arb is the **cleanest** flash-loan use: no directional bet, just capture the spread as prices converge. Two sources of edge:
1. **Intra-venue:** Polymarket YES vs NO prices summing to != 1 (arbitrageable).
2. **Cross-venue:** Polymarket vs Kalshi disagree on the same event.

## Dependencies / verified
- Polymarket Gamma API (`gamma-api.polymarket.com/public-search`) — HTTP 200, keyless.
- Polymarket CLOB (`clob.polymarket.com`) — HTTP 200 (trading needs wallet).
- `py-clob-client` v0.34.6 on PyPI — installs clean.
- Kalshi trade-api (`api.elections.kalshi.com/trade-api/v2/markets`) — HTTP 200, keyless; trading needs auth (401 without).
- `kalshi-python` v2.1.4 on PyPI.

## Reference (cloned)
- `/root/telegraph-usecases/telegraph-supersignal/` — the Polymarket "sniper bot" pattern (signal→match→decide→execute), studied as the execution template.

## Files
- Spec: `09-Green Room/specs/steward-prediction-arb-flash-loan.md`
- Rail assessment: `10-Labs/telegraph-miners/PREDICTION-MARKET-RAIL-ASSESSMENT.md`
- Build target (Phase 1): `Treasury/scripts/steward_prediction.py`

## Action items
- [ ] Build `steward_prediction.py` (Phase 1 dry-run, no live orders)
- [ ] Wire "🎯 Prediction" block into fused Steward report (handoff to Treasury)
- [ ] Defer Phase 2 flash-loan executor until funded + edge proven
- [ ] Post prediction-rail progress on X (feeds Telegraph #49 + Treasury narrative)
