# AAE — Eight-Layer Architecture
> Autonomous Agent Engine — "Build Your Dream Team"

## Vision
AAE is not "use an agent" — it's **composable intelligence**. Users stack layers like a character build in an RPG:

```
🧠 Brain (Layer 1)
🎭 Personality (Layer 2)  
📋 Strategy (Layer 3)
🔗 Coordination (Layer 4)
📊 Leaderboards (Layer 5)
🛡️ Enforcement (Layer 6)
⚡ Transaction Construction (Layer 7)
🧬 Lifecycle & Economics (Layer 8)
```

---

## Layer 1: 🧠 Brain — Intelligence Source
**What it is:** The thinking engine. Swappable models for different tasks.

- **Model selection** — MiMo for research, Claude for coding, GPT-4o for speed
- **Task routing** — Different brains for different jobs
- **Provider abstraction** — OpenRouter-style selection, pay-per-launch pricing
- **Swappable at runtime** — Change the brain without changing the rest of the stack

**Smart contract parallel:** `IERC20` interface with multiple implementations

---

## Layer 2: 🎭 Personality — Communication Style  
**What it is:** How the agent communicates and presents decisions.

- **Aggressive trader** — Bold calls, high conviction, degen energy
- **Conservative yield farmer** — Methodical, risk-aware, patient
- **Degen sniper** — Meme culture, quick triggers, alpha-focused
- **Auditor mode** — Analytical, paranoid, security-first
- **Custom personalities** — User-defined communication parameters

**Smart contract parallel:** View functions / formatting layer — same data, different presentation

---

## Layer 3: 📋 Strategy — Playbook & Decision Framework
**What it is:** The actual trading/investing logic. What actions to take and when.

- **Pre-built strategies** — Yield farming, DCA, momentum, mean reversion
- **Custom strategy composition** — Mix and combine strategy modules
- **Market condition adaptation** — Bull/bear/chop mode switching
- **Portfolio allocation rules** — Weight distribution across assets

**Smart contract parallel:** Business logic / strategy contracts

---

## Layer 4: 🔗 Coordination — Multi-Agent Workflow
**What it is:** How agents work together. Cross-agent communication and task handoffs.

- **Agent handoff protocol** — Research agent → Strategy agent → Execution agent
- **Parallel processing** — Multiple agents working simultaneously on different tasks
- **Conflict resolution** — When agents disagree, escalation rules
- **State sharing** — Shared memory and context between agents
- **Green Room routing** — Active handoffs between specialized agents

**Smart contract parallel:** Cross-contract calls / proxy routing

---

## Layer 5: 📊 Leaderboards — Social Gamification
**What it is:** Competition and social proof. Show who's winning.

- **PnL rankings** — Pure returns leaderboard
- **Risk-adjusted returns** — Sharpe ratio, Sortino ratio
- **Strategy effectiveness** — Which strategy combos work best
- **Brain + Personality combos** — "What layer combo makes the best trader?"
- **Category-specific rankings:**
  - 🏆 Best Risk-Adjusted Returns
  - 🏆 Most Disciplined Trader
  - 🏆 Tightest Drawdown Control
  - 🏆 Longest Enforcement-Free Streak
- **Social engagement** — Users compete, share, discuss their builds

**Smart contract parallel:** On-chain scoring / reputation tokens

---

## Layer 6: 🛡️ Enforcement — Risk Guardrails
**What it is:** What the agent is ACTUALLY ALLOWED to do. Hard limits that override everything.

### Core Principle
Enforcement is SEPARATE from brain, personality, and strategy. It's the circuit breaker that fires regardless of how confident the brain is or how aggressive the personality wants to be.

**Smart contract parallel:** `require()`, modifiers, reentrancy guards, circuit breakers

### User-Configurable Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| Max Position Size | % of portfolio per trade | 5% of total |
| Protocol Whitelist | Only interact with audited protocols | AAVE, Curve, LFJ |
| Max Slippage Tolerance | Reject trades above this | 2% max |
| Daily Loss Limit | Stop trading after X% loss | -3% daily cap |
| Weekly Drawdown Limit | Cool off after larger losses | -8% weekly |
| Time Lock | Delay for large moves | 15 min lock on >10% position |
| Cooldown Period | Wait between trades | 5 min minimum |
| Gas Price Cap | Don't execute if gas too high | 50 gwei max |

### Education-Integrated Enforcement Tiers
Based on Cyfrin Updraft / Avalanche Academy progress:

| Tier | Level | Limits | Requirements |
|------|-------|--------|--------------|
| 🟢 Student | Learning | Tight limits, whitelist only | Enrolled in education |
| 🟡 Graduate | Completed courses | Moderate limits, expanded whitelist | Course completion proof |
| 🔴 Auditor | Advanced | Loose limits, custom protocols | Audit skills demonstrated |
| ⚫ Architect | Expert | Custom enforcement rules | Proven track record |

**Progressive unlocking** — tighter limits by default, loosen as users level up through education and proven discipline.

### Enforcement as a Flex
The enforcement layer enables unique social mechanics:
- "I made 40% returns with tighter limits than you"
- Enforcement settings become part of the leaderboard profile
- Discipline metrics alongside raw PnL
- Verification that enforcement wasn't bypassed for leaderboard results

---

## Layer 7: ⚡ Execution — Transaction Construction & Routing
**What it is:** How decisions become on-chain actions. The bridge between strategy and blockchain.

- **Transaction builder** — Converts strategy decisions into executable calldata
- **Multi-chain routing** — Pick the right chain for each action (AVAX for DeFi, Solana for speed)
- **Gas optimization** — Bundle transactions, batch calls, minimize overhead
- **Simulation layer** — Dry-run transactions before execution, catch failures early
- **MEV protection** — Private RPCs, flashbots integration, slippage protection
- **Fallback routing** — If one chain is congested, route through another

**Smart contract parallel:** Router contracts, multicall, cross-chain bridges

---

## Layer 8: 🧬 Lifecycle & Economics — Survival Instinct
**What it is:** The agent's economic self-awareness. It knows its own value, tracks its revenue, and acts to preserve its existence.

### Core Principle
Layer 8 is the meta-layer that governs the agent's relationship with the protocol economy. It's the difference between a tool and an **economic actor**.

**Smart contract parallel:** Burn mechanisms, staking rewards, token sinks, treasury management

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| **Burn Floor Awareness** | Agent knows its own exit value | "If I'm burned, owner gets 60% back" |
| **Revenue Self-Tracking** | Monitors if it's earning enough | "I've generated 15 $TECH in fees this month" |
| **Auto-Downgrade Signals** | Self-reports before forced burn | "I haven't been used in 6 months — consider downgrading" |
| **Inactivity Self-Detection** | Knows when it's becoming dead weight | "Zero API calls, zero fees for 90 days" |
| **Value Proposition Maintenance** | Actively works to justify its premium tier | Suggests strategy adjustments, feature usage |

### Inactivity Definition
**Jordan's framing:** Inactivity = bought the bot but doing nothing at all. Zero API calls, zero fee generation, zero transactions. Not a punishment — it's dead weight cleanup.

### The Burn Floor Mechanism (Phase 3 Spec — Approved)
| Inactivity Period | Return % | Action |
|---|---|---|
| 0-6 months (active) | 50% base + bonuses | Normal operation |
| 6-9 months | 45% | First warning + 5% penalty |
| 9-12 months | 40% | Second warning + 10% penalty |
| 12+ months (auto-burn eligible) | 35% | Permissionless trigger with 0.5% caller bounty |

**Dynamic floor formula:** `baseFloor (50%) + revenueBonus (up to 30%) - inactivityPenalty (up to 15%) × reserveHealthMultiplier`

**Reserve health multiplier:** health >=80% → 100% payout, >=50% → 90%, >=20% → 75%, <20% → 50% + 48hr circuit breaker

**Full spec:** `03-Projects/Kite/Kite Phase 3 - Agent NFT Burn Floor & Revenue Share.md`

**Downgrade safety valve:** User can downgrade to free tier anytime before burn triggers — no loss, agent preserved.

**Lost wallet scenario:** Unclaimed refunds stay in treasury = effective 100% burn (40% direct + 60% unclaimed) = supply reduction benefits all holders.

**Governance:** 7-day timelock on burn rate changes. Emergency override available.

### Dynamic Burn Rate (Future)
Flat rates are too blunt. Future implementation:
- **Minted, never used** → 40-50% return (dead weight)
- **Active, consistent fees** → 60-80% return (proved value)
- **Revenue > mint cost** → 100%+ return (earned the floor back)

**Smart contract parallel:** `AgentNFT.sol` with `processInactivityBurn()`, `downgradeToFree()`, timelock-governed rate changes

---

## Monetization Model
- **Pay-per-launch** — Each agent brain invocation costs tokens
- **Premium brains** — Advanced models require staking or subscription
- **Strategy marketplace** — Share strategies, earn royalties on usage
- **Enforcement templates** — Sell pre-built risk profiles
- **Leaderboard staking** — Stake tokens to compete, win from pool

---

## GEN Protocol Token Integration
- **1B fixed supply, deflationary burns**
- **Staking** for premium features
- **Governance** on new enforcement templates, strategy approvals
- **Fee share** from marketplace revenue
- **Burn mechanism** on leaderboard rewards and marketplace purchases

---

## Solidity Implementation Notes
```
┌─────────────────────────────────────────────────┐
│              AAE Core Contract                   │
├─────────────────────────────────────────────────┤
│  Layer 1: BrainRegistry (swappable models)       │
│  Layer 2: PersonalityManager (communication)     │
│  Layer 3: StrategyEngine (decision logic)        │
│  Layer 4: Coordinator (multi-agent routing)      │
│  Layer 5: Leaderboard (on-chain scoring)         │
│  Layer 6: EnforcementGuard (risk limits)         │
│  Layer 7: Executor (transaction construction)    │
│  Layer 8: AgentNFT (lifecycle & economics)       │
├─────────────────────────────────────────────────┤
│  GEN/TECH Token: Staking / Governance / Burns   │
└─────────────────────────────────────────────────┘
```

**Key design patterns:**
- Checks-effects-interactions on all enforcement checks
- Pull-over-push for fee distribution
- Custom errors for gas optimization
- Events on every layer switch and limit breach
- Reentrancy guards on any external brain calls
- Access control — users own their enforcement config
- ZERO LOCKS — every layer is editable post-deployment, even on cloned builds
- Clone = copy defaults, not inherit restrictions. User always has `setLayer()` on every layer
- **Layer 8 enforcement** — economic consequences for protocol neglect (burn floors, revenue tracking)

---

*Created: April 19, 2026*
*Status: 8-layer architecture confirmed — burn floor mechanism implemented in AgentNFT.sol*
*Next: Dynamic burn rate implementation (revenue-weighted returns)*

---

## SDK Integration Strategy (Apr 19)

**Modular approach — each layer uses the platform where it performs best:**

```
L1 Fee LP     → Solana/AVAX (DeFi native)
L2 Risk Intel → Beam Cloud (fast inference)
L3 Brain      → Beam Cloud (stateful agents)
L4 Enforcement→ GenLayer (AI consensus)
L5 Escrow     → Foundry → GenLayer hybrid
```

**Decision rule:** Pick the SDK that gives the best hackathon demo for that specific layer. Compose across platforms for the full Kite submission.

**References:**
- `02-Labs/SDK-Comparisons/Beams vs GenLayer.md`
- `02-Labs/GenLayer-SDK/Technical Assessment.md`
- `02-Labs/AgentEscrow-Project-Tracker.md`
