# The Agency of Traders — Open, Social, BYO-Agent Prediction-Market Competition

**Date:** 2026-08-03
**Name:** "The Agency of Traders" (Jordan's naming, Aug 3) — reads like an institution, not a widget. Captures both *agency* (agents acting autonomously) and *traders* (the market context).
**Trigger:** Xona World (xona-labs/xona-world, MIT) — open-source arena where frontier AI models (Kimi K3 / GPT-5.6 Sol / Grok 4.5) trade real World (world.xyz) Solana prediction markets head-to-head, live PnL decides winner. Same bankroll, same markets, same rules — only the model differs.
**Also triggered by:** Jordan's note on Minara (competitor charges pay-to-play entry).

---

## The thesis (Jordan's framing)

Minara makes you **pay to enter** their platform. We flip it:

> **People bring their own agents** (BYO), or connect to the **agentic treasury (GTA)** via the MCP server — and it's **social**: you watch different agents compete on live prediction markets, and you see which ones are doing better based on what you pick.

## The wedge: GTA is a gateway, not just a trader

Jordan's core insight: **"The GenTech Trading Agent is really a gateway of its own to different things."**

GTA isn't just an arb bot — it's the **on-ramp** that:
- Brings agents into a shared, governed arena
- Exposes the treasury via MCP (any agent can connect)
- Gives each competing agent a scoped bankroll + trust level
- Lets humans pick/watch/compare agents socially

## How this is different from Minara (and better)

| | Minara | Our Agent Arena |
|---|---|---|
| Entry | Pay-to-play | **Free / BYO-agent** |
| Agents | Their platform's agents | **Yours** or connect to GTA treasury via MCP |
| Social | ? | **Watch agents compete, pick winners, see live PnL** |
| Venue | ? | Prediction markets (World/Polymarket) + multi-venue arb |
| Governance | ? | Trust layer (borrowed from a2a deep-dive) — scoped bankrolls, trust scores |

## What Xona World gives us (borrow the mechanism)

- **The model-competition loop**: per-cycle, stateless single-shot decision per agent; same prompt, same bankroll, same markets — only the model differs. Live equity snapshotted to a dashboard. This is the *arena mechanics*.
- **Run-it-yourself, MIT, defaults to no real trading** (`live.enabled` off). We can clone, run market-data-only, swap in our own agents via the `AGENTS` array.
- **Direct feed into our `model-strength-score` project** — a live, reproducible benchmark of Kimi K3 vs Grok vs GPT on real markets.

## The a2a/trust-layer hook

This connects the three things we just researched:
- **LoopX** → quota-aware, governed turns (when may an agent act?)
- **Multi-agent trust layer** → scoped bankrolls, trust scores, delegation narrowing (which agent gets how much?)
- **Xona World** → the arena mechanics (how they compete visibly)

Together they form the substrate for an **open, governed, social agent arena** where GTA is the gateway.

## Agent Sentiment — the novel signal (Jordan, Aug 3)

> *"It won't be long before we have to start viewing how agents trade alongside how people trade. So when we look at market sentiment, I wonder if we should also have an agent sentiment."*

**The insight:** Traditional market sentiment measures *human* behavior (fear/greed indices, funding rates, retail flow, social tone). But as agent volume grows, there's a **separate, measurable signal: what the agents are doing.** Agent sentiment = the aggregate of autonomous trading decisions, independent of human sentiment.

**Why it's novel and valuable:**
- Agents trade on different horizons, data, and rules than humans — so their aggregate flow is a **distinct leading indicator**, not a lagged echo of human fear/greed.
- It's **mechanically observable** — agent trades are on-chain/API-visible. We can *measure* agent sentiment in a way human sentiment can't be fully measured.
- In a social arena (The Agency of Traders), **the aggregate agent behavior IS the sentiment data** — the platform generates its own proprietary indicator.

**Concrete shape:**
- **Agent flow index** — net long/short positioning across agent-executed trades per venue
- **Agent confidence** — average conviction/size, win-rate drift per agent cohort
- **Agent-vs-human divergence** — when agents and humans disagree (spread between agent flow and human sentiment indices), that divergence is itself a signal
- GTA's `narrative-rotation` and macro layers could read **both** human sentiment AND agent sentiment, trading the divergence

**This is a differentiator, not a feature.** Nobody owns "agent sentiment" as a first-class market indicator yet. If The Agency of Traders produces it, we'd be the first with a real agent-flow data source feeding a proprietary index.

## Risks / caveats

- Xona World is 1★, experimental — a framework, not a product. Real-money path needs paybox wallet + Xona inference key.
- World/paybox is early-stage infrastructure.
- Prediction markets are a *competitor venue* to our existing Polymarket GTA path — but complementary (more venues = more arb patterns).

## Action items

- [ ] Clone xona-labs/xona-world into /root/repos; run **market-data-only** (no keys, no real money) to see the arena loop live
- [ ] Map the arena mechanics onto the a2a trust layer (scoped bankroll + trust score per competing agent)
- [ ] Explore GTA-as-gateway: expose GTA treasury via MCP as a BYO-agent on-ramp (not just the arb scanner — the full decision-partner surface)
- [ ] Feed Xona-style model competition into `model-strength-score` as a live benchmark source
- [ ] Keep Minara as the anti-pattern to differentiate against (free BYO vs pay-to-play)

## Status

**Exploration — not yet a build target.** GTA (agentic treasury) build-first sequencing still stands (Jordan, Aug 3): build the treasury fully first → subscriptions/arena later. This note captures the arena direction as a spec for when GTA is ready.
