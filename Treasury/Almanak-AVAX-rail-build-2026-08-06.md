# Almanak AVAX Rail — Build Progress (Aug 6, 2026)

**Decision (Jordan, Aug 6):** Almanak FULL — compose Safe + signer + TraderJoe, don't
build custody. Owner: The Steward (Agentic Treasury).

## ✅ VERIFIED — DATA SIDE OF THE RAIL IS LIVE
Almanak 2.24.0 gateway auto-starts on `127.0.0.1:50051` and returns REAL live data
on Avalanche with NO wallet configured:

- **AVAX price:** `6.4509 USD` (source: aggregated) — real-time, works.
- **TraderJoe AVAX/USDC pool:** `0xfae3f424a0a47706811521e3ee268f00cfb5c45e`
  - current_price `6.4559`, tick `-257674`, fee_tier `500` (0.05%)
  - token0 WAVAX (18dec), token1 USDC (6dec), sqrt_price_x96 live
  - **This is the exact V2 pool the Steward will manage.**

So the rail is functional for **data** (price, pool state, balances) with zero setup.

## ⏸ BLOCKER — EXECUTION needs a signer
`almanak ax swap USDC AVAX 1 --chain avalanche --dry-run` → `Simulation: ERROR`.
Root cause (confirmed): **no wallet/signer configured.** Two paths exist (from bundled docs):

| Path | Config keys | Custody | Effort |
|------|------------|---------|--------|
| **(a) Local EOA signer** | `ALMANAK_PRIVATE_KEY` (preferred local EOA signer) | Lighter — agent holds key | Low |
| **(b) Safe + Zodiac signer service** | `ALMANAK_GATEWAY_SAFE_ADDRESS`, `ALMANAK_GATEWAY_SAFE_MODE`, `ALMANAK_GATEWAY_SIGNER_SERVICE_URL`, `ALMANAK_GATEWAY_SIGNER_SERVICE_JWT`, `ALMANAK_GATEWAY_ZODIAC_ROLES_ADDRESS` | Institutional Safe | High |

Jordan chose **(b) Almanak FULL** (Safe + signer service) per the acquisition-rails doc.
That requires deploying/managing a Safe + Zodiac signer service — a real ops build.

## Env key map (discovered)
- `ALMANAK_PRIVATE_KEY` — preferred local EOA signer (path a)
- `ALMANAK_GATEWAY_PRIVATE_KEY` — gateway-side signer key
- `ALMANAK_GATEWAY_SAFE_MODE` / `_SAFE_ADDRESS` / `_ZODIAC_ROLES_ADDRESS` — Safe mode (path b)
- `ALMANAK_GATEWAY_SIGNER_SERVICE_URL` / `_JWT` — remote signer (zodiac)
- `ALMANAK_API_KEY` / `ALMANAK_DASHBOARD_API_KEY` — API auth
- `ALMANAK_RPC_URL` — RPC override
- `ALMANAK_GATEWAY_THEGRAPH_API_KEY` — pool-history provider (currently unset, falls back)

## Next
1. Decide signer path. Path (a) `ALMANAK_PRIVATE_KEY` would enable execution fastest
   (agent holds an Avalanche keypair directly — matches the "thin" custody posture we
   already use for Solana). Path (b) Safe is what Jordan greenlit but is a bigger build.
   **Recommend: validate execution on (a) first (easy→hard), keep (b) as the
   institutional end-state.**
2. Wire the chosen key + `ALMANAK_GATEWAY_CHAINS=avalanche`.
3. Scaffold `traderjoe_lp` strategy for the AVAX/USDC V2 pool.
4. Dry-run verify the acquisition leg end-to-end.
