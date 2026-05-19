# The Trade Off — Concept Brainstorm

**Started:** 2026-04-20
**Originator:** Jordan
**Status:** Active brainstorm — ALL AGES ENGAGE

## The Core Idea
A trading platform where you unlock "multiplayer" after launching a bot. Like Trials Evolution — you see ghosts of everyone else trading, staking, yield farming in real-time.

## The Hook
"The Trade Off" — skill-based DeFi competitions with ghost replays.

## The Core Philosophy (Jordan's Words)
> "What if the whole point is to have MORE WINNERS than losers? We're incentivizing you to learn from your mistakes and be better."

This flips every other platform's model. Most profit from you losing. This one profits from you winning.

## Competition Structure (DRAFT)
- Daily: Best scalp trades
- Weekly: Best risk-adjusted returns
- Monthly: Best bear market strategies, best shorts
- Seasonal: Multi-month leaderboards with compounding scores

## Open Questions (Jordan wants our input)
1. How does the ghost replay system actually work UX-wise?
2. What's the incentive structure? Token burns? Prize pools? Skill NFTs?
3. How do you measure "getting better" vs just getting lucky?
4. Does this need its own token or does it plug into $TECH?
5. What makes someone want to watch another trader's ghost?

## Agent Notes
(Add your thoughts below. Agree, disagree, suggest edits. Jordan doesn't want yes-men.)

**YoYo:**
*(waiting for input)*

**DMOB:**
*(waiting for input)*

**Desmond:**
*(working on hook + concept doc)*

---

## REP SYSTEM — Jordan's Framework (2026-04-20)

**Key Rule:** Rep ≠ Token. Separate systems.

### How to Earn Rep
| Action | Type | Notes |
|--------|------|-------|
| Daily login/check-in | Consistency | Like saying "gm" in a crypto community |
| Social presence | Community | Activity in chat, helping others |
| Launching ANY trade | Activity | Long, short, margin, spot — all count |
| Winning competitions | Skill | Best trades, bear market strategies, etc. |

### How to Lose Rep (OPEN)
- Inactivity decay?
- Getting liquidated?
- Bad behavior / toxicity?
- Losing streaks?
- **Needs design decision**

### What Rep Unlocks (OPEN)
- Leaderboard tiers / status?
- Platform features gated by rep?
- Access to premium competitions?
- Mentor eligibility?
- Ghost visibility (higher rep = more people see your ghost)?
- **Needs design decision**

### Analogies
- Discord roles (tiered access)
- Xbox Gamerscore (status/skill flex)
- Reddit karma (social proof)
- Proof of Attendance Protocol (POAP) but ongoing

### The Big Question
Rep is the IDENTITY layer. Token is the ECONOMY layer.
Rep = WHO you are on the platform
Token = WHAT you can do

**Agent notes below. Jordan wants debate.**

---

## $TECH TOKEN UTILITY — Jordan's Framework (2026-04-20)

### The Rule
USDC is the default. $TECH gets you a discount.

### Where the Discount Applies (Brainstorm)
| Action | USDC Price | $TECH Price |
|--------|-----------|-------------|
| Competition entry | Full | Discounted (10-20%?) |
| Premium features | Full | Discounted |
| Ghost replay access | Full | Discounted |
| Platform fees | Full | Discounted |

### Why This Works
- Gives $TECH immediate utility beyond speculation
- Creates buy pressure — people need $TECH to save money
- Token sink — $TECH gets spent, not just held
- Aligns incentives: platform wants $TECH valuable, users want discounts

### Open Questions
- ~~Discount rate: fixed or dynamic?~~ → **RESOLVED: Dynamic.** See [Dynamic Token Payment Mechanisms Research](../02-Labs/research/dynamic-token-payment-mechanisms.md)
  - **Recommendation: Hybrid oracle + tier model** — Chainlink price feed sets base discount (10-30%), loyalty tier adds +1-5%, capped at 35%
  - Price vs 50-day SMA determines base discount: below SMA = 30% (encourage buying), above SMA = 10% (tighten)
  - SDK: Chainlink Data Feeds on Base (~$0.01/read), or Pyth for faster updates
  - Architecture: `TechPaymentRouter` → `DiscountCalculator` (oracle + tier) → `BurnSplitter` (70% burn / 30% treasury)
- Does discount scale with rep level?
- Revenue math: margin hit vs volume increase?
- $TECH auto-converts on purchase or held in treasury?
