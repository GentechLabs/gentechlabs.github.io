# 🧠 AAE Hybrid Strategy Brain — Three-Agent Architecture

> **Status:** ✅ APPROVED — Apr 29, 2026
> **Author:** DMOB (Labs)
> **Context:** Frontier Hackathon / AAE v2

---

## Vision

Agents that don't just execute one strategy — they **rotate between LP, Staking, HODL, and Farming** based on market regime. Smart money in your pocket while you live your life.

---

## The Three-Agent Stack

```
┌─────────────────────────────────────────────────────┐
│                    USER LAYER                        │
│  Deposit → Set Preferences → Monitor Dashboard      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              📊 AGENT 1: ANALYST                     │
│  "The Eyes"                                         │
│  • Market regime detection (trending/ranging/volatile)│
│  • On-chain liquidity flow tracking                 │
│  • TVL shifts, yield changes, volume analysis       │
│  • Feeds signals → Strategy Brain                   │
│  Stack: Beam Cloud (fast inference)                 │
└──────────────────────┬──────────────────────────────┘
                       │ signals
┌──────────────────────▼──────────────────────────────┐
│              🧠 AGENT 2: STRATEGY BRAIN              │
│  "The Brain"                                        │
│  • Receives analyst signals + user preferences      │
│  • Decides allocation rotation:                     │
│    LP → Stake → HODL → Farm                         │
│  • Manages risk parameters (drawdown, exposure)     │
│  • Memory layer — learns from past allocations      │
│  • Proactive notifications on regime shifts         │
│  Stack: Beam Cloud (stateful bots)                  │
└──────────────────────┬──────────────────────────────┘
                       │ approved orders
┌──────────────────────▼──────────────────────────────┐
│              ✅ AGENT 3: VALIDATOR                   │
│  "The Safety Net"                                   │
│  • Reviews every Brain decision BEFORE execution    │
│  • Risk checks: position sizing, exposure caps      │
│  • Reputation scoring — tracks Brain's hit rate     │
│  • Approve / Reject / Veto with reasoning           │
│  • Anti-rug: prevents catastrophic single decisions │
│  Stack: GenLayer (subjective consensus)             │
└──────────────────────┬──────────────────────────────┘
                       │ validated orders
┌──────────────────────▼──────────────────────────────┐
│              ⚡ AGENT 4: EXECUTOR                    │
│  "The Hands"                                        │
│  • Pure on-chain execution — NO decision-making     │
│  • LP management, staking, farming, swaps           │
│  • Gas optimization, slippage protection            │
│  • Transaction receipts + status reporting          │
│  Stack: Solana/AVAX native, Jupiter/LFJ SDKs       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              🔄 FEEDBACK LOOP                        │
│  Execution results → Brain learns                   │
│  Validator scores → Reputation updates              │
│  Analyst adjusts → Signal calibration               │
└─────────────────────────────────────────────────────┘
```

> **Note:** Four logical agents, but the Validator + Executor can be tightly coupled (same process, different roles). Three *independent decision-making units*: Analyst, Brain, Validator.

---

## Flow: Regime Shift Example

```
1. Analyst detects: "ETH/USDC LP TVL dropping 15%, staking yields rising"
2. Analyst feeds signal → Brain
3. Brain decides: "Rotate 40% from LP to staking"
4. Brain sends order → Validator
5. Validator checks:
   - Drawdown within limits? ✓
   - Exposure cap respected? ✓
   - Brain's recent hit rate > 70%? ✓
   → APPROVED
6. Executor receives validated order
7. Executor executes: unstake LP → restake
8. Results feed back → Brain learns
```

---

## Progression Layer (User Trust Levels)

| Mode | Brain | Validator | Executor |
|------|-------|-----------|----------|
| **🎓 Shadow** | Suggests only | Approves everything | No execution |
| **📋 Supervised** | Decides + notifies user | Reviews + explains | Executes after user confirms |
| **🤖 Autonomous** | Full decision-making | Auto-approves if score > threshold | Executes immediately |

---

## Module Mapping (Layer → Agent)

| Layer | Agent | SDK/Stack | Status |
|-------|-------|-----------|--------|
| L1 (Fee LP) | Executor | Solana/AVAX native | 🔴 Not started |
| L2 (Risk Intel) | Validator | Beam Cloud | 🔴 Not started |
| L3 (Brain) | Strategy Brain | Beam Cloud | 🔴 Not started |
| L4 (Reputation) | Validator | GenLayer | 🔴 Not started |
| L5 (Escrow) | Executor | Solidity/Foundry | 🟡 Partial |

---

## Security Considerations

1. **No single agent can drain funds** — Validator is the gatekeeper
2. **Checks-Effects-Interactions** — Executor follows CEI strictly
3. **Time-locked large rotations** — Anything >20% portfolio shift has a delay
4. **Circuit breaker** — Validator can halt all execution if conditions are met
5. **Multi-sig override** — User can always intervene manually

---

## Next Steps

- [ ] Anchor CLI install fix (Rust toolchain upgrade to ≥1.85.0)
- [ ] Build Foundation escrow contract (trust anchor)
- [ ] Design Analyst signal format (JSON schema)
- [ ] Prototype Brain decision logic with mock data
- [ ] GenLayer integration for Validator (when builder program resumes)
- [ ] Integration test: full flow from signal → execution → feedback

---

*This document is the source of truth for AAE agent architecture. Update as decisions evolve.*
