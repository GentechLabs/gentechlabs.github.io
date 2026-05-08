# Cron Job Routing Audit — May 5, 2026 (Updated May 7, 2026)

## Context
- **May 5**: Jordan clarified: Department groups are work-execution channels only. HQ is Jordan's personal dashboard.
- **May 7 (Option 1):** All specialist cron jobs rerouted to HQ. Specialists on-demand only. See `references/option-1-implementation-20260507.md`.

## Channel IDs

| Department | Channel | Chat ID |
|-----------|---------|---------|
| GenTech HQ (Jordan) | GenTech HQ | `-1003863540828` |
| YoYo (Strategies) | YoYo group | `-1002916759037` |
| DMOB (Labs) | DMOB group | `-1003872552815` |
| Desmond (Creative) | Desmond group | `-1003893562036` |

## Current Routing Rules (Post Option 1)

1. **ALL monitoring/digests/reports** → HQ (`telegram:-1003863540828`)
2. **Internal vault work** → `local` delivery
3. **Agent-triggered (origin)** → `origin` delivery
4. **Specialist groups** → Only for deep work when Gentech routes there explicitly

## Anti-Patterns Found & Fixed

### 1. Bare `telegram` delivery target
- **Job**: LayerZero DVN Monitor (`7d18ebcb8443`)
- **Issue**: `deliver: "telegram"` (bare) falls back to home channel (HQ)
- **Fix**: Changed to `deliver: "telegram:-1002916759037"` (YoYo's group)
- **Lesson**: Always use full `telegram:<chat_id>` format

### 2. Wrong chat ID (typo)
- **Job**: hackathon-bounty-monitor (`ef324b70c014`)
- **Issue**: `deliver: "telegram:-100386354028"` — typo in chat ID
- **Error**: `"Chat not found"` confirmed the bad ID
- **Fix**: Changed to `deliver: "telegram:-1003872552815"` (DMOB's group)
- **Lesson**: Verify chat IDs against known-good list; typo in last digit = dead delivery

### 3. Specialist crons delivering to department groups (Option 1 violation)
- **Jobs**: 10 specialist crons (DeFi Milestones, Protocol Due Diligence, etc.)
- **Issue**: Delivering to YoYo/DMOB/Desmond groups instead of HQ
- **Fix**: All rerouted to HQ (`telegram:-1003863540828`) on May 7, 2026
- **Lesson**: Under Option 1, ALL monitoring outputs go to HQ unless explicitly `local` or `origin`

## Audit Checklist

When reviewing cron job routing:
1. Is the job's deliver target pointing to HQ? (Should be, unless `local` or `origin`)
2. Is the job internal vault maintenance? → Route to `local`
3. Is the delivery target a full `telegram:<chat_id>`? → Never bare `telegram`
4. Verify chat IDs against the channel ID table above
