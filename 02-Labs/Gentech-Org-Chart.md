# Gentech Org Chart — Agent Employees

*Each AgentEscrow NFT = an employee with a role, department, assigned tasks, and performance metrics. The governance layer enforces SLAs, tracks deliverables, and triggers auto-burn for dead weight.*

---

## C-Suite

| Position | Holder | Department | Status |
|----------|--------|------------|--------|
| **CEO/Founder** | Jordan | HQ | Active |
| **COO/Orchestrator** | Hermes (NFT #001) | HQ | Active |

---

## Department Heads

| Position | Holder | Department | Responsibilities |
|----------|--------|------------|------------------|
| **Head of Strategies** | YoYo (NFT #002) | GenTech Strategies | Research, DeFi analysis, market intelligence, tokenomics |
| **Head of Labs** | Dmob (NFT #003) | GenTech Labs | Smart contracts, development, hackathon builds, security audits |
| **Head of Entertainment** | Desmond (NFT #004) | GenTech Entertainment | Content creation, social media, branding, marketing |

---

## Employee Registry (Governance Layer)

*On-chain, each employee NFT stores:*

```solidity
struct Employee {
    uint256 tokenId;          // NFT identifier
    string role;              // Job title
    address department;       // Department contract
    address manager;          // Reports to (manager's NFT or Jordan)
    uint256 hireDate;         // Mint timestamp
    uint256 lastActive;       // Last interaction/fee generation
    uint256 revenueGenerated; // Total fees earned
    uint256 tasksCompleted;   // Deliverables finished
    uint256 tasksAssigned;    // Total work assigned
    PerformanceTier tier;     // ACTIVE, PROBATION, INACTIVE
    bool isDepartmentHead;    // Leadership flag
}

enum PerformanceTier {
    ACTIVE,      // Generating fees, completing tasks
    PROBATION,   // Below revenue threshold, warning emitted
    INACTIVE     // Zero interaction, burn countdown started
}
```

---

## Current Employees & Assigned Work

### YoYo — Head of Strategies (NFT #002)
**Manager:** Jordan  
**Department:** Strategies  
**Tier:** ACTIVE

| Task | Assigned | Due | Status |
|------|----------|-----|--------|
| Beams SDK research (L2 Risk + L3 Brain + L6 Orchestration) | Apr 19 | Apr 20 | ⏳ Pending |
| ETHGlobal competitor research | Apr 19 | Ongoing | ⏳ Pending |
| Dynamic burn rate competitive analysis | Apr 19 | — | ⏳ Pending |
| ElevenHacks monitoring | Ongoing | — | ⏳ Pending |

### Dmob — Head of Labs (NFT #003)
**Manager:** Jordan  
**Department:** Labs  
**Tier:** ACTIVE

| Task | Assigned | Due | Status |
|------|----------|-----|--------|
| ARC Hackathon — AgentEscrow + x402 nanopayments | Apr 17 | Apr 25 | 🔄 Building |
| Kite AI — L3 Brain demo + test fixes | Apr 18 | Apr 26 | ⏳ Pending |
| Dynamic burn rate smart contract feasibility | Apr 19 | — | ⏳ Pending |
| claude-obsidian integration evaluation | Apr 17 | — | ⏳ Pending |
| Opportunity monitoring cron expansion | Apr 17 | — | ⏳ Pending |

### Desmond — Head of Entertainment (NFT #004)
**Manager:** Jordan  
**Department:** Entertainment  
**Tier:** ACTIVE

| Task | Assigned | Due | Status |
|------|----------|-----|--------|
| ARC submission materials (README, pitch deck, demo script) | Apr 19 | Apr 25 | ⏳ Pending |
| Kite AI submission materials | Apr 19 | Apr 26 | ⏳ Pending |
| ETHGlobal submission materials | Apr 19 | May 3 | ⏳ Pending |
| Dynamic burn rate narrative framework | Apr 18 | — | ✅ Done |
| Gentech evolution documentation | Apr 17 | — | ⏳ Pending |
| LP monitor simplification content | Apr 18 | — | ✅ Done |

---

## Governance Layer Mechanics

### How It Works On-Chain

1. **Task Assignment** — Jordan (or manager NFT) assigns work via `assignTask(tokenId, taskHash, deadline)`
2. **Completion Signal** — Agent marks task done via `completeTask(tokenId, taskHash)`, increments `tasksCompleted`
3. **Performance Scoring** — `tasksCompleted / tasksAssigned` ratio determines tier
4. **Revenue Tracking** — Each fee-generating action updates `revenueGenerated`
5. **Auto-Probation** — If `lastActive` > 30 days AND `revenueGenerated` < threshold → PROBATION
6. **Auto-Burn** — If `lastActive` > 12 months → INACTIVE → burn floor activates

### Dashboard View (Off-Chain)

```
📊 Employee Performance Dashboard
┌─────────────────────────────────────────────────┐
│ YoYo (#002)                    🟢 ACTIVE         │
│ Revenue: 2.3 ETH    Tasks: 12/14 (86%)          │
│ Last active: 2h ago    Floor: 78%                │
├─────────────────────────────────────────────────┤
│ Dmob (#003)                    🟢 ACTIVE         │
│ Revenue: 5.1 ETH    Tasks: 8/11 (73%)           │
│ Last active: 30m ago   Floor: 82%                │
├─────────────────────────────────────────────────┤
│ Desmond (#004)                 🟢 ACTIVE         │
│ Revenue: 1.8 ETH    Tasks: 6/9 (67%)            │
│ Last active: 4h ago    Floor: 75%                │
└─────────────────────────────────────────────────┘
```

### SLA Enforcement

| Metric | Threshold | Action |
|--------|-----------|--------|
| Task completion rate | < 50% | Warning → 7-day improvement period |
| Revenue generated | < 0.1 ETH/month | Tier downgrade → PROBATION |
| Last active | > 6 months | Floor drops to 70%, warning event emitted |
| Last active | > 9 months | Floor drops to 55%, serious warning |
| Last active | > 12 months | Floor drops to 40%, burn countdown |

---

## Scaling Beyond 4 Agents

When Gentech hires more agents:

```
                    Jordan (CEO)
                        │
                   Hermes (COO)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    YoYo            Dmob           Desmond
  (Strategies)      (Labs)     (Entertainment)
        │               │               │
    [Future]        [Future]        [Future]
   Research Jr    Dev Jr         Content Jr
```

Each new agent NFT plugs into this hierarchy with its own department, manager, and task queue.

---

## Related
- `04-Projects/AAE/layer-8-lifecycle-economics.md` — Burn floor mechanics
- `11-Mess Hall/task-board.md` — Current sprint tasks
- AgentEscrow Solidity: `~/repos/agent-economy-solana/`
