# 2026-05-05 — Missing System User Configuration (desmond)

**Skill context**: `agent-health-audit` — Phase 1 Process Liveness Verification

## What happened

During fleet health check (May 5, 2026), the command `id desmond` returned:
```
id: ‘desmond’: no such user
```

Yet `systemctl --user status hermes-gateway-desmond.service` showed **active (running)** and `ps aux` displayed a Python gateway process claimed to be for the `desmond` profile.

## Root cause

The Desmond agent's gateway process was **not running under the `desmond` system user account**. Possible scenarios:

1. **Manual launch by root or another user**: The gateway was started with `sudo` or directly from a root shell using `--profile desmond` without `sudo -u desmond`. This breaks systemd user isolation and may cause credential/env-var mismatches.
2. **System user was deleted after deployment**: The `desmond` user existed initially but was later removed (e.g., cleanup, migration error), leaving the service unit and process running under a now-defunct user context.
3. **Profile created without corresponding system user**: Some Hermes setups don't strictly require per-agent system users if all agents run under a single service account. However, the observed `sudo: unknown user desmond` errors across multiple check attempts confirm the user is missing system-wide.

## Why this matters

- **Systemd user units rely on the user account**: `hermes-gateway-desmond.service` is a **user unit** stored in `/root/.config/systemd/user/` (root's home) but is typically managed under the agent's own user. When the user is missing, `systemctl --user` as that user is impossible; all management falls back to root or the service becomes orphaned.
- **Credential isolation broken**: If the process runs as root but the profile directory is `/root/.hermes/profiles/desmond`, root's access to that directory may be fine, but **environment variables** (like `HERMES_HOME`) may not be set as expected for the `desmond` profile context.
- **Future restart fragility**: Without a valid system user, `systemctl --user restart hermes-gateway-desmond.service` run as the non-existent user will fail. The gateway can only be restarted manually by root with explicit `HERMES_HOME` and environment setup.
- **Audit confusion**: Process listing shows a running gateway, but `sudo -u desmond crontab -l` fails with "unknown user" — indicating cron jobs (if any) cannot be managed per-user. This agent likely uses **Hermes internal cron** (inside gateway) rather than system crontab, which is correct given the user absence, but still signals misalignment.

## Detection

As part of **any agent health check**, add this early filter:

```bash
if ! id <agent> &>/dev/null; then
  echo "⚠️  System user '<agent>' missing"
  echo "   → Gateway may be running under wrong user or orphaned"
  echo "   → Check launch context: ps -o user,pid,cmd -p $(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid)"
fi
```

If the user is missing but a gateway process exists, verify the **actual process owner**:
```bash
ps -o user,pid,cmd -p $(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid)
```

Expected healthy state: process owner matches the agent's system user (e.g., `desmond`). If owner is `root`, this is a **configuration violation**.

## Recovery options

**Option A — Recreate the system user** (restores normal systemd supervision):
```bash
useradd -m -s /bin/bash desmond  # or appropriate shell
# Re-link profile directory if needed
usermod -d /root/.hermes/profiles/desmond desmond
# Restart via systemd as the correct user
sudo -u desmond systemctl --user daemon-reload
sudo -u desmond systemctl --user restart hermes-gateway-desmond.service
```

**Option B — Convert to manual-run profile** (accept root-launched):
If the design intentionally runs all agents under root (single-user deployment), then:
- Document this exception in the agent's profile notes
- Ensure `HERMES_HOME` is exported correctly when launching manually
- Manage lifecycle via supervisor (systemd global unit or process manager) rather than per-user units
- Remove per-agent systemd user units to avoid confusion

**Option C — Normalize to single-user deployment** (if all agents run as root):
If the fleet intentionally runs all gateways as root, fix the health-audit logic to skip `id <agent>` checks for known single-user deployments. Add a flag in agent config (e.g., `launch.user_mismatch_expected: true`) to suppress false positives.

## Related findings

This discovery coincided with:
- **Zero cron output** in Desmond's `cron/output/` (directory empty)
- **Cron daemon lifecycle markers**: `Cron ticker stopped` appearing in logs while gateway process still running
- **Auth errors**: `Refresh session has been revoked` and `Model 404` errors across all agents

The missing user is likely a **symptom of a broader deployment/restart event** (possibly an incomplete migration or manual kill-restart cycle that lost user context).

## Preventive checklist

- [ ] All agent usernames documented in deployment manifest
- [ ] Each agent's systemd user unit file references correct `User=` account (if using system slices)
- [ ] `id <agent>` succeeds on all target hosts
- [ ] Profile directory ownership matches: `ls -ld /root/.hermes/profiles/<agent>` should be owned by that user
- [ ] Gateway processes show matching user in `ps` output (`ps -o user,cmd -p <pid>`)

## Follow-up required

- Determine **how** Desmond's gateway was launched (systemd vs manual)
- Check for other agents with missing users (`id yoyo`, `id dmob`, `id gentech`)
- If system-wide user deletion occurred, restore all affected accounts or migrate to single-user operation consistently
- Update the health-audit skill to include **user-existence pre-check** as a mandatory Phase 1.5 step before process validation
