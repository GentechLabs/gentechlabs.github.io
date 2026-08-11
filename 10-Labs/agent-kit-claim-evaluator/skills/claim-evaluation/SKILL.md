---
name: claim-evaluation
description: >
  Evaluate a market claim against the Agent Kit's four proprietary data
  layers (regime, narrative rotation, arb basis, price trend) and return a
  "stack vs. crowd" divergence verdict: AGREE / DIVERGE / CONFIRMED /
  CONTRADICT / UNKNOWN, plus an action read (HOLD / ACCUM / DEFENSIVE /
  TRADE / NEUTRAL).
tags: [verification, divergence, sentiment, agent-kit, aae]
---

# Claim Evaluation (Stack-vs-Crowd)

The kit's built-in **second opinion** layer. When a user or agent makes a
market claim, run it against our OWN data layers — not the crowd's — and
report where they agree or diverge.

## When to use

- A user says "bottom is in", "top is in", "X will pump", "crash coming".
- You need a data-backed verdict on any directional market claim.
- You want the *layer values surfaced* so the user sees the reasoning
  (the demo value), not just the answer.

## How to call

```python
from claim_evaluator import ClaimEvaluator

ev = ClaimEvaluator()
verdict = ev.evaluate("crypto bottom is in", "BTC")
# -> {verdict: DIVERGE, action: HOLD, confidence: 0.65,
#     layers: {regime: {...}, narrative: {...}, arb: {...}, price_trend: {...}}}
```

## Verdict meanings

| Verdict      | Meaning                                                       | Typical action |
|--------------|---------------------------------------------------------------|----------------|
| AGREE        | Claim direction matches a non-decisive data read              | HOLD / DEFENSIVE |
| CONFIRMED    | Claim direction matches a strong, decisive read (regime bull/bear) | ACCUM / TRADE |
| DIVERGE      | Claim is directional but data is flat/neutral — conclusion ahead of data | HOLD / DEFENSIVE |
| CONTRADICT   | Claim direction opposes the data                             | DEFENSIVE / HOLD |
| UNKNOWN      | No clear claim direction OR no data available                | NEUTRAL |

## Decision rules

1. **Regime is decisive.** If the regime rail reads bull/bear, that wins.
2. **No decisive regime** → gather narrative/arb/price; all matching = CONFIRMED
   (2+ rails) or AGREE (1 rail); any disagreement = DIVERGE.
3. **No data at all** → UNKNOWN, never guess.
4. **Stale feed** (rotation >7d) → confidence penalty, surfaced in the layer.

## Hard limits

- Claim text max 4096 chars — longer is rejected with a `ValueError`.
- Each rail fails independently; a broken feed degrades to `None`, never
  blocks the other rails (verified in the test suite).

## Demo script

```bash
python3 demo.py                      # BTC "bottom is in" (canonical example)
python3 demo.py "ETH breakout" ETH
```

## Audit posture

No hardcoded secrets. No error-detail leakage (`str(e)` never surfaces to
callers). No log injection (no f-string logging of user input). Input-length
bound enforced before regex. All per-rail reads wrapped in isolated try/except.
