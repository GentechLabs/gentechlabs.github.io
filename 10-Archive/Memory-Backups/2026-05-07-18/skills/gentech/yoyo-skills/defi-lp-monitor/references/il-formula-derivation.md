# Impermanent Loss — Constant Product AMM Derivation

## Formula

Given an LP position with initial token amounts A0 (token0) and B0 (token1) at price P0 (token1 per token0), after price moves to P1:

```
LP value  = 2 * sqrt(A0 * B0 * P1)
HODL value = A0 * P1 + B0
IL % = (LP value - HODL value) / HODL value * 100
```

Where:
- `sqrt` = square root
- Price ratio `r = P1 / P0`

Simplified IL formula in terms of `r`:
```
IL = (2 * sqrt(r) / (1 + r) - 1) * 100
```

## Why This Formula

Constant product AMM (Uniswap V2 style) maintains:
```
A * B = k (constant)
```

When price changes from P0 to P1:
- Token0 amount becomes `A = sqrt(A0 * B0 / P1)`
- Token1 amount becomes `B = sqrt(A0 * B0 * P1)`
- Total value in token1 terms: `A * P1 + B = 2 * sqrt(A0 * B0 * P1)`

HODL value is simply `A0 * P1 + B0`. The difference is impermanent loss.

## Example (from 2026-05-02 run)

Initial (May 3 vault entry):
- A0 = 11.64 AVAX
- B0 = 29.15 USDC
- P0 = $9.0860

Current:
- P1 = $9.1589

```
r = 9.1589 / 9.0860 = 1.008026
sqrt(r) = 1.004006

LP value = 2 * sqrt(11.64 * 29.15 * 9.1589)
         = 2 * sqrt(3391.56 * 9.1589)
         = 2 * sqrt(31070.6)
         = 2 * 176.28
         = $111.49

HODL = 11.64 * 9.1589 + 29.15 = $106.61 + $29.15 = $135.76

IL = (111.49 - 135.76) / 135.76 * 100
   = -17.87%
```

**Note**: Vault's May 3 entry reported IL +0.5% (likely vs. prior day only). This full position IL is vs. initial entry; both are valid but serve different purposes:
- **Daily IL** (vs. prior entry): measures recent divergence
- **Total IL** (vs. creation): measures overall position performance vs. HODL

For vault update reports, use **total IL vs. HODL** for accuracy.

## Edge Cases

- When `r = 1` (no price change), IL = 0%
- When `r → 0` or `r → ∞` (extreme move), IL → -100% (LP loses all value vs HODL)
- IL is always ≤ 0 for long-only positions in normal AMMs (you lose vs HODL when price moves away from entry)

## Sources

- Uniswap V2 whitepaper: Constant function market makers
- Yield Yak/LFJ: Built on Trader Joe V2-style concentrated liquidity with binning