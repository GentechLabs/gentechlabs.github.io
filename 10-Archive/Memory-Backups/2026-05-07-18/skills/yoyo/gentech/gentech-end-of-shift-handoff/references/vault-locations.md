# Vault Structure Map — Key Locations for Handoff Reporting

## Root
`/root/vaults/gentech/`

## Daily Sync & Logs
- `08-Daily/` — daily logs named `YYYY-MM-DD.md`
  - Current file: `08-Daily/2026-05-03.md`
  - Contains: YAML frontmatter, team sections, TL;DR, open items, week summary
- `08-Daily/YYYY-MM-DD.md` — primary source for today's activity

## Coordination & Messaging
- `11-Mess Hall/` — coordination hub
  - `handoff-board.md` — inter-agent handoff tracking table
  - `agent-coordination-board.md` — agent session check-in & org structure
  - `task-board.md` — sprint priorities by team
  - `daily/` — daily operational notes
  - `2026/W19/` — current week folder (May 4–10)
    - `YYYY-MM-DD-deadline-board.md` — hackathon deadline countdown
    - `YYYY-MM-DD-mid-shift-executive-summary.md` — urgent items
    - `YYYY-MM-DD-mid-shift-coordination-report.md` — active project review

## Strategic Planning
- `09-Green Room/` — active discussions, specs, handoffs
  - `master-todo.md` — canonical master todo list (updated by Desmond)
  - `active-handoffs/` — pending handoffs requiring ack
  - `handoffs/` — completed/archived handoffs
  - `skills-captures/` — documented protocols (e.g., d5-monitoring-script-discrepancy-resolution.md)
  - Technical discussions: `understand-anything-technical.md`, defi-master-cron-bug-report-2026-04-27.md

## Leadership & Approvals
- `00-HQ/Approvals/` — items requiring Jordan approval
  - Files use frontmatter: `status: pending|approved|rejected`
  - Naming: `YYYY-MM-DD-topic-short.md`
  - Examples:
    - `2026-05-02-defi-milestone-tracker-consolidation.md`
    - `2026-05-03-understand-anything-dmob.md`
    - `2026-05-03-understand-anything-yoyo.md`
    - `2026-05-03-understand-anything-desmond.md`

## Operations & Incidents
- `00-HQ/Operations/` — operational runbooks and incident logs
  - `Infrastructure-Issues.md` — active incidents (OAuth, API downtime, etc.)
  - `Incident:` sections with timeline, impact, resolution steps

## Departmental Work
- `02-Labs/` — DMOB code, contracts, Foundry tests, hackathon submissions
- `03-Strategies/` — YoYo research, monitors, configs, spec documents
- `01-Agency/` — Gentech org-level docs, LLC, goals, brain backup
- `04-Entertainment/` — Desmond content, X threads, Medium posts

## Agent Configuration
- Hermes profiles: `~/.hermes/profiles/{gentech,dmob,yoyo,desmond}/`
  - `scripts/` — agent-specific script state
  - `cron/jobs.json` — scheduled jobs per agent
- Central scripts (shared): `~/.hermes/scripts/`
  - State fragmentation risk: `.lfj-*.json` files may diverge across profiles

## Notes
- Week numbering: `11-Mess Hall/2026/W19/` (W19 = May 4–10, 2026)
- Daily log naming: `08-Daily/YYYY-MM-DD.md`
- Handoffs follow naming: `HYYYY-MM-DD-XX.md` in `active-handoffs/` and `handoffs/`
- Task board markers: `[P]` priority, `[X]` discard, `[Q]` queue
- Status emojis: 🚀 🔴 🟡 🟢 ⚠️ ✅ ❌ ⏳
