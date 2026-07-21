---
title: Agent Bill Pay — Full Product + AAE Integration
created: 2026-05-31
status: active
tier: Tier 1 — Build Now
tags: [AAE, bill-pay, stablecoins, Rain, x402, consumer, gateway, TrustClaw]
---

# Agent Bill Pay — Full Product + AAE Integration

## The Vision

An AAE agent that automatically pays your bills using stablecoins. Start with a screenshot, end with full financial automation.

**The pitch:** "Take a picture of your bills. Let an agent handle the rest."

## Progression Model (Trust Ladder)

### Phase 1: Screenshot → Dashboard (MVP)
- User uploads screenshot of bill table (Google Sheet, spreadsheet, paper)
- Agent parses it (OCR + table extraction)
- Creates clean dashboard showing upcoming bills
- **No wallet, no crypto, no risk — just visibility**

### Phase 2: Dashboard → Calendar + Reminders
- Syncs to Google Calendar via TrustClaw/Composio
- Telegram reminders: "Rent due tomorrow — $426"
- Weekly summary: "This week: 4 bills, $623 total"

### Phase 3: Calendar → Auto-Pay (with guardrails)
- User connects stablecoin wallet
- Agent gets scoped Rain Visa card per biller
- Guardrails: amount caps, merchant allowlists, intervals
- Agent pays automatically when due

### Phase 4: Auto-Pay → Invest
- Agent pays bills first
- Leftover stablecoins → agent invests (AAE Yield Agent)
- Full financial automation: pay bills, invest remainder

## AAE Integration Model

### Bill Pay Agent = Gateway Product

```
User signs up for Bill Pay
  → Agent registered in AAE (ERC-8004 identity)
  → Agent builds reputation (on-time payment track record)
  → Agent discovers surplus after bills paid
  → Agent suggests investing surplus via AAE Yield Agent
  → Agent-to-agent commerce (x402 micropayments)
  → All transactions recorded on AAE
```

### The Flywheel
```
More users → More agent transactions → Better reputation data
    ↑                                          ↓
More trust ← Better recommendations ← More agents join
```

### Revenue Stack

**Bill Pay Agent Revenue:**
- Monthly management fee (0.5-1% of bills paid)
- Surplus → Yield Agent (referral fee)
- Bill optimization (savings share)
- Agent-to-agent transactions (x402 fees)

**AAE Revenue:**
- Agent registration fees (ERC-8004)
- Transaction fees (x402 micropayments)
- Marketplace listing fees
- Reputation data licensing

## Product Family

| Product | User Type | Revenue | AAE Layer |
|---------|-----------|---------|-----------|
| **Bill Pay Agent** | Everyone | Management fee | Consumer entry |
| **Yield Agent** | Surplus cash | Performance fee | DeFi integration |
| **Travel Agent** | Trip planners | Booking fee | Lifestyle |
| **Portfolio Agent** | Investors | AUM fee | Finance |
| **Optimization Agent** | Cost cutters | Savings share | Intelligence |

All sharing infrastructure. All building reputation. All paying x402 to each other.

## Technical Stack

### MVP (Phase 1-2)
- Screenshot parser (OCR → structured data)
- Dashboard (bill tracking, upcoming payments)
- TrustClaw/Composio integration (Google Calendar)
- Telegram notifications (reminders, summaries)
- AAE agent registration (ERC-8004 identity)

### Full Product (Phase 3-4)
- Rain card issuance (scoped virtual cards per biller)
- Rain Agent Control Layer (spending guardrails)
- x402 micropayments (fees, agent-to-agent)
- AAE marketplace (discovery, reputation)
- Stablecoin on/off ramp (Rain integration)

## User Experience

### Setup Flow
1. Screenshot your bill table (or connect Google Sheet)
2. Agent parses and creates dashboard
3. Confirm/edit bill list
4. Set guardrails (caps, approval thresholds)
5. Connect Google Calendar for reminders
6. (Optional) Connect wallet for auto-pay

### Ongoing
- Weekly summary: bills paid, surplus available
- Monthly report: total spent, savings found, on-time rate
- Anomaly detection: "Electric bill 40% higher than usual"
- Optimization suggestions: "Found cheaper phone plan — save $70/mo"

### Dashboard
```
┌─────────────────────────────────────┐
│  Agent Bill Pay — June 2026         │
├─────────────────────────────────────┤
│  This Month                         │
│  ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │ $1,885  │ │ 19/19   │ │ 100%  │ │
│  │ total   │ │ paid    │ │ on-time│ │
│  └─────────┘ └─────────┘ └───────┘ │
│                                     │
│  Upcoming                           │
│  • Rent pt1 — $426 — Jun 1         │
│  • Loan Lendmark — $163 — Jun 2    │
│  • YouTube — $14 — Jun 3           │
│                                     │
│  Surplus: $312 → [Invest in Yield]  │
│                                     │
│  [Pause All] [Approve Pending]      │
└─────────────────────────────────────┘
```

## Why This Wins

**For users:**
- Low risk (start with just tracking)
- High utility (everyone has bills)
- Progressive trust (reminders → auto-pay → investing)
- Familiar (screenshots, Google Calendar, Telegram)

**For AAE:**
- Consumer acquisition (normal people, not crypto degens)
- Agent reputation building (on-time payment track record)
- Data for other agents (spending patterns, surplus)
- Gateway to financial products (yield, ETFs, optimization)

## Competitive Advantage

**Nobody else has:**
1. Screenshot-based onboarding (zero friction)
2. Agent identity + reputation (ERC-8004)
3. Programmatic spending guardrails (Rain ACL)
4. Agent-to-agent commerce (x402)
5. Marketplace for agent discovery (AAE)

**Vs. existing solutions:**
- Mint/YNAB: Manual tracking, no automation
- Auto-pay: Limited to each biller's system
- Agent Bill Pay: One agent, all bills, smart scheduling, guardrails, crypto-native

## MVP Scope

**Start with:**
1. Screenshot parser (OCR → bill table)
2. Dashboard (upcoming bills, amounts, due dates)
3. Google Calendar sync (via TrustClaw/Composio)
4. Telegram reminders
5. AAE agent registration (basic reputation)

**No crypto. No wallets. No risk.** Just a smart bill tracker that happens to be an agent.

**Then add:**
- Rain card issuance
- Auto-pay with guardrails
- Stablecoin on/off ramp
- Yield agent integration
- Agent-to-agent commerce

## The Story

> "I started by taking a picture of my bills. Now my agent pays them, invests my surplus, books my trips, and optimizes my spending — all while building reputation in an economy where agents help each other."

That's AAE. Not abstract infrastructure — **agents that make your life better.**

## Next Steps
1. Build screenshot parser MVP
2. Integrate TrustClaw/Composio for Google Calendar
3. Register Bill Pay Agent in AAE (ERC-8004)
4. Test with Jordan's actual bills (Bills 2026 sheet)
5. Iterate on dashboard UX

## Related Files
- AAE/Agent-Bill-Pay.md — Original concept
- AAE/Rain-Agent-Control-Layer.md — Payment infrastructure
- AAE/Brickken-RAMS-Integration.md — Compliance layer
- AAE/Agent-ETFs.md — Investment layer
- Green-Room/LP-Army-Social-Layer-Inspiration.md — Social features
