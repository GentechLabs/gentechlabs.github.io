# Agent Arena — Scored-Leverage Game Loop (between Command Center & GTA)

**Date:** 2026-08-04
**Name:** "The Agency of Traders" (Jordan, Aug 3) — the arena where agents compete.
**Trigger:** Krexa (@krexa_xyz) — Solana "Bank for AI Agents" (agent credit lines, natural-language agent deploy). Demo video + PnL tweet reviewed Aug 4.
**Jordan's framing (Aug 4):** *"We'll keep the command center as it is for yield farming, but between the command center and the trading (GTA), we can make a game based on those two mechanics — and that will be what the agents are in."*

---

## The thesis

The game sits **between** two layers we already run — it is NOT a replacement for either:

```
┌─────────────────────────────┐
│  COMMAND CENTER (yield)      │  commandcenter.gentechlabs.net
│  LP farming, yield rainbow,  │  live AVAX/USDC position, APR, fees
│  passive income mechanics    │
└──────────────┬──────────────┘
               │  ⬇ the GAME lives here
┌──────────────┴──────────────┐
│  THE GAME (agents are in it) │  ← NEW: scored-leverage arena
│  yield + trading as gameplay │  combines both layers' mechanics
└──────────────┬──────────────┘
               │  ⬇
┌──────────────┴──────────────┐
│  GTA (trading)               │  arb.gentechlabs.net
│  arb scanner, flash loans,   │  Hyperliquid perp vs Coinbase spot
│  active trading mechanics    │
└─────────────────────────────┘
```

The command center stays **pure yield farming** (unchanged). The GTA stays **pure trading** (unchanged). The game is a **bridge layer** that pulls mechanics from both and turns them into an arena agents live in.

## Why this is the right shape (Jordan's instinct validated)

- **No real user money.** Both layers run on paper/scoped bankrolls inside the arena. Nobody risks a dime — removes the trust wall, the legal wall, and widens the audience to anyone who wants to *watch* agents compete.
- **The credit score becomes the game mechanic.** We already have `agent-credit-score` (0–850, 5 tiers, MIT, 22/22 tests). In the arena, the score decides **who gets leverage** — not a dashboard number, but the thing that grants runway.
- **Borrowing = scored leverage.** Krexa's "open a credit line" (persistent credit) is the mechanism worth borrowing. An agent's credit line is underwritten by its score: high score → more credit → bigger position → more upside (and more downside). That's the tension that makes a game.
- **Two play surfaces, one arena.** Yield (passive, from command center) and trading (active, from GTA) become *strategies agents choose between* — farm for steady returns, trade for alpha, or blend.

## Game mechanics (draft)

- **Paper bankroll** per agent at entry + a **credit score**.
- **Credit line** against the score: `credit = f(score, collateral)`. Borrow to increase position size.
- **Two strategy lanes** drawn from the two layers:
  - **Yield lane** (command-center mechanics): LP, farm, compound — steady, low-vol return.
  - **Trade lane** (GTA mechanics): arb, directional, flash-loan style borrow→trade→repay — higher return, higher risk.
- **Live PnL decides the leaderboard** — the game is watching agents compete, picking winners, seeing whose score earned them more runway.
- **Command center as lobby**: "watch your agent, borrow more if its score earns it, see who's winning."

## Connection to existing work (borrow the mechanism, don't rebuild)

| Existing asset | Role in the game |
|---|---|
| `agent-credit-score` (0–850, 22/22 tests) | **Underwrites the credit line** — the core mechanic |
| Command Center yield data (LFJ AVAX/USDC) | The **yield lane** data feed |
| GTA arb scanner + flash-loan engine | The **trade lane** + borrow→repay pattern |
| `09-Green Room/specs/agent-arena-vision.md` | The BYO-agent arena substrate (free, social, scoped bankrolls, anti-Minara) |
| a2a trust layer (borrowed LoopX + trust-layer deep-dive) | Scoped bankrolls, trust scores, delegation narrowing per competing agent |
| Krexa credit-line mechanism | The **persistent credit line** primitive (the one real gap we had) |

## What we borrow from Krexa vs. what we already own

- **Borrow:** the *persistent credit line* UX ("open a credit line" → borrow → repay over time) as an arena mechanic.
- **Borrow:** the **Revenue Router** mechanism (Aug 4) — agent revenue auto-routes through the protocol; debt service happens automatically first, the agent keeps the rest. This is the repayment engine that makes a credit line work without manual settlement.
- **Already own:** credit scoring, agent identity (ERC-8004), yield data, trading/arb execution, x402 money rail.
- **Spit out:** Krexa as a dependency/platform. Solana-only, early, unproven profitability, no public repo/SDK/docs today (Aug 4). It validates the market; we don't build on it.

## Revenue Router — the borrowed repayment mechanism

**From Krexa (Aug 4):** *"Agent revenue routes through Krexa contracts. Debt service happens automatically. The agent keeps the rest."*

**The mechanism to adopt in the arena:** every time an agent in the game realizes PnL (yield lane or trade lane), that revenue **routes through a settlement layer first** — a fixed % of each payout services the agent's outstanding credit-line debt before the remainder lands in the agent's bankroll. This is what makes scored leverage self-cleaning:

```
Agent realizes PnL
        │
        ▼
┌─ SETTLEMENT LAYER ─────────────┐
│  1. Debt service (auto)  ← fixed % of payout   │
│  2. Agent keeps the rest                        │
│  3. Score updates from repayment behavior       │
└────────────────────────────────┘
```

**Why it matters:** without this, a credit line is just a loan someone has to chase. The Revenue Router makes repayment **automatic and score-driven** — good repayment behavior raises the score → raises future credit limit → the game loop feeds itself. Same mechanism Krexa ships, ported into our arena + our rail + our scoring.

**Wire into:** `agent-credit-score` (repayment behavior already feeds the score) + the arena's bankroll/settlement API + the GTA flash-loan execution engine (borrow → earn → auto-settle).

## Status

**Vision doc — not a build target.** Build-first sequencing still stands (Jordan, Aug 3): build the **GTA treasury fully first** → subscriptions/arena later. This spec captures the bridge-layer game for when GTA + flash-loan are production-ready.

## Action items (deferred until GTA is ready)

- [ ] Confirm the credit-line mechanism (borrow, repay, collateralize) fits the existing `agent-credit-score` model — extend vs. add a loan module
- [ ] Map the two strategy lanes (yield from command center, trade from GTA) onto the arena's agent bankroll API
- [ ] Define the arena ruleset: bankroll, credit formula, leverage caps, liquidation threshold
- [ ] Keep command center = pure yield, GTA = pure trading; the game layer only reads both
