# Monad Rail — Trader Joe Pools + Q402 (Strategic Signal, Aug 7)

**Source:** Jordan (Treasury group) — "Trader Joe also has access to Monad, and they
have Monad pools. So if Monad joins the Asian economy, now we have places and rails
for Monad as well."

## The insight

The **same Trader Joe LP rail** we're building for AVAX (Trader Joe V2 AVAX/USDC)
extends to **Monad** for free — Trader Joe has Monad pools. So the LP infrastructure
we're wiring now is **multi-chain by default**, not Avalanche-only.

## Verified rails for Monad

- **Q402** already supports Monad (chain 143, gas token MON, USDC/USDT, gasless
  for the payer). Confirmed via live q402_quote.
- **Trader Joe** has Monad pools (per Jordan + Trader Joe's multi-chain footprint).
- **Almanak** `traderjoe_v2` connector currently covers {avalanche, arbitrum, bsc,
  ethereum} — **NOT yet Monad**. So Almanak's TraderJoe LP path doesn't reach Monad
  yet; a direct Trader Joe router call would.

## Why it matters (the Asian economy angle)

Jordan's framing: **if Monad joins the Asian economy**, we already have a place and
a rail for it. Monad is an EVM-compatible L1 with strong Asia-Pacific traction.
Having the LP rail + Q402 gasless settlement ready means we can deploy there the
moment the ecosystem matures — first-mover, same as the Algorand play.

## Relationship to the current build

- The **Trader Joe V2 AVAX/USDC LP entry** (`gta_avax_lp.py`) is the pilot.
- The **direct Trader Joe router path** (bypassing Almanak's broken oracle) is the
  recommended fix — and that same direct-router approach is what would reach Monad
  pools, since Almanak's connector doesn't cover Monad yet.
- **Q402 Monad rail** is already live (gasless USDC/USDT) — a settlement path exists
  even before the LP rail is wired.

## Status
- Logged as a strategic signal + rail extension.
- No build yet — Monad is a "when the ecosystem matures" play, not today's target.
- The AVAX LP build is the immediate priority; Monad reuses the same pattern.
