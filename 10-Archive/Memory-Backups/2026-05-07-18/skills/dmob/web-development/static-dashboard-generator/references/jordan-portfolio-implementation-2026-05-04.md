# Jordan Portfolio — Projects + Roadmap Implementation
**Date:** 2026-05-04  **Skill:** static-dashboard-generator

## Context
Added a `Projects + Roadmap` section to `03-Projects/jordan-portfolio/index.html` using a data-driven approach. Portfolio is static HTML, needs to work offline without backend.

## Decisions

### 1. Embedded JSON vs Fetch
**Chosen:** Embedded JSON inside `<script id="project-data" type="application/json">`
**Why:** Portfolio viewed locally (`file://`), fetch triggers CORS errors. Embedded keeps it single-file and portable.

### 2. Categorization Logic
- **NOW (★):** `status === 'live'` OR (`status === 'building'` AND `deadline` exists)
- **WIP (◐):** (`status === 'building'` AND no deadline) OR `status === 'research'`
- **TBA (○):** Empty placeholder for future roadmap items

Matches hackathon deadlines + WIP mental model Jordan requested.

### 3. Honest Narrative Copy
```
"Real-time snapshot of what's shipping, what's in progress, and what's next.
Building in public — some things ship, some things stall, some things get scrapped.
Everyday is a new struggle, and that's okay."
```
Reflects Jordan's "no promises, everyday struggle" tone.

### 4. Generator Script
Created `generate.py` that:
- Reads `projects.json`
- Replaces the JSON block inside the HTML `<script>` tag
- Simple string replacement, no templating engine needed
- Command: `python3 generate.py`

Keeps HTML + JSON in sync when discovery/update scripts modify `projects.json`.

### 5. Git Handling
The `jordan-portfolio/` folder was initially its own git repo (had `.git`). Discovered via:
```
git status showing: "A  path"  (submodule flag)
```
Fix: removed nested `.git/`, re-added files to parent repo. Now tracked as normal files (mode 100644).

## Schema Used (projects.json)
```json
{
  "projects": [
    {
      "id": "agent-escrow-solana",
      "title": "AgentEscrow",
      "description": "AgentEscrow — GenTech project",
      "tech": ["Solana", "Anchor", "Rust"],
      "status": "building",       // live | building | research | audit
      "deadline": "2026-05-11",   // null if none
      "timeline": "May 2026",
      "highlight": false,
      "vault_path": "03-Projects/agent-escrow-solana"
    }
  ]
}
```

## Files Modified/Created
- `03-Projects/jordan-portfolio/index.html` — added roadmap section (7 projects auto-rendered)
- `03-Projects/jordan-portfolio/projects.json` — data source (copied from `~/.hermes/.../projects.json`)
- `03-Projects/jordan-portfolio/generate.py` — generator script

## CSS Highlights
- 3-column grid on desktop (`grid-template-columns: repeat(3, 1fr)`), stacks on mobile
- Status badges: `status-live` (green), `status-building` (yellow), `status-research` (purple)
- Tech tags in green (`#22c55e`) matching portfolio theme

## Verification Checklist
- [x] All 7 projects render in correct categories (5 NOW, 2 WIP, 0 TBA)
- [x] Embedded JSON valid and parseable
- [x] No console errors in browser
- [x] Responsive at 3 widths (desktop/tablet/mobile)
- [x] Generator script updates HTML without breaking layout
