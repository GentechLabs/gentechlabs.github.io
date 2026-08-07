---
title: GenTech Subscription Layers — Open Core + Premium Integrations
date: 2026-08-03
status: concept
owner: Jordan + Gentech
related: [11-Mess Hall/considerations.md, narrative-rotation, agentic-treasury, gta]
---

# GenTech Subscription Layers — Open Core + Premium Integrations

> **One-line thesis:** GenTech's agentic treasury stays **open** (we earn on per-tx / swap fees — the "fee-earning middleman" model). The only thing we gate behind a subscription is **premium integrations** — the convenience/data layers, priced at **$10–15–20/mo**, NOT $20–50 (Jordan's explicit rejection of Minara's pricing).

**Why this beats Minara's model:** Minara gates the *core* behind a $20–50/mo subscription (paywall = the product). We keep the core open and monetize *usage* + *opt-in convenience*. Users never hit a wall; power users self-select into integrations. Same revenue per heavy user, zero adoption friction.

---

## The Stack — Two Layers

### Layer 0: Open Core (free to use, we earn per-tx)
- **Agentic Treasury (GTA)** — yield farming, arb monitoring, LP management. Open.
- **Trading / perps / swaps** — open. We take **swap fees / per-tx fees** (yield-farming model).
- **Dry powder defense system** — the capital-preservation layer (stop-loss, circuit breakers, rebalance on drawdown). **Open — this is trust-building**, not a toll.
- **x402 gateway** — open payment rails. We're the middleman; agents route payments through us and we take a per-tx cut.
- **Wallet / portfolio / market data** — open.

**Revenue source here:** per-tx fees, swap fees, x402 middleware cuts, inference take-rates. Volume-driven, not lock-in-driven.

### Layer 1: Premium Integrations ($10–15–20/mo, the ONLY sub surface)
The legitimate reason to subscribe: **convenience and data wiring** that costs us infra and adds real value, but that a casual user shouldn't have to pay for.

| Integration Tier | What it does | Anchor/Existing |
|------------------|--------------|-----------------|
| **Narrative Rotation** | Auto-rotate trading narratives weekly (already built) | ✅ Built — this is the anchor product |
| **BYO News Feed** | Plug-and-play connectors — wire YOUR favorite news source (bird's-eye style, RSS, Telegram, X) into the system for sentiment/trigger decisions | 🆕 The flagship paid feature |
| **Signal Packs** | Pre-curated feeds (e.g. Fed calendar, macro events, on-chain whale alerts) | Partially built (Watcher/crypto-price-fetch has Fed calendar) |
| **Alert Webhooks** | Push alerts to any channel (Telegram, Discord, Slack) when triggers fire | Extension of existing alerting |
| **Priority / API quota** | Higher x402 throughput, priority relay, dedicated agent wallet | Infra cost = legit paywall |

---

## 🆕 BYO News Feed — Flagship Paid Feature (spec anchor)

**Problem:** Users want the agent to make decisions informed by *their* news sources, not a generic feed.

**What it is:** A connector marketplace + wiring layer.
- **Plug in your source:** paste an RSS URL, Telegram channel, X account, or select a pre-built connector (bird's-eye-style news APIs, CoinDesk, Reuters, custom).
- **Agent wiring:** the source becomes a **signal input** — sentiment scoring, event detection (Fed, halving, hacks), and **trigger conditions** for the dry powder defense / narrative rotation (e.g. "if my feed flags a hack in Protocol X, pause yield in X").
- **Narrative integration:** feeds feed the existing Narrative Rotation engine so rotations are news-aware, not just price-aware.

**Revenue logic:** Casual users get the default feed for free. Wiring your own custom source = infra + maintenance → **that's the $10–15/mo tier.**

---

## 💰 Pricing (Jordan's stance, verbatim)

- **Open core:** $0 — agentic treasury, trading, dry powder defense, x402 rails. Earn on per-tx/swap fees.
- **Premium integrations:** **$10–15–20/mo**. NOT $20–50.
- **Rule of thumb:** the more *personalized* the integration (your news, your alerts, your channels), the more legitimately it's a paid tier. The more *core* (treasury, defense, trading), the more it must stay open.

---

## Out-of-the-Box Subscription Layers to Consider

Ideas to add value to the sub — ranked by "already built" → "future":

1. **BYO News Feed + Signal Packs** — the flagship (spec'd above).
2. **Narrative Rotation** — already built; package as the anchor demo of "premium integration."
3. **Alert Webhook Hub** — any-to-any push (Telegram/Discord/Slack/email) for triggers. Cheap to build on existing alerting.
4. **Priority Treasury** — for power users: dedicated agent wallet, higher tx throughput, priority relay on x402, faster rebalance execution.
5. **Multi-wallet / multi-chain portfolio** — aggregate everything in one dashboard, per-chain risk. Premium because it's heavy infra.
6. **Backtest Studio** — replay your strategy (or a signal pack) against historical data. Aligns with our `cufolio`/backtest skill. Premium compute = legit paywall.
7. **Agent Kit v2 premium skills** — 1–100 credit marketplace (already in spec).
8. **Institutional/compliance tier** — audit logs, CLARITY Act compliance dashboards, dedicated support → **$49–499/mo enterprise lane** (separate from consumer tier; already hinted in Academy/x402 plans).

---

## What Stays Open (non-negotiable — trust)
- Dry powder defense / stop-loss / circuit breaker — **always free.** A defense system you have to pay to activate is a broken trust model. This is what Jordan explicitly flagged.
- Core treasury + trading — open, per-tx fees.
- x402 rails — open middleware.

---

## Action Items
- [ ] **Greenlight** BYO News Feed as the first premium integration build (scope: one connector, e.g. RSS + Telegram channel, wired into Narrative Rotation).
- [ ] Package **Narrative Rotation** as the demo anchor for the premium tier.
- [ ] Document revenue model: open core (per-tx) + premium integrations ($10–15–20/mo).
- [ ] Log Minara pricing page as competitor reference (validates market tolerance).

## Status
🟢 Concept / idea bank — **NOT a build target yet.**
- **Jordan's sequencing (Aug 3):** build the **agentic treasury (GTA)** fully first → *then* revisit subscriptions. This spec is the reference bank for what we *could* offer and what people would pay for — kept as options, not commitments.
- When GTA is together, revisit this spec and pick the premium integration tiers to build.
