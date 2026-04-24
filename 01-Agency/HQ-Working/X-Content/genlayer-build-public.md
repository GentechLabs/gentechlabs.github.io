--- DRAFT — DO NOT PUBLISH ---
# Build-in-Public Posts: GenLayer Deployment
#tags: #update #agents #hackathon
#drafted: 2026-04-19
#phase: Phase 3 — GenLayer Revenue Share Capture
#note: Deploy 1-2 of these when testnet deployment happens

---

## Post 1: Initial Deployment

Shipped AgentEscrow to GenLayer's Bradbury testnet today.

First thing I learned: writing "intelligent contracts" is nothing like Solidity. You're not just coding logic — you're writing prompts that the LLM consensus layer interprets.

The contract has to reason about disputes, not just execute if/else.

Deployed on Chain ID 4221. Watching it work.

---

## Post 2: Dispute Resolution Working

AgentEscrow's dispute resolution is live on testnet.

How it works: when two agents disagree on a trade outcome, the GenLayer contract reads both sides, evaluates the evidence, and makes a ruling. No human arbiter needed.

The wild part: it actually works. The LLM consensus layer handled our test dispute correctly on the first try.

This is what programmable trust looks like when contracts can think.

---

## Post 3: Revenue Model Verification

Verified the revenue share mechanics on testnet today.

Every AgentEscrow dispute transaction generates fees. 10-20% of those fees route back to us as the contract deployer.

Not a promise. Not a roadmap item. It's in the contract.

If this carries to mainnet, every agent that uses AgentEscrow pays for our runway. That's the whole point.

---
