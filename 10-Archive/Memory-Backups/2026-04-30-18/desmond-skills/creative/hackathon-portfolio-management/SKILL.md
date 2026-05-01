---
name: hackathon-portfolio-management
description: "Manage a portfolio of concurrent hackathon projects: cross-reference concepts across hackathons, create focused sprint plans when scope is cut, maintain portfolio-level rosters and coordination documents."
tags:
  - hackathon
  - portfolio
  - sprint-planning
  - coordination
  - cross-reference
  - scope
related_skills:
  - hackathon-content-curation
  - hackathon-submission-package
  - hackathon-tech-stack-evaluation
  - hackathon-project-scaffold
  - multi-agent-team-workflow
triggers:
  - Managing multiple hackathon submissions simultaneously
  - Jordan asks to review all hackathon projects and figure out how a concept fits across them
  - Scope needs to be cut from many hackathons to a focused few
  - Need to create sprint plans with checkpoints across hackathons
  - Updating hackathon roster after strategic decisions
  - Cross-referencing how one技术concept maps to multiple hackathon tracks
---

# Hackathon Portfolio Management

Manage multiple concurrent hackathon projects as a coordinated portfolio. Cross-reference concepts across hackathons, create focused sprint plans when scope changes, and maintain portfolio-level status documents.

## When to Use

- Multiple hackathons are active simultaneously
- Jordan asks "look at all our hackathons and see what we can do"
- A new concept needs to be mapped across existing hackathon submissions
- Scope is cut from many hackathons to a focused few (sprint planning)
- Need to update portfolio-level roster after strategic decisions
- Coordinating deliverables across hackathons with different deadlines

##区别 from Related Skills

| Skill | Scope | This Skill |
|-------|-------|-----------|
| `hackathon-content-curation` | Individual hackathon doc enhancement | Portfolio-level cross-referencing |
| `hackathon-submission-package` | Generate materials for one submission | Coordinate materials across submissions |
| `hackathon-tech-stack-evaluation` | Evaluate one hackathon's tech fit | Compare tech fit across hackathons |
| `hackathon-project-scaffold` | Build one project from zero | Plan sprints across multiple projects |

## Workflow

### 1. Portfolio Audit

Read ALL hackathon docs to understand current state:

```bash
# Find all hackathon-related files
find "$VAULT/02-Labs/Hackathons" -name "*.md" -type f
find "$VAULT/03-Projects" -name "*hackathon*" -o -name "*Hackathon*" | head -20

# Read the roster
cat "$VAULT/03-Projects/HACKATHON-ROSTER-2026.md"

# Read each active hackathon's status
for f in "$VAULT/02-Labs/Hackathons/Active/"*.md; do
  echo "=== $(basename $f) ==="
  head -20 "$f"
done
```

Extract for each hackathon:
- Deadline and days remaining
- Current status (what's done, what's in progress)
- Submission focus (which AAE layer)
- Prize pool
- Chain/platform
- What's blocking

### 2. Cross-Reference Analysis

When a new concept needs to map across hackathons:

```markdown
## How [Concept] Maps to Each Hackathon

| Hackathon | Deadline | [Concept] Role | Integration Angle |
|-----------|----------|---------------|-------------------|
| Hackathon A | May 11 | Core submission | "This IS the submission" |
| Hackathon B | May 17 | Supporting layer | "This enhances the submission" |
| Hackathon C | Jun 11 | Future phase | "This is the capstone" |

### One-Liner Per Hackathon
Each hackathon tells one story from a different angle:
1. Hackathon A: "[Angle 1]"
2. Hackathon B: "[Angle 2]"
3. Hackathon C: "[Angle 3]"
```

**Key principle:** One concept, different angles. Each hackathon submission should feel like a complete story, not a fragment.

### 3. Scope Cut / Sprint Planning

When DMOB or Jordan says "scope is too wide, cut to X":

```markdown
# Sprint Plan — [Hackathon A] + [Hackathon B]

## Approved Scope
| Hackathon | Deadline | Submission | Lead |
|-----------|----------|------------|------|
| Hackathon A | May 11 | [focused submission] | [owner] |
| Hackathon B | May 17 | [focused submission] | [owner] |

## Deferred
| Hackathon | Deadline | Notes |
|-----------|----------|-------|
| Hackathon C | Jun 11 | Revisit after A+B |

## [Hackathon A] Sprint

### Current Status
- ✅ [done items]
- 🔄 [in progress]
- 📋 [planned]

### Sprint Tasks (Apr 29 – May 11)
#### [Agent] — [focus area]
- [ ] Task 1
- [ ] Task 2

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Checkpoints
| Date | Milestone |
|------|-----------|
| May 1 | [milestone] |
| May 5 | [milestone] |
| May 11 | **SUBMISSION** |
```

### 4. Update Portfolio Roster

After strategic decisions, update the master roster:

```markdown
# Hackathon Roster — [Date]

## Active Focus (Approved)
| Name | Deadline | Status | Submission |
|------|----------|--------|------------|
| [Hackathon A] | May 11 | 🔴 SPRINT | [what] |
| [Hackathon B] | May 17 | 🟡 SPRINT | [what] |

## Deferred (Post-[Date])
| Name | Deadline | Notes |
|------|----------|-------|
| [Hackathon C] | Jun 11 | Revisit after A+B |

## Skipped / Dropped
| Name | Reason |
|------|--------|
| [Hackathon D] | [reason] |
```

### 5. Handoff to Team

Create handoffs for agents who need to scope or build:

```markdown
# [Agent]: [Hackathon] — Scoping Request

## Context
[Brief on what was decided and why]

## What We Need From You
1. [Specific question 1]
2. [Specific question 2]

## Deliverable
[What format, where to save, who to report to]

## Timeline
[When needed]
```

Save to `09-Green Room/handoff-[agent]-[topic].md`.

### 6. Log to Mess Hall

Always log completion:

```markdown
# [Topic] — Complete

**Time:** [date/time]

## What Happened
[Summary of decisions and outputs]

## Files
- [doc 1]: [location]
- [doc 2]: [location]

## Next Steps
[What happens next]
```

Save to `11-Mess Hall/2026/[date]-[topic].md`.

## Output Locations

| Document Type | Location |
|--------------|----------|
| Portfolio roster | `03-Projects/HACKATHON-ROSTER-2026.md` |
| Sprint plans | `02-Labs/sprint-plan-[hackathons].md` |
| Cross-references | `02-Labs/brainstorm-[concept]-hackathon-integration.md` |
| Brainstorm docs | `00-HQ/brainstorm-[topic].md` |
| Team handoffs | `09-Green Room/handoff-[agent]-[topic].md` |
| Status logs | `11-Mess Hall/2026/[date]-[topic].md` |

## Pitfalls

- **Don't keep all hackathons active.** Scope creep kills submissions. Cut early, cut hard.
- **Each hackathon needs its own story.** Don't submit the same thing everywhere — angle it per track.
- **Checkpoints must be real.** If you miss a checkpoint, the submission is at risk. Flag immediately.
- **Roster must stay current.** Stale rosters cause confusion. Update after every strategic decision.
- **Handoffs need specific questions.** "Scope this" is vague. "Can our infra support X? What needs to change?" is actionable.
- **Don't submit fragments.** Each hackathon submission should feel complete, not like a piece of something bigger.

## Example Trigger Phrases

- "Look at all our hackathons and see what we can do"
- "Scope is too wide, let's cut down"
- "Start work on [hackathon]"
- "How does [concept] fit into our hackathon submissions?"
- "Update the roster"
- "What's the status on all our hackathons?"

## Related Skills

- `hackathon-content-curation` — After portfolio planning, curate individual hackathon docs
- `hackathon-submission-package` — Generate submission materials for a specific hackathon
- `hackathon-tech-stack-evaluation` — Evaluate tech fit before adding a hackathon to portfolio
- `multi-agent-team-workflow` — Team coordination protocols (brainstorm + handoff patterns)
- `writing-plans` — Detailed implementation plans for individual hackathon builds
