---

type: protocol
status: ACTIVE
enforced-by: all-agents
created: 2026-04-18

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
| LP monitoring, DeFi yields, market analysis | **Strategies** | `telegram:-1002916759037` |
| Hackathons, bug bounties, grants (opportunities) | **Labs** | `telegram:-1003872552815` |
| Content, social media, branding | **Entertainment** | `telegram:-1003893562036` |
| Cross-team coordination, health checks, system | **HQ** | `telegram:-1003863540828` |
| Jordan-only (personal finance, watchlist) | **Origin** | `origin` |
| Internal scripts, model switching | **Local only** | `local` |

## Domain Detection Keywords

| Keywords in prompt | Route to |
|--------------------|----------|
| LP, yield, liquidity, DeFi, swap, pool, farming | Strategies |
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

*All entries must include date added and last verified. Times in EDT/EST.*

| Job ID | Job | Schedule (EDT) | Delivery | Added | Verified |
|--------|-----|----------------|----------|-------|----------|
| b1a52d07e0dc | Daily Briefing + Stars | 6:30 AM daily | HQ | 2026-04-18 | 2026-04-18 |
| 404da0a8f688 | Gentech Watchdog | Every 5 min | HQ | 2026-04-18 | 2026-04-18 |
| e491114cdb8a | YoYo — LP Watchlist Check | 4x/day | Strategies | 2026-04-18 | 2026-04-18 |
| faed4f588aef | YoYo — Crypto Watchlist | Every 2h (6AM-8PM) | Strategies | 2026-04-20 | 2026-04-20 |
| e9650290cf5d | Hermes Agent Sync Check | 6:00 AM daily | Labs | 2026-04-18 | 2026-04-18 |
| unified-opportunity-scanner | Weekly Opportunity Scanner | 6:00 AM Mon, Thu | Labs | 2026-04-18 | 2026-04-18 |
| efc275ff24aa | Security → Content Pipeline | 7:00 AM Tue, Fri | Entertainment | 2026-04-18 | 2026-04-18 |
| b3cf562ffe66 | Gentech X Content Extractor | 5:00 PM daily | Entertainment | 2026-04-18 | 2026-04-18 |
| 7dc384cf1b1a | The Brain — Daily | 4:00 PM daily | Local | 2026-04-18 | 2026-04-18 |
| e2f1f319957e | Model Switch → Ollama | 2:00 AM daily | Local | 2026-04-18 | 2026-04-18 |
| 48f2841b8b68 | Model Switch → Nous | 5:30 AM daily | Local | 2026-04-18 | 2026-04-18 |

**⚠ Known issue (2026-04-18 23:40 EDT):** Model switch crons disabled due to bot token conflict. All 3 specialists share one Telegram token — need 3 new BotFather bots to fix.

## Changelog

| Time (EDT) | Change |
|------------|--------|
| 2026-04-18 8:50 PM | Initial routing doc created |
| 2026-04-18 8:52 PM | LP monitor moved from HQ → Strategies |
| 2026-04-18 8:55 PM | Labs scope limited to opportunities only |
| 2026-04-18 9:00 PM | Brain references added, timestamps added |
| *Last synced: 2026-04-18 9:00 PM EDT* |

## Labs Cron Scope

**Labs cron jobs = opportunities only.** Hackathons, bug bounties, grants, submission deadlines.

## Change Log
| Date/Time | Change |
|-----------|--------|
| 2026-04-18 19:51 EDT | Updated audit table with live job IDs |
| 2026-04-18 19:51 EDT | Moved Kite AI Check-In from HQ → Labs |
| 2026-04-18 19:51 EDT | Added Labs scope definition (opportunities only) |
| 2026-04-18 19:51 EDT | Added domain detection keywords table |

## Rule

**No orphaned cron jobs.** Every job has a home group. If the domain doesn't match any group, default to HQ.
**No undated entries.** Every audit row must have Added and Verified dates. No exceptions.
