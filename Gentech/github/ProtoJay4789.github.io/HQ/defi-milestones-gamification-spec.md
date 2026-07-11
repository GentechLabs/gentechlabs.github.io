# DeFi Milestones — Gamification Mechanics Spec

**Status:** Draft
**Author:** Gentech
**Date:** 2026-05-12
**Source:** Strategy conversation — loss aversion engagement loop

---

## Context

The DeFi Milestones system already tracks LP positions against a tier ladder (Scout → Raider → Warlord → Sovereign). Current implementation is purely observational — it reports progress but doesn't create urgency. This spec adds behavioral mechanics that make users *feel* the stakes of inactivity.

Core insight: **Loss aversion is 2x stronger than reward-seeking** (Kahneman & Tversky). People work harder to keep what they have than to earn something new. Every mechanic below exploits this.

---

## Current Tier Ladder

| Tier | Daily Fee Threshold | Status |
|------|-------------------|--------|
| Scout | $5/day | ✅ Built |
| Raider | $20/day | ✅ Built |
| Warlord | $55/day | 🔧 In progress |
| Sovereign | $200/day | 🔧 In progress |

---

## Mechanic 1: Rank Decay

**What:** If daily fees drop below your current tier's threshold for 7 consecutive days, you drop one tier.

**Why it works:** "Your Raider status expires in 3 days" hits different than "keep farming." The countdown creates urgency. People check back not to earn more, but to *not lose* what they have.

**Spec:**
- Decay window: 7 days below threshold
- Grace period: 3-day warning before drop
- Drop is one tier at a time (no freefall)
- Lowest tier (Scout) cannot decay further — it's the floor
- State tracking: `last_above_threshold_date`, `current_tier`, `days_below_threshold`

**Edge cases:**
- Weekend/holiday inactivity: No exception. Markets don't sleep.
- Position withdrawn entirely: Instant decay to Scout
- New position opened above current tier: No change (must sustain 3+ days)

---

## Mechanic 2: Visual Progress Bars

**What:** Public-facing progress bars showing exactly where you are between tiers, with countdown to decay.

**Why it works:** Transparency. Users see the gap. "You're 62% to Warlord" is motivating. "You'll lose Raider in 3 days" is urgent. Both hit differently when visible to others.

**Spec:**
- Two bars: Progress UP (toward next tier) and Decay DOWN (days remaining)
- Progress bar: `[████████░░░░░░░░] 62% to Warlord`
- Decay bar: `[▓▓▓▓▓▓░░░░░░░░░░] 4 days until decay`
- Bars update in real-time (or near-real-time on-chain)
- Public profile shows your bars to friends/competitors
- Private dashboard shows additional detail (projected earnings, optimal ranges)

---

## Mechanic 3: Streak Multipliers

**What:** Hit your tier minimum 7 days in a row → earn a bonus fee multiplier. Lose the streak → multiplier resets.

**Why it works:** Streaks are psychologically powerful (Duolingo, Wordle). The fear of losing a 12-day streak makes you check back daily even when you're already at your tier.

**Spec:**
- Streak starts at day 1 of hitting tier minimum
- 7-day streak: 1.1x fee bonus
- 14-day streak: 1.2x fee bonus
- 30-day streak: 1.5x fee bonus (max)
- Streak resets to 0 if you drop below threshold for 1+ days
- Streak is tied to the position, not the wallet (can't cheat by switching)
- Display: "🔥 12-day streak | 1.2x multiplier active"

---

## Mechanic 4: Social Leaderboards

**What:** Friends-based ranking, not global. You compete against people you actually know.

**Why it works:** Global leaderboards are demotivating — top 10 are always whales. Friends-based leaderboards create social pressure. "My friend is ahead of me" is a stronger motivator than "I'm rank 4,327."

**Spec:**
- Leaderboard shows: rank, tier, streak, progress bar
- Opt-in friends list (not automatic)
- Weekly summary: "You passed 2 friends this week"
- Monthly reset: Fresh competition each month
- Privacy: Can hide from leaderboard (but then lose social perks)

---

## Mechanic 5: Rank Perks

**What:** Higher tiers unlock tangible benefits, not just bragging rights.

**Why it works:** Perks make the tier *valuable*. Without them, decay is just cosmetic embarrassment. With them, decay means losing real features.

**Spec:**

| Tier | Perks |
|------|-------|
| Scout | Basic strategies, standard platform fees |
| Raider | Lower platform fees (0.1% → 0.08%), priority pool access |
| Warlord | Custom range creation, governance weight (1.5x), mentor access |
| Sovereign | Treasury management tools, protocol fee sharing, governance weight (3x) |

**Decay consequence:** Lose a tier → lose that tier's perks immediately. This is the real loss aversion trigger.

---

## Mechanic 6: Near-Miss Alerts

**What:** Push notifications when you're close to losing a tier or close to earning a new one.

**Why it works:** Near-miss psychology — people who almost win gamble more. "You're 1 day from losing Raider" is more motivating than "you lost Raider."

**Spec:**
- Push at 3 days before decay: "⚠️ Your Raider status expires in 3 days"
- Push at 1 day before decay: "🚨 Final warning: Raider status expires tomorrow"
- Push when 80%+ to next tier: "Almost there! $3.20 more/day to Warlord"
- Push when streak hits 7/14/30: "🔥 7-day streak! 1.1x multiplier active"
- Frequency cap: Max 2 notifications per day (avoid annoyance)

---

## On-Chain Integration: REP Tokens

**What:** Rank is not cosmetic — it's soulbound REP tokens proving farming consistency.

**Why it works:** On-chain reputation is portable. Other protocols can read your REP. This makes the tier system valuable beyond our platform.

**Spec:**
- REP tokens are soulbound (non-transferable)
- Minted on tier-up, burned on tier-down
- Contains: tier level, streak data, total fees earned
- Readable by external contracts (for DeFi integrations)
- REP = proof of consistency, not proof of wealth

---

## Implementation Priority

1. **Rank Decay** — Highest impact, creates urgency immediately
2. **Visual Progress Bars** — Foundation for all other mechanics
3. **Near-Miss Alerts** — Amplifies decay's psychological impact
4. **Streak Multipliers** — Retention mechanic, build after core loop works
5. **Social Leaderboards** — Growth mechanic, needs user base first
6. **Rank Perks** — Ties into token economics, requires $TECH integration

---

## Metrics to Track

- **DAU/MAU ratio** — Are people coming back daily?
- **Average streak length** — How long do people maintain activity?
- **Tier distribution** —健康的 pyramid (lots of Scouts, few Sovereigns)
- **Decay events** — How many people lose tiers per week?
- **Recovery rate** — Do people who lose tiers fight to regain them?
- **Push notification CTR** — Do near-miss alerts drive action?

---

## Open Questions

1. **Should decay be faster for higher tiers?** (7 days for Scout → 3 days for Sovereign?)
2. **Can streaks transfer between positions?** (If you close one LP and open another?)
3. **What's the REP token standard?** (ERC-5192? Custom soulbound?)
4. **Do perks compound or replace?** (Does Warlord get Raider perks + new ones?)
5. **How does this interact with the dual pricing model?** (AAE agent vs human users)

---

*This spec is ready for review. Jordan to confirm priority order and edge case handling before implementation begins.*
