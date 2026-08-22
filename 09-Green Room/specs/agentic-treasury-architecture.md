# Agentic Treasury — Architecture & Positioning (Canonical)

**Date:** 2026-08-18
**Author:** Jordan's mental model, grounded in the built system
**Status:** Canonical reference — reuse in whitepaper, portfolio, grants, hackathons

---

## The one-line pitch

> A smart wallet is a **container**. The Agentic Treasury is a **manager** — a cabinet of
> AI agents that decide what your money does, autonomously or under your orders, with a
> built-in stopping point to ask you at the decisions that matter.

## The Fed Chair model (Jordan's framing)

The Agentic Treasury is a **cabinet of agents working together to keep your money good** —
not one bot, but a coordinated team under a single decision-maker.

| Role | Agent | What it does |
|------|-------|--------------|
| **The Fed Chair** (over it all) | **Steward** | Reads the market regime, picks the LP shape, decides rebalance/hold, executes on-chain. `steward_rebalance.py` (decision loop) + `steward_execute.py` (on-chain operator, proven live: 43.47 USDC landed) + `steward-dashboard.html` (command center PWA). |
| **Trading agent** | **Arbiter** | Cross-venue arbitrage — DEX spot (GeckoTerminal) vs Hyperliquid perp mids, fee-fenced, mint-keyed (rejects lookalike phantoms). Consigliere strategy + `cross_venue_arb` routine. |
| **Yield farming agent** | **Yield Rail Finder** | Cross-rail yield heat-map (Base/Aerodrome, Solana/Meteora, Avalanche/LFJ, Monad). Ranks APY, flags volatile native-token yields. |
| **Narrative / rotation agent** | **AAE Narrative Rotation** | Rotates across sectors (AI, RWA, DeFi, L1/L2, Meme, Gaming) via regime classifier + Monid Social Intel. News-aware, not just price-aware. |

All four share the **same capital** and the **same goal**: keep the money good.

## The two operating modes (the differentiator)

The Steward ships with a **tier toggle** — the answer to "what's the difference vs a smart wallet":

1. **Operator mode (full autonomy)** — the Steward rebalances on its own, alerts Jordan
   *after* it acts, silent when healthy.
2. **User mode (recommend + confirm)** — it proposes, Jordan approves, it executes.

**The "stopping point" is the trust layer.** It's not a black box that moves your money —
it's an agent that *can* act alone but is designed to check in at the decisions that matter.
That's what a smart wallet cannot do.

## Why this wins (positioning)

- **Not a wallet** — a manager. The wallet holds; the treasury decides.
- **Not a black box** — human-gated guardrails at the decision points.
- **Not one bot** — a coordinated cabinet under a single Fed Chair.
- **Proven, not theoretical** — the Steward's exit rail fired live (43.47 USDC landed),
  the Arbiter detects real cross-venue routes, the Yield Rail Finder ranks live APYs.

## Reuse

- Whitepaper: `Treasury/agentic-treasury-whitepaper.md`
- Portfolio: lead with the Fed Chair + cabinet model
- Grants / hackathons: the "smart wallet vs manager" pitch is the hook
