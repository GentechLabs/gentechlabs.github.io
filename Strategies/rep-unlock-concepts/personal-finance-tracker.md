# 💰 Personal Finance Tracker — REP Unlock Concept

**Proposed by:** Jordan  
**Date:** April 26, 2026  
**Owner:** YoYo (Strategies) + DMOB (Labs)  
**Status:** Awaiting code from Jordan

---

## 🎯 Concept

A **personal finance dashboard** that unlocks once a user reaches a certain REP threshold. Tracks:
- Net worth (on-chain + off-chain)
- Asset allocation (tokens, LP positions, stables)
- P&L over time
- Yield farming performance
- Budget vs. actual spending (if manual input supported)

## 🔑 REP Gating Proposal

| REP Tier | Unlock | Feature |
|---|---|---|
| **Tier 1 (0-500 REP)** | Basic wallet tracker | View holdings, simple pie chart |
| **Tier 2 (500-2000 REP)** | Performance analytics | P&L history, yield tracking, LP monitoring |
| **Tier 3 (2000+ REP)** | Full dashboard | Budgeting, alerts, export to CSV, cross-chain view |

## 📊 Strategy Value

- **Retention:** Users grind REP to unlock tools they actually need
- **Education:** Tracking P&L teaches risk management — aligns with "more winners than losers" philosophy
- **Stickiness:** Personal data creates lock-in; users won't abandon their tracked history
- **Onboarding:** Free tier gets them hooked, paid/REP tier gets them committed

## 🔧 Technical Notes (for DMOB)

- Jordan has existing code — likely HTML/JS or Python
- Need to decide: standalone page vs. embedded in AAE dashboard
- Data sources to consider:
  - **On-chain:** Direct RPC calls for wallet balances
  - **DeFi:** DeFi Llama API for yield/LLP data
  - **Manual:** User-inputted off-chain assets (bank, stocks, etc.)
- **Security:** If manual input, encrypt at rest; if on-chain, read-only

## 📅 Next Steps

1. ⏳ Jordan sends existing code to DMOB (~6:20 PM)
2. DMOB reviews code, scopes integration effort
3. YoYo defines REP tiers and gating logic
4. Desmond drafts user-facing feature announcement
5. Build + test

## 💡 Expansion Ideas

- **Leaderboard:** "Top savers" or "Best yield hunters" by REP tier
- **Challenges:** "Track your spending for 30 days" → earn REP
- **AI Insights:** "You're 80% in ETH — consider diversifying" (YoYo can power this)
- **Export:** Tax-ready CSV for crypto gains

---

*This is a GenTech product feature — not just a hackathon entry. Build it right.*
