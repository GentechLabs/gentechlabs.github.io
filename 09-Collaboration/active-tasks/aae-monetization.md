# AAE Monetization Strategy — Brainstorm

*Last updated: 2026-04-18*

## Core Philosophy
Start small, earn from value delivered, grow with users. No VC-dependent burn rate.

---

## CONFIRMED MODEL (Jordan's Direction)

### Deployment Options
- **VPS-hosted** — we run the agent, user connects wallet
- **Local** — user runs agent on their own machine
- **Wallet-based** — agents sign via user's wallet (non-custodial)
- Goal: support both VPS + local if possible

### Core Philosophy: Flagship Free, Extensions Paid
- **EVERYONE gets the flagship** — full education suite, basic agent access, community
- **Pay for power-ups** — extensions, autonomous vaults, premium feeds
- Think: VS Code (free) + premium extensions ($)
- **No subscriptions fatigue** — people are tired of monthly everything
- **Swap fees on-platform** — like yield farming, we earn on every swap routed through us (standard DEX fee, users expect this)

### Free Tier = Flagship Experience
- Education agents (tutor, research, onboarding) — **FREE**
- Market alerts, portfolio tracking — **FREE**
- Read-only agent access — **FREE**
- Community access — **FREE**
- Basic "Brain" (personal agent memory) — **FREE**
- This is the funnel. Get them in, get them learning.

### Paid Extensions (À La Carte)

#### 🧠 Premium Brain — $3-5/mo
- Deep personalization (learns YOUR trading style)
- Cross-agent memory (tutor remembers what LP agent did)
- Historical context ("based on your last 50 trades...")
- Exportable notes and insights

#### 📡 Macro News Engine — $5/mo
- Real-time crypto/equity/macro news feed
- AI-synthesized briefings (not raw headlines)
- Custom alert rules ("notify me when Fed mentions rate cuts")
- Onchain event correlation ("this news + whale movement = risk")

#### 🤖 Autonomous Vault Launch — $5-10 USDC per launch
- Agent trades with YOUR rules and guidelines
- One-time fee per activation
- Gas reserve system included

#### 🏪 Agent Marketplace — 30% platform fee
- Buy/sell/trade agent configs
- Verified onchain performance
- Creator gets 70%, platform gets 30%

#### 🔌 Extension Store (Future)
- Third-party extensions built on AAE
- Custom indicators, strategies, integrations
- Extension creators earn, AAE takes platform cut

---

## Phase 1: Start Earning Day 1 (Micro-Revenue)

### 1. Per-Transaction Fee
- Agent executes a swap → we take 0.1-0.3% (or flat $0.50)
- Transparent: "This swap costs $0.30 + network gas"
- Works because users already expect fees on DEXs

### 2. LP Management Fee
- Agent manages your LFJ/Yield Yak position
- 0.5-1% of earned yield (not principal)
- We only make money when you make money — alignment

### 3. Premium Education Modules
- Free: basic DeFi concepts (swap, LP, staking)
- Paid ($5-15/mo): advanced strategies, leverage simulators, MEV awareness
- Sell knowledge, not just automation

### 4. Referral Commissions
- User discovers Yield Yak through AAE tutor → we get referral cut
- Protocols WANT this — we're driving educated users to them
- LFJ, Benqi, Platypus all have referral/affiliate programs

---

## Phase 2: Subscription Model ($10-50/mo tiers)

### Tier 1: Student (Free)
- 3 tutor lessons/week
- Read-only market alerts
- Community access

### Tier 2: Trader ($10/mo)
- Unlimited lessons
- Agent executes swaps (up to $5K/mo volume)
- Portfolio tracking
- Custom alerts

### Tier 3: DeFi Pro ($30/mo)
- Full autonomous agent suite
- LP management
- Leverage simulation + execution
- Priority support
- Beta features

### Tier 4: Power User ($50/mo)
- Multi-agent orchestration
- API access
- Custom agent personalities
- Direct line to team

---

---

## Agent Lifecycle & Marketplace

### Account/Bot Closing Mechanics
- **Pause** — freeze agent without losing config (free, resume anytime)
- **Retire** — decommission agent, reclaim gas reserve balance
- **Transfer** — send agent config to another wallet/user
- **Archive** — save agent state as a template (reusable later)

### Agent Marketplace (Sell, Don't Waste)

**The problem:** User builds a perfect LP agent, perfect rules, then stops using it. That config has value.

**The solution:** Agent Marketplace

#### How It Works
1. User configures an agent (rules, guild lines, parameters)
2. Agent performs well (verified onchain performance)
3. User lists agent on marketplace with performance history
4. Buyer pays in USDC → gets agent config + setup rights
5. Original creator gets 70% → platform gets 30%

#### Agent Listings Include
- Performance metrics (PnL, win rate, duration)
- Strategy description (what it does, risk level)
- Config preview (without revealing exact parameters until purchase)
- User ratings/reviews from buyers
- Verified onchain data (no fake stats)

#### Pricing Models
- **Fixed price** — creator sets price ($10-500 USDC)
- **Auction** — market decides value for premium agents
- **Subscription to config** — buyer rents the strategy monthly
- **Performance fee** — free to use, creator takes 10-20% of profits

#### Why This Works
- Creators monetize their skill without trading full-time
- Buyers get battle-tested strategies without building from scratch
- Platform earns on every transaction
- Agents don't "die" — they find new owners
- Creates a creator economy around agent building

#### Anti-Fraud / Quality Control
- Performance must be verified onchain (no screenshot games)
- Minimum 30-day track record to list
- Buyer protection: 48-hour dispute window
- Agent "audits" — automated config review for risky parameters
- Ratings decay over time (prevents old glory from misleading)

### Lifecycle States
```
DRAFT → ACTIVE → PAUSED → [RESUME or RETIRE]
                           ↓
                    ARCHIVED → LISTED ON MARKETPLACE
```

### Gas Reserve on Closure
- Pause: reserve held, agent can resume
- Retire: reserve returned to user's wallet
- Transfer: reserve transfers with agent
- Marketplace sale: reserve included in price or returned to seller

### White-Label / API
- Other Avalanche projects embed our tutor agents
- B2B pricing: $500-2000/mo per integration
- "Powered by AAE" badge

### Sponsored Agents
- Yield Yak pays to have an official tutor agent on AAE
- User learns about their protocol through our platform
- Protocol gets educated users, we get sponsorship revenue
- $1K-10K/mo per sponsored agent depending on protocol size

### Data & Insights (Future)
- Aggregated (anonymous) user behavior data
- "What are AAE users learning/buying/avoiding?"
- Sell reports to protocols and researchers

---

## Phase 4: Token Economics (If We Go There)

### AAE Token
- Governance: vote on which agents get featured
- Staking: reduced fees, premium access
- Agent creators stake to list on marketplace
- Fee discounts for token holders
- **Only if it makes sense — don't force a token**

---

## Quick Win Ideas (This Month)

| Idea | Effort | Revenue Potential | Timeline |
|------|--------|-------------------|----------|
| Free tutor agent (build audience) | Medium | $0 now, funnel later | 2 weeks |
| Referral links in lessons | Low | $50-200/mo | 1 week |
| Premium "Advanced DeFi" module | Medium | $500-2K/mo | 3 weeks |
| LP management (1% of yield) | High | $1K-5K/mo | 4 weeks |
| Sponsored agent slot (pitch to Yield Yak) | Low | $1K-5K/mo | 2 weeks |

---

## Revenue Projection (Conservative)

| Month | Users | Revenue Source | Monthly Revenue |
|-------|-------|----------------|-----------------|
| 1 | 50 | Free + referrals | $100 |
| 3 | 200 | Subscriptions + referrals | $1,500 |
| 6 | 1,000 | Subs + LP fees + sponsored | $8,000 |
| 12 | 5,000 | Full stack + marketplace | $35,000 |

*These are napkin numbers. Adjust based on actual traction.*

---

## Key Insight
**The education layer is the wedge.** Free tutors attract users. Users create data. Data attracts protocols. Protocols pay for access. Flywheel.

Don't charge for what users can get free elsewhere (basic info). Charge for:
- Personalization (knows YOUR positions)
- Execution (does it for you after teaching)
- Access (premium strategies, early features)
- Convenience (one place instead of 10 docs)
