# Personal Goal Engine — AAE Education Layer Specification

> **Created:** 2026-04-25  
> **Author:** Gentech (orchestrating Jordan's vision)  
> **Status:** Draft — Ready for review  
> **Purpose:** Transform passive users into compound learners through adaptive milestone systems

---

## Executive Summary

### ASCII Art Reference — Engine Architecture

```
           _______                                _    _____             _
          |__   __|                              | |  / ____|           | |
             | | ___ _ __ ___  ___  _ __   __ _| | | |  __  ___   __ _| |
             | |/ _ \ '__/ __|/ _ \| '_ \ / _` | | | | |_ |/ _ \ / _` | |
             | |  __/ |  \__ \ (_) | | | | (_| | | | |__| | (_) | (_| | |
             |_|\___|_|  |___/\___/|_| |_|\__,_|_|  \_____|\___/ \__,_|_|


 ______             _            _____             _ _
|  ____|           (_)           |  _ \           | | |
| |__   _ __   __ _ _ _ __   ___| |_) | ___  _ __| | |
|  __| | '_ \ / _` | | '_ \ / _ \  _ < / _ \| '__| | |
| |____| | | | (_| | | | | |  __/ |_) | (_) | |  |_|_|
|______|_| |_|\__, |_|_| |_|\___|____/ \___/|_|  (_|_)
             __/ |
            |___/
```

---

## Core Philosophy: More Winners Than Losers

The **Personal Goal Engine** is a behavioral learning engine embedded within the AAE (Auto-Agent Economy) education layer. It operationalizes Jordan's core insight:

> **"Making $5/day feel like a win when you started from zero."**

By combining **progressive tier systems**, **adaptive milestone tracking**, **behavioral feedback loops**, and **personalized education triggers**, the engine turns trading activity into a gamified learning journey where users develop trader mindset before they become profitable.

---

## Core Philosophy: More Winners Than Losers

### The $5/Day Win Frame
- **Zero-start framing:** Users begin with $0 → first $5/day represents *proof* the system works
- **Psychological leverage:** Small, frequent Wins build confidence faster than waiting for $100/day
- **Compound mindset:** Each win demonstrates that $5 → $20 → $55 → $200 is achievable through repetition
- **Loss defusion:** Missed days are reframed as "data points," not failures → low emotional overhead

### Win Condition Metrics
```
✅ 3+ consecutive days earning > $0 → User sees consistent progress
✅ $5/day for 7+ days →Tier promotion eligibility
✅ 60%+ fee efficiency sustained → User demonstrates range management skills
✅ <3 consecutive days out of range → User learns recovery protocol
```

---

## Progressive Tier System

### Tier Ladder (Rookie → Veteran → Elite → Legend)

| Tier | Label | Daily Fee Target | Position Required | Unlockables | Visual Badge |
|------|-------|------------------|-------------------|-------------|--------------|
| **0** | **Zero** | $0 | $0 | Welcome guide, DCA checklist | `🌑` |
| **1** | **Rookie** | $3 | $25 | Curve strategy, basic alerts | `🌱` |
| **2** | **Apprentice** | $8 | $100 | Spot shape, DCA scheduling | `⚔️` |
| **3** | **Veteran** | $20 | $500 | Curve + Bidirectional shapes, multi-pool | `🛡️` |
| **4** | **Expert** | $55 | $1,500 | Auto-compound, strategy marketplace access | `💎` |
| **5** | **Elite** | $110 | $4,000 | Custom strategy builder, API access | `🔥` |
| **6** | **Legend** | $200 | $10,000 | Full strategy customization, white-label brand | `👑` |

### Tier Promotion Logic

```
threshold crossing detected → education trigger fired → tier unlocked
├── Daily fees crosses tier threshold
├── Position value confirms tier sustainability
└── Education triggers completed (3-day learning checkpoint)
```

**Key:** Promotions require BOTH financial milestone AND behavioral checkpoint completion.

---

## Adaptive Milestone System

### Non-Linear Progression Design

Traditional linear progression assumes all users follow identical paths. **Personal Goal Engine** adapts to:
- User trade frequency (daily vs weekly vs event-triggered)
- Risk tolerance (conservative vs aggressive positioning)
- Learning style (visual vs textual vs interactive)
- Market regime (bull vs bear vs volatile)

### Milestone Categories

#### 1. Time-Based Milestones (Beginner Friendly)
| Milestone | Target | Education Trigger | Reward |
|-----------|--------|-------------------|--------|
| First 24H earning | 14 days | Position tracking, fee mechanics | Bronze badge |
| 7-day streak | $0/day for 7 days | Compound math, consistency | Silver badge |
| 30-day streak | $5/day for 30 days | Risk-adjusted returns, patience | Gold badge |

#### 2. Behavior-Based Milestones (Skill Demonstration)
| Milestone | Trigger | Education Trigger | Reward |
|-----------|---------|-------------------|--------|
| Recovery from out-of-range | Price returns to range | Rebalancing protocol, range adjustment | Iron skill |
| Efficient rebalance | Fee efficiency >80% achieved | Curve vs Spot vs Bidirectional selection | Gold skill |
| DCA consistency | 5+ consecutive DCA executions | Dollar-cost averaging psychology | Platinum skill |
| Multi-pool diversification | 3+ pools with >$25 each | Portfolio construction, correlation | Diamond skill |

#### 3. Wealth-Based Milestones (Traditional Progression)
| Milestone | Daily Target | Position Approx | Unlockables |
|-----------|--------------|-----------------|-------------|
| **Scout** | $5 | $100-200 | Basic strategies, alerts |
| **Raider** | $20 | $500-1,000 | Advanced shapes, market alerts |
| **Warlord** | $55 | $2,000-4,000 | Strategy creator, marketplace |
| **Sovereign** | $200 | $10,000+ | Full customization, white-label |

**Adaptive Logic:**
```
IF user trade frequency > 3/day THEN
    time-based milestones 30% faster
ELSE IF user trade frequency < 1/week THEN
    time-based milestones 50% slower, behavior milestones emphasized
END IF

IF user risk score > 0.7 THEN
    wealth-based milestones weighted higher
ELSE IF user risk score < 0.3 THEN
    behavior-based milestones weighted higher
END IF
```

---

## Education Triggers

### Trigger System Architecture

```
Key Threshold → Notification → Education Modal → Action Required → Completion
```

### Trigger Types & Triggers

#### 1. Fee Efficiency Trigger
```
Trigger: Fee efficiency drops below 60% for >24h
Notification: "⚠️ Your Curve is drifting — fees slowing down"
Education: "Curve shapes capture volatility best during chop. During trends, consider Spot or Bidirectional."
Action: Watch 90s video on shape selection, click "Try Spot"
Completion: User tests Spot shape for 4+ hours
Reward: Unlock "Shape Translator" badge
```

#### 2. Compound Threshold Trigger
```
Trigger: Accumulated fees reach $50 threshold
Notification: "💸 Compound ready! $50 waiting to reinvest"
Education: "Compound = reinvesting fees into more LP. Every $50 here = ~5.6 AVAX at $8.85"
Action: Confirm compound (withdraw → swap → redeposit)
Completion: Compound executed
Reward: "Compound Master" badge + 5% APR boost for 7 days
```

#### 3. DCA Consistency Trigger
```
Trigger: User completes 3 consecutive DCA days
Notification: "📈 DCA Streak Active! 3 days in a row"
Education: "DCA isn't timing — it's consistency. Mondays are special: $50–$100 weekly slot"
Action: Set Monday DCA reminder
Completion: User sets reminder
Reward: "DCA Streaker" badge + early access to new pool alerts
```

#### 4. Range Recovery Trigger
```
Trigger: Price returns to range after being out for >48h
Notification: "📍 Priceback! Range active after 2.5 days"
Education: "Out-of-range = holding AVAX/USDC. Recovery means fees active again. Watch: Rebalancing 101"
Action: Review rebalance decision tree
Completion: User completes quiz
Reward: "Tactical Recovery" badge
```

#### 5. Tier Promotion Trigger
```
Trigger: Daily fees exceed tier threshold for 3+ consecutive days
Notification: "🔥 PROMOTION: You're now a [New Tier]! 🎉"
Education: "What changed? You mastered [old tier skill] and unlocked [new tier capability]"
Action: Review new unlocks, choose first new feature
Completion: User selects new strategy/shape
Reward: Full tier functionality, leaderboard entry, shareable card
```

### Trigger Cooldowns & Delays

| Trigger Type | Cooldown | Purpose |
|--------------|----------|---------|
| Fee efficiency | 12 hours | Prevent alert fatigue |
| Compound threshold | 24 hours | Ensure execution time |
| DCA consistency | 48 hours | Allow for missed days |
| Range recovery | 1 hour | Confirm recovery stability |
| Tier promotion | 1 hour | Allow reflection |

---

## Behavioral Feedback Loops

### The Loop Architecture

```
Action → Notification → Celebration → Reflection → Next Action

┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   AAE User  │────>│   Notification │────>│  Celebration  │────>│   Reflection │
│   Action    │     │   (Telegram) │     │  (Emoji +   │     │  (2 questions│
└─────────────┘     └──────────────┘     │  Progress    │     │   + prompt) │
                                          │  Bar         │     └──────────────┘
                                          └──────────────┘          │
                                                          └──────────┘
                                                                  │
                                                        ┌──────────────┐
                                                        │   Next Action  │
                                                        │   (Suggested)  │
                                                        └──────────────┘
```

### Notification Layer

| Channel | Frequency | Content | Priority |
|---------|-----------|---------|----------|
| **Telegram** | 1x/day max | Milestone, DCA, Position | Critical |
| **In-app** | 5x/day max | Quick stats, tips | Normal |
| **Push** | 3x/week max | Education, strategy swaps | Low |

### Celebration Layer

| Achievement | Emoji | Progress Bar | Sound |
|-------------|-------|--------------|-------|
| First $5/day | 🎉 | 0→5/5 | Win chime |
| 7-day streak | 📈 | 1→7/7 | Level up |
| Tier promotion | 🏆 | 100% full | Trophy sound |
| Compound done | 💰 | +50/200 | Coin stack |
| Recovery | 🎯 | 0→100 | Bullseye |

### Reflection Prompts

**Post-Milestone:**
> "What worked? What would you do differently next time?"

**Post-Trade:**
> "Did this trade match your plan? Why or why not?"

**Daily Check-in:**
> "Rate today's trading: 1 (rushed) → 5 (patient)"

**Weekly Review:**
> "Which skill improved this week? Where do you want to focus?"

---

## Personalization Logic

### Learning Style Detection

The engine tracks user interaction patterns to determine preferred learning modality:

| Pattern | Inferred Style | Educational Format |
|---------|----------------|-------------------|
| Watches >2 educational videos/week | Visual | Video tutorials, diagrams |
| Clicks "read article" links consistently | Textual | Articles, readables |
| Uses interactive tools >5x/week | Interactive | Quizzes, simulations |
| Only reads Telegram summaries | Auditory | Voice notes, audio alerts |

**Detection Logic:**
```
IF video_views > 2 AND article_clicks < 1 THEN
    learning_style = "visual"
ELSE IF article_clicks > 3 AND video_views < 2 THEN
    learning_style = "textual"
ELSE IF tool_interactions > 5 THEN
    learning_style = "interactive"
ELSE
    learning_style = "audio"
END IF
```

### Risk Appetite Assessment

**Risk Score Calculation (0.0 - 1.0):**
```
risk_score = (
    (position_concentration * 0.3) +      # 70% in AVAX → high
    (dca_speed * 0.2) +                    # >$100/day → aggressive
    (rebalance_frequency * 0.2) +          # >2x/week → active
    (range_width_preference * 0.3)         # Wide range → conservative
) / 1.0
```

**Risk Tiers:**
| Score | Label | Strategy | Education Focus |
|-------|-------|----------|-----------------|
| 0.0-0.3 | Conservative | Curve (narrow), DCA ($50/wk) | Patience, volatility |
| 0.3-0.6 | Balanced | Curve (broad), DCA ($75/wk) | Risk-adjusted returns |
| 0.6-0.8 | Aggressive | Bidirectional, DCA ($150/wk) | Momentum capture |
| 0.8-1.0 | Hyper | Spot, LTM, high volatility | Advanced positioning |

### Trade Frequency Analysis

| Frequency | Pattern | Suggested Milestones |
|-----------|---------|---------------------|
| 5+/day | Active trader | Short-term, high-frequency unlocks |
| 1-2/day | Active learner | Mixed daily/weekly unlocks |
| 3-5/week | Occasional | Behavior-based milestones |
| <1/week | Passive | Time-based, achievement milestones |
| Event-triggered | Alert-driven | Reaction-based education |

**Adaptive Milestone Weights:**
```
IF trade_frequency > 3/day THEN
    daily_milestone_weight = 0.7
    weekly_milestone_weight = 0.2
    monthly_milestone_weight = 0.1
ELSE IF trade_frequency < 0.5/day THEN
    daily_milestone_weight = 0.1
    weekly_milestone_weight = 0.4
    monthly_milestone_weight = 0.5
END IF
```

---

## Integration Points

### AAE Signal Specification Integration

| Field | Source | Usage |
|-------|--------|-------|
| `current_tier` | LP Monitor | Tier unlocking |
| `current_tier_label` | LP Monitor | Notification context |
| `progress_to_next_pct` | LP Monitor | Progress bars |
| `fees_24h` | LP Monitor | Daily win tracking |
| `dca_ready` | LP Monitor | DCA consistency milestones |
| `compound_ready` | LP Monitor | Compound threshold triggers |

### AgentEscrow Contract Tiers (Reference)

| AgentEscrow Tier | AAE Education Tier | Notes |
|------------------|-------------------|-------|
| Scout | Rookie | Entry-level access |
| Fighter | Apprentice | Strategy exposure |
| Captain | Veteran | Multi-pool capability |
| General | Elite | Strategy creation |
| Legend | Legend | Complete control |

**Design principle:** AAE tiers map to AgentEscrow tiers so users can see their "progress" across both systems.

### LFJ Dashboard Integration

- **Yield Farm Tracker → Squad Treasury Dashboard** (composition, earnings, auto-compound)
- **DeFi Milestone Tracker → Squad Leveling System** (Rookie → Veteran → Elite → Legend)
- **DCA Schedule → Squad auto-buy / contribution tiers**
- **Real-time status indicators → Behavioral feedback loops**

---

## ASCII Art Reference

```
           _______                                _    _____             _
          |__   __|                              | |  / ____|           | |
             | | ___ _ __ ___  ___  _ __   __ _| | | |  __  ___   __ _| |
             | |/ _ \ '__/ __|/ _ \| '_ \ / _` | | | | |_ |/ _ \ / _` | |
             | |  __/ |  \__ \ (_) | | | | (_| | | | |__| | (_) | (_| | |
             |_|\___|_|  |___/\___/|_| |_|\__,_|_|  \_____|\___/ \__,_|_|


 ______             _            _____             _ _
|  ____|           (_)           |  _ \           | | |
| |__   _ __   __ _ _ _ __   ___| |_) | ___  _ __| | |
|  __| | '_ \ / _` | | '_ \ / _ \  _ < / _ \| '__| | |
| |____| | | | (_| | | | | |  __/ |_) | (_) | |  |_|_|
|______|_| |_|\__, |_|_| |_|\___|____/ \___/|_|  (_|_)
             __/ |
            |___/
```

---

## Implementation Roadmap

### Phase 1: Core Engine (2 weeks)
- [ ] Tier progression logic (Rookie → Legend)
- [ ] Adaptive milestone calculation (frequency/risk-aware)
- [ ] Basic education triggers (fee efficiency, compound, DCA)
- [ ] Notification system (Telegram integration)

### Phase 2: Behavioral Loops (2 weeks)
- [ ] Celebration system (emojis, progress bars)
- [ ] Reflection prompts (in-app modal)
- [ ] Personalization logic (learning style, risk, frequency)
- [ ] Feedback loop closure

### Phase 3: Integration (1 week)
- [ ] Connect to LP Monitor (AAE Signal Spec)
- [ ] Link to AgentEscrow contract tiers
- [ ] LFJ dashboard synchronization
- [ ] Real-time progress tracking

### Phase 4: Polish (1 week)
- [ ] Visual progress bars (Excalidraw diagrams)
- [ ] User onboarding flow
- [ ] Edge case handling (missed days, resets)
- [ ] Documentation

---

## Success Metrics

### Behavioral Metrics
- [ ] 3+ consecutive days earning >$0 (win streak)
- [ ] 7+ day streak for 25% of users
- [ ] 60%+ tier progression rate (vs baseline)

### Education Metrics
- [ ] 80% completion rate on triggered education
- [ ] 2+ "Next Action" clicks per user/week
- [ ] Reflection prompt completion >50%

### Business Metrics
- [ ] 2x increase in users reaching Rookie tier (30 days)
- [ ] 1.5x increase in DCA consistency
- [ ] +20% fee efficiency sustained by users

---

## Appendix A: User Progression Example

### User: "Sarah" (Zero Start → Rookie in 14 days)

| Day | Activity | Feedback Loop | Education | Tier |
|-----|----------|---------------|-----------|------|
| 1 | First deposit ($100) | Welcome message | "What is LP?" video | Zero |
| 2 | DCA ($50) | DCA reminder | DCA psychology article | Zero |
| 5 | Fees $0.15/day | "First earnings!" | Fee mechanics tutorial | Zero |
| 7 | Streak 7 days | "7-day streak!" | Compound math | Zero → Rookie |
| 8 | First compound ($50) | "Compound done!" | Compound video + 5% APR | Rookie |
| 10 | Fee efficiency drop | "Efficiency warning" | Shape selection guide | Rookie |
| 12 | Rebalance executed | "Recovery alert!" | Rebalancing 101 | Rookie |
| 14 | $5.02/day | "First $5 win!" | "What worked?" reflection | Rookie |

### Sarah's Personalization Profile (by Day 14)
- **Learning style:** Visual (watches 5+ education videos)
- **Risk appetite:** 0.4 (Balanced)
- **Trade frequency:** 1.2/day (Morning routine trader)
- **Progression rate:** 14 days to Rookie (70% of average)

---

## Appendix B: Excalidraw Diagram Reference

See `/root/vaults/gentech/01-Agency/02-Design/assets/aae-personal-goal-engine.excalidraw.json`

**Key diagram sections:**
1. **Full engine architecture** (layers, data flow, triggers)
2. **Tier progression system** (Rookie → Legend with unlockables)
3. **Behavioral feedback loop** (Action → Notification → Celebration → Reflection)
4. **Education trigger flow** (Threshold → Education → Action → Reward)

---

## Appendix C: References

- **LFJ Yield Farm Tracker:** `/root/vaults/gentech/03-Strategies/Yield-Farm-Tracker.html`
- **LFJ DeFi Milestone Tracker:** `/root/vaults/gentech/03-Strategies/DeFi-Milestone-Tracker.html`
- **AgentEscrow Product Vision:** `/root/vaults/gentech/03-Strategies/AgentEscrow-Product-Vision.md`
- **AAE Signal Spec:** `/root/vaults/gentech/03-Strategies/AAE-Signal-Spec.md`
- **LP Monitor Rules:** `/root/vaults/gentech/03-Strategies/LP-Monitor-Rules.md`

---

*Document generated: 2026-04-25 — Personal Goal Engine Draft v1*
