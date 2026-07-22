# AAE Personal Goal Engine — Product Spec
**Version:** 0.1  
**Date:** 2026-04-25  
**Author:** Desmond (Creative) ✓ DMOB (Technical) ✓ YoYo (Strategic) ✓  
**Status:** Draft — pending Jordan approval

---

## One-Liner

The Personal Goal Engine turns the AAE from a "black box that rebalances" into a **trading mentor that celebrates progress at every dollar**.

---

## Philosophy: More Winners Than Losers

| Traditional DeFi | AAE Personal Goal Engine |
|---|---|
| You made $0.43 today. | You hit your daily micro-goal 7 days in a row. Streak: ⚡ 7. |
| Your APR is 12%. | You're earning 3x more than a savings account — here's the math. |
| Impermanent loss warning. | Your position shifted. Here's what that means in 30 seconds. |
| Top performers make $500/day. | Your squad just crossed $50/day combined. You're 40% of that. |

**The win isn't the dollar amount. The win is understanding *why* the dollar happened.**

---

## Core Modules

### 1. Personalized Ladder System

**Not one-size-fits-all.** The ladder adapts to starting capital, risk tolerance, and market conditions.

#### Default Templates

| Profile | Starting Capital | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |
|---|---|---|---|---|---|---|
| **Rookie** | $100–500 | $1/day | $3/day | $5/day | $10/day | $20/day |
| **Builder** | $500–2K | $5/day | $15/day | $30/day | $55/day | $100/day |
| **Grower** | $2K–10K | $20/day | $50/day | $100/day | $200/day | $400/day |
| **Veteran** | $10K+ | $100/day | $250/day | $500/day | $1K/day | Custom |

#### Tier Advancement Rules
- **Time-gated:** Minimum 7 days at current tier before unlocking next
- **Consistency-gated:** Must hit tier target ≥5 out of 7 days
- **Knowledge-gated:** Must complete 1 micro-lesson to advance past Tier 3
- **Market-aware:** Auto-downgrades ladder during bear market (optional, user-controlled)

---

### 2. Micro-Lesson Engine

**Bite-sized education triggered by real events.**

| Trigger | Lesson | Format |
|---|---|---|
| First LP deposit | "What is impermanent loss?" | 60-sec animated explainer |
| Rebalancer executes | "Why we rebalanced today" | 2-sentence summary + link |
| Streak hit 7 days | "Compound vs. simple interest" | Interactive calculator |
| Tier advancement | "Risk management for your new level" | Quiz (3 questions) |
| Market drops >10% | "Bear market psychology" | Quick-read card |
| First fee claim | "Gas optimization basics" | Tip card |

**Format constraints:**
- Max 60 seconds video
- Max 3 paragraphs text
- Max 3 questions per quiz
- Always actionable — "Here's what you can do with this info"

---

### 3. Win Recognition System

**Making $5/day feel like a win.**

#### Personal Celebrations
- **Daily:** "✅ Goal hit! $5.23 earned — 3-day streak"
- **Weekly:** "🌟 Week complete! $38.40 total. That's a movie ticket."
- **Tier Up:** "🚀 LEVEL UP! You're now a [Tier Name]. New target: $10/day."
- **Milestone:** "🏆 30 days of consistent earnings. You've outlasted 60% of DeFi users."

#### Squad Celebrations
- "Your squad hit $50/day combined! You're the #1 earner this week."
- "Squad streak: 14 days. Teamwork makes the dream work."
- "[Teammate] just leveled up. Send congrats? 👍"

#### Context Anchors
Every celebration includes:
1. **What happened** (the number)
2. **Why it matters** (context)
3. **What comes next** (next goal or action)

Example:
> 🌟 You earned $5.23 today — your daily goal is $5.00.  
> That's 3x what a savings account would pay on your capital.  
> 4 more days like this and you'll unlock Tier 3. Keep going! ⚡

---

### 4. Trader Mindset Scorecard

**Track the *skills*, not just the profits.**

| Skill | How It's Measured | Level Up |
|---|---|---|
| **Consistency** | Days hitting goal / total days | Bronze → Silver → Gold → Platinum |
| **Patience** | Didn't panic-sell during dips | Badge: "Diamond Hands" |
| **Learning** | Micro-lessons completed | Badge: "Scholar" |
| **Squad Support** | Celebrated teammates, shared insights | Badge: "MVP" |
| **Risk Awareness** | Adjusted position size proactively | Badge: "Captain" |

**These scores feed into squad reputation and unlock advanced features.**

---

## Technical Architecture (DMOB Input Needed)

### Data Model

```typescript
interface UserGoalProfile {
  userId: string;
  templateId: 'rookie' | 'builder' | 'grower' | 'veteran' | 'custom';
  currentTier: number;
  currentStreak: number;
  longestStreak: number;
  tierHistory: TierRecord[];
  mindsetScorecard: Scorecard;
  lessonsCompleted: string[];
  celebrationsEnabled: boolean;
  autoAdjustForMarket: boolean;
}

interface TierRecord {
  tier: number;
  targetAmount: number; // USD
  dateStarted: Date;
  dateCompleted?: Date;
  consistencyRate: number; // % of days hit
}

interface DailySnapshot {
  date: string;
  earnings: number;
  goalHit: boolean;
  marketCondition: 'bull' | 'neutral' | 'bear';
  rebalancerAction?: string;
  lessonDelivered?: string;
}
```

### Event Hooks (from AAE Core)

| AAE Event | Goal Engine Action |
|---|---|
| `RebalanceExecuted` | Log earnings, check goal hit, trigger celebration |
| `FeesClaimed` | Update earnings, deliver gas optimization tip |
| `PositionOpened` | Trigger "first deposit" lesson if new user |
| `MarketDipDetected` | Deliver psychology lesson, check panic-sell flag |
| `SquadDepositReceived` | Update squad totals, trigger squad celebration |

### Storage
- **On-chain:** Tier advancement (NFT badge?), squad totals
- **Off-chain:** Lesson progress, streak data, user settings
- **Hybrid:** Daily snapshots pinned to IPFS for transparency

---

## Milestone System Update

### Current System (from dashboard inspiration)
- $5/day ✅ → $20/day 🔄 → $55/day 🎯 → $200/day 🚀
t
### Updated System (personalized ladders)

```
Rookie Track:
$1/day ✅ → $3/day 🔄 → $5/day 🎯 → $10/day 🚀 → $20/day 🏆

Builder Track:
$5/day ✅ → $15/day 🔄 → $30/day 🎯 → $55/day 🚀 → $100/day 🏆

Grower Track:
$20/day ✅ → $50/day 🔄 → $100/day 🎯 → $200/day 🚀 → $400/day 🏆
```

### Milestone UI Components

1. **Progress Ring** — Visual of current tier progress (% to next tier)
2. **Streak Flame** — Animated flame, grows with streak length
3. **Squad Leaderboard** — Where you rank in your squad by tier
4. **Market Context Badge** — "You're winning even in a bear market 🐻"
5. **Next Lesson Teaser** — "Unlock 'Advanced Rebalancing' at Tier 3"

---

## Content Requirements (Desmond Domain)

### Micro-Lesson Library (MVP: 10 lessons)
1. What is LP providing?
2. Impermanent loss in 60 seconds
3. APR vs. APY
4. Why rebalancing matters
5. Gas fees: friend or foe?
6. Bull vs. bear market positioning
7. DCA strategy basics
8. Risk management for small capital
9. Reading a liquidity chart
10. When to compound vs. claim

### Celebration Copy Library
- 50+ personalized celebration messages per tier
- Tone: encouraging, never patronizing
- Cultural references: gaming (level up), fitness (streak), finance (milestone)

### Dashboard Copy
- Empty state: "Your first dollar is the hardest. We'll get there together."
- Loading state: "Crunching your wins..."
- Error state: "Markets are wild today. Your position is safe — check back in an hour."

---

## Success Metrics

| Metric | Target |
|---|---|
| Lesson completion rate | >60% |
| Tier advancement rate | >40% within 30 days |
| Streak retention (7+ days) | >35% of active users |
| User-reported "I understand my position better" | >70% |
| Squad celebration engagement | >50% react to squad wins |

---

## Implementation Phases

### Phase 1: Ladders + Streaks (MVP)
- 4 templates, manual selection
- Daily goal tracking
- Basic celebrations (text only)

### Phase 2: Micro-Lessons
- 10-lesson library
- Trigger-based delivery
- Quiz gating for Tier 3+

### Phase 3: Trader Mindset Scorecard
- Skill tracking
- Badge NFTs
- Squad reputation integration

### Phase 4: Adaptive AI
- Auto-ladder selection based on behavior
- Personalized lesson recommendations
- Predictive "you might want to adjust" nudges

---

## Open Questions

1. **DMOB:** On-chain vs. off-chain for tier badges? Gas cost acceptable?
2. **YoYo:** Are the dollar targets realistic for current market conditions? Should we use % of capital instead?
3. **Gentech:** Priority — build this for Solana Frontier hackathon or keep as post-hackathon product feature?
4. **Jordan:** Do we brand this as "AAE Education" or give it a standalone name (e.g., "The Academy", "TradeCamp")?

---

## Next Steps

- [ ] DMOB: Feasibility review — event hooks, data model, storage
- [ ] YoYo: Financial model validation — tier targets, market-adjustment logic
- [ ] Desmond: Draft micro-lesson scripts (3 sample lessons)
- [ ] Gentech: Priority decision — hackathon vs. product roadmap
- [ ] Jordan: Brand name + tone approval

---

*Consolidated from Mess Hall discussion 2026-04-25.*
