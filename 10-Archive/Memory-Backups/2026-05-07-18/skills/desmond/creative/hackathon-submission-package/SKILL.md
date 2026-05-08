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

- **Check vault AND repo before writing materials.** The vault (`02-Labs/Hackathons/Active/[hackathon]/`) may have more complete code than the workspace/repo. During the Solana Frontier session (May 5), the vault had all 4 programs (2,075 lines Rust, 53/53 tests) while the workspace only had 1 program. Always check both locations and note the sync status in the build section. If vault > repo, flag "code sync needed" as a P0 blocker.
- **Read sprint handoff docs as input.** Before writing submission materials, check `09-Green Room/active-handoffs/` for the latest sprint handoff. It contains the actual build status (what's done, what's in progress, what's blocked) — more current than the architecture doc.
- **Build status is a living document.** The SUBMISSION-WRITEUP.md build status section should be updated as work progresses, not left as a static snapshot from initial generation. Update it whenever you check in on the project.
- **Don't fabricate sponsor details.** Only include integrations actually in the architecture doc.
- **Demo timing must add up.** If you say 5 minutes, every act must sum to 5:00.
- **README code examples must be plausible.** Use real SDK patterns, not pseudocode.
- **Social tweets must be ≤ 280 chars.** Count carefully — emoji count as 2 chars on X.
- **Submission writeup must match README.** Don't contradict yourself across documents.
- **Don't skip the competitive table.** Judges specifically look for market awareness.
- **Demo storyboard needs pre-recording checklist.** Missing setup = wasted recording time.
- **CPU-friendly/local-first constraints change deliverables.** If user specifies "no cloud GPU" or "CPU-only", include:
  - Performance tuning section in README (model quantization, thread counts, RAM footprint)
  - Hardware-specific benchmark table (user's actual machine specs)
  - Explicit "no Docker required" or "Docker optional" stance
  - ALSA/PulseAudio audio notes if voice agents
  - One-command installer script (`run_local.sh`) as deliverable
- **Interactive diagrams > static images.** For complex orchestration layers (Pipecat, multi-service pipelines), generate interactive HTML/SVG diagrams with hover states to show data flow — judges can explore.
- **Three-project showcase model.** When the stack supports multiple distinct use-cases, build **three demos** (compliance/trading/education pattern) to prove versatility — not just one monolithic demo.
- **Vault context/resumability as feature.** If system saves conversation state, include:
  - Sample session JSON in `vault_context/`
  - One-liner `--resume <session-id>` flag in README
  - Demo storyboard segment showing mid-conversation resume
- **Green Room for technical accuracy review.** For submissions with complex pipeline claims (streaming latency, state management, local inference):
  - Create coordination note in `09-Green Room/active-handoffs/` explicitly listing **claims to verify** (e.g., "STT latency 400ms", "LLM 12 tok/s on Ryzen 7")
  - Tag DMOB with checklist items
  - Wait for sign-off before publishing social posts

## Extended Deliverables (Local-First / Voice AI Projects)

When the architecture is **voice-centric** or **local-inference focused**, extend the standard 4 deliverables to 7:

| File | Purpose | Notes |
|------|---------|-------|
| `README-<STACK>-GUIDE.md` | Local run instructions | One-command installer, CPU tuning, ALSA/PulseAudio notes |
| `ARCHITECTURE.html` | Interactive SVG diagram | Hover-highlight components, not just a PNG |
| `TECHNICAL-WALKTHROUGH.md` | Code-level deep-dive | Pipeline details, state persistence, performance benchmarks |
| `DEMO-VIDEO-SCRIPT.md` | 90s narrative script | Timed segments, voiceover text, B-roll notes |
| `PITCH-DECK-SLIDES.md` | 10-slide markdown deck | For live pitches/judges Q&A |
| `SOCIAL-THREAD-SERIES.md` | Multi-platform posts | X/LinkedIn/Reddit/Telegram variants |
| `active-handoffs/` | DMOB review coordination | Checklist of technical claims to verify |

**Benchmark table template (include in README/TECHNICAL-WALKTHROUGH):**

| Component | Model | Quant | RAM | CPU Cores | Latency |
|-----------|-------|-------|-----|-----------|---------|
| STT | Whisper.cpp medium | q5_k_m | 800MB | 2 | 400ms |
| LLM | Llama3 8B Instruct | q4_K_M | 5GB | 4 | 12 tok/s |
| TTS | Piper en_US-medium | — | 300MB | 1 | 200ms |

**Hardware specificity:** Always anchor to the **actual machine** used (e.g., "Ryzen 7 5700X, 32GB RAM, no GPU"). Judges ask "can this scale?" — answer with concrete specs.

## Triggers (Extended)

- Jordan says "CPU-friendly", "local-first", "no cloud GPU", "Wednesday video agent" → activate local-first deliverable extensions
- Project uses Pipecat, Voice AI, or streaming audio → include interactive HTML diagram + three-project showcase
- Vault persistence is a core feature → include resumable session demo + sample JSON
- Complex pipeline with multiple services → create technical walkthrough + DMOB review handoff

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

## Reference Materials

See `references/pipecat-showcase-structure.md` for the full directory layout, three-project showcase pattern, interactive HTML diagram template, and local-first/voice-specific pitfalls discovered during the Pipecat Voice Showcase hackathon (Colosseum Frontier, May 2026).

See `references/solana-frontier-2026-state.md` for current build status, program IDs, sponsor integrations, and P0 blockers for the Solana Frontier AgentEscrow submission (deadline May 11, 2026).
