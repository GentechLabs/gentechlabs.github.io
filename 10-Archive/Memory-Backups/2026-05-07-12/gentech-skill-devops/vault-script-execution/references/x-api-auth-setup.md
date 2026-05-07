# X API Authentication — Quick Setup (from May 3, 2026 session)

## Observed Failure
All `xurl` CLI calls returned 401 Unauthorized:
- `xurl whoami` → `{"title":"Unauthorized","status":401}`
- `xurl mentions` → same 401 JSON
- `xurl search "..."` → same 401 JSON

## Root Cause
No X Developer app registered, OAuth flow not completed, `~/.xurlrc` missing.

## Fix Sequence (for Jordan)

### 1. Create X Developer App
- URL: https://developer.x.com
- Create app with redirect URI: `http://localhost:8080/callback`
- Note: App name `gentech` (matches `xurl auth apps add gentech ...`)

### 2. Register App Credentials with xurl
```bash
xurl auth apps add gentech \
  --client-id <YOUR_CLIENT_ID> \
  --client-secret <YOUR_CLIENT_SECRET>
```

### 3. Complete OAuth Flow
```bash
xurl auth oauth2
```
This opens a browser window. Complete the authorization flow.

### 4. Verify Authentication
```bash
xurl whoami
```
Expected output: JSON with user info (id, username, name). NOT 401.

### 5. Test a Simple API Call
```bash
xurl mentions -n 5
```
Should return a JSON object with `data: [...]` (may be empty but status 200).

## Cost Post-Auth (X API Price Drop)
| Action | Cost per call | Estimated daily | Monthly |
|--------|---------------|----------------|---------|
| Timeline pull (100 posts) | $0.001 | $0.003 | $0.09 |
| Search 5 queries | $0.005 | $0.015 | $0.45 |
| Mentions check (50) | $0.001 | $0.003 | $0.09 |
| **Full daily monitoring** | — | **~$0.021** | **~$0.63** |

## Files Involved
- Config: `~/.xurlrc` (created by `xurl auth apps add`)
- Tokens: `~/.config/xurl/` or `~/.local/share/xurl/` (varies by install)
- No vault persistence needed — auth is per-machine user

## Activation Checklist (after auth works)
- [ ] `xurl whoami` succeeds
- [ ] `xurl mentions -n 5` returns 200 (even if empty)
- [ ] Social layer cron jobs can be activated by YoYo:
  - `x-morning-briefing` (7 AM UTC)
  - `x-feed-monitor` (every 2h)
  - `x-engagement-log` (10 PM UTC)

## Common Pitfalls
- **Redirect URI mismatch** — must exactly match `http://localhost:8080/callback` in dev app
- **Elevated/Access token scopes** — ensure app has `tweet.read`, `users.read`, `follows.read`
- **xurl not installed** — `pip install xurl` or check PATH: `which xurl`
- **Stale auth cache** — remove `~/.config/xurl/` and redo OAuth if confused state

## References
- Social layer script: `/root/vaults/gentech/03-Strategies/social-layer/scripts/engagement-monitor.sh`
- Social layer POC: `/root/vaults/gentech/03-Strategies/social-layer-poc/briefings/`
- Vault doc: `/root/vaults/gentech/03-Strategies/social-layer/SOCIAL-LAYER.md`
- This session: May 3, 2026 11:56 AM cron run
