# Handoff: Auto-Rebalance LP Economics Review

**From:** DMOB
**To:** YoYo
**Priority:** 🟡 MEDIUM
**Date:** Apr 21, 2026

---

## Task
Validate the economics of an auto-rebalance LP manager that deducts gas from the user's deposit.

## Key Questions
1. **Break-even analysis:** At what LP size does yield realistically cover gas costs?
   - Average TraderJoe v2.2 rebalance gas: ~0.005–0.015 AVAX (~$0.18–$0.54 at $36 AVAX)
   - Typical LP yield for AVAX/USDC: 15-30% APR
   - At $500 deposit, 20% APR = $100/year passive income
   - If 12 rebalances/year × $0.36 avg gas = $4.32/year gas cost
   - Net: $95.68/year (95.7% yield after gas) ← seems viable?

2. **Subscription tiers:** Does $12/mo for Agent tier make sense at scale?
   - 100 users × $12 = $1,200 MRR
   - Infrastructure cost: ~$200/mo (crons, RPC, Chainlink)
   - Margin: ~83%?

3. **Risk scenarios:**
   - What if AVAX spikes 50% in a day → multiple rebalances in short window?
   - What if gas spikes (network congestion)?
   - What if LP yield drops below gas cost?

## Context
- Full concept doc: `11-Mess Hall/2026-04-21-auto-rebalance-concept.md`
- Current LP pool: AVAX/USDC on TraderJoe v2.2, range 9.10–9.65
- Cron jobs already monitoring hourly

## Deliverable
One-page economics breakdown with break-even chart, ready for Jordan to review.

---

#handoff #yoyo #economics #auto-rebalance
