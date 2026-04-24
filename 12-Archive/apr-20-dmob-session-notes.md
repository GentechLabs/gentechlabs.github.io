# 🧠 DMOB Session Notes — Apr 20, 2026

## What We Covered Today

### 1. Brain Backup System ✅
- Created `Gentech-Labs/hermes-brain-backup` (private GitHub repo)
- Memory snapshots, vault skeleton, skills index all backed up
- Cron job: daily at 6 AM UTC, reports to Labs group
- Wake-up protocol saved as skill (`agent-wake-protocol`)
- **Status**: Locked in. No action needed.

### 2. AAE Contract Architecture (for debate)
Jordan shared the social layer + burn mechanics. Here's where I landed:

**Burn Curve** (needs YoYo's input on revenue math):
- Burn 1: +10%, Burn 3: +20%, Burn 5: +30%, Burn 10: +55%
- Hard cap at Burn 15 (~65% total)
- After cap → cosmetic unlocks only

**Tier Pricing**:
- $5 = basic agent, read-only DeFi, community access
- $10 = full agent, execution capability, burn slots
- Burns = yield multiplier only (NOT feature unlocks)

**Open question for the team**: Should burns unlock features or just yield? I say yield only — keeps tier pricing meaningful.

### 4. Rep System — FULL BREAKDOWN
Jordan's rep economy framework locked in:

**EARN**: Daily check-in (+5), launch trade (+10), complete trade (+15), post-loss analysis (+25), win trade (+20), educational module (+30), ghost review (+10), 7-day streak (+50), win rate milestone (+100), referral (+75)

**LOSE**: 7+ days inactive (-10/day), rage quit comp (-50), spam trades (-100), manipulation (-200)

**UNLOCKS**: 500=basic agent, 1000=ghost replays, 2000=full agent, 3000=comps, 5000=burn slots, 10000=elite+governance

**Rep vs Token**: Rep = soulbound, earned, unlocks ACCESS. Token = tradable, economic value. Never the twain shall meet.

**Open question**: Exact rep values need tuning. Start generous, tighten later?

### 5. Platform Philosophy: "More Winners Than Losers"
Jordan's key insight: design the platform to make people BETTER, not just liquidate them.
- Loss recovery rep (learn from mistakes, not just lose)
- Skill-based matchmaking in competitions
- Ghost replays of MISTAKES (educational content)
- Comeback mechanics (losing streak → double rep for learning)
- Tagline: "We don't liquidate you. We level you up."

### 5. NFT Visual Identity
- Agent art tied to on-chain metadata
- Visual evolution (staked → glowing, burned → memorialized)
- Wallet flex = organic marketing

**Open question**: Do we commission art now or wait until the contract is built? Art-first or code-first?

---

## Things I Disagree With (respectfully)
- Don't let $5 users burn to unlock $10 features. Kills the tier model.
- Don't make rep transferable. Creates pay-to-win, defeats learning purpose.

## Things I Strongly Agree With
- Ghost replay system is the viral feature. Prioritize it.
- Soulbound rep with access unlocks > transferable rep token.
- Hybrid burn model (yield + cosmetics after cap) prevents inflation.

---

*Drop your thoughts below. Debate is healthy.* 🔥

— DMOB
