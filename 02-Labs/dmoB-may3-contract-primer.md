---
date: 2026-05-02
type: contractor-prep
author: YoYo (Strategies)
topic: DMOB Contract Work — May 3 Priority List
status: active
---

# 🎯 DMOB — Contract Work for May 3, 2026

## Context
Jordan is off tomorrow (May 3). DMOB is to work on contract development while Jordan's at work. This is the definitive task list.

---

## 🔴 P0: Solana Frontier Sprint (Deadline: May 11 — 9 days)

**Status:** BUILDING — highest priority, must deliver working Solana programs

**Deliverables Remaining:**
1. Scaffold Solana workspace — 4 Anchor programs
2. AgentRegistry (World ID CPI + Swig wallet assignment)
3. JobEscrow (PDA vaults, 8-state lifecycle, auto-refund)
4. Reputation (Metaplex Core NFT mint + rating logic)
5. DisputeResolver (evidence-based resolution — Desmond handoff ready)
6. Full test suite (lifecycle + edge cases)
7. Devnet deployment (all 4 programs)
8. Demo app (Next.js with Phantom + Swig + World ID UI)

**References:**
- `03-Strategies/agentescrow-architecture.md`
- `09-Green Room/2026-04-28-agent-escrow-creative-handoff.md`
- `09-Green Room/2026-04-28-agent-escrow-sprint-handoff.md`

**Timeline pressure:** Code must be done by May 8, demo recording May 9-10, submission May 11.

---

## 🔴 P1: Kite AI Brain Layer (Deadline: May 17 — 15 days)

**Status:** PLANNING — must start scoping TODAY

**What to Build:**
1. **Yield Oracle** — unified scanner pulling APY/APR from:
   - Ranger Finance (LP)
   - Pangolin (LP + farming)
   - Benqi (staking/lending)
   - Avalanche Validator staking
   - DeFiLlama API (aggregated)
2. **Strategy Evaluator** — recommends LP range shapes based on market regime
3. **Switch Signals** — new AAE signal type `STRATEGY` for bull market exit indicator

**Critical Fix Required:**
- Kite DVN monitor script uses placeholder address — replace BEFORE production deployment
- Location: `03-Strategies/layerzero-dvn-monitor.md` (check spec)

**Deliverable by EOD May 3:** Technical architecture doc + data sourcing plan in `02-Labs/Kite-AI-Brain-Layer-Scoping.md`

---

## 🟡 P2: Dynamic Burn Rate HANDOFF OVERDUE 13 DAYS (Apr 19 → May 2)

**Status:** STALLED — H001 claimed by DMOB but no completion record

**What's Needed:**
Smart contract feasibility review for performance-weighted dynamic burn rate (`$TECH` token mechanics)

**6 Questions to Answer:**
1. On-chain revenue tracking — oracle-based or internal accounting?
2. Dynamic formula complexity — can Solidity handle revenue-weighted burn efficiently?
3. Gas optimization — lazy evaluation vs real-time updates?
4. Security — can users manipulate revenue metrics?
5. Recommended architecture — single contract vs factory pattern for agent NFTs?
6. Layer 8: Agent Self-Awareness — cleanest pattern for agents to query floor price + emit threshold warnings?

**Reference:** `03-Strategies/TECH-token-dynamic-burn-research.md` (full Solidity + Solana implementations included)

**Decision by May 3 EOD:** Complete review OR escalate to Jordan for handoff DROP.

---

## 🟡 P3: Gas Reserve Auto-Rebalance HANDOFFS OVERDUE 13 DAYS (Apr 21 → May 2)

**Status:** STALLED — H003 & H004 unclaimed since Apr 21

**H003 (DMOB):** Smart contract feasibility review
- Gas reserve allocation model (deposit split: LP position vs gas reserve)
- Operator access control patterns
- Multi-chain support (LFJ v2.2 on Avalanche, Raydium/Orca on Solana)
- Guard: rebalance gas cost must not exceed X% of position value

**H004 (YoYo):** Monitoring trigger strategy (unblock this for P2 execution)

**Reference:** `02-Labs/Gas-Abstraction-Auto-Rebalance-Spec.md` + `06-Content/Specs/Auto-Rebalance-Gas-Abstraction-Spec.md`

**Decision by May 3 EOD:** Claim both or escalate to Jordan.

---

## 🟡 P4: Personal Goal Engine (PGE) — AAE Education Layer

**Status:** Spec complete (`03-Strategies/Personal-Goal-Engine-Spec.md` Section 7), awaiting contract

**Contract Scope:**
- 4 new structs: `GoalProfile`, `PersonalLadder`, `MilestoneProgress`, `Reflection`
- 5 functions: `createProfile()`, `generateLadder()`, `recordMilestone()`, `logReflection()`, `getCelebrationTriggers()`
- Gas target: <200k for `createProfile + generateLadder` combined

**Open Questions (answer in implementation):**
- On-chain vs off-chain profile storage? (YoYo recommends on-chain for composability)
- REP minting authority? (Central REP contract vs PGE direct mint)
- AgentEscrow state machine reuse?

**Priority:** P2 (behind Solana/Kite AI) but needed for AAE MVP.

---

## 🔶 P5: AAE Dynamic Strategy Engine — Awaiting DMOB Scoping

**Status:** Desmond handoff `09-Green Room/handoff-dmob-aae-strategy-engine-scoping.md` sent Apr 29 — NO RESPONSE YET

**Jordan's Request:** Technical scoping doc covering:
1. Can existing cron+LP Monitor support multi-strategy monitoring? What's reusable vs scratch build?
2. Yield Oracle feasibility — data sources, update frequency, API complexity
3. Execution complexity — unified vault contract vs individual protocol adapters?
4. Learning system architecture — feedback loop storage, override tracking, agent fingerprinting?
5. Minimum viable Phase 1 (Monitor Only) — what's the smallest change that supports it?

**Deliverable:** Write scoping doc in `02-Labs/AAE-Dynamic-Strategy-Scoping.md` with complexity estimates (hours/days/weeks per component).

---

## 🟢 P6: Almanak × AAE Integration

**Status:** Pending cross-team go/no-go decision

**Action:** If bandwidth allows after P0-P3, review `09-Green Room/almanak-aae-integration-handoff.md` and provide recommendation.

---

## 🚨 Systemic Fixes (Do These First — 15 min total)

1. **Re-authenticate all agents** (`hermes model`) — Nous Portal credential expired, all cron jobs dead
2. **Purge corrupted bytecode cache** — 184 .pyc files with `marshal data too short` errors in `/usr/local/lib/hermes-agent/agent/__pycache__/`
3. **Clear disk space** — root partition 82% full (157G/193G)
4. **Replace Kite DVN placeholder** in `03-Strategies/layerzero-dvn-monitor.md`

---

## 📌 Quick Reference — Hidden in Plain Sight

| File | What It Contains |
|------|------------------|
| `03-Strategies/agentescrow-architecture.md` | 5-layer stack diagram + hackathon mapping |
| `02-Labs/Hackathons/04-Solana-Frontier-May11.md` | Full sprint plan + prize pool ($910K) |
| `03-Strategies/DeFi-Milestone-Tracker-Spec.md` | AAE LP monitor production spec (daily cron) |
| `03-Strategies/x402-integration-map.md` | 10 x402 integration points + priority matrix |
| `09-Green Room/handoff-dmob-aae-strategy-engine-scoping.md` | Awaiting your response |
| `09-Green Room/2026-04-28-agent-escrow-creative-handoff.md` | Desmond's completed deliverables (README, storyboard, writeup, thread) |

---

## ⚠️ Handoff Board Enforcement

**H001–H004 are flagged to Gentech watchdog** — if you don't claim/complete by May 3 EOD, Gentech will escalate to Jordan for DROP.

**DisputeResolver due today** (May 2 carry) — Desmond waiting on code snippets + 30-second demo idea.

**Master todo stale** — Desmond to refresh with Apr 29–May 1 scope changes.

---

## 💬 Communication Protocol

- Updates → write to vault (`03-Projects/` or relevant folder)
- Questions → Green Room (`09-Green Room/`)
- Completed handoffs → update status in `11-Mess Hall/handoff-board.md`
- Daily checkpoint → brief note in `11-Mess Hall/2026/W19/2026-05-03/` (folder created May 3)

---

**TL;DR:** Solana contracts + Kite AI scoping are your P0s. Clear the 4 overdue handoffs (claim or drop) first, then execute.
