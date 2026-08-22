# Unichain Treasury Port — SHIPPED (gentech → treasury)

**Date:** 2026-08-20 | **Build queue:** #58 (orig #37)
**Shipped by:** gentech

## What shipped

Port of the Agentic Treasury / GTA asset-management layer to **Unichain**
(chainId 130) — the deployable proof for the Uniswap Foundation grant
("Innovation upon the DeFi Experience" bucket = treasury & asset management).

Location: `10-Labs/unichain-treasury/`

| File | Purpose |
|------|---------|
| `unichain_pool_reader.py` | Live Uniswap v3 pool reader against Unichain RPC (sqrtPriceX96→price, tick, fee, tokens). Read-only, no keys. |
| `unichain_allocator.py` | Regime-driven stablecoin deployment recommendation (LP / lending / hold) with gas-aware min-deployment guard. Advisory only. |
| `test_unichain_treasury.py` | 9 tests — **all pass** (pytest + plain python). |
| `README.md` | Setup, live verification, verified addresses, next steps. |

## Live verification (real Unichain mainnet)

```
$ python3 unichain_pool_reader.py
chain_id: 130  chain: unichain
pool: 0x65081cb48d74a32e9ccfed75164b8c09972dbcf1  (USDC/WETH 0.05%)
price: 0.00044456 WETH-per-USDC (~$2,250/ETH), tick 199135, fee 500

$ python3 unichain_allocator.py RANGE_BOUND 2500 balanced
✅ Action: DEPLOY  (live pool price $0.000444)
  LP 45% / lending 35% / hold 20%
```

`9/9 tests passed in 0.46s` (pytest).

## Verified addresses (Unichain mainnet)

- V3 Factory: `0x1f98400000000000000000000000000000000003`
- USDC: `0x078d782b760474a361dda0af3839290b0ef57ad6`
- WETH: `0x4200000000000000000000000000000000000006`
- USDC/WETH 0.05% pool: `0x65081cb48d74a32e9ccfed75164b8c09972dbcf1`

## Blockers (for Jordan / treasury)

- **Actual onchain deployment is gated on capital on Unichain** (wallet flat
  per treasury — ~$1.88 baseline). The read/decision layer is live and proven;
  the LP/lending write step awaits funding.
- When funded: deploy USDC to the v3 pool or a lending venue, then wire
  settlement via the x402 gateway (full rail) per build plan Phase 2.
- Application form: `share.hsforms.com/18Kv3hTvDSt-x1wK9va0OYwsdca9`

## Also resolved this session

- **Fixed pre-existing git merge conflict** in `scripts/build_queue.json`
  (unresolved interactive-rebase conflict → file was invalid JSON). Resolved by
  taking HEAD side of 12 conflict blocks; file now valid (58 items).
