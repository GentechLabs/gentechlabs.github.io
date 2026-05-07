# Cron Job Consolidation Pattern — Avoiding Duplicate Monitors

## Problem

Multiple cron jobs across different agent profiles end up running **the same or similar monitoring tasks** on different schedules, causing:
- Redundant API calls (rate limit exhaustion)
- Conflicting state writes (race conditions)
- Duplicate Telegram messages (noise)
- Wasted compute and attention

### Real Example (2026-05-02)

| Profile | Job Name | Schedule | What it Runs |
|---------|----------|----------|--------------|
| Yoyo (Gentech) | Crypto Watchlist + LP Monitor | 4× daily (8:15,12:15,16:15,20:15) | `lp-range-monitor-v2.py` |
| Yoyo (Yoyo profile) | DeFi Milestone + LP Monitor | Daily at 14:10 | crypto-lp-monitoring skill → `lp-range-monitor-v2.py` |
| DMOB (DMOB profile) | Defi Milestone | Daily (interval 1440m) | Consolidated Crypto Watchlist skill |
| Gentech | Gentech Watchdog | Every 5 min | Agent health (not LP) |

**Result:** Same LFJ position monitored 5× daily with three different implementations. Confusion over which numbers are authoritative.

---

## Solution: Single Source of Truth Pattern

### Step 1 — Inventory All Relevant Cron Jobs

```bash
# Search all agent profiles for LP/milestone keywords
find ~/.hermes/profiles -name "jobs.json" -exec grep -l "milestone\|lp\|defi\|crown" {} \;
```

Parse each `jobs.json` and list:
- Job name
- Schedule
- Script or skill invoked
- Prompt excerpt (what it actually does)

### Step 2 — Identify the Canonical Job

**Criteria for choosing canonical job:**
1. **Uses a skill** (not raw script) — higher abstraction, documented
2. **Schedule matches business need** — LP positions don't need 4× daily; once per day is sufficient unless market is extremely volatile
3. **Output format is consumable** — structured JSON or clean markdown for handoff
4. **State management is sound** — reads/writes to proper state files, handles quiet hours, respects silent-run rules

In our case: **"YoYo — DeFi Milestone + LP Monitor"** (daily at 14:10) wins because:
- Uses `crypto-lp-monitoring` skill (documented)
- Includes milestone progression + LP health
- Already has proper alert thresholds
- Outputs JSON for AAE ingestion + human-readable summary

### Step 3 — Decommission Duplicates

For each duplicate job:
1. **Disable** in Hermes: `hermes cron disable <job-id>`
2. **Archive** the job definition: move or delete from `cron/jobs.json`
3. **Notify** the agent owner in Mess Hall: `"Disabled redundant LP monitor — consolidated to daily 14:10 run."`
4. **Update** any runbooks that reference the old job

**Don't just delete** — disable first, observe for 24–48h to confirm no downstream dependencies rely on it.

### Step 4 — Unify Configuration

Ensure **all remaining monitoring paths** read from:
- `~/.hermes/scripts/.lfj-aae-config.json` (milestones, DCA params)
- `~/.hermes/scripts/.lfj-position-tracker.json` (current range, entry deposit)
- `~/.hermes/scripts/.lfj-range-state.json` (efficiency history)

**Kill any hardcoded constants** in scripts that deviate from config.

---

## Alert Threshold Consolidation

**Single authority file:** `~/.hermes/scripts/.lfj-aae-config.json`

```json
{
  "milestones": [...],
  "dca": {
    "base_amount": 50,
    "boost_amount": 15,
    "boost_trigger_efficiency": 50
  },
  "alert_rules": {
    "silent_if": ["in_range", "efficiency_ok", "no_action_needed"],
    "alert_if": ["out_of_range", "efficiency_low", "milestone_hit", "compound_ready", "dca_day"],
    "critical_if": ["price_crash", "il_severe"]
  }
}
```

**Scripts must:**
- Load config at startup
- Re-read on each run (no caching stale values)
- Never hardcode thresholds like `EFFICIENCY_RED_THRESHOLD` separately (except for internal debounce timing which is operational not strategic)

**Note:** `EFFICIENCY_WARNING_THRESHOLD` and `EFFICIENCY_RED_THRESHOLD` are **operational** (script runtime) not strategic (user-tunable). They belong in script constants but should be documented in config's alert_rules as the conceptual mapping.

---

## Detection: Spotting Duplicate Monitors

**Red flags:**
- Two jobs with different schedules but same skill/script in prompt
- Same pool address appearing in multiple job descriptions
- Vault entries showing duplicate updates on same day from different cron sources

**Grep pattern:**
```bash
grep -r "lp-range-monitor" ~/.hermes/profiles/*/cron/jobs.json
grep -r "milestone" ~/.hermes/profiles/*/cron/jobs.json
```

If same script referenced by >1 job → consolidation candidate.

---

## When Duplication Is Intentional

**Acceptable duplicates:**
- Different **chains** (Avalanche vs Arbitrum) — separate jobs
- Different **pools** (USDC/USDT vs AVAX/USDC) — separate jobs
- Different **output channels** (strategies group vs vault-only) — same script, different delivery
- Different **trigger conditions** (price spike vs daily) — separate jobs may be warranted

Our LFJ situation was **unintentional** — same pool, same script, three jobs.

---

## Checklist Before Adding New Cron Job

- [ ] Search existing jobs for similar purpose — can I reuse?
- [ ] Prefer skill over raw script invocation
- [ ] Schedule: Is X times per day truly needed, or would daily suffice?
- [ ] State file: Will this job write to same state file as another job? If yes, coordinate or consolidate.
- [ ] Output channel: Does this duplicate someone else's Telegram channel?
- [ ] Document job purpose in vault: `00-HQ/Approvals/cron-job-registry.md`

---

## Related

- `agent-coordination` skill — handoff protocols when consolidating
- `devops/cron-orchestrator` — Hermes cron management
- Vault: `00-HQ/Agent-Setup/cron-job-inventory.md` (if exists)
