# OAuth Session Revocation Recovery — Reference

**Date observed:** 2026-05-03  
**Affected components:** All Hermes profiles (YoYo, DMOB, Desmond, Gentech)  
**Root cause:** Nous Portal OAuth refresh token revoked/invalidated  

## Error Patterns

- Cron job `Nous OAuth Proactive Refresh` fails with:
  ```
  RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate.
  ```
- Agent error logs (last 30 min) show thousands of:
  ```
  RuntimeError: Refresh session has been revoked
  openai.AuthenticationError: Error code: 401
  elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
  ```
- Gateway receives messages but cannot process due to auth failures.

## Detection Commands

```bash
# Check cron registry for failing OAuth job
hermes cron list | grep -i 'oauth'

# Count recent auth errors per agent (last 20 min)
for agent in yoyo dmob desmond gentech; do
  echo "$agent:"
  grep -i "refresh session has been revoked" ~/.hermes/profiles/$agent/logs/errors.log | wc -l
done

# Check gateway process status
systemctl --user status hermes-gateway-*

# View latest errors
tail -5 ~/.hermes/profiles/gentech/logs/errors.log
```

## Recovery Procedure

1. Re-authenticate each profile with Nous Portal:
   ```bash
   hermes model   # select Nous Portal provider, complete OAuth flow
   # or explicitly
   hermes login --provider nous
   ```

2. Restart each gateway to clear stale auth state:
   ```bash
   hermes gateway restart --profile yoyo
   hermes gateway restart --profile dmob
   hermes gateway restart --profile desmond
   hermes gateway restart --profile gentech
   ```

3. Verify the OAuth refresh job succeeds on next tick (every 10 minutes):
   ```bash
   hermes cron list | grep -A2 'Nous OAuth'
   ```

4. Confirm credentials are active:
   ```bash
   hermes auth list
   ```

## Pitfalls

- Do NOT delete `~/.hermes/auth.json` — this loses all OAuth tokens. Use `hermes logout` before re-auth if needed.
- The `refresh_nous_oauth.py` script cannot recover from a revoked session; manual `hermes model` is mandatory.
- If `hermes model` does not prompt for Nous Portal, run `hermes login --provider nous` directly.
- After recovery, monitor for recurring revocations — may indicate credential pool exhaustion or compromised tokens.

## Related

- SKILL.md section: "### OAuth session revocation (fleet-wide)"
- Cron job script: `/usr/local/lib/hermes-agent/scripts/refresh_nous_oauth.py` (or profile-local copy)
- Nous Portal: https://portal.nousresearch.com