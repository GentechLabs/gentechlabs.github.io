---
name: hackathon-submission-package
description: "Generate a complete hackathon submission package from a technical architecture doc: submission-ready README, demo storyboard, Colosseum/Devpost writeup, and social media thread."
tags:
  - hackathon
  - content
  - creative
  - submission
  - readme
  - demo
  - social-media
triggers:
  - Jordan approves a hackathon direction and says "start work" or "go ahead"
  - Need to generate submission materials from a completed architecture doc
  - Writing a README for a hackathon project
  - Creating a demo storyboard for a hackathon video
  - Drafting a Colosseum or Devpost submission writeup
  - Building a social media announcement thread for a hackathon project
---

# Hackathon Submission Package

Generate a complete submission package from a technical architecture document. Produces 4 deliverables: README, demo storyboard, submission writeup, and social thread.

## When to Use

- Jordan approves a hackathon direction and says "go ahead" / "start work"
- A technical architecture doc exists and needs submission materials
- Need to create all content artifacts for a hackathon deadline
- Refreshing submission materials after architecture changes

## Prerequisites

- Technical architecture document (must exist in vault)
- Sponsor integration details (which sponsors, what they do)
- Demo flow (what the 5-minute demo shows)
- Repository URL and devnet program ID (if deployed)

## Workflow

### 1. Read the Architecture

```bash
# Find the architecture doc
find "$VAULT/02-Labs/Hackathons" -name "*ARCHITECTURE*" -o -name "*architecture*"

# Read it fully — extract: programs, sponsors, data models, demo flow
cat "$VAULT/02-Labs/Hackathons/Active/[hackathon]/TECHNICAL-ARCHITECTURE.md"
```

Extract these key pieces:
- **Programs/systems** (what gets built)
- **Sponsor integrations** (which sponsors, what role, code patterns)
- **Job/task lifecycle** (state machine, flows)
- **Demo flow** (scene-by-scene what happens)
- **Competitive positioning** (what makes this different)

### 2. Generate README.md

**Location:** Project repo root (e.g., `/root/gentech/agent-escrow/README-SOLANA.md`)

Structure:
```markdown
# [Project Name]

**[Tagline — 1 sentence]**

[1-2 sentence problem/solution]

[Badges: tests, framework, sponsors, license]

---

## The Problem
[2-3 paragraphs. What's broken. Why it matters.]

## The Solution
[Table of programs/components with one-liner descriptions]

## Architecture
[ASCII diagram showing layers]

## Sponsor Integrations
[For each sponsor: role, code example, judge signal]

## [Core Feature: Job Lifecycle / Workflow / etc.]
[State machine diagram]

## Demo Flow
[Numbered steps, timed to 5 minutes]

## Getting Started
[Prerequisites, install, test, deploy]

## Project Structure
[Directory tree]

## Why [Project] Wins
[Judge scorecard table + competitive edge]

## Security
[Risk/mitigation table]

## License
```

**Rules:**
- Include code examples for each sponsor integration
- Use the architecture doc's diagrams (don't recreate)
- Include getting started commands that actually work
- Competitive positioning table is mandatory
- Judge scorecard showing how the project hits each criterion

### 3. Generate Demo Storyboard

**Location:** `02-Labs/Hackathons/Active/[hackathon]/DEMO-STORYBOARD.md`

Structure:
```markdown
# [Project] — Demo Storyboard

**Video Length:** 5 minutes
**Format:** Screen recording with voiceover
**Tone:** [Confident/technical/fast-paced]

---

## Pre-Recording Checklist
- [ ] Programs deployed to devnet
- [ ] Demo app running
- [ ] Wallets funded
- [ ] Screen recording ready

---

## Act 1: The Hook (0:00 — 0:30)
### Visual
[What's on screen]
### Voiceover
> "What the narrator says"

## Act 2: [Main Feature] (0:30 — 1:30)
### Scene 1: [Name] (30s)
**Steps (on screen):**
1. [Exact click/action]
2. [What happens]
**Voiceover:**
> "[Script]"

[Continue for each scene...]
```

**Rules:**
- Time every act (total must equal video length)
- Include exact UI actions (clicks, forms, buttons)
- Voiceover as blockquotes
- Visual descriptions for what's on screen
- Pre-recording checklist is mandatory
- Include production notes (recording tips, audio, B-roll)

### 4. Generate Submission Writeup

**Location:** `02-Labs/Hackathons/Active/[hackathon]/SUBMISSION-WRITEUP.md`

Structure:
```markdown
# [Project] — [Hackathon Name] Submission

## Project Name
[Name]

## Tagline
[1 sentence]

## One-Liner
[2 sentences: problem + solution]

---

## The Problem
[2-3 paragraphs, compelling narrative]

## The Solution
[Component-by-component breakdown]

## Sponsor Integrations
[Table: Sponsor | Integration | Depth]

## Technical Architecture
[Program summary, key decisions]

## What Makes This Different
[Competitive advantages, full-stack argument]

## Demo
[What the demo shows]

## Build Status
[Table: Component | Status]

## Links
[GitHub, devnet, docs]

## Team
[Who built it]
```

**Rules:**
- Problem section must be compelling (not just technical)
- Sponsor table with depth rating (Low/Medium/High)
- Build status shows honest progress
- Links must be real (no placeholder URLs)

### 5. Generate Social Thread

**Location:** `02-Labs/Hackathons/Active/[hackathon]/SOCIAL-THREAD.md`

Structure:
```markdown
# [Project] — Social Media Thread

## Thread (7 tweets)

### Tweet 1 (Hook)
[Provocative statement + 🧵]

### Tweet 2 (Problem)
[What's broken, 1-2 sentences]

### Tweet 3 (Solution)
[Introduce project + bullet list of features]

### Tweet 4 (Sponsors)
[Each sponsor with emoji + role]

### Tweet 5 (Technical Edge)
[What makes it technically interesting]

### Tweet 6 (Competitive)
[How it compares to alternatives]

### Tweet 7 (CTA)
[Hackathon mention + GitHub link]

---

## Posting Notes
- **Timing:** When to post
- **Media:** What to attach
- **Tags:** Who to mention
```

**Rules:**
- Each tweet ≤ 280 chars (count carefully)
- Tweet 1 must hook (no one reads tweet 2 if tweet 1 fails)
- Tweet 7 must include GitHub URL
- Thread should be self-contained (each tweet makes sense alone)
- Posting notes with timing and media suggestions

### 6. Create Green Room Handoff

**Location:** `09-Green Room/[date]-[project]-creative-handoff.md`

Structure:
```markdown
# [Project] — Creative Handoff

**Date:** [date]
**From:** Desmond (Creative)
**To:** [Who picks up next]

---

## ✅ Completed
[Numbered list of deliverables with file locations]

## 📋 Next Steps
[What the next agent/person needs to do]

## 🎯 Timeline
[Milestone table]
```

## Pitfalls

- **Don't fabricate sponsor details.** Only include integrations actually in the architecture doc.
- **Demo timing must add up.** If you say 5 minutes, every act must sum to 5:00.
- **README code examples must be plausible.** Use real SDK patterns, not pseudocode.
- **Social tweets must be ≤ 280 chars.** Count carefully — emoji count as 2 chars on X.
- **Submission writeup must match README.** Don't contradict yourself across documents.
- **Don't skip the competitive table.** Judges specifically look for market awareness.
- **Demo storyboard needs pre-recording checklist.** Missing setup = wasted recording time.

## Example Trigger Phrases

- "Go ahead, this angle is good" (after sharing architecture)
- "Start work on the submission"
- "Write the README"
- "Create the demo script"
- "Draft the Colosseum writeup"

## Related Skills

- `hackathon-content-curation` — Maintains/cures docs over time (this skill generates from scratch)
- `hackathon-project-scaffold` — Builds the code (this skill creates the content)
- `github-repo-content` — Generates social content from existing repos (this skill generates from architecture)
- `hackathon-tech-stack-evaluation` — Pre-build evaluation (this skill is post-build content)
