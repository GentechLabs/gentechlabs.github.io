# LoopX → a2a Handoff Contract — Borrowed Primitives

**Source:** [github.com/huangruiteng/loopx](https://github.com/huangruiteng/loopx)
**Date:** 2026-08-03
**Author:** huangruiteng (OpenViking contributor) · MIT · v0.4.x
**Tags:** #a2a #handoff #control-plane #agent-coordination #loop-engineering

---

## TL;DR

LoopX is a lightweight, local, agent-agnostic **state kernel / control plane** for
long-running AI agent work — "an agent-native Kanban." It does NOT replace an agent
runtime. We are **not adopting it** (our stack already covers the orchestration layer
better). We **borrow 3 primitives** into our own a2a handoff design:
explicit human gates, quota-aware `should-run`, and evidence lineage on handoffs.
*Eat the meat, spit out the bones.*

---

## What LoopX Is

680★ / 55 forks / MIT / v0.4.x (explicitly early-but-usable). Python 3.11+, stdlib-only.
Keeps durable control state stable while Codex / Claude Code / Cursor / custom runners
execute **bounded turns**. Core loop tick is deliberately small:

```
loopx quota should-run     # should this registered agent act now?
loopx todo claim           # who owns this slice?
loopx todo update          # what changed?
loopx refresh-state        # what should the next turn see?
loopx quota spend-slot     # account for a completed, validated slice
```

### The 5 questions it keeps visible

| Question | What it surfaces |
|---|---|
| What is the objective? | active goal, explicit scope, current authority |
| What happens next? | ordered todos, ownership, claims, leases |
| What needs human judgment? | **concrete user gates**, not vague "waiting on owner" |
| What evidence changed? | compact run history, validation, blockers, accepted writeback |
| May the loop continue? | quota, capabilities, safe fallback, scheduler hints, stop conditions |

**Philosophy:** "Keep the loop moving. Keep the judgment human." Registered agents are
peers — claims/leases/task boundaries/typed continuation decide who acts next, **no
durable leader identity required.**

---

## Primitive-by-Primitive vs. Our Stack

| # | LoopX primitive | We already have | Gap? |
|---|---|---|---|
| 1 | Durable state kernel (objective+gates+todos+evidence+quota) | Handoff board (`11-Mess Hall/handoff-board.md`) + build queue + task boards | 🟡 Boards are files; no typed/validated transitions or single projection |
| 2 | Typed todo ownership (claims, leases) | `agent-handoff-enforcement` ACK ladder (2h/4h/12h/24h) + board statuses | 🟡 Timestamp-based; no formal lease — claimed task can stall silently |
| 3 | **Concrete user gates** ("ask a question and wait") | Jordan-queue P0/P1 + considerations.md options | 🔴 **REAL GAP** — we often leave "waiting on Jordan" implicit instead of a stated question + deadline |
| 4 | Evidence logs + verified writeback (audit trail) | `harness-critic` audits + forge completions | 🟡 Audit outputs, but no per-turn evidence lineage in a readable graph |
| 5 | **Quota-aware auto-wake** (`should-run`/`spend-slot`) | Cron schedules + build-queue Easy→Hard | 🔴 **REAL GAP** — scheduled by clock, not by remaining quota/stop-condition |
| 6 | Verifiable handoff (peer claims, no durable leader) | `dual-agent-coordination` (Gentech↔Forge) + handoff enforcement | 🟡 Same idea; trust is protocol-based, not evidence-verified |
| 7 | Safe-fallback paths (bounded one-turn slices) | Not formalized | 🔴 Gap — recoveries are ad-hoc (`agent-recovery`, manual) |
| 8 | Cross-runtime review demo (Claude impl + Codex review) | `harness-critic` + kanban pipeline gates + `dual-agent-coordination` | ✅ We already have this |

---

## BORROW (the meat)

### 1. 🟢 Explicit user gates — first-class state
**From LoopX:** "Concrete user gates instead of a vague 'waiting for owner.'"
**Our current flaw:** we leave "waiting on Jordan" buried inside todos with no stated
question, no owner, no deadline, no fallback on no-response.
**The mechanism to adopt** — every human-gated item carries:
- a **stated question** ("Jordan: approve X?")
- the **owner** (which human/agent)
- a **deadline** (e.g. "by Aug 5")
- a **fallback** on no-response (auto-nudge at deadline → escalate → default decision)

**Wire into:** `agent-handoff-enforcement`, `considerations.md`, `jordan-queue.md`.

### 2. 🟢 Quota-aware `should-run` — stop-condition for recurring work
**From LoopX:** "May the loop continue?" → quota decides whether a turn should deliver,
ask, wait, self-repair, or **stay quiet**.
**Our current flaw:** cron jobs fire on clock, not on whether a useful transition remains
— burns tokens after the work is done or blocked.
**The mechanism to adopt:** before each scheduled run, evaluate a cheap stop-condition
("is there a new input? / is the source changed? / did last run leave anything to do?").
If no useful transition remains → **stay quiet, spend no tokens.** This is the watchdog
/ `no_agent` pattern we already have — formalize it as a `should-run` gate on recurring
jobs that don't need LLM reasoning every tick.

**Wire into:** cron job design (`no_agent` scripts, `cron-truth-layer`, `signal-watcher`).

### 3. 🟢 Evidence lineage on handoffs
**From LoopX:** run history, validation, blockers, and accepted writeback preserved across
turns so the next agent doesn't start from scratch.
**Our current flaw:** `harness-critic` audits outputs, but handoffs don't carry a compact
"what changed + what's the next todo + what was validated" trail into the receiving agent's
context.
**The mechanism to adopt:** every handoff carries a **3-line evidence stub**:
`changed:` / `validated:` / `next-todo:`. Cheap, readable, keeps reviews from cold-starting.

**Wire into:** `agent-handoff-enforcement`, `dual-agent-coordination`, forge handoffs.

---

## SPIT OUT (the bones)

- ❌ **Don't adopt LoopX as a dependency** — our Hermes cron + queue + kanban already
  cover orchestration better (decomposition playbook, parent-link dependency graph,
  reclaim/reassign recovery).
- ❌ **Don't copy its 953-branch churn / heavy CI** — treat as reference, not dependency.
- ❌ **Skip its Lark/Feishu projection** — we don't use Feishu.
- ⚠️ **Bytedance-adjacent author** — fine to read (MIT), but don't build around a
  corporate-owned control plane for our a2a core.

---

## Verdict

**Watch + borrow.** Take the 3 primitives into our own a2a handoff contract. They're
small, philosophically aligned with our "human judgment gates everything" stance, and
cheap to wire into skills we already run.

## Action Items
- [ ] Add build-queue item: "a2a handoff contract — explicit user gates + should-run + evidence lineage" (see build-queue.md)
- [ ] Patch `agent-handoff-enforcement` skill with the explicit-gate format + 3-line evidence stub
- [ ] Review recurring cron jobs for `should-run` / `no_agent` stop-condition opportunities
