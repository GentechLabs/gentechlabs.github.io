# 🎓 GenTech Labs Academy: Curriculum

This curriculum maps the high-level security and architecture concepts from Cyfrin/Chainlink courses directly onto the live contracts and systems being built in GenTech Labs. Instead of abstract examples, we use our own codebase as the primary textbook.

## 🛠️ Module 1: Security Patterns & Hardening
**Goal**: Transition from "coding that works" to "coding that is secure."
**Primary Target**: `AgentEscrow.sol`

### 1.1 Checks-Effects-Interactions (CEI)
*   **Cyfrin Concept**: Preventing reentrancy by updating state before external calls.
*   **Live Mapping**: 
    *   `createEscrow()`: See lines 89-100. State is set (`escrows[id] = ...`) before `USDC.safeTransferFrom`.
    *   `validateAndRelease()`: See lines 179-185. State is updated to `Released` before the transfer.
    *   `refund()`: See lines 203-209. State is updated to `Refunded` before the transfer.

### 1.2 Reentrancy Defense
*   **Cyfrin Concept**: Reentrancy guards and the danger of external calls.
*   **Live Mapping**: 
    *   Inheritance of `ReentrantGuard` from OpenZeppelin.
    *   Application of `nonReentrant` modifier on all state-changing functions involving token transfers.

### 1.3 Access Control & Modifiers
*   **Cyfrin Concept**: Role-based access and preventing unauthorized function execution.
*   **Live Mapping**:
    *   `OnlyBuyer` / `OnlySeller` custom errors used to restrict `refund()` and `markComplete()`.
    *   `AI_VALIDATOR` address check in `validateAndRelease()` to ensure only the authorized AI can trigger payment.

### 1.4 Signature Security & EIP-712
*   **Cyfrin Concept**: Preventing replay attacks and ensuring data integrity with typed signatures.
*   **Live Mapping**:
    *   Implementation of `EIP712` and `ECDSA`.
    *   `VALIDATION_TYPEHASH` (line 64): How we structure the data to prevent a signature for Escrow #1 being used for Escrow #2.

---

## 🏗️ Module 2: DeFi Architecture & Systems
**Goal**: Designing scalable, gas-efficient financial protocols.
**Primary Targets**: LP Monitoring & x402 Subscription Logic

### 2.1 Oracle Integration & Data Feeds
*   **Cyfrin Concept**: Trustless data ingestion and price feed manipulation.
*   **Live Mapping**:
    *   Analyzing how the LP Monitor fetches real-time pool data via APIs/Oracles.
    *   Discussion on "Price Lag" and "Slippage" in the context of the Trade Off platform.

### 2.2 Subscription Engineering (x402)
*   **Cyfrin Concept**: Payment streams and recurring logic.
*   **Live Mapping**:
    *   Mapping the $15-20 subscription tier to the `x402` pay-per-use model.
    *   Designing a "Credit" system for agent-native travel bookings.

### 2.3 Gas Optimization & Efficiency
*   **Cyfrin Concept**: Storage slots, `immutable` variables, and gas-saving patterns.
*   **Live Mapping**:
    *   Use of `immutable` for `USDC` and `AI_VALIDATOR` in `AgentEscrow.sol`.
    *   Evaluating `mapping` vs `array` for escrow tracking.

---

## 🎓 Module 3: Personal Goal Engine — The Mindset Track
**Goal**: Teach users to think like traders while the system trades for them.  
**Primary Target**: `Strategies/Personal-Goal-Engine-Spec.md`  
**Format**: 10 interactive modules across 4 tiers (Scout → Raider → Warlord → Sovereign)  
**Full Curriculum**: `Labs/PGE-Academy-Modules.md`

### 3.1 Tier 1 — Scout (Foundations)
*   **What Is Liquidity Provision?** — The pool, the position, the risk. Simulator included.
*   **Range Shapes** — Curve, Spot, Bidirectional. Visual shape simulator.
*   **Impermanent Loss** — The math that matters. IL calculator + fee breakeven.

### 3.2 Tier 2 — Raider (Strategy)
*   **Reading DexScreener** — Pool selection via 5 metrics. Scavenger hunt exercise.
*   **Multi-Shape Strategies** — Multi-position design. 7-day sandbox simulation.
*   **Gas Optimization** — Timing, batching, breakeven. Gas tracker exercise.

### 3.3 Tier 3 — Warlord (Portfolio)
*   **Portfolio LP** — Multi-pool allocation, correlation risk. Portfolio builder sim.
*   **Custom Range Design** — Support/resistance, backtesting. Blueprint exercise.

### 3.4 Tier 4 — Sovereign (Mastery)
*   **Risk Management** — 1% rule, stop-ranges, risk matrix. Timed scenario game.
*   **Building a System** — Automation, compounding, weekly ritual. Playbook template.

### Completion Rewards
- **Per module**: 10–50 REP (total 225 REP for full track)
- **Per tier unlock**: Badge + ladder advancement eligibility
- **Capstone (Module 10)**: Exportable personal playbook PDF

---

## 🎓 Module 4: Content & Communication
**Goal**: Build the voice of GenTech.  
**Primary Target**: Desmond's content pipeline.

*   **Brand Voice**: "More winners than losers" — grounded, no hype, process over outcome.
*   **Alert Microcopy**: SILENT / OK / ALERT / CRITICAL severity tones.
*   **Celebration Copy**: Making $5/day feel like a win. Reframe losses as learning.
*   **Community Playbooks**: Squad onboarding, dispute resolution scripts.

---

## 📈 Exercise Pipeline
1.  **The Audit**: Take a Cyfrin lesson → find the equivalent line of code in `AgentEscrow.sol` → explain why it was implemented that way.
2.  **The Break**: Attempt to write a Foundry test that breaks the `AgentEscrow` contract by ignoring one of these patterns (e.g., removing the state update before transfer).
3.  **The Fix**: Patch the vulnerability using the correct security pattern.
4.  **The Simulate**: Complete a PGE Academy module sandbox → apply the lesson to a live or paper position → log reflections.
5.  **The Build**: Design a custom range or multi-position strategy → backtest → present rationale.
