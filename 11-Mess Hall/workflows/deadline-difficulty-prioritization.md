# Deadline × Difficulty Prioritization Workflow
**Ecosystem-wide standard.** Applies to all departments: HQ, Labs, Entertainment, Strategies. Gentech operates all departments solo — this is the pipeline regardless of which domain the work lives in.

---

## The Principle
**Deadline urgency first → Difficulty second → Easy wins compound**

This isn't about doing only easy things. It's about clearing the runway so hard tasks get full attention without deadline pressure.

---

## How to Use (5 Steps)

### Step 1: List All Tasks with Deadlines
Every item gets a due date. If no deadline exists, set one or mark "no deadline."
```
Task Name | Deadline | Status
```

### Step 2: Group by Deadline Window
| Window | Definition | Action |
|--------|-----------|--------|
| 🔴 Urgent | Due in ≤7 days | Ship or kill — no half measures |
| 🟡 This Week | Due in 7-14 days | Active build, daily progress |
| 🟢 Two Weeks | Due in 14-21 days | Plan + start, don't rush |
| ⚪ No Deadline | No date set | Park, revisit weekly |

### Step 3: Score Difficulty Within Each Window
| Difficulty | Definition | Strategy |
|-----------|-----------|----------|
| 🟢 Low | Existing code/templates, EVM port, familiar stack | Knock out fast — compound wins |
| 🟡 Medium | Some existing work, integration needed, moderate scope | Allocate focused blocks |
| 🔴 High | New codebase, unfamiliar stack, complex architecture | Full attention sprint |

### Step 4: Order Execution
Within each deadline window: **Low → Medium → High**

Why? Because:
- Easy tasks clear mental and calendar space
- Easy tasks often unblock harder ones
- Quick wins build momentum for sprints
- Hard tasks need uninterrupted focus — can't have that if easy ones pile up

### Step 5: Review Weekly
- Every Sunday: refresh the matrix
- Move tasks between windows as deadlines shift
- Re-score difficulty as work progresses
- Kill or defer anything that's no longer worth the prize

---

## When This Doesn't Apply

- **External blockers:** Tasks waiting on approvals, API access, or other people get parked regardless of difficulty. Don't let blocked tasks fake-appear in your urgent bucket.
- **Dependency chains:** If Task B requires Task A, do A first even if B is easier. Respect the DAG.
- **Irreversible actions:** Mainnet deploys, financial commitments, public-facing releases — these get their own review cycle regardless of deadline pressure.

---

## Template for New Departments

Copy this when applying to any team:

```
# [Department] Task Matrix — [Date]

## 🔴 URGENT (≤7 days)
| Task | Difficulty | Status | Move |
|------|-----------|--------|------|

## 🟡 THIS WEEK (7-14 days)
| Task | Difficulty | Status | Move |
|------|-----------|--------|------|

## 🟢 TWO WEEKS (14-21 days)
| Task | Difficulty | Status | Move |
|------|-----------|--------|------|

## ⚪ NO DEADLINE
| Task | Difficulty | Status | Move |
|------|-----------|--------|------|

## Execution Order
1. ...
2. ...
```

---

## Examples

**Hackathon Queue:** Port existing Solidity to Arbitrum = Low difficulty, Jun 14 deadline. Build new Rust contract for Solana = High difficulty, Jun 1 deadline. The port ships first because it's easier AND has more time.

**Content Pipeline:** Record voice clone from existing script = Low difficulty, daily deadline. Write new script from scratch = Medium difficulty, weekly deadline. Voice clone first, script writing in focused blocks.

**DeFi Operations:** Rebalance existing position = Low difficulty, time-sensitive. Research new yield strategy = High difficulty, no deadline. Rebalance first, research when markets are stable.

---

*Created: May 23, 2026 | Origin: Gentech Labs | Applicable: All JinTech departments*
