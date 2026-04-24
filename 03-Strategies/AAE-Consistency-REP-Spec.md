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

## 4. Implementation Path for DMOB
- **SBT Logic**: Update REP contract to track `last_active_timestamp` and trigger decay if `> 30 days`.
- **Escrow Bridge**: Integrate AVAX/BASE bridge for the "Intelligence Budget" payouts.
- **Burn Function**: Implement the `burn_on_exit` function in the Validator stake contract.
