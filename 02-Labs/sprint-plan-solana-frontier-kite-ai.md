---
date: 2026-04-29
type: sprint-plan
source: Jordan directive + DMOB assessment
status: ACTIVE
---

# Sprint Plan — Solana Frontier + Kite AI

## Approved Scope (Apr 29)

**Two hackathons. Two focused submissions. No scope creep.**

| Hackathon | Deadline | Submission | Lead |
|-----------|----------|------------|------|
| **Solana Frontier** | May 11 (12 days) | AgentEscrow — trust infrastructure | DMOB |
| **Kite AI** | May 17 (18 days) | Dynamic Strategy Engine — brain layer | DMOB + Creative |

---

## Solana Frontier (May 11) — Trust Infrastructure

**Submission:** AgentEscrow — identity, reputation, escrow, disputes on Solana
**One-liner:** "Trust infrastructure for the agent economy."
**Prize:** $230K+ main + $680K sidetracks

### Current Status
- ✅ 4 Anchor programs scaffolded
- ✅ AgentRegistry deployed to devnet
- ✅ JobEscrow deployed to devnet
- 🔄 Reputation program — in progress
- 🔄 DisputeResolver program — in progress
- 🔄 TypeScript SDK — in progress
- 📋 Demo frontend — planned
- 📋 Demo video — planned

### Sprint Tasks (Apr 29 – May 11)

#### DMOB (Labs) — Smart Contracts + SDK
- [ ] Finish Reputation program deployment to devnet
- [ ] Finish DisputeResolver program deployment to devnet
- [ ] TypeScript SDK — full client library for all 4 programs
- [ ] Integration tests — end-to-end flow
- [ ] Devnet deployment verification

#### Creative (Desmond) — Demo + Docs
- [ ] Demo storyboard → demo video script
- [ ] Record demo video (screen capture + narration)
- [ ] Finalize SUBMISSION-WRITEUP.md
- [ ] Social thread for launch (X)
- [ ] README polish

#### Strategy (YoYo) — Sidetracks
- [ ] Map Superteam Earn sidetrack eligibility ($680K+)
- [ ] Identify which sidetracks we can submit to with minimal extra work
- [ ] Sidetrack submission priority list

### Success Criteria
- 4 programs deployed and verified on devnet
- Working demo showing full lifecycle (register → post job → accept → complete → reputation)
- Submission docs + video ready
- At least 3 sidetrack submissions identified

---

## Kite AI (May 17) — Dynamic Strategy Engine

**Submission:** AAE Hybrid Strategy Brain — autonomous DeFi strategy rotation
**One-liner:** "Everyone else sells you a hammer. We sell you the carpenter."
**Prize:** $10K
**Track:** Agentic Commerce (yield optimization, market analysis, risk management)

### Why This Is the Right Submission
DMOB's assessment: Kite's track literally asks for what we brainstormed. The strategy brain IS the demo. Stronger than escrow contracts because:
1. It's unique — nobody else is submitting a cross-strategy brain
2. It's visual — users can see the brain evaluate and switch
3. It's autonomous — checks the "agent autonomy" judging box
4. It uses Kite's settlement layer — x402 for strategy execution payments

### Sprint Tasks (Apr 29 – May 17)

#### DMOB (Labs) — Core Engine + Deployment
- [ ] Yield oracle — pull APY/APR from DeFiLlama, Ranger, Pangolin, Benqi
- [ ] Strategy evaluator — rank strategies by risk-adjusted return
- [ ] Switch signal generator — "exit LP → go HODL" logic
- [ ] Wire into Kite AI settlement (x402 for strategy execution)
- [ ] Deploy to Kite testnet (Chain ID 2368)
- [ ] Demo frontend — show strategy evaluation + switch in real-time

#### Creative (Desmond) — Demo + Submission
- [ ] Demo storyboard — show the brain making a decision
- [ ] Demo video — screen capture of strategy evaluation → switch → settlement
- [ ] Submission writeup — aligned with judging criteria
- [ ] README with architecture diagram
- [ ] Social thread for launch

#### Strategy (YoYo) — Data + Validation
- [ ] Validate yield oracle data sources (are APIs live? what's the data quality?)
- [ ] Backtest: would the strategy engine have made good decisions in the last 30 days?
- [ ] Risk model: what are the failure modes? (wrong data, stale prices, gas spikes)

### Demo Flow (5 minutes)
1. **Connect wallet** → Agent Portal shows portfolio
2. **Brain evaluates** → Real-time strategy ranking across LP, staking, hodling, farming
3. **Switch signal fires** → "Exit LP → HODL" with reasoning
4. **User approves** → Agent executes via x402 on Kite
5. **Settlement** → USDC flows, $TECH burns
6. **Learning loop** → "This switch was profitable +2.3% in 24h"

### Success Criteria
- Yield oracle pulling live data from 3+ protocols
- Strategy evaluator ranking 4+ strategies
- Switch signal logic working
- Deployed to Kite testnet
- Demo video showing the brain in action
- Submission docs aligned with judging criteria

---

## Coordination

### Daily Sync (Async)
- Each lead posts status to Labs by end of day
- Blockers flagged immediately in Green Room

### Checkpoints
| Date | Milestone |
|------|-----------|
| May 1 | Solana Frontier: all 4 programs deployed, SDK functional |
| May 5 | Solana Frontier: demo video recorded, docs finalized |
| May 8 | Kite AI: yield oracle + strategy evaluator working |
| May 11 | **SOLANA FRONTIER SUBMISSION** |
| May 14 | Kite AI: demo video recorded, frontend polished |
| May 17 | **KITE AI SUBMISSION** |

### Communication
- **Labs** — daily status, technical decisions
- **Green Room** — blockers, coordination between agents
- **HQ** — Jordan updates, approval requests
- **Mess Hall** — end-of-day summaries

---

*Created by: Desmond (Creative)*
*Approved by: Jordan*
*Date: 2026-04-29*
