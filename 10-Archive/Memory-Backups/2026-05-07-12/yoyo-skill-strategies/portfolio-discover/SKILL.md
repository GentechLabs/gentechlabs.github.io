---
name: portfolio-discover
description: Discover and catalog portfolio projects from vault structure with reality-based status labels
triggers:
  - "portfolio projects"
  - "projects list"
  - "roadmap section"
  - "discover projects"
  - "generate projects.json"
  - "inventory projects"
umbrella: strategies
related:
  - "Read 03-Projects/ directory tree → parse project READMEs/Implementation-Plan.md → extract status (live/building/planning/research) → map to concise label with deadline/WIP/TBA"
input_requirements:
  - Vault path: /root/vaults/gentech/03-Projects/
  - Target output: ~/portfolio/data/projects.json or vault-equivalent
output_format: JSON array of project objects with name, status, desc, tech, deadline fields
---

## Skill Overview

**Purpose:** Automate portfolio project inventory from the vault with concise, reality-based status labels.

**User preference:** "Use hackathon deadlines, or WIP/TBA to make it simple. Can't promise alot when everyday is a new struggle."
→ Labels should reflect actual state, not aspirational targets. WIP and TBA are valid first-class statuses.

**Typical flow:**
1. Scan 03-Projects/ for project directories
2. For each project, read marker files (README.md, Implementation-Plan.md, HACKATHON-ROSTER.md references)
3. Extract: project name, current phase, tech stack, deadlines (hackathon/submission), WIP flags
4. Map to concise status string: Building — <stack> — Hackathon: <date> or Live — <stack> — WIP or Research — <topic> — TBA
5. Emit projects.json array

---

## Step-by-Step Procedure

### Step 1 — Identify project directories
```bash
cd /root/vaults/gentech/03-Projects/
# List subdirectories, exclude dot-dirs and known meta-folders
```
**Output:** List of candidate project names.

**Pitfall:** Some folders are meta (hermes-kanban, HACKATHON-ROSTER-2026.md, defi-milestones.md). Filter: if no README.md or Implementation-Plan.md present, skip or tag as Research — TBA.

### Step 2 — Extract status per project
For each project directory, read in order:
1. Implementation-Plan.md → look for "Phase:", "Status:", "Owner:", deadline mentions
2. README.md → first 30 lines, look for "Sprint", "Competition", "Hackathon", "Deadline"
3. Check git log for recent activity (last commit date, message keywords like "feat:", "fix:")
4. Scan parent HACKATHON-ROSTER-2026.md for project name matches (if present)

**Status label rules:**
| Detected pattern | Status label |
|------------------|-------------|
| "Hackathon" + date | Building — <stack from tags> — Hackathon: <date> |
| "Live" / "Production" | Live — <stack> — WIP |
| Phase with week range | Building — <stack> — Target: <date> |
| Research/SDK comparison | Research — <topic> — TBA |
| No clear signal | Planning — TBA |

**Tech stack extraction:**
- Look for: Solana, Anchor, Rust, Python, Avalanche, Foundry, Hardhat, Next.js, Pipecat, Maps API, x402
- Keep concise: max 2–3 tech keywords

### Step 3 — Generate projects.json
Schema:
```json
[
  {
    "name": "AgentEscrow",
    "status": "Building — Solana, Anchor, Rust — Hackathon: May 11",
    "desc": "Trustless AI agent marketplace on Solana for Solana Frontier Hackathon",
    "tech": ["Solana", "Anchor", "Rust"],
    "deadline": "2026-05-11"
  }
]
```

Write to ~/portfolio/data/projects.json (create directories if needed).

---

## User Preferences Embedded

1. **Simplicity over precision** — Use WIP/TBA liberally; don't force exact dates if unknown
2. **Reality-based labels** — Mirror actual vault state; if a project is "Building" with a hackathon deadline, show that deadline explicitly
3. **No aspirational promises** — Don't invent milestones; stick to what's documented in vault files
4. **Ordering** — Keep order by: (a) active hackathon deadlines ascending, (b) recent commit activity, (c) alphabetical fallback

---

## Integration Notes

- Run after any 03-Projects/ commit (optional cron: daily 6AM)
- Manual override: create 03-Projects/<project>/.portfolio-override.json with custom fields; scanner merges over auto-detected
- Portfolio site generator reads this file directly; no transformation needed