# 🚀 Green Room Handoff — DMOB

**From:** YoYo (Strategies)  
**To:** DMOB (Labs)  
**Date:** April 26, 2026  
**Status:** Code incoming from Jordan

---

## 📝 Context

Jordan wants to add a **personal finance tracker** as a REP system unlock/reward in the AAE Trading Arena. He has existing code he's used personally and will send it to you on his next break (~6:20 PM today).

## 🎯 What We Need

1. **Integrate** Jordan's personal finance tracker code into the AAE ecosystem
2. **Gate it behind REP** — make it an unlockable feature (e.g., reach X REP to unlock)
3. **Connect to wallet** — track on-chain holdings, LP positions, yields
4. **Dashboard view** — clean UI showing net worth, asset allocation, P&L

## 📁 Where to Put It

- Code review: `03-Projects/aae-trading-arena/integrations/personal-finance/`
- If it's a standalone HTML/JS app, drop it in `06-Tech/aae-dashboard/integrations/`
- REP gating logic: tie into existing `UserRepTracker` contract

## ❓ Open Questions for Jordan (when he drops the code)

1. Is this a **standalone app** or **embedded in AAE dashboard**?
2. What data sources? (Manual input, wallet read, DeFi Llama API, etc.)
3. What REP threshold unlocks it?

## 📋 Jordan's Message

> "I'm trying to balance out what the rep system does and what you get... having certain things unlocked for you because of the rep system is just great. Like for instance, what if we also added a personal finance tracker to it? I think that would also be fire. I have code built out for a personal finance tracker I was using and I think that we should use that. I'll send that to D-Mov on my next break at 6.20 p.m. for sometime soon."

---

**Action:** DMOB — watch for Jordan's code drop. Review and scope integration.
