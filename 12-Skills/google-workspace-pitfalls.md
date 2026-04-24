# Google Workspace Setup — Pitfalls Learned (Apr 18, 2026)

## Issues Encountered

### 1. `--services` and `--format` flags don't exist
The setup.py script does NOT support `--services` or `--format` flags.
Running `$GSETUP --auth-url --services sheets,drive --format json` fails with:
`error: unrecognized arguments: --services sheets,drive --format json`

**Fix:** Just use `$GSETUP --auth-url` — it requests all scopes by default.

### 2. Client secret JSON format
When user provides raw client_id/client_secret (not a file), you must create
a FULL Desktop OAuth JSON with `auth_uri` and `token_uri`:
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost"]
  }
}
```
Without these fields: `ValueError: Client secrets is not in the correct format.`

### 3. "Access blocked" error
If Google returns "Access blocked: This app's request is invalid":
- Add user as test user: https://console.cloud.google.com/auth/audience
- OR publish the app (no review needed for personal use)

### 4. Redirect URI must be `http://localhost`
The library uses `http://localhost:1` internally. Cloud Console needs just
`http://localhost` in authorized redirect URIs (not a custom port/path).

---
*These pitfalls should be patched into the google-workspace skill but security
scan blocked the edit. Keeping here as reference.*
