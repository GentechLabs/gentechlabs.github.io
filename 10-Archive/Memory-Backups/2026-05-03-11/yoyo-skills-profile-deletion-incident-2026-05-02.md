# Profile Deletion Incident — Forensic Analysis (May 2, 2026)

## Incident Summary

On May 2, 2026, a profile deletion/recovery event affected all four Gentech agents:

| Agent | Status During Incident | Recovery Time | Notes |
|-------|----------------------|---------------|-------|
| yoyo | Down 15:38–20:17 | ✅ Restored | Restarted via systemd at 20:17 |
| dmob | Down 15:38–20:17 | ✅ Restored | Restarted via systemd at 20:17 |
| desmond | Down 15:38–20:17 | ✅ Restarted | Restarted via systemd at 20:17 |
| gentech | **Up entire time** (PID 1118093) | ⚠️ Degraded | Gateway ran continuously since 15:39; home directory minimal after recovery |

**Downtime:** ~4h 40m (15:38–20:17) for yoyo/dmob/desmond. Gentech nominally "up" but likely operating with corrupted/missing profile data.

## Root Cause: One-Way Backup Sync & Missing Restore Path

** backup.sh behavior:**
- **Direction:** `live profiles → hermes-brain repo` only (push)
- **Missing:** `hermes-brain repo → live profiles` (pull/restore)
- **Impact:** If local profiles are deleted (accident, bug, or manual `hermes profile delete`), they are **NOT** automatically rebuilt from the canonical brain repo.

**Trigger event (~15:38–15:39):**
- All three agents (yoyo, dmob, desmond) shut down simultaneously (gateway.log shows last activity at 15:38:39-15:38:42)
- Profile directories for those agents appear to have been removed/cleared between 15:38–15:39, then partially restored at 20:17
- Gentech profile was **never deleted** — it was running as a systemd-managed service and remained alive through the incident

**Recovery action (~20:17):**
- Systemd auto-restarted yoyo/dmob/desmond gateways (services `hermes-gateway-*.service` with `Restart=on-failure`)
- Profile data reappeared (state.db files restored) — source unknown, but not from backup.sh (brain repo was not modified between 12:00 and 18:00)
- All four gateways reported `✓ telegram connected` by 20:17–20:25

## Forensic Detection Methodology

This incident was identified through **timestamp forensics** and **process correlation**:

### 1. Gateway日志 timestamp gaps
```bash
# yoyo/dmob/desmond: last pre-gap entry at ~15:38, next entry at 20:17
# gentech: continuous entries from 15:38 through 20:40 with no gap
```
This revealed that three agents stopped abruptly while gentech kept running.

### 2. Profile directory mtime vs. content staleness
```bash
# Profiles showed:
yoyo: state.db mtime May 2 15:37 (older than 20:17 restart)
dmob: state.db mtime May 1 10:01 (much older)
desmond: state.db mtime May 2 13:25 (older)
gentech: state.db mtime May 2 20:00 (fresh)
```
Even after restarts, the yoyo/dmob/desmond state.db files had **pre-incident timestamps**, indicating either:
- StateDB was not rewritten on restart (cached/stale), OR
- The files were restored from an older snapshot

### 3. Systemd service status correlation
```bash
systemctl --user status hermes-gateway-yoyo.service
# shows Active: active (running) since 20:17:25
```
Confirming the restart time from process supervisor.

### 4. Git repo history check
```bash
cd /root/repos/hermes-brain
git log --oneline --since="1 hour ago"   # shows commit at 14:36
git reflog                               # reveals any reset/pull activity
```
The brain repo showed **no changes between 12:00 and 18:00**, confirming the recovery did **not** come from the brain backup repo.

### 5. backup.sh log analysis
brain-backup.log entries:
- 06:01 — push from live → brain
- 12:00 — push from live → brain (profiles still present at that time)
- 18:00 — push from live → brain (after recovery; pushed restored state)

No restore operation appears in backup logs. The recovery must have come from:
- A manual copy from another location
- An ad-hoc script not in `/root/scripts/`
- Systemd unit ExecStartPre/ExecStartPost actions
- Or a one-off `hermes profile clone` or `hermes brain restore` command run manually

## Key Observations

### Gentech's anomalous uptime
- PID 1118093 has been running since **15:39:40** (5+ hours) while others restarted at 20:17
- This process survived whatever event killed the other three gateways
- **Hypothesis:** The event targeted the **profile directories**, not the processes. Gentech's running process kept memory state; after profile deletion, it continued operating with open file handles to deleted inodes (still functional for existing sessions, but new sessions would fail once those handles closed or were needed)
- Gentech's gateway.log shows continuous message handling through 20:40, suggesting it was still partially functional

### Profile deletion mechanism (unknown)
The exact cause of the deletion was not identified in code review:
- No `hermes profile delete` invocation found in logs or scripts
- No `shutil.rmtree(profile_dir)` in update/restore code paths
- Possible scenarios:
  1. **Manual deletion** (`rm -rf ~/.hermes/profiles/{yoyo,dmob,desmond}`) unintentionally
  2. **Misbehaving maintenance script** (backup.sh variant, brain restore script, brain prune script)
  3. **Hermes brain sync operation** with `--clean` or `--reset` flag (not in current backup.sh)
  4. **Profile migration/move** operation that moved rather than deleted (but destination unknown)

### State.db presence but stale
After recovery, yoyo/dmob/desmond all have `state.db` files, but sizes and mtimes suggest they may be **older restored versions**, not freshly generated:
- yoyo: 114MB, mtime 15:37 (pre-deletion)
- dmob: 20MB, mtime May 1 (day-old)
- desmond: 18MB, mtime 13:25 (pre-deletion)
- gentech: 130MB, mtime 20:00 (fresh)

This implies restoration from a **pre-deletion backup** (possibly from brain repo's earlier state or from the May 1 dmob backup).

## Recovery Checklist (When Profiles Are Missing)

**Step 1 — Confirm profile loss:**
```bash
ls -la ~/.hermes/profiles/
# Look for: empty directories, missing state.db, missing home/.hermes
```

**Step 2 — Check brain repo for canonical profiles:**
```bash
ls -la /root/repos/hermes-brain/profiles/
# All four agent directories should exist with state.db, config.yaml, SOUL.md
```

**Step 3 — Restore from brain repo (if present):**
```bash
# Stop all gateways first
for a in yoyo dmob desmond gentech; do
  systemctl --user stop hermes-gateway-$a.service 2>/dev/null || true
done

# Copy missing profile data from brain repo
rsync -a /root/repos/hermes-brain/profiles/yoyo/   ~/.hermes/profiles/yoyo/
rsync -a /root/repos/hermes-brain/profiles/dmob/   ~/.hermes/profiles/dmob/
rsync -a /root/repos/hermes-brain/profiles/desmond/ ~/.hermes/profiles/desmond/
rsync -a /root/repos/hermes-brain/profiles/gentech/ ~/.hermes/profiles/gentech/

# Ensure correct ownership
chown -R root:root ~/.hermes/profiles/

# Restart services
for a in yoyo dmob desmond gentech; do
  systemctl --user start hermes-gateway-$a.service
done
```

**Step 4 — Verify restoration:**
```bash
# Check state.db exists and is non-empty in each profile
for a in yoyo dmob desmond gentech; do
  stat -c '%s %n' ~/.hermes/profiles/$a/state.db
done

# Check gateway logs for successful startup (last 20 lines)
tail -20 ~/.hermes/profiles/yoyo/logs/gateway.log | grep '✓ telegram connected'
```

## Prevention: Add a Restore Mechanism to backup.sh

Current backup.sh only **pushes** to brain. Add a companion `restore.sh`:

```bash
#!/usr/bin/env bash
# Hermes Brain Restore — recover profiles from canonical repo
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/root/.hermes}"
REPO_DIR="/root/repos/hermes-brain"
LOG_FILE="/root/.hermes/logs/brain-restore.log"

log() { echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*" | tee -a "$LOG_FILE"; }

log "=== Brain Restore Start ==="

# Stop all gateways first
for agent in yoyo dmob desmond gentech; do
  systemctl --user stop hermes-gateway-$agent.service 2>/dev/null || true
done

# Restore each profile from repo
for profile in yoyo dmob desmond gentech; do
  if [ -d "$REPO_DIR/profiles/$profile" ]; then
    log "Restoring $profile from brain repo..."
    mkdir -p "$HERMES_HOME/profiles/$profile"
    rsync -a --delete "$REPO_DIR/profiles/$profile/" "$HERMES_HOME/profiles/$profile/"
  else
    log "⚠ Profile $profile not found in brain repo — skipping"
  fi
done

# Restart gateways
for agent in yoyo dmob desmond gentech; do
  systemctl --user start hermes-gateway-$agent.service
done

log "=== Brain Restore Complete ==="
```

**Schedule:** Add a weekly dry-run verify that brain repo contains all expected profiles:
```bash
0 6 * * 0 /root/scripts/verify-brain-profiles.sh >> /root/.hermes/logs/brain-verify.log 2>&1
```

## Open Questions

1. **What triggered the profile deletion?** No smoking gun found in code or logs. Could be human error (`rm -rf`) on the command line, or a script outside the examined paths (`/root/scripts/`, hermes-agent code).
2. **Why did Gentech's process survive?** Because it was launched by systemd (`hermes-gateway-gentech.service`) with `Restart=on-failure`; the process itself didn't crash, so systemd had no reason to kill/restart it. The other three were running under manual `hermes gateway run` commands or a different supervisor that exited, triggering the restart cascade.
3. **How were profiles restored?** Not via backup.sh (brain repo unchanged). Likely a manual copy from a snapshot or from Gentech's still-populated home (it had `profiles/` symlink? Actually Gentech home had a `profiles/` directory — possibly the other profiles were copied from there).

## Procedure for Future Incidents

1. **Immediate check:** Are all four gateway processes running? (`ps aux | grep hermes`)
2. **Check profile directory integrity:** `ls -la ~/.hermes/profiles/*/state.db`
3. **Compare with brain repo:** `diff -r ~/.hermes/profiles/yoyo/ /root/repos/hermes-brain/profiles/yoyo/` (quick check)
4. **If profiles missing/empty:** Use the restore script above (or manual rsync from brain)
5. **Verify:** `tail -20 ~/.hermes/profiles/<agent>/logs/gateway.log` for `✓ telegram connected`
6. **Post-mortem:** Check `~/.bash_history` for accidental `rm -rf` commands around the incident time; audit `/root/scripts/` for any destructive operations.

---

**Related:** `gentech-agent-reactivation` skill covers broader agent restart scenarios; this reference focuses specifically on **profile directory loss** and **brain↔live sync asymmetry**.
