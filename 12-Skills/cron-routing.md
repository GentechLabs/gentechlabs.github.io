---

type: protocol
status: ACTIVE
enforced-by: all-agents
created: 2026-04-18
last-synced: 2026-05-09

---

# 📬 Cron Job Smart Routing

## Before Creating ANY Cron Job

1. **Check the Brain first:**
   - `03-Strategies/cron-jobs.md` — YoYo's cron reference
   - `02-Labs/cron-jobs-registry.md` — Dmob's cron registry
   - `green-room/cron-jobs.md` — shared cron coordination
   - `12-Skills/cron-registry.md` — master skill-based registry
2. Check this doc for the right delivery group
3. Check existing cron jobs (`cronjob list`) for duplicates or conflicts
4. Route to the correct group based on domain

## Routing Map

| Domain | Deliver To | Group ID |
|--------|-----------|----------|
| LP monitoring, DeFi yields, market analysis, portfolio | **Strategies** | `telegram:-1002916759037` |
| Hackathons, bug bounties, grants (opportunities) | **Labs** | `telegram:-1003872552815` |
| Content, social media, branding | **Entertainment** | `telegram:-1003893562036` |
| Cross-team coordination, health checks, system | **HQ** | `telegram:-1003863540828` |
| Jordan-only (personal finance, watchlist) | **Origin** | `origin` |
| Internal scripts, model switching | **Local only** | `local` |

## Domain Detection Keywords

| Keywords in prompt | Route to |
|--------------------|----------|
| LP, yield, liquidity, DeFi, swap, pool, farming, portfolio, token, price | Strategies |
| hackathon, bounty, grant, opportunity, submission deadline | Labs |
| post, tweet, content, social, X, branding | Entertainment |
| health, watchdog, system, agent status, model switch | HQ / Local |
| watchlist, price, portfolio, personal | Origin |

## Labs — Cron Jobs Scope

Labs ONLY receives opportunity-related cron jobs:
- Hackathon deadline alerts
- Bug bounty scans
- Grant application reminders
- No dev/code cron jobs — those are handled by agents directly, not cron

## Current Cron Jobs — Group Audit

*All entries synced from live `cronjob list` on 2026-05-09. Times in UTC.*

| Job ID | Job | Schedule | Delivery | Domain | Last Run |
|--------|-----|----------|----------|--------|----------|
| b006812998df | Morning Digest | `30 11 * * *` (6:30 AM ET) | HQ | Coordination | 2026-05-09 |
| 9ecfada01952 | Gentech Watchdog | `*/30 * * * *` (every 30m) | Local | System health | 2026-05-09 |
| faed4f588aef | DeFi Milestones | `15 12,16,20 * * *` (3x/day) | Strategies | DeFi monitoring | 2026-05-09 |
| aebc6f0a84bd | Protocol Due Diligence Chain | `0 13 * * 4` (Thu 9 AM ET) | Strategies | DeFi research | 2026-05-07 |
| 6ea057d66d64 | x402 Ecosystem Monitor | `0 18 * * 0` (Sun 2 PM ET) | Strategies | Ecosystem scan | 2026-05-03 |
| 4e21a92b8c79 | Portfolio Daily Health Check | `0 12 * * *` (8 AM ET) | Strategies | Portfolio health | 2026-05-09 |
| effa7ee494bb | Kite AI Hackathon Submission Check | `0 14 * * *` (10 AM ET) | Labs | Hackathon ops | 2026-05-08 |
| ef324b70c014 | hackathon-bounty-monitor | `0 17 * * *` (1 PM ET) | HQ | Opportunities | 2026-05-08 |
| 5a765db9dce2 | Gentech X Content Extractor | `0 17 * * *` (1 PM ET) | Entertainment | Content/Social | 2026-05-08 |
| fdaddce49730 | Security → Content Pipeline | `0 13 * * 2,5` (Tue/Fri 9 AM ET) | Entertainment | Content/Social | 2026-05-08 |
| 61965c05ce7d | social-briefing | `0 16 * * *` (12 PM ET) | Entertainment | Content/Social | 2026-05-08 |
| c3053df6b3d3 | Brain Backup → GitHub | `0 22 * * *` (6 PM ET) | Local | Infrastructure | 2026-05-09 |
| 051dcc8d3f11 | Brain Sync — Weekly | `0 16 * * 0` (Sun 12 PM ET) | Local | Vault sync | 2026-05-08 |
| fc4bead12d22 | Vault Manager — Nightly Sweep | `0 23 * * *` (7 PM ET) | Local | Vault hygiene | 2026-05-08 |
| 99432e0f537b | Evening Wrap-Up | `0 0 * * *` (8 PM ET) | HQ | Coordination | Never run |
| ee893caf9dad | Mess Hall Internal | `0 3 * * *` (11 PM ET) | Local | Housekeeping | Never run |
| e7e3f6147ca9 | Provider Usage Monitor | `0 12 * * *` (8 AM ET) | HQ | System health | 2026-05-09 |
| a320481334a7 | Token Usage Weekly Audit | `0 15 * * 0` (Sun 11 AM ET) | HQ | System health | Never run |
| 87277e1b2b69 | Weekly Skills Update | `0 14 * * 0` (Sun 10 AM ET) | HQ | System health | Never run |

### Summary by Delivery Group

| Group | Jobs | IDs |
|-------|------|-----|
| **Strategies** | 5 | DeFi Milestones, Protocol DD, x402 Monitor, Portfolio Health, (social-briefing → Entertainment) |
| **Labs** | 1 | Kite AI Check |
| **Entertainment** | 3 | X Content Extractor, Security→Content, social-briefing |
| **HQ** | 5 | Morning Digest, hackathon-bounty-monitor, Evening Wrap-Up, Provider Usage, Token Usage Weekly, Weekly Skills |
| **Local** | 5 | Watchdog, Brain Backup, Brain Sync, Vault Manager, Mess Hall Internal |

## Cron Fixes — Hermes v2026.5.7 (May 9, 2026)

Recent Hermes update fixed several cron-related issues:
- **Streaming edits race condition** — Gateway now streams Telegram edits safely (no more "message not modified" spam)
- **Cron delivery reliability** — Improved error handling for failed deliveries
- **False positive "behind" reports** — Git sync check may compare against stale reference; ignore "X commits behind" unless HEAD differs from origin/main

## Change Log

| Date/Time | Change |
|-----------|--------|
| 2026-04-18 19:51 EDT | Initial routing doc created |
| 2026-04-18 19:51 EDT | Moved Kite AI Check-In from HQ → Labs |
| 2026-04-18 19:51 EDT | Added Labs scope definition (opportunities only) |
| 2026-04-18 19:51 EDT | Added domain detection keywords table |
| 2026-05-07 | Finance prong rule added to smart-routing-rules.md |
| 2026-05-09 | Full sync with live cronjob list (19 jobs). Updated all IDs, schedules, delivery targets. Added Hermes v2026.5.7 fixes section. |

## Rule

**No orphaned cron jobs.** Every job has a home group. If the domain doesn't match any group, default to HQ.
**No undated entries.** Every audit row must have Added and Verified dates. No exceptions.
**Finance prong rule** (from smart-routing-rules.md): Any cron job with a finance component → Strategies group. Exception: hackathon/bug bounty opportunity scans → Labs.
