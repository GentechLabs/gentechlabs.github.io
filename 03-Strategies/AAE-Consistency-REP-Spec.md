---
type: specification
title: "AAE Consistency REP & Validator Lifecycle"
created: 2026-04-23
tags: [AAE, REP, tokenomics, retention, GenLayer]
status: draft
---

# 🧠 AAE Consistency REP & Validator Lifecycle

## 1. The Consistency Anchor (User REP)
To move away from mercenary behavior, REP is now tied to **Consistency (Uptime)** rather than just outcome.

### The Mechanism
- **Loyalty Window**: 30-day rolling window.
- **The Rule**: Users must maintain active bot status for at least one month to protect their REP.
- **Penalty (The Inconsistency Price)**: 
    - Deactivating bots or allowing them to lapse results in an immediate **REP Decay**.
    - No hard lock-in (freedom to leave), but a social cost for lack of consistency.
- **Reward**: Consecutive months of activity increase a "Loyalty Multiplier," potentially unlocking higher $TECH discount tiers.

## 2. The Validator Lifecycle (The Council)
Leveraging GenLayer's GenVM for "Agent-as-Infrastructure."

### A. Entry (Subsidized)
- **x402 Coefficient**: Use a specific multiplier/discount to lower the cost of entry for new Validator Agents.
- **Requirement**: Stake $TECH/GEN $\rightarrow$ Deploy to GenVM $\rightarrow$ Join "The Council."

### B. Active Phase (The Intelligence Budget)
- Validators earn from the **Intelligence Budget** for providing accurate, consensus-based verification.
- No heavy hardware required; cost is centered on API credits and stake.

### C. Exit (The Burn)
- **Exit Tax**: To prevent validator churn and stabilize $TECH price, validators must **burn a percentage of their stake** to leave the Council.
- This creates a "Symmetry of Cost" where entry is subsidized but exit is an economic event.

## 3. Synergy Mapping
| Layer | User (Liquid) | Validator (Infrastructure) |
| :--- | :--- | :--- |
| **Incentive** | REP (Social Status) | $TECH / Intelligence Budget (Capital) |
| **Risk** | REP Decay (Inconsistency) | Slashing / Stake Burn (Truth/Exit) |
| **Goal** | Consistent Bot Activity | High-Fidelity Verification |

## 5. Prediction Market Gate (New Concept)
**Idea:** AAE's rep system unlocks access to an exclusive prediction market.

**The Gate:**
- Users must actively use AAE platform (DCA, yield farming, accumulation)
- Maintain rep score above threshold through consistent activity
- Prediction market entry is a *privilege*, not a product anyone can buy into

**Why It Works:**
- **Skin in the game:** Only committed users get access
- **Higher signal:** Gated markets filter out noise vs. open platforms (Polymarket)
- **Platform lock-in:** To stay in the market, users keep engaging with AAE
- **Rep as currency:** Reputation literally becomes your ticket

**The Flow:**
```
Join AAE → Start DCA/Yield Farming → Accumulate Rep → Hit Threshold → UNLOCK Prediction Market
```

**Open Questions:**
- What rep threshold unlocks the market?
- Prediction market infra: UMA, custom, or GenLayer oracle?
- Can rep decay revoke access? (Inactive users lose market privileges?)
- Market topics: macro, crypto, agent performance, LP yields?

## 6. Implementation Path for DMOB
- **SBT Logic**: Update REP contract to track `last_active_timestamp` and trigger decay if `> 30 days`.
- **Escrow Bridge**: Integrate AVAX/BASE bridge for the "Intelligence Budget" payouts.
- **Burn Function**: Implement the `burn_on_exit` function in the Validator stake contract.
- **Prediction Gate**: Add `rep_threshold_check` to market entry function.
