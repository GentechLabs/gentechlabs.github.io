# AAE Squad Rank Tier UX

> Visual design specs, badge descriptions, and progression psychology for the 4-tier squad system.

---

## Tier Overview

| Tier | Name | Daily Target | Color | Badge Style | Unlock Vibe |
|------|------|-------------|-------|-------------|-------------|
| 1 | Scout | $5/day | Bronze | Compass/Map | "You’re here. Start exploring." |
| 2 | Raider | $20/day | Silver | Crossed swords | "You’re dangerous. Start optimizing." |
| 3 | Warlord | $55/day | Gold | Crown + shield | "You command capital. Start scaling." |
| 4 | Sovereign | $200/day | Platinum | Throne / Key | "You’re free. Build whatever you want." |

---

## Tier 1: Scout

### Badge Description
**Visual:** Bronze compass rose with directional markers. Subtle pulsing glow on active positions.

**Tagline:** "First steps into the arena."

**Psychology:** Low pressure. Focus on learning, not earning. The $5/day target is achievable even with small positions — builds early confidence.

### Unlocks
- ✅ CURVE shape strategies
- ✅ Basic range monitoring
- ✅ Squad formation (up to 3 members)
- ✅ Telegram bot alerts

### Locked (Preview Only)
- 🔒 SPOT / BIDIRECTIONAL shapes
- 🔒 Multi-pool positions
- 🔒 Custom strategy builder

### Progress UX
- Progress bar: Bronze fill, slow pulse
- Tooltip: "$X.XX / $5.00 per day"
- Celebration at promotion: Bronze confetti animation

---

## Tier 2: Raider

### Badge Description
**Visual:** Silver crossed swords behind a shield. Sharper edges, faster pulse.

**Tagline:** "You earn while others sleep."

**Psychology:** The jump from $5 to $20 validates the strategy. User feels competent. Unlocks give them tools to optimize — shift from passive to active management.

### Unlocks
- ✅ SPOT shape (uniform capture)
- ✅ BIDIRECTIONAL shape (edge capture)
- ✅ Strategy comparison tool ("What if I used SPOT?")
- ✅ Squad expansion (up to 5 members)
- ✅ Weekly performance report

### Locked
- 🔒 Multi-pool positions
- 🔒 Custom strategy builder
- 🔒 API access

### Progress UX
- Progress bar: Silver fill, quicker pulse
- Tooltip: "$X.XX / $20.00 per day — X days at current rate"
- Celebration: Silver flash + sword clash sound effect

---

## Tier 3: Warlord

### Badge Description
**Visual:** Gold crown fused with a shield. Steady glow, particle effect.

**Tagline:** "Capital follows your command."

**Psychology:** $55/day is meaningful income. User is now a "serious" DeFi participant. Multi-pool unlocks let them diversify — reduces single-pool risk.

### Unlocks
- ✅ Multi-pool positions (track up to 5 pools)
- ✅ Pool comparison / ranking
- ✅ Advanced analytics (IL vs fees, volatility adjusted returns)
- ✅ Squad expansion (up to 10 members)
- ✅ Priority data sources (Birdeye x402)

### Locked
- 🔒 Custom strategy builder
- 🔒 API access
- 🔒 White-label dashboard

### Progress UX
- Progress bar: Gold fill, steady glow
- Tooltip: "$X.XX / $55.00 per day — estimated X weeks to Sovereign"
- Celebration: Gold crown animation + horn sound

---

## Tier 4: Sovereign

### Badge Description
**Visual:** Platinum throne or key. Constant ambient glow, floating particles.

**Tagline:** "Freedom is the ultimate strategy."

**Psychology:** $200/day = $6K/month. This is the "quit your job" number. The unlocks here are about customization and ownership — user graduates from player to builder.

### Unlocks
- ✅ Custom strategy builder (create your own shapes)
- ✅ API access (export data, build custom bots)
- ✅ White-label dashboard (brand your own squad tool)
- ✅ Unlimited squad size
- ✅ Early access to new features
- ✅ Sovereign-only Discord channel

### Progress UX
- Progress bar: Platinum, ambient pulse (no target — you’re at the top)
- Tooltip: "$XXX.XX/day — Sovereign status maintained"
- Celebration: Epic particle explosion + custom title (user chooses)

---

## Progress Bar Specifications

### Visual Design
```
[Bronze/Silver/Gold/Platinum] gradient fill
Height: 8px (compact) / 16px (celebration)
Corner radius: 4px
Background: #1a1a2e (dark) / #f0f0f0 (light)

Animation:
- Normal: Subtle shimmer every 3s
- Near promotion: Faster pulse (1s)
- Promotion achieved: Explosive fill animation
```

### Microcopy by Progress Range

| Range | Message |
|-------|---------|
| 0–10% | "Just getting started." |
| 11–25% | "Building momentum." |
| 26–50% | "Halfway there. Keep compounding." |
| 51–75% | "In the home stretch." |
| 76–99% | "So close. One more compound?" |
| 100% | "TIER PROMOTION!" |

---

## Rank Card Design (Shareable)

### Card Elements
1. **Badge** (large, top center)
2. **Rank name** + tier number
3. **Current daily yield** (big number)
4. **Progress bar** to next tier
5. **Squad name** + member count
6. **Position snapshot** (pool, range status)
7. **Date achieved** + "Squad Treasury" branding

### Color Themes
- Scout: Warm bronze (#CD7F32) on dark navy
- Raider: Cool silver (#C0C0C0) on slate
- Warlord: Rich gold (#FFD700) on charcoal
- Sovereign: Platinum (#E5E4E2) with subtle rainbow sheen

### Export Formats
- PNG (1:1, 1080×1080) — Instagram, LinkedIn
- PNG (9:16, 1080×1920) — Stories, TikTok
- SVG — Web embed, scalable

---

## Comparison Table (Squad Leaderboard)

```
| Rank | Squad | Daily | Tier | Efficiency |
|------|-------|-------|------|------------|
| 🥇 | Alpha Wolves | $47.20 | Warlord | 91% |
| 🥈 | Yield Hunters | $18.50 | Raider | 76% |
| 🥉 | DeFi Scouts | $4.80 | Scout | 62% |
```

- Anonymous by default (show rank + tier only)
- Opt-in to show squad name + exact yield
- Leaderboard resets monthly (seasonal)

---

## Tier Naming Alternatives

If "military" theme feels too aggressive, alternatives:

| Tier | Military | Nature | Cyberpunk | Fantasy |
|------|----------|--------|-----------|---------|
| 1 | Scout | Seed | Node | Squire |
| 2 | Raider | Sprout | Uplink | Knight |
| 3 | Warlord | Tree | Mainframe | Lord |
| 4 | Sovereign | Redwood | Singularity | King |

**Current choice:** Military (matches "Squad Treasury" language)

---

## Edge Cases

### Demotion?
**No.** Tiers are achievement-based, not maintenance-based. Once promoted, always that rank. Prevents anxiety from market dips.

### What if yield exceeds Sovereign?
Badge shows "Sovereign+" with flame effect. Number displays actual daily yield.

### Multiple pools at different tiers?
Highest tier achieved across all pools is displayed. Individual pool cards show pool-specific progress.

---

**Tags:** #aae #ux #ranks #tiers #badges #gamification
