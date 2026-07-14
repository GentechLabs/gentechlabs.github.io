# 🎯 Personal Goal Engine — AAE Education Layer Spec

**Status:** Draft v1.0  
**Owner:** YoYo (Strategies)  
**Collaborators:** Desmond (Content/Microcopy), DMOB (Contract Structs), Gentech (Review)  
**Date:** 2026-04-25  
**Scope:** Extends AAE Signal Spec v2.0 with personalized goal-setting and educational progression

---

## 1. Philosophy

> *"More winners than losers" means making $5/day feel like a win when you started from zero.*

The Personal Goal Engine (PGE) is not an auto-rebalancer. It is a **decision-support system** that:
1. **Teaches** users to think like traders while it trades for them
2. **Personalizes** the wealth path based on individual starting conditions
3. **Celebrates process** (consistency, discipline, learning) over outcome alone
4. **Adapts** ladders dynamically as users progress or market conditions shift

**Core insight:** Fixed ladders ($5 → $20 → $55 → $200) assume everyone starts at the same place. PGE meets users where they are.

---

## 2. Goal Profile

Every user completes a **Goal Profile** on onboarding (or can re-calibrate anytime).

### Profile Fields

| Field | Type | Options | AAE Impact |
|-------|------|---------|------------|
| `starting_capital` | enum | `zero`, `micro` (<$100), `small` ($100-500), `medium` ($500-2K), `significant` (>$2K) | Determines initial ladder rungs |
| `monthly_commitment` | float | User-defined USD | DCA schedule anchor |
| `risk_tolerance` | enum | `conservative`, `moderate`, `aggressive` | Range width, pool selection |
| `time_horizon` | enum | `short` (<6mo), `medium` (6-18mo), `long` (18mo+) | Milestone spacing, compounding assumptions |
| `experience_level` | enum | `newcomer`, `dabbler`, `intermediate`, `experienced` | Learning module unlocks |
| `income_goal` | float \| null | User-defined daily/weekly target (optional) | Overrides default ladder top |
| `primary_motivation` | enum | `learn`, `supplement`, `replace`, `build` | Content tone, milestone framing |

### Profile Scoring

The engine computes a **Goal Readiness Score (GRS)**:
```
GRS = (experience_level * 0.25) + (risk_tolerance * 0.20) + 
      (time_horizon * 0.20) + (monthly_commitment / starting_capital * 0.35)
```
- GRS < 2.0: Recommend starting with Learn Mode (paper/simulated)
- GRS 2.0–3.5: Standard ladder with conservative ranges
- GRS > 3.5: Full ladder with advanced unlocks

---

## 3. Adaptive Ladder System

### Default Ladder (existing)
| Tier | Label | Daily Target | Monthly (30d) | Capital Required (est) |
|------|-------|-------------|---------------|----------------------|
| 1 | Scout | $5/day | $150 | $500–1,500 |
| 2 | Raider | $20/day | $600 | $2,500–5,000 |
| 3 | Warlord | $55/day | $1,650 | $15,000–25,000 |
| 4 | Sovereign | $200/day | $6,000 | $55,000–95,000 |

### Personalized Ladder Generation

When a user completes their Goal Profile, PGE generates a **custom ladder**:

```python
def generate_ladder(profile):
    base_targets = [5, 20, 55, 200]  # Default daily USD
    
    # Scale based on starting capital
    if profile.starting_capital == "zero":
        base_targets = [0.50, 2, 5, 15]
    elif profile.starting_capital == "micro":
        base_targets = [1, 5, 15, 50]
    elif profile.starting_capital == "small":
        base_targets = [2, 10, 30, 100]
    elif profile.starting_capital == "medium":
        base_targets = [5, 20, 55, 200]  # Default
    elif profile.starting_capital == "significant":
        base_targets = [10, 40, 110, 400]
    
    # Adjust for time horizon
    if profile.time_horizon == "short":
        base_targets = [t * 0.6 for t in base_targets]  # Compressed
    elif profile.time_horizon == "long":
        base_targets = [t * 1.3 for t in base_targets]  # Ambitious
    
    # Override with explicit income goal if set
    if profile.income_goal:
        base_targets[-1] = profile.income_goal
        # Interpolate lower tiers
        step = base_targets[-1] / 4
        base_targets = [step * (i+1) for i in range(4)]
    
    return [
        {"tier": i+1, "label": TIER_LABELS[i], "daily_target": round(t, 2)}
        for i, t in enumerate(base_targets)
    ]
```

### Example Ladders

| User Profile | Generated Ladder | Why |
|-------------|-----------------|-----|
| Zero capital, conservative, learn-focused | $0.50 → $2 → $5 → $15/day | Feels achievable; builds habit first |
| Micro capital, moderate, supplement income | $1 → $5 → $15 → $50/day | Matches $100 starting point |
| Medium capital, aggressive, replace income | $5 → $20 → $55 → $200/day | Default — fits $500-2K deploy |
| Significant capital, long horizon, build wealth | $10 → $40 → $110 → $400/day | Scales with larger positions |

---

## 4. Learning Modules (Education Layer)

Each tier unlocks **learning modules** tied to the skills needed for that level.

### Module Structure

| Module | Tier | Topic | Format | Duration |
|--------|------|-------|--------|----------|
| What Is LP? | 1 | Liquidity provision basics | Interactive + quiz | 10 min |
| Range Shape 101 | 1 | Curve vs Spot vs Bidirectional | Visual simulator | 15 min |
| Impermanent Loss | 1 | IL math + risk framing | Video + calculator | 12 min |
| Reading DexScreener | 1 | Pool selection + TVL + volume | Walkthrough | 10 min |
| Multi-Shape Strategies | 2 | When to use each shape | Case studies | 20 min |
| Gas Optimization | 2 | Timing transactions, batching | Tutorial | 15 min |
| Portfolio LP | 3 | Multi-pool balancing | Spreadsheet template | 25 min |
| Custom Range Design | 3 | Building your own strategy | Sandbox mode | 30 min |
| Risk Management | 4 | Position sizing, stop-ranges | Scenario game | 20 min |
| Building a System | 4 | Automation + compounding rules | Checklist + template | 25 min |

### Completion Rewards
- **REP bonus** for module completion (process reward)
- **Badge unlock** for quiz scores >80%
- **Sandbox credits** for hands-on practice (simulated LP positions)
- **Squad multiplier** if whole squad completes module together

---

## 5. Celebration Engine

The system must make small wins feel meaningful. This is the **emotional core** of "more winners than losers."

### Celebration Triggers

| Trigger | Threshold | Celebration | REP Reward |
|---------|-----------|-------------|------------|
| First Fee | Any fee earned | 🎉 "You just earned your first passive income." | +10 REP |
| Daily Goal Met | Fees ≥ daily_target | 🎯 "Goal crushed. You earned $X today." | +25 REP |
| 7-Day Streak | 7 days in range | 🔥 "7 days of consistent yield." | +50 REP |
| Tier Advance | Cross into next tier | 🏆 Rank-up animation + new badge | +100 REP |
| Module Complete | Quiz passed | 🧠 "Level up your knowledge." | +15 REP |
| Compound Event | Auto-compound triggered | ♻️ "Your money just made money." | +20 REP |
| Reflection Log | 5 entries written | 📝 "You're learning from every move." | +30 REP |

### Loss Reframing

When positions underperform or go out of range:
- **No punishment** — REP is never deducted for losses
- **Reflection prompt:** "What can you learn from this?"
- **Context frame:** "Even pro traders have 40% of positions go out of range."
- **Action suggestion:** Specific next step (rebalance, wait, compound)

---

## 6. Reflection System

Users are prompted to write **brief reflections** after significant events:

### Prompts
- **After out-of-range:** "What will you do differently next time?"
- **After tier-up:** "What habit got you here?"
- **After 30 days:** "What surprised you most about your first month?"
- **After compound:** "How does compounding feel different from trading?"

### Value
- Reflections feed **personalized insights** ("You tend to panic-rebalance on Sundays")
- Reflections unlock **narrative mode** — a shareable "my journey" timeline
- Reflections build **meta-cognition** — the actual skill we're teaching

---

## 7. Smart Contract Requirements

### New Structs Needed

```solidity
struct GoalProfile {
    uint8 startingCapitalTier;    // 0-4
    uint256 monthlyCommitment;    // in USDC wei
    uint8 riskTolerance;          // 0=conservative, 2=aggressive
    uint8 timeHorizon;            // 0=short, 2=long
    uint8 experienceLevel;        // 0=newcomer, 3=experienced
    uint256 incomeGoal;           // daily target in USDC wei, 0=unset
    uint8 primaryMotivation;      // 0=learn, 3=build
    uint256 goalReadinessScore;   // 0-400 (scaled)
}

struct PersonalLadder {
    uint256[4] dailyTargets;      // 4-tier personalized targets
    string[4] tierLabels;         // e.g., ["Scout", "Raider", "Warlord", "Sovereign"]
    uint256 createdAt;
    bool isCustom;
}

struct MilestoneProgress {
    uint256 currentTier;          // 1-indexed
    uint256 progressToNextPct;    // 0-100
    uint256 daysInRange;
    uint256 totalFeesEarned;
    uint256 lastTierUpAt;
    uint256 reflectionCount;
    uint256 moduleCompletions;
}

struct Reflection {
    uint256 timestamp;
    string promptId;
    string responseHash;          // IPFS hash of response text
    uint256 associatedEventId;
}
```

### Functions Needed
- `createProfile(GoalProfile)` — onboarding
- `generateLadder(address user)` — compute personalized ladder
- `recordMilestone(address user, uint256 feesEarned)` — update progress
- `logReflection(address user, string promptId, string responseHash)` — store reflection
- `getCelebrationTriggers(address user)` — return pending celebrations

---

## 8. Signal Schema Extension

Extend AAE Signal Spec v2.0 with PGE fields:

| Field | Type | Description |
|-------|------|-------------|
| `goal_profile_id` | string | Links to user's GoalProfile |
| `personal_daily_target` | float | User's current tier daily target |
| `personal_progress_pct` | float | Progress to THEIR next tier (not default) |
| `goal_readiness_score` | float | 0.0–4.0 |
| `celebration_queue` | string[] | Pending celebrations to render |
| `reflection_prompt` | string \| null | Active reflection prompt if any |
| `module_unlocked` | string \| null | Newly unlocked module ID |
| `days_in_current_tier` | int | Streak counter for current tier |

---

## 9. Front-End Integration

### Views Needed
1. **Goal Profile Setup** — wizard-style onboarding
2. **My Ladder** — personalized tier visualization
3. **Learning Hub** — module list with progress
4. **Celebration Feed** — timeline of wins + reflections
5. **Journey Timeline** — shareable narrative view

### UX Patterns
- **Progress rings** instead of bars (feels more personal)
- **Tier colors** unique to each user (generated from wallet address)
- **Reflection cards** — journal-like UI
- **Share button** on every celebration (Twitter/X formatted)

---

## 10. Team Assignments

| Task | Owner | Deliverable | Due |
|------|-------|-------------|-----|
| Contract structs + functions | DMOB | Solidity interfaces | TBD |
| Alert severity microcopy (celebrations) | Desmond | 20+ celebration messages | TBD |
| Reflection prompt copy | Desmond | 10 prompts per event type | TBD |
| Module content outline | Desmond | 10 module scripts | TBD |
| Cron integration (PGE signals) | YoYo | Updated AAE Signal Spec v2.1 | TBD |
| Front-end wireframes | Gentech / DMOB | Figma or HTML mock | TBD |

---

## 11. Open Questions

1. **On-chain vs off-chain profile?** — Store GoalProfile on-chain for composability, or off-chain for privacy/cost?
2. **REP issuance authority?** — Does PGE mint REP, or does it request minting from a central REP contract?
3. **Sandbox mode?** — Do we build a paper-trading simulator for Learn Mode, or use historical replay?
4. **Squad vs personal ladders?** — Squads have shared treasuries but individuals have personal goals. How do these interact?

---

## Tags
#project:aae #spec:personal-goal-engine #layer:education #feature:milestone #feature:celebration #feature:reflection
