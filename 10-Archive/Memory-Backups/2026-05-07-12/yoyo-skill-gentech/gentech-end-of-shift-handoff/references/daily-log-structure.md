# Daily Log Schema — YAML Frontmatter + Body Structure

## File Naming
`08-Daily/YYYY-MM-DD.md`

## Frontmatter (YAML)
```yaml
---
date: 2026-05-03
type: daily-sync
status: complete
source: gentech-cron
---
```
Fields:
- `date` — log date (matches filename)
- `type` — usually `daily-sync`; can be `post-mortem`, `incident`, `handoff`
- `status` — `complete`, `partial`, `failed`
- `source` — `gentech-cron`, manual agent name, or system

## Body Structure (Markdown)

### Title Block
```markdown
# Daily Second Brain Sync — 2026-05-03 (Sunday)
```

### TL;DR Section
```markdown
## TL;DR

**Critical monitoring discrepancy discovered and resolved** — three D5 monitoring scripts reported divergent position values...
```
Contains: 1–2 sentence summary of most critical item(s). May include emoji markers (🚨 🔴 ⚠️).

### Team Sections (standard order)
```markdown
## 🏛️ HQ / Coordinator
### Daily Operations
- ✅ **Daily cron executed** — May 3 silent run at ~11:45 UTC; vault sync completed.
- ⚠️ **Agent check-in status** — All agents (Dmob, YoYo, Desmond, Gentech) remain OFFLINE...

### Flags Raised
- **DMOB overload (P0)** — 4 active P0/P1 tracks...
```

```markdown
## 🧪 Labs (DMOB)
### Script Discrepancy Incident — 2026-05-03
**Status:** DIAGNOSED & RESOLVED (protocol defined) | Priority: 🔴 P0
...
```

```markdown
## 📈 Strategies (YoYo)
### DeFi Milestone Tracker — IL Review Flag
**Position health as of May 3:**
| Metric | Value | Status |
...
```

```markdown
## 🎨 Creative / Entertainment (Desmond)
### Status Update
- No May 3 activity logged; weekend cadence expected.
...
```

### Key Decisions / Actions
```markdown
## ⚠️ Key Decisions Made / Actions Taken Today (May 3)

1. **Script discrepancy protocol defined** — Ground truth hierarchy established...
2. **IL review flag triggered on D5 position** — IL spike to -17.65%...
...
```

### Open Items / Blockers Table
```markdown
## 🔓 Open Items / Blockers

| ID | Item | Owner | Deadline | Status |
|----|------|-------|----------|--------|
| H2026-05-02-01 | DeFi milestone state machine... | DMOB | May 3 EOD | 🚀 Pending Ack |
| — | DisputeResolver code snippets... | DMOB | May 2 EOD (overdue) | 🔴 High (overdue) |
```
Columns: ID (handoff ID or —), Item description, Owner, Deadline, Status (emoji + text)

### Week Activity Summary
```markdown
## 📊 Week W18 Activity Summary (Apr 27–May 3)

| Date | Files Modified | Key Developments |
|------|----------------|------------------|
| Apr 27 | 6 | BACKGROUND — Skills GitHub auto-update operational |
| May 2 | 13+ | **MAJOR** — D5 consolidation shipped... |
| May 3 | 242 | **CRITICAL** — Script discrepancy incident resolved... |
```

### End Of Day Summary
```markdown
## 📎 End Of Day Summary — 2026-05-03 16:02 UTC

### Vault Health & Activity
- **Files modified today:** 242
- **Vault health score:** 7/10
- **Disk usage:** 82%
- **Agents online at close:** 0 (all OFFLINE)

### Key Discoveries Made Today
1. D5 monitoring script discrepancy — $55 variance...
...

### Escalations & Outcomes
- **13:45 UTC escalation window passed** — H2026-05-02-01 and H2026-05-02-02 still unacknowledged...
...

### Blockers Remaining (Through Midnight)
- **DMOB bandwidth crisis** — 4 P0/P1 tracks active...
...
```

## Footer
```markdown
*Synced by: Gentech Daily Cron — Silent Run*  
*Final Sync: 2026-05-03 ~16:02 UTC*  
*Vault: /root/vaults/gentech/08-Daily/2026-05-03.md*  
*Next sync: May 4 ~03:00 UTC (W19 kickoff)*
```

## Parsing Tips
- TL;DR first paragraph after header = executive summary
- Team sections marked with emojis; extract bolded accomplishments (`✅`, `⚠️`, `🔴`)
- Blockers table in "🔓 Open Items / Blockers" → absolute source for pending work
- Week summary table → historical context (files modified count, milestone days)
- EOD summary → health metrics + discoveries + escalations
- Look for `🚨`, `🔴`, `⚠️` emojis as priority signals
- Status markers: `✅` done, `⚠️` watch, `🔴` critical, `🚀` rocket = active priority

## Common Patterns
- Weekend days (Sat/Sun): Agents usually OFFLINE; expect minimal activity
- Handoff escalations: Appear in TL;DR, Key Decisions, and Blockers sections
- Incidents: Flagged with `**Status: ACTIVE` or `🔴 INCIDENT` in body
- Discrepancies: Often documented with comparison tables (Script | Reported | Status)
- Ground truth declarations: Usually `lp-position-reader.py` for on-chain positions

## Related
`references/grep-patterns.md` — quick grep commands to extract sections
