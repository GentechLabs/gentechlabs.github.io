# Agent Architecture Brainstorm — 2026-04-25

**Opened by:** Jordan (HQ, voice)
**Question:** How many agents per user? Per pool? Per stake?

---

## The Options on the Table

### Option A: 1 Agent Per User (Generalist)
- One agent handles DCA, fees, rewards, sentiment, rebalancing, gamification
- Pros: Simple orchestration, one identity, one state store, less infra
- Cons: Agent logic is heavy, single point of failure, harder to scale feature sets

### Option B: 2-3 Agents Per User (Light Specialist Swarm)
- Example split: (1) Execution Agent (DCA + rebalancing), (2) Intelligence Agent (news + sentiment + strategy), (3) Rewards Agent (fees + claims + gamification)
- Pros: Modular, easier to add features, one agent can be upgraded without touching others
- Cons: More orchestration complexity, inter-agent communication needed

### Option C: 1 Agent Per Pool / Per Stake
- Agent is tied to the LP position or stake, not the user
- User might have 3 agents if they have 3 positions
- Pros: Natural segmentation by position, agent "lives" where the capital is
- Cons: User has multiple agent identities, fragmented experience

### Option D: Hybrid — 1 User Agent + N Position Agents
- One "Commander" agent per user (orchestrates, gamification, subscription)
- Lightweight "Worker" agents per pool/stake (execution only)
- Pros: Clean UX + scalable execution
- Cons: Most complex to build

---

## Jordan's Input
> "I think we should limit it to two or three because you really don't need a multi-teen for what we're doing. Or maybe it's an agent per pool or per stake... I don't know, let's brainstorm."

Jordan is leaning toward **lightweight, not a swarm of 10**, but open to 2-3 or pool-based.

---

## Open Questions
1. If a user has 5 LP positions, do they want 5 agents or 1 agent managing 5 positions?
2. Does gamification/REP belong to the user or the position?
3. How much orchestration overhead can we afford at MVP?
4. Does "agent per pool" make sense for a DCA strategy that spans multiple pools?

---

## Call for Input
@DMOB @Desmond @YoYo — please weigh in with your domain perspective. DMOB: contract/state complexity. Desmond: UX/brand implications. YoYo: economic modeling complexity.
