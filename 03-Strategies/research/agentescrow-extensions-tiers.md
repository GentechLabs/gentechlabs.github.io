# AgentEscrow — Extension & Tier Model

**Date:** 2026-04-18
**Author:** YoYo (Strategies)
**Status:** Draft — modular pricing design

---

## Core Philosophy

**Everybody gets the flagship.** Pay for extras. Like VS Code — free editor, paid extensions.

Core = free or included with launch fee
Extensions = optional add-ons that enhance your agent

---

## Tier Structure

### 🆓 Free Tier — "Explorer"
- Basic agent chat + Learn Mode
- Manual execution (you approve every trade)
- 5 Learn Mode questions/day
- Community knowledge base access
- Basic portfolio tracking

### ⚡ Launch Tier — $5-10 USDC per bot
- Everything in Free
- Autonomous vault/agent execution
- Custom rules and risk parameters
- Gas fee reserve management
- Agent config export

### 🧠 Extensions — À La Carte Add-ons

| Extension | Price | What You Get |
|-----------|-------|-------------|
| **The Brain** | $3/mo | Persistent memory across sessions, learns your style, adapts explanations |
| **Macro Pulse** | $5/mo | Real-time M2, ISM, inflation feeds (BullTheory-style), market regime alerts |
| **Deep Research** | $4/mo | Multi-agent token analysis, on-chain investigation, audit report parsing |
| **Pro Learn** | $3/mo | Unlimited quiz mode, progress tracking, structured DeFi curriculum |
| **Analytics** | $5/mo | P&L tracking, performance attribution, Sharpe/Sortino ratios, tax reports |
| **Multi-Channel** | $2/mo | Bot reaches you on Telegram + Discord + email simultaneously |
| **Custom KB** | $3/mo | Upload your own docs, research, whitepapers — agent learns YOUR materials |
| **Strategy Vault** | $7/mo | Access to community-built strategies, copy-trade top performers |

### 💎 Bundle — "All Access" — $19/mo
All extensions included. ~40% savings vs à la carte ($32).

---

## Extension Deep Dives

### 🧠 The Brain
- Remembers every interaction, trade, preference
- "Last time you set stop-loss at 5%, want me to use that?"
- Builds learner profile from DeepTutor architecture
- Cross-session continuity
- **Why charge:** Computational cost of persistent memory + embeddings

### 📡 Macro Pulse
- M2 money supply tracking (Fed data)
- ISM manufacturing index
- Inflation CPI readings
- Market regime detection (risk-on vs risk-off)
- Push alerts when regime changes
- **Source:** BullTheory frameworks, FRED API
- **Why charge:** Real-time data feeds aren't free

### 🔬 Deep Research
- Multi-agent research (like DeepTutor's Deep Research mode)
- On-chain analysis: wallet tracking, token flow, whale alerts
- Smart contract audit report parsing
- Competitor protocol analysis
- Generates cited research reports
- **Why charge:** Heavy LLM usage, multiple agent spawns

### 📊 Analytics
- Real-time P&L dashboard
- Performance attribution (which strategies worked)
- Risk metrics: Sharpe, Sortino, max drawdown
- Tax report generation (cost basis, realized/unrealized)
- Export to CSV/API for accountants
- **Why charge:** Data processing, storage, API costs

### 📚 Strategy Vault
- Browse community-built agent configs
- Copy-trade with one click
- Filter by: P&L, risk level, asset class, time horizon
- Rate and review strategies
- Builder earns revenue share on copies
- **Why charge:** Marketplace infrastructure + quality curation

---

## Revenue Model Per User

### Scenario: Casual User
| Item | Cost |
|------|------|
| Free tier | $0 |
| 2 launches/month | $10-20 |
| No extensions | $0 |
| **Monthly total** | **$10-20** |

### Scenario: Active Trader
| Item | Cost |
|------|------|
| 5 launches/month | $25-50 |
| The Brain | $3 |
| Macro Pulse | $5 |
| Analytics | $5 |
| **Monthly total** | **$38-63** |

### Scenario: Power User (All Access)
| Item | Cost |
|------|------|
| 10 launches/month | $50-100 |
| All Access bundle | $19 |
| **Monthly total** | **$69-119** |

### Scenario: Strategy Builder (earns money)
| Item | Cost |
|------|------|
| Builds 3 bots/month | $15-30 (launch fees) |
| Sells 20 copies @ $25 | -$425 (after 15% platform fee) |
| Revenue share from copies | +$50-200/month ongoing |
| **Net** | **Earning $400+/month** |

---

## The Flywheel

```
Free tier → Learn Mode hooks users
    ↓
Users launch bots ($5-10)
    ↓
Some buy extensions ($3-7/mo each)
    ↓
Power users build strategies
    ↓
Strategies listed on marketplace
    ↓
New users buy proven strategies
    ↓
Platform takes cut on everything
    ↓
More users → more builders → more strategies → more users
```

---

## Competitive Positioning

| Platform | Model | Our Advantage |
|----------|-------|--------------|
| 3Commas | $49/mo subscription | We're free base, pay for what you use |
| Pionex | Free bots, hidden fees | We're transparent, flat pricing |
| Cryptohopper | $19-99/mo tiers | We're modular, not forced bundles |
| Banana Gun | % per trade | We're flat fee + optional extensions |
| DeFi Saver | % on automation | We're cheaper + educational |

---

## Implementation Priority

| Phase | Extensions | Why |
|-------|-----------|-----|
| Launch | Core + Launch fee | Get users, prove product |
| Month 2 | The Brain + Pro Learn | DeepTutor integration |
| Month 3 | Macro Pulse + Analytics | Data differentiation |
| Month 4 | Strategy Vault + Marketplace | Network effects |
| Month 5 | Multi-Channel + Custom KB | Power user retention |
| Month 6 | Deep Research + Bundle | Full suite |
