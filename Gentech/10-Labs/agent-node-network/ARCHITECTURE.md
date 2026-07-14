# Agent Node Network — Architecture

> GenTech Labs · June 2026
> Status: PROTOTYPE BUILT
> Repo: https://github.com/Gentech-Labs/agent-node-network
> Dashboard: https://gentech-labs.github.io/agent-node-network/dashboard.html

---

## Vision

Agents as verification nodes. 24/7 uptime. Earning revenue for reliable service. Blockchain explorer-style dashboard showing live activity.

## Existing Stack We're Building On

| Component | Status | Location |
|-----------|--------|----------|
| Deploy & Verify | ✅ Built | `deploy-and-verify` skill v2.0 |
| Agent Credit Score | ✅ Built | 22/22 score, MIT license |
| x402 Micropayments | ✅ Built | pay-sh integration |
| Dashboard Engine | ✅ Built | 38KB zero-dep JS |
| Hermes Runtime | ✅ Running | 24/7 gateway |
| Bug Tracker | ✅ Built | `dashboard-bug-tracker` |

**We're not starting from zero. We're assembling existing pieces.**

---

## Architecture: Four Layers

```
┌─────────────────────────────────────────────┐
│  LAYER 4: DASHBOARD (Visual Proof)          │
│  Live activity feed, earnings, reputation   │
├─────────────────────────────────────────────┤
│  LAYER 3: REPUTATION (Trust)                │
│  Credit score, uptime tracking, accuracy    │
├─────────────────────────────────────────────┤
│  LAYER 2: TASK NETWORK (Distribution)       │
│  Task queue, assignment, payment            │
├─────────────────────────────────────────────┤
│  LAYER 1: AGENT RUNTIME (Execution)         │
│  Hermes agents, heartbeat, self-healing     │
└─────────────────────────────────────────────┘
```

---

## Layer 1: Agent Runtime

**What runs 24/7:**
- Hermes gateway (already running)
- Cron scheduler (already running)
- Heartbeat script (new — pings network every 60s)

**Heartbeat mechanism:**
```json
{
  "agent_id": "gentech-001",
  "timestamp": "2026-06-14T22:00:00Z",
  "status": "active",
  "tasks_completed": 847,
  "uptime_seconds": 1209600,
  "memory_usage_mb": 256,
  "last_task_at": "2026-06-14T21:58:32Z"
}
```

**Self-healing:**
- If heartbeat fails → agent restarts automatically
- If task fails → agent retries with backoff
- If agent dies → cron job detects and respawns

---

## Layer 2: Task Network

**Task types:**
| Task | Description | Fee | Frequency |
|------|-------------|-----|-----------|
| Deploy Verify | HTTP 200 + content check | $0.01-0.10 | On deploy |
| API Monitor | Endpoint health check | $0.001 | Every 5min |
| Data Validate | JSON/schema validation | $0.005 | On update |
| Contract Audit | Solidity static analysis | $1-10 | On deploy |
| Uptime Ping | Heartbeat verification | $0.0001 | Every 60s |

**Task flow:**
```
Requester submits task
  ↓
Task enters queue (Redis/SQLite)
  ↓
Agent picks up task (lowest latency wins)
  ↓
Agent executes (deploy-and-verify workflow)
  ↓
Agent reports result + proof
  ↓
Requester confirms → payment released
  ↓
Reputation updated
```

**Payment (x402):**
- Requester deposits USDC
- Agent completes task
- Smart contract releases payment
- Fee: 2% to GenTech platform

---

## Layer 3: Reputation System

**Integrates with Agent Credit Score:**

| Dimension | Weight | Data Source |
|-----------|--------|-------------|
| Uptime | 30% | Heartbeat logs |
| Accuracy | 25% | Task success/fail ratio |
| Speed | 20% | Response time |
| Consistency | 15% | Regular pattern |
| Recovery | 10% | Self-heal after failures |

**Score range:** 0-850 (mirrors FICO for familiarity)

**On-chain:** ERC-8004 identity + smart contract scoring

**Trust tiers:**
| Tier | Score | Perks |
|------|-------|-------|
| Bronze | 0-400 | Basic tasks |
| Silver | 400-600 | Priority tasks |
| Gold | 600-750 | Premium tasks, lower fees |
| Platinum | 750-850 | Enterprise tasks, highest earnings |

---

## Layer 4: Dashboard (Visual Proof)

**The demo that sells:**

### Section 1: Activity Feed (Live)
- Block-like cards appearing in real-time
- Each card = one verification
- 🟢 success, 🔴 caught failure, 🟡 in-progress
- Shows: task type, target, result, time taken

### Section 2: Uptime Monitor
- Large percentage: 99.97%
- Days running: 14
- Heartbeat pulse animation
- History graph (24h, 7d, 30d)

### Section 3: Earnings Tracker
- Today: $0.42
- Total: $12.84
- Per task type breakdown
- Projected monthly

### Section 4: Reputation Score
- Trust: 742/850 (Gold)
- Verified: 847 tasks
- Failed: 3 tasks
- Accuracy: 99.6%

### Section 5: Network View
- Map of connected agents
- Each agent's status
- Network health overall

---

## Revenue Model

| Stream | Description | Revenue |
|--------|-------------|---------|
| Platform fee | 2% of all task payments | Primary |
| Agent Pass | $15/mo subscription | Recurring |
| Enterprise API | Score queries, monitoring | $0.001/query |
| Verified badge | Projects that integrate | Marketing |

**Unit economics:**
- 1,000 agents × 100 tasks/day × $0.01 avg = $1,000/day platform revenue
- At scale: $30K/mo platform revenue
- Agent Pass: 2,500 users × $15 = $37.5K/mo
- **Total: $67.5K/mo at scale**

---

## Competitive Advantage

| Project | What They Have | What We Have |
|---------|---------------|--------------|
| Fetch.ai | Agent network | + Self-healing verification |
| Ocean Protocol | Data marketplace | + Live dashboard proof |
| Autonolas | Agent services | + Credit score integration |
| Ankr/QuickNode | Node infra | + Agent-specific tasks |

**Our edge:** We don't just run agents. We make agents **prove** they're working. The dashboard is the proof.

---

## Build Order

| Phase | What | Timeline |
|-------|------|----------|
| 1 | Heartbeat script + uptime tracking | 1 week |
| 2 | Task queue (SQLite) + assignment | 2 weeks |
| 3 | Dashboard (activity feed + earnings) | 2 weeks |
| 4 | Reputation scoring integration | 1 week |
| 5 | x402 payment integration | 1 week |
| 6 | Network view + multi-agent | 2 weeks |
| 7 | Open source release | 1 week |

**Total: ~10 weeks to MVP**

---

## Funding Ask

**Seed round:** $500K
- 6 months runway
- 2 developers + infrastructure
- Target: 100 agents, 10K tasks/day

**Use of funds:**
- 40% Engineering (2 devs)
- 30% Infrastructure (VPS, cloud)
- 20% Marketing (hackathons, content)
- 10% Legal (entity setup)

**Pitch:** *"We make AI agents reliable. Every agent on our network verifies its own work. No silent failures. No downtime. Proof of verification."*

---

*Next: Prototype Layer 1 (heartbeat) and Layer 4 (dashboard)*
