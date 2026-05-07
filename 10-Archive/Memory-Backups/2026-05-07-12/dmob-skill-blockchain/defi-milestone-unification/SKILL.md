---
name: defi-milestone-unification
description: Standardize DeFi Milestone thresholds, migrate daily cron → hourly unified monitor, sync vault→runtime
triggers:
  - consolidate_defi_milestones
  - migrate_defi_cron
  - unify_milestone_tracking
  - defi_milestone_cron_consolidation
  - milestone_threshold_sync
  - d5_milestone_unification
  - d5_cron_consolidation
patterns:
  - "Apply the changes we talk about earlier"
  - "DeFi Milestone consolidation"
  - "unified defi milestone and lp cron"
  - "switch to hourly unified monitoring"
  - "standardize milestone thresholds"
---

# DeFi Milestone Unification — Standardize & Consolidate

> Governs end-to-end standardization of DeFi Milestone thresholds across scripts, migration from fragmented daily cron to a single hourly unified monitor, and vault→runtime sync.

## When to Use

Use this skill when:
- Standardizing milestone tiers across multiple DeFi monitoring scripts
- Migrating from multiple daily cron jobs (morning/evening/all-day) to a single hourly unified monitor
- Aligning `lp-aae-signal-monitor.py` (the AAE signal engine) with the canonical 5-tier DeFi Milestone ladder
- Syncing vault configs to `~/.hermes/scripts/` for Hermes cron execution
- Resolving discrepancies between position tracker ranges and milestone summary ranges

## Naming Convention

**Always use "DeFi Milestone"** — never abbreviate as "D5". Jordan explicitly corrected this naming (May 2026). Use full form in all reports, chat messages, vault docs, and code comments.

## Trigger Condition Checklist

- [ ] `MILESTONES` arrays found in ≥2 scripts with mismatched thresholds
- [ ] Daily DeFi Milestone cron jobs (morning/evening/every-1440m) run alongside a broken/unscheduled unified monitor
- [ ] `~/.hermes/scripts/` contains stale copies of DeFi Milestone scripts (vault updated, runtime not)
- [ ] Hermes cron creation fails with "Script path must be relative to ~/.hermes/scripts"
- [ ] `defi-milestone-summary.py` range differs from `.lfj-position-tracker.json`

## Core Workflow

### Phase 1 — Audit & Baseline
1. Collect current thresholds from every DeFi Milestone script:
   - `d5-master-cron.py`
   - `defi-milestone-summary.py`
   - `lp-aae-signal-monitor.py` (DEFAULT_CONFIG)
   - `lp-unified-monitor.py` (if present)
   - `.lfj-aae-config.json`
2. Document discrepancies (tier labels, `daily_fees` values, `range_low/high`)
3. Test each script manually to confirm they run without NameError/KeyError

### Phase 2 — Canonical Threshold Standardization (5-Tier)
The unified DeFi Milestone ladder (Jordan-approved):

```json
[
  {"tier": 1, "label": "Scout",     "daily_fees": 5.0},
  {"tier": 2, "label": "Raider",    "daily_fees": 20.0},
  {"tier": 3, "label": "Warlord",   "daily_fees": 50.0},
  {"tier": 4, "label": "Sovereign", "daily_fees": 100.0},
  {"tier": 5, "label": "Freedom",   "daily_fees": 200.0}
]
```

Update **all** of these in both vault and runtime:
- `.lfj-aae-config.json` → `milestones` array
- `d5-master-cron.py` → `MILESTONES` list
- `defi-milestone-summary.py` → `MILESTONES` list
- `lp-aae-signal-monitor.py` → DEFAULT_CONFIG `milestones`
- `lp-unified-monitor.py` → `MILESTONES` list (if present)

**Pitfall:** `defi-milestone-summary.py` also hardcodes pool `range_high` in its `POOLS` block — align it with `.lfj-position-tracker.json` (currently 9.30).

### Phase 3 — Unified Monitor Verification
1. Run `~/.hermes/scripts/lp-aae-signal-monitor.py` manually → must exit 0 and emit JSON
2. Confirm `determine_severity()` uses time-based out-of-range escalation:
   - `OUT_OF_RANGE_WARNING_MINUTES = 10`
   - `OUT_OF_RANGE_RED_MINUTES = 15`
   - State field `out_of_range_since` tracks timestamp
3. If missing, patch `determine_severity()` and state handling (lines ~750–780) to implement debounce

### Phase 4 — Cron Migration
1. **Remove daily DeFi Milestone job** (usually `Defi Milestone` every 1440m):
   ```bash
   hermes cron remove <job_id>
   ```
2. **Create hourly unified job** (see `templates/hermes-cron-lp-hourly.txt` for copy-paste):
   ```bash
   hermes cron create "0 11-23/1 * * *" \
     "If status is SILENT, output nothing. Otherwise output only the human_report field." \
     --name "LP Position Monitor Hourly" \
     --script "lp-aae-signal-monitor.py" \
     --deliver origin
   ```
   **Note:** Script must live in `~/.hermes/scripts/` (home-relative, not absolute path). Cron rejects absolute paths.

3. Verify:
   ```bash
   hermes cron list | grep "LP Position Monitor"
   ```
   Next run time should align with schedule.

### Phase 5 — Vault → Runtime Sync
Hermes cron executes from `~/.hermes/scripts/`, not the vault. After any script/config change:

```bash
# Copy updated files from vault to runtime
cp /root/vaults/gentech/02-Labs/scripts/lp-aae-signal-monitor.py ~/.hermes/scripts/
cp /root/vaults/gentech/02-Labs/scripts/d5-master-cron.py ~/.hermes/scripts/
cp /root/vaults/gentech/02-Labs/scripts/defi-milestone-summary.py ~/.hermes/scripts/
cp /root/vaults/gentech/02-Labs/scripts/.lfj-aae-config.json ~/.hermes/scripts/
```

**Never** rely on symlinks; Hermes profile environments may not follow them. Use explicit copy.

### Phase 6 — Sanity Check
- Run each updated script from `~/.hermes/scripts/`:
  ```bash
  cd ~/.hermes/scripts && python3 lp-aae-signal-monitor.py
  ```
- Confirm tier progression (current_tier_label, next_tier_label) matches expected thresholds
- Verify `defi-milestone-summary.py` range matches tracker (`9.0–9.30`)

### Phase 7 — Archive Legacy (Optional)
After 1 week of stable unified runs, rename to `.bak`:
```bash
mv ~/.hermes/scripts/d5-master-cron.py{,.bak-$(date +%Y-%m-%d)}
mv ~/.hermes/scripts/defi-milestone-summary.py{,.bak-$(date +%Y-%m-%d)}
```

Keep vault originals intact; archive only runtime copies.

## Verification

Run the bundled consistency checker **before** and **after** applying changes:

```bash
python3 ~/.hermes/profiles/dmob/skills/blockchain/defi-milestone-unification/scripts/verify_milestone_consistency.py
```

Expected output:
```
✅ config: Scout:5.0, Raider:20.0, Warlord:50.0, Sovereign:100.0, Freedom:200.0
✅ master_cron: ...
✅ summary: ...
...
🎉 All files consistent with 5-tier DeFi Milestone ladder.
```

If any file shows a mismatch, reconcile it against the canonical 5-tier ladder before creating cron jobs.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Using absolute script path in `hermes cron create` | "Script path must be relative to ~/.hermes/scripts" | Copy file to `~/.hermes/scripts/` first, then use bare filename |
| Updating vault but not runtime | Cron runs old code, thresholds appear unchanged | Always sync vault→`~/.hermes/scripts/` after edits |
| Missing `Freedom` tier in config | Unified monitor shows only 4 tiers, progression stalls at Sovereign | Append tier 5 to every `milestones` array |
| `range_high` mismatch between summary and tracker | Summary shows 9.45, tracker shows 9.30 → confusion | Update hardcoded `range_high` in `defi-milestone-summary.py` POOLS block |
| State file format drift | `out_of_range_since` missing → debounce fails | Let script initialize fresh state; don't manually edit state JSON |
| Using "D5" abbreviation | Jordan corrected this — always use "DeFi Milestone" | Full form in all reports, chat, vault docs, and code |

## Outputs & Handoffs

- **Updated in vault:** `/root/vaults/gentech/02-Labs/scripts/` (source of truth)
- **Synced to runtime:** `~/.hermes/scripts/` (where Hermes cron executes)
- **Cron jobs:** `hermes cron list` should show only the hourly unified job active (plus any unrelated jobs)

## Related Skills

- `blockchain-operations` — broader DeFi ops; this skill specializes DeFi Milestone consolidation
- `vault-atomic-operations` — for concurrent-safe vault writes during multi-agent coordination (not needed here; single-writer session)

## References

- Consolidation plan: `/root/vaults/gentech/10-Archive/Memory-Backups/2026-05-03-11/dmob-skills-d5-cron-consolidation-plan.md`
- Handoff: `/root/vaults/gentech/10-Archive/green-room-handoffs/handoff-desmond-dmob-lp-cron.md`
- Position tracker: `/root/vaults/gentech/02-Labs/scripts/.lfj-position-tracker.json`
