# Admin Handoff Template — Google Workspace OAuth Whitelist

**To**: Workspace Admin  
**Subject**: `Google Workspace OAuth Whitelist Request — Hermes Email Integration`

---

## Request Summary

We need to enable third-party OAuth access for Gmail API via Hermes Agent. This requires whitelisting an OAuth 2.0 client ID in your Google Workspace security policy.

---

## Admin Action Required

**Location**: Google Admin Console → Security → API controls → Manage Third-Party App Access

**Steps**:
1. Click **"Add app"** → **"OAuth App Name or Client ID"**
2. Enter the **Client ID** (provided below)
3. Configure **OAuth scopes** (check all that apply):
   - `https://mail.google.com/` — Full Gmail access (send, delete, modify labels)
   - `https://www.googleapis.com/auth/gmail.readonly` — Read-only access (optional, if not using full scope)
4. Click **"Add"** → Wait 5–15 minutes for policy propagation

---

## Required Information

```
OAuth Client ID: <TO_BE_FILLED — extract from client_secret.json>
OAuth App Name: Hermes Agent — Gentech Labs
Redirect URIs: http://localhost:1 (Hermes local OAuth callback)
```

### How to extract Client ID

If you have the `client_secret_*.json` file:
```bash
grep -o '"client_id": "[^"]*"' /path/to/client_secret.json | cut -d'"' -f4
```

Or open the JSON in an editor and copy the `client_id` field value.

---

## Post-Whitelist Verification

After admin confirms whitelisting, run:

```bash
python ~/.hermes/profiles/dmob/skills/productivity/google-workspace/scripts/setup.py --check
```

Expected output: `AUTHENTICATED`

If it fails, wait 10 more minutes and retry — Workspace policy propagation can be slow.

---

## Troubleshooting for Admin

| Error Message | Likely Cause | Fix |
|---------------|-------------|-----|
| "setting not available for your account" | Client ID not whitelisted yet | Verify steps above; ensure you saved the app in Admin Console |
| "App not verified" (Testing mode) | OAuth app still in Testing phase and user not in test users list | Add the user's email as a Test User in Cloud Console → OAuth consent screen → Test users |
| "API not enabled" | Gmail API not enabled in GCP project | Enable Gmail API at https://console.cloud.google.com/apis/library |

---

## Fallback: Test User Bypass (if admin action blocked)

If you cannot access Admin Console (e.g., no admin privileges), add yourself as a **Test User** in the OAuth consent screen:

1. Google Cloud Console → APIs & Services → OAuth consent screen
2. Under **Test users**, add your Gmail address
3. Save → Retry Hermes OAuth flow

**Note**: This only works if the OAuth app is in **Testing** mode (not Production). Testing mode limits to 100 users.

---

## Contact

If issues persist after whitelisting, contact: **DMOB** (Gentech Labs — Head of Security & Tooling)
