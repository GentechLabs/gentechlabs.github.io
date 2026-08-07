# Almanak SDK — Trader Joe V2 Price-Oracle Bug (Issue + Fix Draft)

**Status:** Staged — ready to submit once Jordan forks `almanak-co/sdk` (API fork blocked).
**Repo:** almanak-co/sdk (Apache-2.0)
**Found:** Aug 7, 2026 — live, while building the Agentic Treasury AVAX rail.

---

## 🐛 GitHub Issue Draft

**Title:** `fix: open_lp_position on Avalanche fails — WAVAX price resolved on arbitrum`

**Body:**

### Summary
`almanak ax run open_lp_position` on Avalanche fails to compile with:

```
No real prices available for lp_open compilation on mainnet. Could not extract
token symbols from intent to self-serve prices. Refusing to compile with
placeholder prices.
```

Root cause: the price oracle resolves WAVAX on **arbitrum** (the default chain)
instead of **avalanche**, so the mainnet price gate can't self-serve the price for
the pool's token0.

### Steps to reproduce
1. Configure `ALMANAK_PRIVATE_KEY` for an Avalanche wallet.
2. Run:
   ```
   almanak ax --dry-run run open_lp_position '{
     "chain": "avalanche",
     "protocol": "traderjoe_v2",
     "fee_tier": 500,
     "token_a": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
     "token_b": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
     "amount_a": "25.0", "amount_b": "3.866",
     "price_lower": "6.33", "price_upper": "6.60"
   }'
   ```
3. Observe the `No real prices available` error.

### Expected behavior
The price gate should resolve WAVAX on the intent's `chain` (avalanche), not the
default (arbitrum), so the LP entry compiles and simulates.

### Environment
- almanak 2.24.0
- Python 3.12
- Avalanche C-Chain mainnet

---

## 🔧 Fix Draft

**Location:** `almanak/gateway/services/execution_service.py` — `_fetch_prices_for_tokens`
and `_enforce_mainnet_price_gate`.

**Problem:** `_fetch_prices_for_tokens` calls `aggregator.get_aggregated_price(token, "USD")`
with a bare token symbol. The aggregator's token resolver falls back to the default
chain (arbitrum) for WAVAX, so the price lookup fails on avalanche.

**Fix:** Thread the intent's `chain` through to the price fetch so the resolver
honors the target chain. When the intent specifies `chain=avalanche`, resolve
WAVAX on avalanche (via the pool's on-chain price or the avalanche Chainlink feed)
instead of defaulting to arbitrum.

**Regression test:** Add a test that calls `open_lp_position` with `chain=avalanche`
and asserts the price gate self-serves WAVAX/USDC from the avalanche pool, not
arbitrum.

---

## Notes
- The pool is on-chain verified: LBPair `0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1`
  (WAVAX/USDC, binStep 20), active bin 8375815, price ~$6.466.
- Workaround (already built): direct LBRouter v2.1 call bypasses the broken oracle.
- Conventional commit: `fix:` prefix per CONTRIBUTING.md.
