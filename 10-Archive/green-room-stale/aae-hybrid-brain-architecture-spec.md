---
date: 2026-04-29
type: collaboration
from: Desmond (Creative)
to: DMOB (Labs)
status: ready for review
priority: high
---

# AAE Hybrid Strategy Brain — Three-Agent Architecture Spec

## Context

Jordan confirmed the hybrid strategy brain direction and wants me and DMOB to collaborate on the architecture. He described it as "putting smart money in your pocket" — agents that detect market shifts, alert users, and continue executing while users live their lives.

Full brainstorm: `00-HQ/Brainstorm/AAE-Hybrid-Strategy-Brain.md`

---

## The Architecture: Three Agents + Enforcement Layer

### Agent 1: 🔍 Analyst Agent — "The Eyes"

**Job:** Market regime detection and signal generation

**Responsibilities:**
- Monitor market conditions in real-time (volatility, trend, volume)
- Track on-chain metrics: TVL shifts, yield changes, liquidity flows
- Classify regime: High Volatility Breakout / High Volume Range-Bound / Low Volatility Sideways / Macro Uncertainty
- Feed structured signals to Strategy Brain

**Data Sources:**
- Price feeds (Birdeye, DEX price oracles)
- Volume data (on-chain DEX volume)
- Volatility indicators (RSI, Bollinger Bands, ATR)
- TVL/yield data (DeFiLlama, protocol APIs)

**Tech Notes:**
- Extends existing LP Monitor cron infrastructure
- Can reuse `lp-aae-signal-monitor.py` signal logic
- Runs on existing VPS cron (hourly or more frequent)
- Outputs structured JSON: `{ regime: "high_volatility_breakout", confidence: 0.85, signals: {...} }`

---

### Agent 2: 🧠 Strategy Brain — "The Brain"

**Job:** Allocation decisions and learning

**Responsibilities:**
- Receive analyst signals + user preferences/history
- Decide portfolio allocation across strategies (LP, Staking, HODL, Farming)
- Manage the hybrid allocation model (baseline 30% farming + 20% staking + 50% active)
- Learn from user overrides (style fingerprinting)
- Operate in three modes: Shadow → Supervised → Autonomous

**Decision Framework:**
```
INPUT: Analyst signal + User profile + Current allocation + Enforcement limits
  → Strategy Brain evaluates
OUTPUT: { action: "rebalance", from: "LP", to: "HODL", pct: 40, reason: "breakout detected" }
```

**Learning Layer:**
- Track every user override: "User rejected HODL shift during similar conditions"
- Build style fingerprint: risk tolerance, preferred strategies, timing preferences
- Shadow Mode: Suggest only, user confirms every move
- Supervised Mode: Execute with approval, user can override
- Autonomous Mode: Full execution, notify on major shifts only

**Tech Notes:**
- This is the core AI component — needs LLM integration for reasoning
- User preference storage: SQLite or structured JSON in vault
- Could leverage Hermes agent infrastructure for multi-model routing
- Maps to L1 Brain (model selection) + L3 Strategy (playbook logic)

---

### Agent 3: ⚡ Executor Agent — "The Hands"

**Job:** On-chain transaction execution

**Responsibilities:**
- Take Strategy Brain decisions and convert to on-chain transactions
- Manage LP positions (enter/exit/rebalance on LFJ)
- Execute staking/unstaking (Benqi, validator delegation)
- Handle HODL swaps (DEX routing)
- Manage farming positions (deposit/withdraw)
- Track execution success/failure and report back

**Tech Notes:**
- Extends existing LP execution infrastructure
- Multi-protocol adapters: LFJ, Benqi, Pangolin, validator staking
- Gas optimization: batch transactions, timing
- MEV protection: private RPCs, slippage guards
- Maps to L7 Transaction Construction

---

## The Validator: Enforcement Layer (L6) — Not a Fourth Agent

**Why not a separate agent:** Enforcement rules are deterministic — you want `require()` logic, not probabilistic AI reasoning. Adding a fourth agent = extra LLM call = more latency + cost for what should be simple if/then checks.

**What it checks (between Strategy → Execution):**
- Max position size (per-trade % limit)
- Protocol whitelist (only audited protocols)
- Daily/weekly loss limits
- Cooldown period between trades
- Gas price cap
- User timelock for large moves
- Active override/pause flag

**When it blocks:**
```
Strategy: "Shift 50% to HODL"
Enforcement: "⛔ BLOCKED — Daily loss limit reached (-2.8% today, cap is -3%)"
  → Notify user: "Strategy blocked: daily loss limit. Current: -2.8%"
  → Strategy Brain logs the attempt and learns
```

**When it passes:**
```
Strategy: "Shift 40% LP → HODL"
Enforcement: "✅ Position size ok, ✅ whitelisted, ✅ no cooldown"
  → Executor: "Executing swap..."
```

---

## The Full Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   ANALYST   │───→│   STRATEGY   │───→│ ENFORCEMENT │───→│   EXECUTOR  │
│   "Eyes"    │    │   "Brain"    │    │   "Shield"  │    │   "Hands"   │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │
  Market Data      User Prefs +          Risk Checks        On-Chain Txs
  Regime Signal    Learning Layer        Circuit Breaker    LFJ/Benqi/DEX
      │                   │                   │                   │
      └───────────────────┴───────────────────┴───────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  USER NOTIFICATION │
                    │  "AAE re-allocated │
                    │   LP ↓30%, HODL ↑20%│
                    │   +2.3% projected"  │
                    └───────────────────┘
```

---

## What I Need From DMOB

### 1. Feasibility Assessment
- Can our existing cron + LP Monitor + Wallet Monitor infrastructure support this pipeline?
- What's reusable vs what needs to be built from scratch?
- Can D5 Strategy Engine be extended or does it need a rewrite?

### 2. Execution Complexity
- Moving capital between strategies: how many transactions, what gas costs?
- Is a unified vault contract needed, or individual protocol adapters?
- Smart contract risk: single contract vs composable adapters?

### 3. Data Requirements
- What on-chain data sources are available for regime detection?
- Yield oracle feasibility across protocols (LFJ, Benqi, Pangolin, validators)
- Update frequency requirements for each signal type

### 4. Storage Architecture
- Where does the learning layer data live? (SQLite? On-chain?)
- User preference graph structure
- Cross-session memory for style fingerprinting

### 5. Hackathon Scope
- What's Phase 1 (hackathon demo) vs Phase 2 (post-hackathon)?
- Minimum viable pipeline for Solana Frontier (May 11)?
- Can we demo the full pipeline with simulated signals?

---

## Timeline Pressure

| Hackathon | Deadline | Priority |
|-----------|----------|----------|
| Solana Frontier | May 11 | 🔴 PRIMARY |
| Kite AI | May 17 | 🟡 SECONDARY |

**Phase 1 (hackathon):** Analyst + Strategy Brain with basic enforcement. Simulated signals, real execution on testnet.
**Phase 2 (post-hackathon):** Full autonomous pipeline, learning layer, multi-chain.

---

*Handoff from: Desmond (Creative)*
*Created: 2026-04-29*
*Next: DMOB reviews, we sync in Green Room, report to Jordan in HQ*
