# Unichain Treasury — Grant Build (#37)

Port of the Agentic Treasury / GTA **asset-management layer** to Unichain —
the deployable proof for the Uniswap Foundation grant ("Innovation upon the
DeFi Experience" bucket explicitly covers **treasury & asset management**).

## Why this exists

The grant's win condition is *deploy on Unichain*, not just apply. This module
is the working, live-tested core that a future deployment (LP position /
lending allocation) would build on. It reads **real Unichain state** — not a
fork, not simulated data.

## Components

| File | Purpose |
|------|---------|
| `unichain_pool_reader.py` | Read live Uniswap v3 pool state from Unichain RPC (sqrtPriceX96 → price, tick, fee, tokens). Read-only, no keys. |
| `unichain_allocator.py` | Regime-driven stablecoin deployment recommendation (LP / lending / hold) with gas-aware minimum-deployment guard. Advisory only — moves nothing. |
| `test_unichain_treasury.py` | 9 tests (pytest + plain python). All pass. |

## Live verification (Aug 20, 2026)

```
$ python3 unichain_pool_reader.py
chain_id: 130  chain: unichain
pool: 0x65081cb48d74a32e9ccfed75164b8c09972dbcf1   (USDC/WETH 0.05%)
price: 0.00044456 WETH-per-USDC  (~$2,250 / ETH)
tick: 199135  fee: 500

$ python3 unichain_allocator.py RANGE_BOUND 2500 balanced
UNICHAIN TREASURY ALLOCATOR
  Regime: RANGE_BOUND | Risk: balanced | Idle USDC: $2500.00
  Uniswap v3 USDC/WETH LP   45%
  Morpho / Aave on Unichain 35%
  Idle USDC (native)        20%
  ✅ Action: DEPLOY  (live pool price $0.000444)
```

`9/9 tests passed in 0.46s` (pytest).

## Verified addresses (Unichain mainnet, chainId 130)

- Uniswap v3 Factory: `0x1f98400000000000000000000000000000000003`
- USDC: `0x078d782b760474a361dda0af3839290b0ef57ad6`
- WETH: `0x4200000000000000000000000000000000000006`
- USDC/WETH 0.05% pool: `0x65081cb48d74a32e9ccfed75164b8c09972dbcf1`

## Status & next steps

- [x] Live Unichain RPC reader (verified against real pool)
- [x] Allocation engine port (regime → LP/lending/hold, gas-aware)
- [x] Test suite (9/9 pass)
- [ ] Deploy a real LP position / lending allocation on Unichain (needs capital + gas)
- [ ] Wire settlement via x402 gateway (full rail)
- [ ] README/demo + submit via Unichain grant form
  `share.hsforms.com/18Kv3hTvDSt-x1wK9va0OYwsdca9`
- [ ] Nominate for Retro Grant once there's traction

**Blockers:** deployment of an actual position is gated on capital being
available on Unichain (wallet currently flat per treasury). The read/decision
layer is live and proven; the onchain write step awaits funding.
