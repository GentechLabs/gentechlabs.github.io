# Cron Non-Interactive Auth Recovery Limitation — 2026-05-06 Incident

**Incident Date:** 2026-05-06  
**Detected:** During scheduled Gentech Watchdog run  
**Impact:** Nous Portal OAuth refresh failed with "Refresh session has been revoked"  
**Root Cause:** Refresh token fully revoked; cannot recover via `hermes model` in cron context  

## Executive Summary

During a routine scheduled cron job (Gentech Watchdog), the Nous Portal OAuth token refresh failed with the message: "Refresh session has been revoked". This triggered the standard auth incident response playbook, but it was discovered that **`hermes model` cannot be executed in a non-interactive cron environment** due to terminal (TTY) requirements. This creates a situation where manual intervention is the **only** recovery path when device flow is unavailable.

## Key Discovery

### `hermes model` Requires an Interactive Terminal

The `hermes model` command (and `hermes auth add`) require an interactive terminal to complete the OAuth flow. When running in a scheduled cron job context:
- There is no TTY available
- The command fails with: "Error: 'hermes model' requires an interactive terminal. It cannot be run through a pipe or non-interactive subprocess. Run it directly in your terminal instead."

This means that **cron jobs cannot recover from certain OAuth failures autonomously**. Manual intervention by a user with interactive access is required.

## Timeline of Events

- **2026-05-06 14:00 UTC**: Gentech Watchdog cron job runs
- **Pre-run script** detects: `{"success": false, "message": "Refresh session has been revoked Run `hermes model` to re-authenticate.", "needs_reauth": true}`
- Attempt to run `hermes model` directly fails due to non-interactive environment
- Attempt to use `hermes auth add` also fails for same reason
- Conclusion: Manual re-authentication required

## Technical Details

### Error Messages Observed

```json
{
  "success": false,
  "message": "Refresh session has been revoked Run `hermes model` to re-authenticate.",
  "tokens": {},
  "needs_reauth": true,
  "critical": false,
  "hermes_home": "/root/.hermes/profiles/gentech"
}
```

### Commands Attempted

```bash
hermes model  # Failed — requires interactive terminal
hermes auth add nous  # Failed — requires interactive terminal
```

### Root Cause Analysis

The OAuth refresh token had been fully revoked (likely due to expiration or explicit revocation). The refresh script (`refresh_nous_oauth.py`) detected this and returned `needs_reauth: true`, indicating that manual re-authentication is required.

However, in a cron environment:
- No TTY is available
- `hermes model` cannot be executed
- `hermes auth` commands cannot be completed

Thus, **the recovery path is blocked** until a human operator intervenes with an interactive terminal session.

## Implications

1. **Cron jobs have a single point of failure for OAuth-based providers** when refresh tokens are fully revoked
2. **Manual intervention is required** for certain auth failures, even with proactive refresh scripts scheduled
3. **Monitoring must be enhanced** to detect when cron jobs are stuck in `needs_reauth` state
4. **Future automation** should consider fallback providers that use API keys rather than OAuth to avoid this limitation

## Recommended Mitigations

### 1. Add API-Key-Based Fallback Providers (Critical)

Ensure all Hermes profiles have at least one API-key-based fallback provider configured:

```yaml
model:
  provider: auto
fallback_providers:
  - ollama-cloud
  - opencode-go
```

This allows the system to fall back to an alternative provider when the primary OAuth provider is unavailable, though it won't fix the original auth issue.

### 2. Enhance Gentech Watchdog Monitoring

Update the Watchdog to:
- Check cron job output for `needs_reauth: true` in JSON payloads
- Detect when refresh scripts are failing but exit code is 0 (the "exit code 0 trap")
- Alert on cron jobs that are stuck in failed auth state

### 3. Document the Limitation Clearly

This reference file documents the specific limitation discovered during this incident. The `hermes-auth-incident-response` skill has been updated to include this caveat in the Incident Declaration Checklist.

### 4. Consider Alternative Authentication Flows

For future integrations, explore whether device flow can be completed programmatically without browser interaction, or if refresh tokens can be managed in a way that avoids full revocation requiring interactive re-auth.

## Lessons Learned

- **Cron jobs cannot run `hermes model`** — this is a fundamental limitation
- **OAuth refresh failures may require human intervention** in scheduled automation
- **Monitoring must look beyond exit codes** and parse JSON output for `needs_reauth: true`
- **Cross-profile token sharing** exacerbates the impact (all profiles affected simultaneously)

## Follow-Up Actions

- [ ] @DMOB: Run `hermes model` to re-authenticate Nous Portal
- [ ] @DMOB: Verify refresh script success after re-auth
- [ ] @DMOB: Update all profiles' `config.yaml` to add fallback providers
- [ ] @Gentech: Enhance Watchdog to detect cron auth failures
- [ ] @Gentech: Document this incident in the operations log

## Related Resources

- `hermes-auth-incident-response/SKILL.md` — Updated with this limitation
- `references/auth-incident-post-mortem-2026-05-04.md` — Earlier post-mortem
- `references/hermes-home-path-quirk-2026-05-03.md` — Related path resolution issue
- `references/device-code-rate-limiting-2026-05-06.md` — Rate limiting considerations

**Prepared:** 2026-05-06 14:30 UTC  
**Next Steps:** Complete manual re-authentication and verify recovery