---
type: architecture
title: "AAE Intelligence Budget & Layer Coordination"
created: 2026-04-23
tags: [AAE, architecture, GenLayer, intelligence-budget, risk-management]
status: active
---

# 🧠 AAE Intelligence Budget & Layer Coordination

## The Core Thesis
Move from "Single Point of Failure" (one master verifier) to a **"Consensus of Experts"** via a distributed Intelligence Budget.

## 🏗️ Architectural Layers
The system operates as a distinct architectural layer where Agents (Users) execute and GenLayer nodes (Infrastructure) verify.

### Layer Roles
1. **Agents (The "Users")**: 
   - Responsible for calling APIs, writing code, and moving funds.
   - Operates as the "execution arm" of the AAE ecosystem.
2. **GenLayer Nodes (The "Infrastructure")**:
   - Acts as the specialized execution environment (GenVM).
   - Decides if a user's (agent's) action was correct.
   - Provides AI-native consensus to verify GitHub contributions and on-chain movements.

## 💰 The Intelligence Budget
To avoid conflicts of interest and maximize efficiency, AAE should utilize different bots that feed into a shared **Intelligence Budget**.

- **Distributed Verification**: Instead of one bot deciding a task is complete, multiple specialized bots (experts) must reach consensus.
- **Budget Allocation**: The "Intelligence Budget" governs the computational/financial resources allocated to these verification cycles.
- **Risk Mitigation**: By separating the agent that *does* the work from the node that *verifies* the work, we eliminate a primary conflict of interest.

## 🔄 Integration with existing AAE Layers
This structure integrates with the existing AAE framework:
- **Body Layer**: Position awareness and yield tracking (The "what").
- **Brain Layer (Watchdog)**: Coordination and responsiveness monitoring (The "how").
- **GenLayer Infrastructure**: The final truth/verification layer (The "is it correct?").

## ✅ Implementation Notes
- **No Scratch Starts**: This is an additive layer to the current scaffold, not a rebuild.
- **Bot Separation**: Execution bots $\neq$ Verification bots.
- **Consensus Pattern**: Use a `check-and-execute` pattern via KeeperHub or GenLayer AutoBounty.
