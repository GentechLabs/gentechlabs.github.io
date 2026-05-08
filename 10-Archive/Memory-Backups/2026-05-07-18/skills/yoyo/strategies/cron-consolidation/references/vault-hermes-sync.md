# Vault → Hermes-Brain Sync: Deployment Pattern

**Context**: Strategies department scripts live in vault (`03-Strategies/scripts/`) but Hermes agents run from `hermes-brain` repo. Sync required for cron jobs to execute.

## Sync Mechanics

```
Vault (source of truth)
  └─ 03-Strategies/scripts/<script>.py
         ↓ (manual copy or rsync)
Hermes-Brain (runtime)
  └─ /root/repos/hermes-brain/profiles/<profile>/home/.hermes/scripts/<script>.py
         ↓ (Hermes gateway reads jobs.json)
Execution
  └─ hermes-cli gateway run --profile <profile>
```

## Step-by-Step Sync

1. **Copy script**
   ```bash
   cp /root/vaults/gentech/03-Strategies/scripts/d5-milestone-tracker.py \
      /root/repos/hermes-brain/profiles/yoyo/home/.hermes/scripts/
   ```

2. **Set permissions**
   ```bash
   chmod +x /root/repos/hermes-brain/profiles/yoyo/home/.hermes/scripts/d5-milestone-tracker.py
   ```

3. **Commit to hermes-brain**
   ```bash
   cd /root/repos/hermes-brain
   git add profiles/yoyo/home/.hermes/scripts/d5-milestone-tracker.py
   git commit -m "feat(cron): add D5 Milestone Tracker (consolidation of 4 jobs)"
   ```

4. **Update jobs.json** (after approval only)
   ```bash
   # Edit: /root/repos/hermes-brain/profiles/yoyo/cron/jobs.json
   # Remove old entries:
   #   - "YoYo — LP Fee Efficiency Monitor" (id: c2c2e40b440e)
   #   - "YoYo — Crypto Watchlist" (id: faed4f588aef)
   #   - "D5 Master Cron" (if exists)
   # Add new entry:
   #   {
   #     "id": "<new-uuid>",
   #     "name": "D5 Milestone Tracker",
   #     "schedule": {"expr": "15 8,12,16,20 * * *", "display": "15 8,12,16,20 * * *"},
   #     "script": null,  # Hermes auto-detects from profiles/yoyo/home/.hermes/scripts/
   #     "model": "kimi-k2.6"
   #   }
   ```

5. **Restart gateway**
   ```bash
   hermes gateway restart --profile yoyo
   ```

6. **Verify**
   ```bash
   # Check running jobs
   hermes gateway jobs --profile yoyo
   # Check state file updated
   ls -la /root/.hermes/profiles/yoyo/home/.hermes/scripts/.d5-lp-state.json
   ```

## Common Pitfalls

- **Script not executable**: Hermes gateway silently skips non-executable files
- **Wrong profile path**: Scripts must be under `profiles/<profile>/home/.hermes/scripts/` not just `profiles/<profile>/scripts/`
- **jobs.json syntax error**: Use JSON validator; malformed entries prevent ALL jobs from loading
- **Gateway not restarted**: Changes to jobs.json require gateway restart to take effect
- **State file location**: Scripts write state to `$HERMES_HOME/home/.hermes/scripts/` not the script directory itself

## Validation Checklist

- [ ] Script copied to hermes-brain with correct path
- [ ] File permissions: `-rwxr-xr-x` (755)
- [ ] jobs.json updated (old entries removed, new entry added)
- [ ] JSON syntax valid (`python -m json.tool jobs.json`)
- [ ] Hermes gateway restarted for profile
- [ ] First run produces Telegram message in Strategies group (-1002916759037)
- [ ] State file appears within 5 minutes

## Rollback

If deployment fails:
```bash
# 1. Restore old jobs.json from git
git checkout HEAD -- profiles/yoyo/cron/jobs.json
# 2. Restart gateway
hermes gateway restart --profile yoyo
# 3. Remove new script from hermes-brain (keep vault copy)
rm profiles/yoyo/home/.hermes/scripts/d5-milestone-tracker.py
```

---

*Session: 2026-05-02 — D5 Milestone Tracker consolidation*