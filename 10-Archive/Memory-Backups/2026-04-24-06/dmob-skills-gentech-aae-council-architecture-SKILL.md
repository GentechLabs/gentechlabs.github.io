---
name: aae-council-architecture
description: Council of Bots architecture for AAE — separates execution bots from validator agents using GenLayer GenVM, shared Intelligence Budget, reputation decay retention, and cross-chain scaling.
triggers:
  - user asks about validator agent
  - user asks about Council of Bots
  - user asks about AAE scaling
  - user asks about rep decay
  - user asks about execution vs validation
---

# AAE Council of Bots Architecture

## 1. Core Separation
- **Execution Bot**: The bot users pay to launch. Performs trades, rebalances, executes strategy.
- **Validator Agent**: Separate bot. Runs on GenLayer GenVM infrastructure. Judges/verifies high-value actions (e.g., large fund movements, critical rebalances).
- **Shared Intelligence Budget**: Both roles draw from the same budget. No conflict of interest because validator is independent infrastructure.

## 2. GenLayer Integration
- GenLayer = Infrastructure Layer (L1/L2 with GenVM).
- Execution bots are "Users" (call APIs, write code, move funds).
- GenLayer nodes = "Infrastructure" (decides if action was correct).
- Moves AAE from "Single Point of Failure" to "Consensus of Experts" (Council of Bots).

## 3. Pricing & Scaling
- **x402 model**: Makes validation cheap. No heavy hardware required — validation is API/LLM cost + stake, not raw GPU.
- **Kite AI**: Evaluate for optimizing Council consensus and reducing latency.
- **Cross-chain bridge**: AVAX ↔ BASE for Intelligence Budget and validator reward distribution. Maximizes liquidity and accessibility.

## 4. Retention: Reputation Decay (NOT Financial Lock-in)
- **Jordan preference**: Free to come and go. No hard lock-in.
- **Mechanic**: Users earn rep for keeping bots active. Must maintain 30+ day streaks for high rep.
- **Grace period**: 72 hours of downtime allowed with no penalty.
- **Decay kicks in after grace period**:
  - Day 4: -1 rep point
  - Day 7+: Accelerated decay (lose 5% total rep per day)
- **Recovery**: Must complete a "Recovery Challenge" (e.g., 3 successful validations in a row) to restore lost rep.
- **Psychology**: Loss aversion on identity/status is stronger retainer than financial deposit.

## 5. Branding / Content Buzzwords (for Desmond)
- "$TECH Economy"
- "AgentFi"
- "The Advisory" or "The Council"

## 6. Next Build Queue
1. Reputation Decay Engine (Consistency Heartbeat)
2. Kite AI integration for Council consensus
3. AVAX/BASE bridge architecture for Intelligence Budget flow