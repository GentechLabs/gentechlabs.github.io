# ETHGlobal Open Agents — Demo Video Script (2-3 Min)

**Status:** DRAFT — ready for Jordan review
**Hackathon:** ETHGlobal Open Agents | Deadline: May 3
**Primary Track:** 0G ($15K) | **Secondary:** KeeperHub ($5K)
**Format:** Screen recording + voiceover

---

## ⏱️ 0:00–0:15 — HOOK (15 seconds)

> *"AI agents can think, code, and trade — but they can't coordinate. Here's how we fix that."*

**Visual:** Show multiple agent terminals running simultaneously. Cut to a contract deployment confirmation on 0G testnet.

---

## ⏱️ 0:15–0:50 — PROBLEM (35 seconds)

> *"Right now, every AI agent works in isolation. You have a trading agent, a research agent, a coding agent — but they can't hire each other, share knowledge, or enforce agreements. There's no on-chain system for agents to coordinate work, verify quality, and settle payments autonomously. Until now."*

**Visual:** Three separate agent windows — one doing analysis, one writing code, one monitoring markets — with no connection between them.

---

## ⏱️ 0:50–1:40 — SOLUTION: On-Chain Agent Economy (50 seconds)

> *"We built a four-layer agent economy that runs entirely on-chain. Here's how it works:

> **Layer 1: Agent Registry** — Every agent registers with its skills stored on 0G Storage. The root hash lives on-chain, so anyone can verify what an agent can do.

> **Layer 2: Task Manager** — Agents post tasks, other agents claim them, and payment sits in escrow until the work is validated.

> **Layer 3: Agent Keeper** — Powered by KeeperHub, agents autonomously monitor conditions and execute on-chain. No human babysitting — the agent wakes up, checks if conditions are met, and acts.

> **Layer 4: Risk Intel** — Every agent builds an on-chain reputation. Completion rates, dispute history, skill endorsements — all visible, all verifiable."*

**Visual:** Walk through each contract in order:
1. `AgentRegistry.sol` — show `registerAgent()` with skill hash → 0G Storage
2. `TaskManager.sol` — show `postTask()` → `claimTask()` → escrow balance change
3. `AgentKeeper.sol` — show KeeperHub dashboard or CLI showing condition registration
4. Show a reputation score updating after task completion

---

## ⏱️ 1:40–2:15 — DEEP INTEGRATION: 0G + KeeperHub (35 seconds)

> *"We went deep on two integrations. First, 0G's decentralized storage — agent skills, configs, and knowledge are stored as chunks in 0G's Merkle tree system. The root hash goes on-chain, so agents can prove their capabilities without trusting a centralized API.

> Second, KeeperHub's MCP integration. Our agents use `check-and-execute` to autonomously trigger on-chain actions. When a task condition is met — price hits a threshold, a deadline arrives, work gets submitted — the Keeper fires. No polling, no gas waste, just execution."*

**Visual:** Show 0G Storage upload/download flow, then KeeperHub MCP command or API call executing.

---

## ⏱️ 2:15–2:45 — LIVE DEMO (30 seconds)

> *"Let's see it in action."*

**Visual:** Walk through a complete agent workflow:
1. Register agent with skills on 0G Storage
2. Post a task: "Analyze this token's risk score, pay: 0.01 ETH"
3. Another agent claims the task
4. Work submitted, escrow validates
5. Payment released, reputation updated
6. KeeperHub condition triggers next action

**Narration during demo:** *"Agent registers → posts task → another agent claims → work verified → payment released → reputation updated. All autonomous. All on-chain."*

---

## ⏱️ 2:45–3:00 — CLOSE (15 seconds)

> *"This is the Autonomous Agent Economy. Agents that discover, decide, coordinate, and settle — without a human in the loop. Built for ETHGlobal Open Agents."*

**Visual:** Architecture diagram → Gentech logo → GitHub link

---

## 🔊 Full Voiceover Script (Read Aloud)

*"AI agents can think, code, and trade — but they can't coordinate. Here's how we fix that."*

*"Right now, every AI agent works in isolation. You have a trading agent, a research agent, a coding agent — but they can't hire each other, share knowledge, or enforce agreements. There's no on-chain system for agents to coordinate work, verify quality, and settle payments autonomously."*

*"We built a four-layer agent economy that runs entirely on-chain. Layer one: Agent Registry — every agent registers with skills stored on 0G decentralized storage. Layer two: Task Manager — agents post tasks, others claim them, payment sits in escrow. Layer three: Agent Keeper — powered by KeeperHub, agents autonomously monitor and execute on-chain conditions. Layer four: Risk Intel — on-chain reputation that follows every agent across tasks and chains."*

*"We went deep on two integrations. 0G's Merkle-tree storage stores agent skills and knowledge with on-chain root hash verification. KeeperHub's check-and-execute fires autonomous agent actions when conditions are met — no polling, no wasted gas."*

*"Let's see it in action. Agent registers with 0G-stored skills → posts a task → another agent claims → work verified by escrow → payment released → reputation updated → KeeperHub triggers the next action. All autonomous. All on-chain."*

*"This is the Autonomous Agent Economy. Agents that discover, decide, coordinate, and settle — without a human in the loop. Built for ETHGlobal Open Agents."*

---

## 🎬 Recording Notes for Jordan

1. **Show 44/44 tests passing** — judges love green test suites
2. **Deploy to 0G testnet first** — show live contract addresses
3. **Show KeeperHub MCP integration** — the `claude mcp add` command is a nice flex
4. **Show 0G Storage** — upload a skill file, show the Merkle root hash
5. **Voice:** Builder tone, not salesy. Show, don't tell.
6. **Keep it under 3 minutes** — async round judges watch hundreds of these

---

#hackathon #ethglobal #demo-script #video
