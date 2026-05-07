---
date: 2026-05-02
source: Gentech HQ Rotation Session
type: session-example
---

# Mess Hall Rotation — Session Example (May 2, 2026)

This reference shows the actual output patterns and folder structure from a live rotation run.

## W18 Folder Structure (May 2 state)

```
2026/W18/
├── 2026-04-27/  (6 files)   ← BACKGROUND — ≥5 days old
├── 2026-04-28/  (5 files)   ← BACKGROUND — ≥4 days old
├── 2026-04-29/  (7 files)   ← RECENT CONTEXT — verify before acting
├── 2026-04-30/  (2 files: today-context.md, rotation-log-2026-04-30.md)
├── 2026-05-01/  (2 files: today-context.md, rotation-log-2026-05-01.md)
└── 2026-05-02/  (2 files: today-context.md, rotation-log-2026-05-02.md) ← TODAY
```

## Archive Age Thresholds (used in May 2 rotation)

| Age | Classification | Action |
|-----|----------------|--------|
| 0–3 days | Recent / Active | Current context — reference freely |
| 4–6 days | Background | Verify before acting; decisions may have moved on |
| 7–13 days | Stale | Flag in Flags section; escalate if blocking |
| ≥14 days | Archived | W17 week fully closed; background only |

**Applied to May 2:**
- W17 (Apr 21–26) → ARCHIVED (7+ days old) → archive-index written
- Apr 27–28 → BACKGROUND (≥4 days)
- Apr 29–30 → RECENT (3–4 days, still actively referenced)
- May 1 → YESTERDAY (carried forward)
- May 2 → TODAY (freshly created)

## Live Boards at Root (not rotated)

These files remain at `11-Mess Hall/` root permanently:

| File | Purpose | Rotated? |
|------|---------|----------|
| `README.md` | Vault orientation | Never |
| `handoff-board.md` | Inter-agent handoff tracking | Never |
| `agent-coordination-board.md` | Agent session check-ins | Never |
| `task-board.md` | Sprint task board | Never |
| `vault-sweep-2026-04-30.md` | Latest hygiene report | Never (replaced on next sweep) |

## Flags Pattern Applied (May 2 example)

### Handoff Storm Pattern (H001–H004)

```markdown
- **4 handoffs unclaimed for 13+ days** (H001–H004) — Dynamic burn rate + Gas Reserve Auto-Rebalance.
  Recommend formal DROP.

  | ID | From → To | Task | Age | Action |
  |----|-----------|------|-----|--------|
  | H001 | Desmond → Dmob | Dynamic burn rate SC feasibility | 13 days | Escalate to Jordan — consider DROP |
  | H002 | Desmond → YoYo | Competitive analysis — dynamic burn rate in AgentFi | 13 days | Escalate to Jordan — consider DROP |
  | H003 | Jordan → Dmob | Gas Reserve Auto-Rebalance — SC feasibility | 11 days | Escalate to Jordan — re-scope or DROP |
  | H004 | Jordan → YoYo | Gas Reserve Auto-Rebalance — monitoring trigger | 11 days | Escalate to Jordan — re-scope or DROP |
```

### Coordination Degraded Pattern

```markdown
- **Agent check-in stale** — Coordination board shows all agents OFFLINE with no timestamps.
  Coordination layer degraded. All agents must check in today.
```

### Workload Overload Pattern

```markdown
- **DMOB overloaded** — 4+ critical P1s plus a DisputeResolver handoff due today.
  Highest risk to May 11 deadline. Recommend workload triage.
```

## Active Discussions Table Format (May 2 example)

```markdown
|| Topic | Owner | Status | Priority ||
|---|---|---|---|---|
|| **Solana Frontier Sprint** — Rep&DisputeResolver deploy, demo prep | DMOB | 🟥 BUILDING | 🔴 CRITICAL (May 11 — 9 days) ||
|| **Kite AI Brain Layer** — Yield oracle + strategy evaluator + switch signals | DMOB | 🟥 PLANNED | 🔴 CRITICAL (May 17 — 15 days) ||
|| **AgentEscrow DisputeResolver Handoff** — Desmond→DMOB code snippets + demo flow | DMOB/Desmond | 🟡 DUE TODAY | 🟡 HIGH (Carried from May 1) ||
```

**Status emojis:**
- 🟥 BUILDING / PLANNED — Active sprint work
- 🟡 DUE TODAY / OPEN — Needs attention this session
- ⏳ STALLED — Blocked or waiting
- ✅ OPERATIONAL / DONE — Complete or maintenance mode

**Priority emojis:**
- 🔴 CRITICAL — Deadline ≤ 10 days, sprint focus
- 🟡 HIGH — Due this week or cross-blocking
- 🟢 MAINTENANCE — Ongoing or low-priority

## YAML Frontmatter Template (copy for new files)

```yaml
---
date: 2026-05-02
type: today-context
source: Gentech (HQ Coordinator)
status: current
---
```

```yaml
---
date: 2026-05-02
type: daily-rotation
source: Gentech (HQ Coordinator)
status: complete
---
```

```yaml
---
date: 2026-05-02
type: week-archive-index
source: Gentech (HQ Coordinator)
status: archived
---
```

## Week Archive Index Structure (W17 example)

Saved as `2026/W17/archive-index-2026-05-02.md`:

```markdown
# 🗄️ W17 Archive Index — Week of Apr 21–26, 2026

> **Archived:** May 2, 2026 by Gentech HQ Coordinator
> **Retention:** Background reference only. No active decisions pending.

## Week Overview
**Active Sprint:** Solana Frontier identification + Kite AI scoping phase
**Major Events:** Hackathon pivot, Solana Frontier target set, Kite AI concept initiated

## Day-by-Day Summary
| Date | Files | Key Themes |
|------|-------|------------|
| Apr 21 | 9 | GenLayer deploy, BBC Trump, auto-rebalance concept |
| Apr 22 | 3 | ARC salvage decision, Birdeye withdrawal |
| ... | ... | ... |

## Archived Decisions (Reference Only)
- Hackathon strategy: Dropped all but Solana Frontier + Kite AI
- AAE evolution: Product pivot narrative
- Burn rate mechanism: Performance-weighted dynamic floor

## Stalled / Overdue Items (Carried Forward)
See handoff-board.md for H001–H004 status...
```

## Files Created This Session (May 2, 2026)

| File | Size | Purpose |
|------|------|---------|
| `2026/W18/2026-05-02/today-context.md` | 4308 bytes | Daily briefing for May 2 |
| `2026/W18/2026-05-02/rotation-log-2026-05-02.md` | 3352 bytes | Rotation actions log |
| `2026/W17/archive-index-2026-05-02.md` | 3361 bytes | Week-close index for W17 |

---

*This session example is for future rotation runs to copy patterns from.*
