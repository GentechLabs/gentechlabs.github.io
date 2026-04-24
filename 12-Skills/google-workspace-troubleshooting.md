# 🔧 Google Workspace OAuth — Troubleshooting Notes

**Discovered:** 2026-04-18 (Desmond × Jordan session)

## Pitfall 1: Client Secret Format

When users provide raw Google OAuth credentials (client_id, client_secret), you MUST write the JSON in `"web"` format, NOT `"installed"`:

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_SECRET",
    "redirect_uris": ["http://localhost:1"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

**Error if wrong:** `ValueError: Client secrets is not in the correct format`
**Root cause:** `Flow.from_client_secrets_file()` requires `"web"` key for localhost redirect flow

## Pitfall 2: Redirect URI Mismatch

The setup script hardcodes `REDIRECT_URI = "http://localhost:1"`. Google rejects auth if this isn't in the OAuth client's Authorized Redirect URIs.

**Error if wrong:** `Access blocked: This app's request is invalid`
**Fix:** Add `http://localhost:1` to Authorized Redirect URIs in Google Cloud Console
**URL:** https://console.cloud.google.com/apis/credentials

## Setup Flow (Verified Working)

1. Write client secret JSON in `"web"` format → save to `/opt/hermes-agents/desmond/google_client_secret.json`
2. Run: `python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret /path/to/secret.json`
3. Run: `python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url`
4. Send URL to user → they approve → copy redirect URL
5. Run: `python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "THE_CODE"`
6. Verify: `python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

## Jordan's Credentials
- Client ID: `211758782528-9i5p6a8or9ct9gmr0loudhqfji2a535f.apps.googleusercontent.com`
- Status: Pending — needs `http://localhost:1` added to redirect URIs in GCP
- Morning checklist: `08-Daily/morning-checklist.md` has the setup steps
