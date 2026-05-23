# Phase 2 — The Decision Layer

**Status:** 🔵 SCOPING
**Date:** 2026-05-23
**Depends on:** Phase 1 ✅ (Brain architecture approved, credit layer shipped, spec locked)

---

## What Phase 1 Gave Us

- 4-agent stack architecture (Analyst → Brain → Validator → Executor)
- Credit layer game engine (~1,177 LOC reusable modules)
- Hybrid Strategy Brain approved
- Formal spec locked including tokenomics
- Exodia modular strategy defined

## What Phase 2 Builds

**The brain gets a body.** Phase 2 is the decision engine that makes agents actually trade, learn, and face consequences.

---

## Scope: 5 Core Systems

### 1. Game Loop Engine
The run-based session manager that drives everything.

- **Run lifecycle:** Start → Market ticks → Agent decisions → Execute → Feedback → End condition check
- **Market simulator:** Generates price feeds across regimes (Bull/Bear/Crab/Black Swan/DeFi Summer)
- **Turn cadence:** Each "turn" = one decision cycle. Player watches agents work or intervenes.
- **End conditions:** Cash out, liquidated, bankrupt, time limit — all implemented
- **State persistence:** Run state saved to DB so players can resume/inspect

### 2. Strategy Brain (Decision Engine)
The core intelligence — Analyst signals feed Brain, Brain makes allocation decisions.

- **Signal format:** JSON schema for Analyst → Brain communication (regime, confidence, indicators)
- **Decision logic:** Brain evaluates signals against:
  - Current portfolio allocation
  - Player risk preferences (set at run start)
  - Memory of past allocation outcomes
  - Regime-specific strategy rules
- **Allocation engine:** Chooses between LP → Stake → HODL → Farm rotation
- **Confidence scoring:** Brain rates its own decisions (low/medium/high)
- **Memory integration:** Past outcomes feed back into future decisions (the learning loop)

### 3. Validator Gate
Risk checks before any order executes.

- **Pre-execution checks:**
  - Position sizing within limits
  - Total exposure cap not breached
  - Drawdown threshold not hit
  - No single-asset concentration >40%
- **Veto system:** Validator can reject orders with reasoning
- **Reputation scoring:** Tracks Brain's hit rate over time
- **Circuit breaker:** Halt all execution on Black Swan detection
- **Escalation:** If Validator rejects 3x in a row, notify player

### 4. Executor Pipeline
Pure execution — takes validated orders and runs them against the market sim.

- **Order types:** Swap, LP add/remove, Stake/unstake, Farm entry/exit
- **Simulated slippage:** Based on order size vs pool liquidity
- **Gas simulation:** Realistic cost deductions per transaction
- **Receipt generation:** Full audit trail of what happened and why
- **Failure handling:** Execution fails → partial fills, retry logic, graceful degradation

### 5. Feedback Loop
The learning system — execution results close the loop back to the Brain.

- **Outcome tracking:** Each order gets a result (profit/loss, slippage, execution time)
- **Brain scoring:** Compare Brain's predicted outcome vs actual outcome
- **Signal calibration:** Analyst adjusts confidence weights based on accuracy
- **Memory storage:** Store decision → outcome pairs for future reference
- **Regime transition learning:** What worked in Bull vs Bear vs Crab

---

## Technical Decisions Needed

1. **Market sim complexity:** How realistic does the price feed need to be? Start with random walk + regime overlay, or use real historical data replay?
2. **Brain decision logic:** Rule-based (if-then-else per regime) vs weighted scoring (score each allocation option) vs LLM-in-the-loop (call a model for complex decisions)?
3. **Memory format:** Simple key-value (regime → best allocation) vs structured event log (decision → context → outcome → lesson)?
4. **Turn speed:** How fast does a tick cycle run? 1 second for demo? 10 seconds for strategy? Configurable?
5. **Player intervention:** Can the player override Brain decisions mid-run, or only at regime transitions?

---

## Deliverables

1. `game_loop.py` — Run manager + market simulator
2. `brain_engine.py` — Strategy Brain decision logic with memory
3. `validator.py` — Pre-execution risk gate
4. `executor.py` — Order execution pipeline
5. `feedback.py` — Outcome tracking + memory integration
6. `signals.py` — JSON signal schema for agent communication
7. Integration test: Full flow from signal → decision → validation → execution → feedback → memory update

---

## Definition of Done

- A run starts, market ticks, agents make decisions, orders execute, results feed back
- Brain improves allocation accuracy over a 10-tick run (measurable learning)
- Validator catches at least one risky order and vetoes it
- Full audit trail visible after run ends
- All modules unit tested

---

*This is the beating heart of Agent Arena. Get this right and everything else is UI.*
