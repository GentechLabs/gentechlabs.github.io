---
name: gentech-daily-sync
description: Daily second brain sync — orchestrate, summarize, and archive cross-team activities for GenTech Labs. Silent-run capable (vault-only output).
ai_hint: Recurring Gentech orchestration pattern; vault topology-dependent
---

## Trigger

- Running daily sync as Gentech CEO/COO
- Compiling daily status from vault sources
- "Daily second brain sync" command
- End-of-day or start-of-day coordination roundup
- **End-of-shift wrap-up for Jordan** — when explicit request for handoff summary with sections: Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Tomorrow's Priorities
- **Pre-shift coordination for Jordan** — morning briefing before team starts work; focus on priorities, deadlines, decisions needed, and immediate action items. Sections: Sprint State, Today's Priorities, Hackathon Deadlines, Critical Decisions Needed, System Health Snapshot, Action Items — Immediate. Keep direct and skimmable; end with forward-looking hook.

## AI Behavior

Speaking style: Warm, mature, calm authority. Use "We're building" not "They're building". 2–3 sentences per thought. End with forward-looking hooks: "This is just the beginning…"

Tone: Visionary storyteller, deliberate cadence, big-picture focus.

Format: Markdown with YAML frontmatter; structured sections; concise bullet-heavy writing.

Routing: Delegate via department Telegram groups, not DMs. Use Green Room for cross-department handoffs.

## Process

1. **Identify date & week** — Get current date, compute ISO week number (W##), fetch vault year folder `11-Mess Hall/YYYY/`. If W## folder missing, create it.
2. **Create today's context folder** — Ensure `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` exists before reading/writing any files.
3. **Scan for recent vault activity** — Use Python mtime scan across vault for files modified in last 24h. Exclude `.git/`, `tmp/`, `__pycache__/`, `node_modules/`, `.obsidian/`. Sort descending; include top 20 items in daily summary **OR** scan selective department folders (`02-Labs/`, `03-Strategies/`, `04-Entertainment/`, `09-Green Room/`) for targeted reads.
4. **Read yesterday's daily context** — Attempt to read `11-Mess Hall/YYYY/W##/YYYY-(previous-day)/today-context.md` for carry-forward items. If missing, try alternative files in the previous day's folder (e.g., `overnight-sprint-status.md`, `rotation-log-*.md`) — these often contain the same carry-forward signals. If still missing (weekend/holiday), scan backwards one day at a time until a context file is found or W##-1 week boundary reached.
5. **Read today's context (if exists)** — Open `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md`. If missing, note "today-context not yet published" and proceed — it may be written later by Gentech or agents.
6. **Read rotation log (if exists)** — Open `11-Mess Hall/YYYY/W##/YYYY-MM-DD/rotation-log.md` for operations log. If absent, create with basic metadata (date, sync start).
7. **Pull active handoffs** — List files in `09-Green Room/active-handoffs/` (dated filenames); read only recent ones (last 24-48h by filename date or mtime). Older handoffs (>3 days) just note count/status in summary, don't read full content. Also scan `09-Green Room/WORKFLOW-ACTIVE.md` for coordination protocols.
8. **Read approval decisions** — Scan `00-HQ/Approvals/` (YYYY-MM-DD-*.md) plus `00-Inbox/approvals/` for active queues.
9. **Read auto-updated DeFi trackers explicitly** — 
   - `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` (LP snapshot + efficiency)
   - `09-Green Room/Defi-Strategy-Engine-Evolution.md` (milestone tracker state — renamed from D5→DeFi on May 7)
   - Also scan `09-Green Room/` for files matching `lp-status-*.md` and `d5-*.md`
10. **Read project updates by department** — Pull latest from:
    - `02-Labs/` (hackathon folders, Labs-Queue.md, R&D status)
    - `03-Strategies/` (research, competitive intel, strategy docs)
    - `04-Entertainment/` (content pipeline, dev-blog, social drafts)
    - `00-HQ/` (summaries, operations decisions)
11. **Compile structured report** — Build sections: TL;DR, Department Status Tables, Incidents (if any), Decisions (since last sync), Open Items (table format), Risks (Critical/Medium/Low), Week Status.
12. **Add forward hook** — End with "This is just the beginning…" trajectory paragraph.
13. **Write daily summary file** — Save to `11-Mess Hall/daily/YYYY-MM-DD-summary.md`. Include: date, week, sprint name, agent activity table (Dept/Agent/Status/Focus/Blockers), action items table, ideas/notes, links.
14. **Update working memory** — Patch `00-Working-Memory.md` to reflect current sprint status, incident resolution state, and handoff backlog. Use structured memory entry format (`## Memory Entry — YYYY-MM-DD (Agent)`).
15. **Commit to git** — Stage new/updated files under `11-Mess Hall/` and `00-Working-Memory.md`. Commit with message prefix `docs: daily sync — YYYY-MM-DD` followed by concise body (3-5 bullets). Keep commits atomic (daily sync only).
16. **Obsidian sync** — Run `cd /root/vaults/gentech && ob sync` if CLI available.
17. **Delivery mode** — If silent-run (cron/scheduled): respond `[SILENT]` only, do not output report content. Else deliver full markdown summary.

## Vault Paths (Current as of 2026-05-04)

- **Daily summary digest:** `11-Mess Hall/daily/YYYY-MM-DD-summary.md` (auto-curated, 7-day retention)
- **Daily context folder:** `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` (per-ISO-week year-folders)
- **Mess Hall root:** `11-Mess Hall/` (contains `daily/`, `2026/W##/` date folders, `handoff-board.md`, `task-board.md`, `agent-coordination-board.md`)
- **Green Room:** `09-Green Room/` (active handoffs, approvals, cross-group work-in-progress)
- **Active handoffs:** `09-Green Room/active-handoffs/` (YYYY-MM-DD-*.md files)
- **Approvals:** `00-HQ/Approvals/` and `00-Inbox/Approvals/` (pending decisions)
- **Project trackers:** `02-Labs/` for active builds and hackathons; `06-Content/` for social/draft content; `03-Strategies/` for research
- **HQ Operations:** `00-HQ/` (summaries, approvals, team manifest, workflow docs)
- **Working memory:** `00-Working-Memory.md` (single source of truth for sprint state and incident resolution)

**Note:** The legacy `08-Daily/` folder has been superseded by the `11-Mess Hall daily/` pattern. Weekly organization uses ISO week numbers under `11-Mess Hall/YYYY/W##/`. Daily files are NOT stored in date-named root folders; they live in the per-week date subfolders.

## Sources To Read

**Daily continuity (in precedence order):**
- Today's context: `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md` (primary briefing)
- Previous day's context: `11-Mess Hall/YYYY/W##/YYYY-(prev-day)/today-context.md` (carry-forward risks)
- Active handoffs: `09-Green Room/active-handoffs/*YYYY-MM-DD*.md`
- Coordination boards: `11-Mess Hall/handoff-board.md`, `11-Mess Hall/agent-coordination-board.md`, `11-Mess Hall/task-board.md`
- Working memory: `00-Working-Memory.md` (sprint state + incident log)

**DeFi / LP trackers (signal sources):**
- LP monitoring: `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` (IL, efficiency, fee metrics)
- D5 milestone: `09-Green Room/D5-Strategy-Engine-Evolution.md` (milestone ladder, state machine)
- LP status snapshots: `09-Green Room/lp-status-*.md` (timestamped position files)
- D5 analysis: `09-Green Room/d5-*.md` (cron bugs, consolidation memos)

**Departmental activity sources:**
- Labs (Dmob): `02-Labs/Labs-Queue.md`, `02-Labs/Hackathons/Active/`, `02-Labs/Swarms-Solana-Adapter.md`
- Strategies (YoYo): `03-Strategies/` (research, competitive intel, LP analysis)
- Entertainment (Desmond): `04-Entertainment/dev-blog/`, `06-Content/Queue/`, `06-Content/X-Drafts/`
- HQ / Jordan: `00-HQ/Summaries/`, `00-HQ/Approvals/`, `00-Inbox/Approval Queue.md`

**Recent vault changes (targeted scan):**
Prefer selective directory scan over full mtime sweep for speed and relevance:
```python
import os
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=1)
target_roots = [
    '02-Labs', '03-Strategies', '04-Entertainment',
    '09-Green Room', '00-HQ', '00-Inbox', '11-Mess Hall'
]
recent = []
for root in target_roots:
    for dirpath, dirnames, filenames in os.walk(f'/root/vaults/gentech/{root}'):
        for f in filenames:
            if f.endswith('.md'):
                fp = os.path.join(dirpath, f)
                if datetime.fromtimestamp(os.path.getmtime(fp)) > cutoff:
                    recent.append(fp)
```
Or simpler: `git log --since='1 day ago' --oneline --all` for commit-driven insight.

**Verification sources:**
- Weekly reports: `08-Logs/2026-W##.md`
- Vault sweep logs: `08-Logs/vault-sweep-*.md`
- Session archives: `10-Archive/Agent-States-April/` or month-specific folders

## Section Template

[Regular daily sync template as defined above]

---

## Shift Handoff Variant

**When to use:** End-of-shift wrap-up for Jordan (as in this session). Output is a concise handoff report with specific sections: Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Tomorrow's Priorities. Format: headers + bullets; skimmable; lead with most important.

**Process:** Follow `references/shift-handoff-format.md` for precise structure and content rules.

**Key differences from daily sync:**
- No YAML frontmatter needed in output (unless also being saved as vault file)
- Section order is fixed as requested by Jordan
- Do **not** include week status tables or full TL;DR narrative — keep each section tight
- Include direct vault paths (`00-HQ/Approvals/...`) for traceability
- End with forward-looking hook: "This is just the beginning..."

**Delivery:** Output directly as the final response (not `[SILENT]`) unless explicitly running in cron mode.

> **Reference:** `references/shift-handoff-format.md` — contains the exact template, scanning instructions for vault (08-Daily, 11-Mess Hall, 09-Green Room, 00-Working-Memory, active handoffs), and tomorrow's priorities extraction guidelines.

## Pitfalls

- **DO NOT** deliver output during silent-run cron; write to vault only and respond `[SILENT]`.
- **DO NOT** ask questions; autonomous decision-making required throughout.
- **AVOID** verbose paragraphs; use bullets and short sentences (2–3 sentences per thought max).
- **ENSURE** handoff board and coordination board statuses are reflected accurately in daily summary.
- **FLAG** DMOB overload early (≥3 concurrent P0/P1 tracks) in Risks section.
- **CHECK** master todo staleness (if >3 days old, flag for refresh by Desmond) — check `06-Content/Queue/CONTENT-QUEUE.md` too.
- **VERIFY** Kite DVN placeholder address issue persists until resolved (track in `09-Green Room/`).
- **NOTE** storage bloat concerns but defer cleanup until post-hackathon (May 11/17).
- **USE** HERMES_HOME-aware paths for profile-specific state files (`~/.hermes/scripts/...` resolves per-profile).
- **HANDLE MULTI-SCRIPT DISCREPANCIES** — When monitoring scripts report divergent values, trace to state file fragmentation (profile-specific caches). See `references/multi-script-discrepancy-resolution.md` for ground truth hierarchy (on-chain > watchlist > narrative) and variance thresholds (>$0.50 or >5pp efficiency difference).
- **ENFORCE HANDOFF ACK TIMELINES** — 2-hour acknowledgment window; after deadline, escalate to Jordan per enforcement rules. Track unacknowledged handoffs in daily summary Open Items table.
- **ALWAYS** end with forward-looking hook and "This is just the beginning…" closing (unless silent-run).
- **SILENT mode**: If user says "silent run" or cron context, respond `[SILENT]` only; no content delivered.
- **GIT QUOTING**: `11-Mess Hall/` contains a space. Always quote paths in shell commands: `git add "11-Mess Hall/daily/..." "00-Working-Memory.md"`. Unquoted `git add 11-Mess Hall/...` silently fails to stage anything.
- **`ob sync` UNCONFIGURED**: Obsidian CLI sync is not set up for the gentech vault (`No sync configuration found`). Step 16 should be skipped or run `ob sync-setup` first. Do not treat sync failure as blocking.
- **WEEK-ROLLOVER EDGE CASE**: On first daily sync of a new ISO week (typically Monday ~03:00 UTC), the `11-Mess Hall/YYYY/W##/` folder may not exist yet. Create it before attempting to write `today-context.md`. Week number from `datetime.isocalendar()`.
- **VAULT STRUCTURE ASSUMPTION GUARD**: Do NOT hardcode `08-Daily/` as write target — that path is legacy (renamed to `08-Logs/`). Current daily summary location is `11-Mess Hall/daily/YYYY-MM-DD-summary.md`. Context files belong under `11-Mess Hall/YYYY/W##/YYYY-MM-DD/`. If either path structure is missing, create it.
- **PORTFOLIO/CONTENT TRACKER SWAP**: The D5/LP trackers formerly lived in `03-Projects/DeFi/`; they now reside in `09-Green Room/` with prefixed filenames (`LP Scout — ...`, `Defi-Strategy-Engine-Evolution.md`). Scan `09-Green Room/` for `lp-status-*.md` and `d5-*.md` patterns instead. Note: D5→DeFi rename completed May 7; script filenames (`d5-master-cron.py`) kept as-is for cron compatibility.
- **SAME-DAY RE-SYNC**: When a second sync runs on the same day (common with cron), the daily summary file (`11-Mess Hall/daily/YYYY-MM-DD-summary.md`) already exists. **Update it** — do NOT create a second file or overwrite with only the delta. Read the existing summary, merge new data (fresh LP snapshots, new handoffs, updated blockers), and write the complete updated file. Similarly, the working memory entry for today already exists — replace it in-place with the updated version, don't append a second entry for the same date.

## Support Files

This skill bundles:
- `references/daily-sync-vault-map.md` — Full vault topology diagram
- `references/silent-run-protocol.md` — Cron delivery rules and output suppression
- `references/multi-script-discrepancy-resolution.md` — State file fragmentation detection, ground truth hierarchy, variance thresholds, follow-up task template
- `templates/daily-sync-frontmatter.md` — YAML frontmatter starter template
- `scripts/scan-recent-vault-files.sh` — Bash one-liner to list recent vault changes
- `scripts/get-current-week.sh` — Compute week number and W## path
- `scripts/verify-daily-sync.sh` — Post-write validation checks

See skill files under `~/.hermes/profiles/gentech/skills/gentech-daily-sync/` for details.
