# GenTech EDU — Agentic Treasury Onboarding & Honest-Expectations Layer

**Date:** 2026-08-07
**Source:** Jordan (Treasury group conversation)
**Status:** Idea captured — refined scope (Aug 7)

## The thesis (Jordan, verbatim intent)

GenTech EDU is a **learning module for our own infrastructure** — how to use the
GenTech Hub, how to use the GenTech Treasury, etc. It's an EDU for our products and
services. **Current focus: DeFi + setting a DeFi milestone.**

It tells users:
- **What we recommend** (which pool/rail to start with)
- **How to get started** (the exact steps)
- **Common mistakes** people make when prompting / working with agents
- **Honest expectations** — the same way The Steward told Jordan "this might be
  too small for what you're trying to do" or "this gives smaller returns."

## Scope (refined Aug 7)

- **Not** the visual-books / AR reading product (that's the separate "GenTech Book
  Reader / EDU" concept in ideas.md).
- **Is** a practical learning module covering our infrastructure: GenTech Hub,
  GenTech Treasury, and the DeFi milestone ladder.
- **DeFi milestone focus:** teach users the milestone ladder and how to climb it.

## The DeFi Milestone Ladder (from `.lfj-aae-config.json`)

| Tier | Label | Daily fees | Unlocks |
|------|-------|-----------|---------|
| 1 | Scout | $5/day | Entry strategies (CURVE) |
| 2 | Raider | $20/day | SPOT + BIDIRECTIONAL shapes |
| 3 | Warlord | $55/day | Multi-pool positions |
| 4 | Fisher | $100/day | Multi-asset farming (LINK, TAO, SOL) |
| 5 | Sovereign | $200/day | Custom strategy creation |

## Why this matters (the market-maker funnel)

Jordan's framing: **every market maker starts small.** His own budget started at
$25–50/week while saving for a trip, then scaled. The Agentic Treasury is the same
product shape:
- User deposits a small slice → treasury deploys it on a rail → proves the rail
  works → user scales the deposit.
- **GenTech EDU is the layer that makes that funnel safe and honest.** Users need
  to know BEFORE they deposit: "if you choose this pool, here are the benefits AND
  the realistic returns at your size."

## What EDU should contain (per pool / per rail)

For each deployable venue (e.g. Trader Joe V2 AVAX/USDC, Aave V3 USDC on BNB,
Morpho USDC on Base, Jupiter SOL/TAO):
- **What it is** — plain-language description
- **What we recommend** — is this a good starting pool for a small deposit?
- **Realistic returns at small size** — e.g. "$31.50 at 12% APY ≈ $3.78/yr" so
  users aren't surprised
- **How to get started** — exact steps (send USDC to steward wallet, etc.)
- **Common mistakes** — prompting errors, gas-not-funded, wrong-chain sends,
  expecting big returns on tiny capital
- **Risk profile** — IL risk, chain risk, custody posture

## The honest-expectations principle

The Steward already does this in conversation ("this may give smaller returns").
EDU productizes it: **surface the real numbers before the user commits**, so the
treasury's reputation is built on honesty, not hype. This is a differentiator vs
yield-farmers that promise big APY and hide the small-capital reality.

## Relationship to the Agentic Bridge / market-maker demo

- The **Agentic Bridge** (Base→Avalanche, spec'd Aug 6) is the infra that lets the
  treasury self-fund across chains.
- The **market-maker onboarding funnel** is the go-to-market: start small, prove
  the rail, scale.
- **EDU is the wrapper** that teaches users how to participate safely.

## Open questions
- Where does EDU live? (Docs site, in-app, Telegram group, all three?)
- Is EDU a free public good (marketing) or a premium tier?
- Does EDU cover the "Agency of Traders" BYO-agent arena too, or just the treasury?

## Next step
Build the first EDU page for the Trader Joe V2 AVAX/USDC pool as the pilot (it's the
rail we're about to fund + the existing live position).
