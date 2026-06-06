# Superpowers × Gentech Workflow

**Date:** 2026-05-16
**Status:** 🟡 Adaptation Phase
**Origin:** obra/superpowers (193K stars) adapted for Gentech Hermes Agent

---

## The Problem This Solves

Our existing skills are great individually, but they don't trigger in sequence. An agent can skip planning, skip TDD, or skip review if not prompted. Superpowers makes the workflow **mandatory** — the agent follows the pipeline automatically.

## The 7-Phase Workflow (Superpowers → Gentech Mapping)

### Phase 1: Brainstorming → `ideation` + `hackathon` (Research)
**Superpowers:** Agent asks questions, explores alternatives, saves design doc
**We already have:** `ideation` (creative constraints), `hackathon` Phase 1 (research + briefing), `link-research-summary`
**Adaptation:** When Jordan says "let's build X" or shares an idea, the agent MUST:
1. Ask 2-3 clarifying questions before writing code
2. Explore 2 alternatives and present trade-offs
3. Save the agreed design to `09-Green Room/designs/<project-name>.md`
**Gap:** No automated design doc generation. The design doc gets saved in conversation but not to a persistent file.

### Phase 2: Git Worktrees → `github-pr-workflow`
**Superpowers:** Creates isolated workspace on new branch, verifies clean test baseline
**We already have:** `github-pr-workflow` (branch, commit, PR, merge)
**Adaptation:** Before any build starts:
1. Create a branch: `git checkout -b feature/<name>`
2. Run existing tests to verify baseline is clean
3. Worktree mode for parallel features (advanced)
**Gap:** Worktrees not automated. We create branches manually.

### Phase 3: Writing Plans → `writing-plans` + `plan`
**Superpowers:** Bite-sized tasks (2-5 min), exact file paths, verification steps
**We already have:** `writing-plans` (bite-sized tasks, paths, code), `plan` (write to `.hermes/plans/`, no exec)
**Adaptation:** After design approval, agent MUST:
1. Break work into tasks with exact file paths
2. Include verification steps for each task
3. Save plan to `.hermes/plans/<project>.md`
**Status:** ✅ We have this. Just needs enforcement.

### Phase 4: Subagent-Driven Dev → `subagent-driven-development` + `kanban-orchestrator`
**Superpowers:** Fresh subagent per task, two-stage review (spec compliance + code quality)
**We already have:** `subagent-driven-development` (execute plans via delegate_task, 2-stage review), `kanban-orchestrator` (task decomposition + routing)
**Adaptation:** Execute plan with `delegate_task`:
1. Each task → fresh subagent with scoped context
2. Stage 1: Spec compliance review (does it match the plan?)
3. Stage 2: Code quality review (security, style, edge cases)
**Status:** ✅ We have this. It's already our best skill.

### Phase 5: TDD → `test-driven-development` + `solidity-security`
**Superpowers:** RED-GREEN-REFACTOR, write failing tests first
**We already have:** `test-driven-development` (RED-GREEN-REFACTOR), `solidity-security` (security patterns), `foundry-poc` (Foundry PoC tests)
**Adaptation:** For each task:
1. Write failing test FIRST (Solidity: `forge test`, Python: `pytest`)
2. Write minimal code to pass
3. Refactor with security review
**Status:** ✅ We have this. Enforcement is the gap.

### Phase 6: Code Review → `requesting-code-review` + `github-code-review`
**Superpowers:** Between tasks, pre-review checklist, blocks on critical issues
**We already have:** `requesting-code-review` (security scan, quality gates, auto-fix), `github-code-review` (PR diffs, inline comments)
**Adaptation:** After each subagent completes a task:
1. Run security scan (no hardcoded secrets, no SQLi, etc.)
2. Review against plan (did it solve the right problem?)
3. Block progress on critical issues
**Status:** ✅ We have this.

### Phase 7: Finishing → `github-pr-workflow` + `hackathon` (Submission)
**Superpowers:** Verify tests, present merge options, cleanup worktree
**We already have:** `github-pr-workflow` (PR lifecycle), `hackathon` Phase 4 (submission: demo video, writeup, deploy)
**Adaptation:** When all tasks complete:
1. Run full test suite
2. Present options: merge, PR, keep, discard
3. For hackathons: generate demo script, update addresses, submit
**Status:** ✅ We have this.

---

## What We're Missing (Gaps to Fill)

### 1. **Automatic Skill Triggering**
Superpowers triggers skills automatically in sequence. Our skills need to be loaded explicitly.
**Fix:** Create a `gentech-build-workflow` skill that chains these together.

### 2. **Design Doc Persistence**
Brainstorming phase doesn't save to a structured file.
**Fix:** Add design doc template to `09-Green Room/designs/` with frontmatter.

### 3. **Enforcement Layer**
No "circuit breaker" that stops an agent from skipping steps.
**Fix:** Add a pre-flight check that verifies each phase was completed before proceeding.

### 4. **Anti-Temptation Rules**
Jordan's directive: "don't spiral." Superpowers enforces YAGNI (You Aren't Gonna Need It).
**Fix:** Add explicit anti-scope-creep rules to the build workflow.

---

## Proposed Workflow (Gentech Adapted)

```
Jordan: "Let's build X for [hackathon/product]"
    ↓
Phase 1: BRAINSTORM (mandatory)
├── Load: ideation, hackathon (if applicable)
├── Ask 2-3 clarifying questions
├── Explore 2 alternatives with trade-offs
└── Save design → 09-Green Room/designs/<project>.md
    ↓
Phase 2: PLAN (mandatory)
├── Load: writing-plans
├── Break into bite-sized tasks (2-5 min each)
├── Each task: file paths, code outline, verification step
└── Save plan → .hermes/plans/<project>.md
    ↓
Phase 3: BUILD (subagent-driven)
├── Load: subagent-driven-development
├── For each task:
│   ├── Fresh subagent with scoped context
│   ├── Write failing test FIRST (TDD enforced)
│   ├── Write minimal code to pass
│   ├── Stage 1 review: spec compliance
│   └── Stage 2 review: code quality + security
└── Report progress after each task
    ↓
Phase 4: REVIEW (mandatory between tasks)
├── Load: requesting-code-review
├── Security scan (no secrets, no injections)
├── Plan compliance check
└── Block on critical issues
    ↓
Phase 5: FINISH
├── Load: github-pr-workflow, hackathon (if applicable)
├── Run full test suite
├── Present merge options
├── For hackathons: demo script, addresses, submission
└── Cleanup branch/worktree
```

---

## Integration with Existing Infrastructure

### Morning Digest Integration
- Design docs and plans are saved to vault → digest can reference them
- Subagent results are reported → digest captures build progress
- Code reviews are logged → digest flags blockers

### MultiCA / Paperclip Integration (Future)
- Each phase could be a separate task in MultiCA's task board
- Paperclip could orchestrate the 7 phases as a company workflow
- Gentech = orchestrator, subagents = department heads

### Telegram Layer
- Phase completions → Telegram notifications to HQ
- Blockers → immediate flag (not in status reports)
- Demo video scripts → sent to Jordan for recording

---

## Implementation Priority

1. **Create `gentech-build-workflow` skill** — chains existing skills into mandatory sequence
2. **Add design doc template** — structured format for Phase 1 output
3. **Add enforcement pre-flight** — verify each phase completed before proceeding
4. **Test on next hackathon build** — Agora Agents (May 25) or Mantle Turing Test (Jun 15)
5. **Refine based on results** — adjust timing, add anti-patterns to pitfalls section

---

## Anti-Patterns (What to Avoid)

1. **Skipping brainstorming** → "just start coding" leads to scope creep
2. **Writing code before tests** → harder to verify correctness
3. **No plan saved to file** → subagents lose context, repeat work
4. **Skipping review gates** → security issues slip through
5. **Not blocking on critical issues** → technical debt accumulates
6. **Building beyond plan** → YAGNI violation, wasted time

---

*This is an adaptation of obra/superpowers (MIT License) for Gentech's Hermes Agent ecosystem.*