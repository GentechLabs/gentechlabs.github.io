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
  - Jordan asks to review all hackathon projects (e.g., "look at all our hackathons and see what we can do")
  - Scope needs to be cut (e.g., "no longer doing X hackathon", "scope is too wide, cut to Y")
  - Need to audit active projects and report status (e.g., "what’s the progress on our current projects?")
  - Updating submission materials after scope changes (e.g., "sync writeups, READMEs, demo storyboards")
  - Creating sprint plans with checkpoints across hackathons
  - Updating hackathon roster after strategic decisions
  - Cross-referencing how a concept maps to multiple hackathon tracks
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

# Check vault vs repo sync status (vault may be more complete)
for dir in "$VAULT/02-Labs/Hackathons/Active/"*/; do
  echo "=== $(basename $dir) ==="
  if [ -d "$dir/programs" ]; then
    echo "VAULT has programs code"
    find "$dir/programs" -name "*.rs" -o -name "*.sol" | wc -l
  fi
  if [ -d "$dir/agent-escrow-solana" ]; then
    echo "VAULT has Anchor project"
    cat "$dir/agent-escrow-solana/Anchor.toml" 2>/dev/null | grep -c "programs"
  fi
done

# Check cron job routing (are hackathon-related jobs delivering to the right place?)
cd /root/.hermes && for profile in profiles/*/cron/jobs.json; do
  python3 -c "
import json
data=json.load(open('$profile'))
for j in data.get('jobs',[]):
    name = j.get('name', '')
    if any(kw in name.lower() for kw in ['hackathon', 'bounty', 'contest', 'scout']):
        print(f'  {profile}: {name} → deliver={j.get(\"deliver\",\"?\")} | last={j.get(\"last_status\",\"never\")}')
" 2>/dev/null
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

### 7. Sync Submission Materials

After updating the roster and sprint plans, **sync submission materials** for active hackathons:

```bash
# List all active hackathon folders
ls -1 "$VAULT/02-Labs/Hackathons/Active/"

# Check for missing submission docs
for dir in "$VAULT/02-Labs/Hackathons/Active/"*; do
  echo "=== $(basename "$dir") ==="
  ls -1 "$dir" | grep -E "SUBMISSION-WRITEUP|README|DEMO-STORYBOARD|SOCIAL-THREAD"
  echo
```

**Actions:**
- If submission docs are missing, flag for `hackathon-submission-package` generation.
- If docs exist but are stale (e.g., old sponsors, wrong scope), update them.
- Ensure demo storyboards match the current sprint focus.
- Verify READMEs reflect the latest architecture and sponsor integrations.

**Save updates to:**
- `02-Labs/Hackathons/Active/[hackathon]/SUBMISSION-WRITEUP.md`
- `02-Labs/Hackathons/Active/[hackathon]/README.md`
- `02-Labs/Hackathons/Active/[hackathon]/DEMO-STORYBOARD.md`
- `02-Labs/Hackathons/Active/[hackathon]/SOCIAL-THREAD.md`

**Handoff to Creative:**
```markdown
# Creative: [Hackathon] — Submission Sync

**Context:** Scope changes approved. Submission materials need refresh.

**Files to Update:**
- [ ] SUBMISSION-WRITEUP.md
- [ ] README.md
- [ ] DEMO-STORYBOARD.md
- [ ] SOCIAL-THREAD.md

**Deadline:** [date]
```

Save to `09-Green Room/handoff-creative-[hackathon]-sync.md`.

## Pitfalls

- **Don't keep all hackathons active.** Scope creep kills submissions. Cut early, cut hard.
- **One hackathon at a time, go deep.** Jordan (May 2026): "We do one at a time." Don't spread across too many hackathons trying to do the same thing simultaneously. Focus on one, submit it well, then move to the next. Landshare was an example of what happens when you spread too thin.
- **Each hackathon needs its own story.** Don't submit the same thing everywhere — angle it per track.
- **Checkpoints must be real.** If you miss a checkpoint, the submission is at risk. Flag immediately.
- **Roster must stay current.** Stale rosters cause confusion. Update after every strategic decision.
- **Handoffs need specific questions.** "Scope this" is vague. "Can our infra support X? What needs to change?" is actionable.
- **Don't submit fragments.** Each hackathon submission should feel complete, not like a piece of something bigger.
- **Vault-repo sync drift.** The vault may have more complete code than the workspace/repo. During portfolio audits, check both locations. If vault > repo, flag as P0 blocker before submission. (Discovered during Solana Frontier audit: vault had 4 programs/2,075 lines, workspace had 1.)
- **Hackathon cron jobs need routing audit.** When auditing hackathon portfolio, also check cron jobs across all profiles. Duplicate hackathon scout/bounty jobs across profiles cause noise and wasted compute. One owner per job type.

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
