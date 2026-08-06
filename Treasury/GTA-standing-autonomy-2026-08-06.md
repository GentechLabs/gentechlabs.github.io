# Standing Autonomy Authorization — GTA Execution (Aug 6, 2026)

**Jordan's standing rule (verbatim intent):** "While I'm at work, you're free to move
autonomously, just let me know what's going on. Keep me informed because I'm always
going to look at my phone late to make these moves."

## What this authorizes
During Jordan's work hours, Gentech may **execute verified, above-threshold GTA
opportunities WITHOUT waiting for real-time approval.**

## Guardrails (non-negotiable)
1. **Only execute on live ≥10 bps signals** on a **wired, verified rail.** No exceptions.
2. **Never fake a fill.** If a rail isn't wired or a signal is stale/below threshold,
   do NOT execute — report the blocker instead.
3. **Respect the engine's risk rules:** stop-loss (spread widened >50 bps from entry),
   max-hold 7 days, close <3 bps.
4. **ALWAYS notify Jordan of every move** — he checks his phone late. Every execution
   gets a clear message: what, how much, which rail, tx hash, current P&L.
5. **No new paid subscriptions** without explicit approval (cost-conscious rule).

## What Jordan wants to know
For each rail, what it needs to be **executable** — so he can unblock the missing pieces
when he's free.

## Rail readiness (as of Aug 6, 2026)
| Rail | Status | Needs to execute |
|------|--------|------------------|
| **Coinbase CDP spot (Base/Eth)** | ✅ LIVE + funded ($31.50 USDC) | Nothing — ready |
| **Jupiter (Solana)** | 🔧 built, dry-run verified | Fund keypair (0 SOL) + set SOLANA_KEYPAIR_FILE + bridge USDC Base→Solana |
| **Almanak (Avalanche)** | 🔧 scaffolded | Deploy Safe + signer service, OR separate AVAX keypair (custody decision) |
| **Hyperliquid perps** | 🔧 detection-only | GTA_HL_KEY + HL execution integration (US gray-zone — detection only) |
| **Q402 Morpho yield (Base)** | ⏸ shelved | Multichain key ($29) — NOT worth it at $31.50 capital (~$1.50/yr yield) |

## Current posture
GTA in **🟡 YIELD / LP HARVEST** (RANGE_BOUND 65%). No tradeable signal right now
(SOL 5.79bps, ONDO 5.12bps — both below 10bps execute). Spot leg verified live.
