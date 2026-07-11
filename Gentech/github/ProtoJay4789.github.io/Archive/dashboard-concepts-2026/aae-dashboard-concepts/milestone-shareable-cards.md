# Milestone Shareable Cards

> Auto-generated cards when squads hit tier promotions, compound milestones, or streak achievements.
> Designed for Twitter/X, Instagram, LinkedIn, and Telegram.

---

## Card Types

### Type A: Tier Promotion
**Trigger:** Daily fees cross tier threshold
**Vibe:** Celebration, achievement, unlocking power

### Type B: Compound Milestone
**Trigger:** Cumulative fees hit $50, $100, $250, $500, $1000
**Vibe:** Growth, momentum, snowball effect

### Type C: Streak Achievement
**Trigger:** 7, 30, 90, 180 days in range
**Vibe:** Discipline, reliability, consistency

### Type D: Squad Formation
**Trigger:** First squad member joins, squad reaches 5/10 members
**Vibe:** Community, teamwork, stronger together

---

## Card Template: Tier Promotion

### Layout (Square — 1080×1080)
```
+----------------------------------+
|  [Animated badge — large]        |
|                                  |
|     🏆 SQUAD PROMOTED            |
|                                  |
|       SCOUT → RAIDER             |
|                                  |
|   "You earn while others sleep"  |
|                                  |
|  New unlocks:                    |
|  ✅ SPOT shape                   |
|  ✅ BIDIRECTIONAL shape          |
|  ✅ Strategy comparison tool     |
|                                  |
|  $20/day target achieved         |
|  Squad: Alpha Wolves             |
|                                  |
|  [AAE — Squad Treasury]         |
+----------------------------------+
```

### Color by Tier
| From → To | Gradient |
|------------|----------|
| Scout → Raider | Bronze → Silver |
| Raider → Warlord | Silver → Gold |
| Warlord → Sovereign | Gold → Platinum |

### Copy Variants

**Twitter/X (short):**
> 🏆 Squad promoted: Scout → Raider
> 
> $20/day target ✅
> Unlocked: SPOT + BIDIRECTIONAL
> 
> DeFi hits different when you run it as a squad.
> 
> #AAE #DeFi #SquadTreasury

**LinkedIn (professional):**
> Milestone unlocked: Our squad just promoted to Raider tier in the AAE Squad Treasury system.
>
> What this means:
> • $20/day estimated fee generation ✅
> • Access to SPOT and BIDIRECTIONAL liquidity strategies ✅
> • Strategy comparison tools for data-driven decisions ✅
>
> Started at Scout ($5/day) three weeks ago. The compound effect is real.
>
> #DeFi #LiquidityMining #Web3 #PassiveIncome

**Instagram (visual-focused):**
> ✨ SQUAD PROMOTED ✨
>
> Scout → Raider
>
> $20/day ✅
> New strategies unlocked 🔐
>
> Swipe to see what we unlocked →
>
> #defi #crypto #passiveincome #web3 #squad

---

## Card Template: Compound Milestone

### Layout
```
+----------------------------------+
|  [Growing plant / snowball anim]  |
|                                  |
|     🔄 COMPOUND MILESTONE        |
|                                  |
|       $500 FEES EARNED           |
|                                  |
|  Position growth:                |
|  $83.92 → $127.50 (+52%)        |
|                                  |
|  Total compounds: 12             |
|  Days tracked: 89                |
|                                  |
|  "Each compound builds the next" |
|                                  |
|  [AAE — Squad Treasury]         |
+----------------------------------+
```

### Milestone Triggers
| Milestone | Badge | Copy Hook |
|-----------|-------|-----------|
| $50 | Seedling | "First compound — the snowball starts" |
| $100 | Sprout | "Doubled. Momentum building." |
| $250 | Sapling | "$250 in fees. Position growing." |
| $500 | Tree | "Halfway to a grand. Keep stacking." |
| $1,000 | Redwood | "$1K in fees earned. This is working." |
| $5,000 | Forest | "$5K. Your squad is a machine." |

---

## Card Template: Streak Achievement

### Layout
```
+----------------------------------+
|  [Fire emoji / flame trail]      |
|                                  |
|     🔥 30-DAY STREAK            |
|                                  |
|     IN RANGE FOR 30 DAYS         |
|                                  |
|  Squad: Alpha Wolves             |
|  Pool: AVAX/USDC                 |
|  Fees earned: $47.30             |
|  Efficiency avg: 78%             |
|                                  |
|  "Consistency beats intensity"   |
|                                  |
|  [AAE — Squad Treasury]         |
+----------------------------------+
```

### Streak Tiers
| Days | Badge | Copy |
|------|-------|------|
| 7 | 🔥 Spark | "1 week in range. The habit is forming." |
| 30 | 🔥 Flame | "30 days. Your range discipline is solid." |
| 90 | 🔥 Inferno | "90 days. You’re a machine." |
| 180 | 🔥 Eternal | "6 months. Unstoppable." |

---

## Card Template: Squad Formation

### Layout
```
+----------------------------------+
|  [Squad avatars in circle]       |
|                                  |
|     SQUAD ASSEMBLED              |
|                                  |
|     5 MEMBERS STRONG             |
|                                  |
|  Total pooled: $420.00           |
|  Position power: 5x solo         |
|  Gas efficiency: MAX             |
|                                  |
|  "Solo you survive.             |
|   Squad you thrive."             |
|                                  |
|  [AAE — Squad Treasury]         |
+----------------------------------+
```

### Formation Tiers
| Members | Badge | Copy |
|---------|-------|------|
| 2 | Duo | "First ally joined. The squad begins." |
| 5 | Crew | "5 members. Positions getting serious." |
| 10 | Squad | "Full squad. Capital deployed." |
| 25 | Battalion | "25 strong. You’re an army." |

---

## Technical Specs

### Static Cards (PNG)
- Resolution: 1080×1080 (square), 1080×1920 (story)
- Format: PNG with transparency for badge overlays
- File size: <500KB each
- Font: Inter Bold (headlines), Inter Regular (body)

### Dynamic Cards (SVG)
- Template-based with text injection
- Badge color changes based on tier
- Progress bars animate on load
- Exportable to PNG via headless browser

### Animated Cards (MP4/GIF)
- 3-second loop
- Badge pulse, confetti burst on promotion
- Progress bar fill animation
- Resolution: 720×720 (GIF), 1080×1080 (MP4)

---

## Auto-Generation Logic

```python
def should_generate_card(event_type, data):
    if event_type == "TIER_PROMOTION":
        return True  # Always generate
    elif event_type == "COMPOUND_MILESTONE":
        return data["cumulative_fees"] in [50, 100, 250, 500, 1000, 5000]
    elif event_type == "STREAK":
        return data["days_in_range"] in [7, 30, 90, 180]
    elif event_type == "SQUAD_FORMATION":
        return data["member_count"] in [2, 5, 10, 25]
    return False

def generate_card(event_type, data, format="png"):
    template = load_template(event_type)
    template.fill(data)
    return template.render(format)
```

---

## Share Flow

1. **Event triggers** (promotion, milestone, streak, formation)
2. **Card auto-generates** (stored in `~/.hermes/media/cards/`)
3. **Bot sends to squad Telegram** with "Share your win?"
4. **One-tap share** to Twitter/X, Instagram, LinkedIn
5. **Referral link embedded** (invite to join squad)

---

## Hashtag Sets

**Tier Promotion:**
`#AAE #SquadTreasury #DeFi #LiquidityMining #Web3 #PassiveIncome #Crypto #SquadGoals`

**Compound Milestone:**
`#CompoundEffect #DeFi #Crypto #PassiveIncome #WealthBuilding #SquadTreasury #AAE`

**Streak:**
`#Consistency #DeFi #Crypto #HODL #SquadTreasury #Streak #AAE`

**Squad Formation:**
`#SquadUp #DeFi #Web3 #Community #SquadTreasury #AAE #Crypto`

---

**Tags:** #aae #shareable #cards #social #milestones #content
