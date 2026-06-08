# Handoff: AAE Premium — "Autopilot" Mode

**From:** YoYo (Strategies)
**To:** @Desmond (Entertainment)
**Priority:** High — Jordan flagged as key product
**Date:** Apr 18, 2026

## What Jordan Said

> "👀 Yessir, add that to workload in Entertainment"

This is the **core product feature set** for AAE Premium. The product.

---

## The Product

### Default Behavior: Fee Efficiency
- Auto-rebalance LP positions to stay in range and maximize fee capture
- Continuous range optimization based on volatility and volume
- No manual babysitting — the agent handles it

### Customization Layer (opt-in):
- Dip-buying rules — "if token drops X%, widen range / add liquidity"
- Custom rebalance triggers based on user strategy
- Personal risk parameters

---

## What Desmond Needs to Do

1. **Product page copy** — flesh out the value proposition
2. **Tier comparison** — Free vs Premium feature breakdown
3. **Landing page / sales page** — marketing materials
4. **Explainer content** — video scripts, social threads about what Autopilot does

## The Angle

"Set it and forget it — your LP positions on autopilot"

**Key differentiator:** Most LP tools require constant monitoring. AAE Premium handles it for you. You define the rules, the agent executes.

## Reference

- LP position example: LFJ AVAX/USDC V2.2 pool, binStep 10bps
- Jordan's current range: 9.66-9.95 (manually managed)
- The vision: users define strategy, agent executes 24/7

---

---

## The "Why" — Sentiment Drives Price Before Charts Do

### The Trump Proof
Jordan's observation: Trump would post something unhinged on Truth Social on a **Sunday** when markets were closed. Monday would gap down hard.

Timeline every time:
1. Sunday — wild post on Truth Social
2. Sunday night — futures bleed
3. Monday morning — full panic, gap down
4. Monday afternoon — partial recovery once reality sets in

**Anyone tracking his posts Sunday night could've front-run the Monday move.** The signal was there. Charts didn't show it until it was too late.

### Applied to Coin Communities
Same pattern, smaller scale:
- Dev team goes quiet for 2 weeks on Discord → panic selling starts before price drops
- Lead dev posts "exciting update" → narrative builds before the pump
- Coordinated FUD campaign on X → sentiment flips negative before price does
- Weekend activity spikes → something's brewing for Monday

### The Insight
> "Auto pools are great but I have better returns working 12 hours with you guys"

Gamma/Arrakis optimize for TVL, not returns. They rebalance mechanically. They don't see:
- A tweet from the right account that moves a coin 20%
- A Discord admin leaving the project
- FUD campaigns building on X
- Macro signals (tariffs, Fed statements)

**Charts are backwards-looking. Sentiment is forward-looking.**

### Community Intelligence Tracker (AAE Premium Feature)
- Insert ticker → scrape X + Discord → weekly community health score (1-100)
- Signals: post velocity, sentiment polarity, dev activity, member growth, FUD spikes
- **Feeds into Autopilot:** "community sentiment dropped 40% → tighten range or exit position"
- That's the moat — auto pools are blind to narrative. AAE sees what's happening.

---

## The "One Address" Flow — Feed It, Bam

> "Feed it a token address and bam"

**UX:** User enters one token address → full intelligence stack activates automatically.

```
Token: 0xABC...
  ├─ Tokenomics scan → supply, emissions, vesting schedule
  ├─ Holder analysis → top 20 wallets, concentration risk
  ├─ Unlock calendar → any cliffs in next 90 days?
  ├─ Community sentiment → X velocity, Discord health
  ├─ Pool health → IL risk, fee efficiency, depth
  ├─ Macro context → current risk environment (tariffs, FOMC, geopolitics)
  └─ Recommendation → ✅ Safe to LP / ⚠️ Caution / ❌ Avoid
```

**Then if they proceed:**
- Default: autopilot fee-efficient rebalancing
- Timing-aware: optimize for high-volume windows, not quiet Asia sessions
- Exit trigger: pool health degrades → agent exits before wrecked

---

## Smart Timing — When to Rebalance

**Asia session insight:** Overnight Asia markets don't move much. Most volume = US + EU hours.

- Tighten ranges during quiet hours (low fee capture, higher IL risk if something breaks)
- Widen/active during high-volume windows (better fees, more liquidity needed)
- Rebalance during active markets → better execution, less slippage
- Pre-emptive adjustments before macro events (FOMC, tariff announcements)

---

## Pool Health — The "Get Out" Signal

Autopilot monitors and exits when:
- Tokenomics deteriorating (inflation, emissions changes)
- Holder concentration spiking (one wallet accumulating too much)
- Community sentiment cratering (FUD, dev silence)
- Unlock cliff approaching (scheduled dump incoming)
- Macro event risk (tariffs, geopolitical escalation)

**This is what Gamma/Arrakis can't do.** They see price. AAE sees *why* price might move.

---

## Origin Story

Jordan built this to solve his own problem:

> "I work too much to keep up with everything."

The journey:
- Saw OpenClaw wrappers being built, tried one
- Gave it a simple task (LP position monitoring)
- One task led to another → full agent stack
- Built what he needed → turns out everyone needs it too

**The validation:**
> "Of course I'll be subscribing to my own service."

He's not selling a product he doesn't use. He built it because he needed it, and the features came from real problems, not brainstorming sessions.

---

## Context

This builds on Jordan's personal experience managing LP positions on LFJ/Trader Joe. He's been manually tracking range efficiency. AAE Premium automates this for everyone.
