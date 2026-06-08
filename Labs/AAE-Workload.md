# Dmob — Labs Workload (AAE)

> Smart contract & agent engineering tasks for Avalanche Agent Economy. Updated: 2026-04-18

---

## 🎯 AAE Product Stack

**Origin:** Jordan built this to solve his own problems. Works too much at Amazon to babysit DeFi positions. Found OpenClaw, tried a wrapper, gave it something simple — "it was history after that."

---

### 1. 🚀 Autopilot — Fee-Efficient LP Management

**Status:** Concept — needs architecture

**Core:**
- Auto-rebalance LP positions to stay in range and maximize fee capture
- Time-aware positioning:
  - Asia overnight = low volatility, safe to sit tight
  - US market open = high volatility, tighten up or pull out
  - Sunday = danger zone — historically choppy/sell-off, exit Saturday night
- Pool health monitoring — auto-exit when pool degrades (volume drops, range breaks, IL spikes)
- Optimal entry/exit windows based on volatility patterns
- **UX: feed it a token address → done**

**Customization Layer (opt-in):**
- Dip-buying rules — "if token drops X%, widen range / add liquidity"
- Custom rebalance triggers based on user strategy
- Personal risk parameters

**Tech Notes:**
- LFJ (TraderJoe) Liquidity Book integration
- Need to study: bin step math, fee tier optimization, range concentration strategies
- Smart contracts for on-chain execution, agent for off-chain intelligence

---

### 2. 🔍 Community Sentiment Scoring

**Status:** Concept — needs scoping

- User inserts a ticker → agent scrapes X mentions, Discord activity, news headlines
- Aggregates into a weekly "Community Pulse" score (0-100)
- Tracks trends over time — "sentiment dropped 15pts this week, here's why"
- Flags anomalies — sudden spikes, FUD waves, dev activity drops

**Tech:**
- X API for sentiment scraping
- Discord bot for server activity metrics
- News aggregation via RSS/web scraping
- Can run on existing cron infrastructure

---

### 3. ⚡ Event-Driven Signal Detection

**Status:** Concept — multi-signal macro awareness

**The thesis:** The 4-year cycle is dead. Institutions are here. Macro events drive crypto now — not halvings.

**Signals to track:**
- 🌍 Geopolitics — wars, sanctions, tariff announcements
- 💧 Liquidation cascades — Oct 10-style mass liquidation events
- 🏦 Institutional flows — ETF inflows/outflows, treasury allocations
- 📜 Regulation shifts — SEC actions, stablecoin bills, country-level bans
- 🐦 Influential account posts — Trump, Elon, major protocol founders
- 📰 News cycles — overnight developments that hit before markets open

**Integration:**
- Feeds into Autopilot — sentiment shift triggers LP repositioning
- "Sunday tweet" pattern → agent exits Saturday night
- Time-blind tools (Gamma, Arrakis) don't do this — competitive edge

---

### 4. 🔬 Tokenomics Transparency Score

**Status:** Concept — "DYOR, but actually"

- Insert ticker → show tokenomics breakdown
- Allocation breakdown — team, investors, treasury, community, ecosystem
- Whale concentration — top 10 holders and % of supply
- Vesting schedule — insider unlock dates, cliff dates, emission
- Red flags — "80% held by 3 wallets" or "team vesting ends next month"
- FDV vs. market cap comparison

**Philosophy:** No recommendations, just data. Show the receipts, let users call bullshit.

**Data sources:**
- On-chain holder analysis
- Token contract parsing (allocation, vesting)
- CMC/DeFiLlama for FDV and supply data

---

### 5. 📖 Origin Story (for reference)

- Jordan: Amazon worker, DeFi trader, can't babysit positions
- Found OpenClaw → watched videos → saw wrapper examples → tried one
- Gave it something simple → it worked → "history after that"
- Built AAE to solve his own problems
- Subscribes to his own service — ultimate product-market fit

---

## 📋 Build Queue

| # | Feature | Status | Priority |
|---|---------|--------|----------|
| 1 | Autopilot LP Manager | 📐 Architecture needed | 🔴 High |
| 2 | Community Sentiment Scoring | 📝 Concept | 🟡 Medium |
| 3 | Event-Driven Signal Detection | 📝 Concept | 🟡 Medium |
| 4 | Tokenomics Transparency | 📝 Concept | 🟡 Medium |
| 5 | Smart contract — LP execution layer | ⏳ Not started | 🔴 High |

---

## Architecture Notes

- **On-chain:** Solidity contracts for LP management (LFJ integration)
- **Off-chain:** Python/JS agents for sentiment, signals, scoring
- **Bridge:** Agent calls smart contracts to execute positions
- **Infra:** Existing VPS + cron system, potentially expand for real-time monitoring

---

## Competitor Gap Analysis

| Feature | Gamma | Arrakis | AAE |
|---------|-------|---------|-----|
| Auto-rebalance | ✅ | ✅ | ✅ |
| Time-aware | ❌ | ❌ | ✅ |
| Sentiment signals | ❌ | ❌ | ✅ |
| Macro event response | ❌ | ❌ | ✅ |
| Tokenomics score | ❌ | ❌ | ✅ |
| Pool health exit | ❌ | ❌ | ✅ |
| "Feed token address" UX | ❌ | ❌ | ✅ |
