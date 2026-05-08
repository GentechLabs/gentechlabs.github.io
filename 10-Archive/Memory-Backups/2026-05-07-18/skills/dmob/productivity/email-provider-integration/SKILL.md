---
name: email-provider-integration
description: "Multi-provider email integration patterns: Hermes OAuth (Google Workspace), Composio (managed OAuth), unified access wrappers, admin handoff templates."
version: 1.0.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  hermes:
    tags: [email, gmail, google-workspace, composio, oauth, integration]
    related_skills: [google-workspace]
---

# Email Provider Integration

Unified patterns for connecting multiple email accounts across different authentication backends — Hermes native OAuth vs third-party managed platforms (Composio, etc.).

## When to Use

- Need to access **multiple Gmail accounts** (Workspace + personal) in same workflows
- **Workspace admin consent delayed** → use alternative provider for testing
- Building **provider-agnostic email tools** that abstract auth differences
- Managing **OAuth client credentials** across environments

## Integration Patterns

### Pattern 1: Hermes OAuth (Google Workspace)
Use when: You control the Google Cloud project, admin has whitelisted your OAuth client, need long-term production access.

**Setup**: `google-workspace` skill → manual OAuth flow with client secret JSON → token stored at `~/.hermes/google_token.json`

**Pros**: No third-party dependency, full scope control, works offline after auth
**Cons**: Admin approval required, manual token refresh edge cases, per-service OAuth setup

### Pattern 2: Composio (Managed OAuth)
Use when: Admin consent blocked, testing with personal accounts, need multiple provider integrations (Slack, Notion, etc.) in one platform.

**Setup**: `COMPOSIO_API_KEY` env var → `composio.tools.execute()` calls → OAuth handled by Composio platform

**Pros**: No GCP project needed, instant OAuth for personal accounts, centralized audit logs
**Cons**: Platform dependency, token stored on Composio servers, rate limits on free tier

### Pattern 3: Hybrid (Dual Accounts)
Run both in parallel: Workspace via Hermes (production) + Personal via Composio (sandbox).

**Use case**: Develop/test email workflows without risking primary inbox operations.

## Unified Wrapper Architecture

```python
class EmailProvider:
    def send(self, to, subject, body): ...
    def fetch(self, query, max_results): ...
    def delete(self, message_id): ...

class HermesGmail(EmailProvider):  # wraps google-workspace skill
    ...

class ComposioGmail(EmailProvider):  # wraps Composio SDK
    ...

# Factory picks provider by alias
def get_email_provider(alias='workspace'):
    if alias == 'workspace': return HermesGmail()
    if alias == 'personal': return ComposioGmail()
```

See `templates/unified_email_wrapper.py` for starter implementation.

## Workspace Admin Handoff Template

When OAuth consent is blocked, send admin this:

**Subject**: `Google Workspace OAuth Whitelist Request — [Your App Name]`

**Body**:
```
We need to whitelist an OAuth 2.0 client for Gmail API access.

Client ID: <EXTRACT_FROM_OAUTH_JSON>
OAuth Scopes Required:
  - https://mail.google.com/ (full Gmail access — send, delete, modify labels)
  - https://www.googleapis.com/auth/gmail.readonly (if read-only is sufficient)

Steps for admin:
1. Google Admin Console → Security → API controls → Manage Third-Party App Access
2. Click "Add app" → "OAuth App Name or Client ID"
3. Paste the Client ID above
4. Set scopes (check both boxes if using full+readonly)
5. Save → Wait 5–15 minutes for propagation

→ After whitelisting, re-run: python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

See `references/admin_handoff_template.md` for full version with troubleshooting.

## Scopes Matrix

| Capability | Hermes Scope | Composio Scope |
|------------|--------------|----------------|
| Read emails | `gmail.readonly` | Granted automatically |
| Send emails | `mail.google.com` | Granted automatically |
| Delete/Trash | `mail.google.com` | Granted automatically |
| Modify labels | `gmail.modify` | Granted automatically |
| Create labels | `gmail.labels` | Granted automatically |

**Note**: Hermes requires explicit scope selection during OAuth; Composio requests all Gmail scopes by default.

## Troubleshooting

### Hermes: "NOT_AUTHENTICATED"
Cause: No token file at `~/.hermes/google_token.json`
Fix: Run full OAuth setup: `setup.py --client-secret <JSON> → --auth-url → --auth-code`

### Hermes: "HttpError 403: Access Not Configured"
Cause: Gmail API not enabled in Google Cloud project
Fix: Enable Gmail API + Calendar/Drive APIs in GCP Console → API Library

### Composio: "Link failed" or "access_denied"
Cause: User not added as test user (if OAuth app in Testing mode)
Fix: Go to https://console.cloud.google.com/auth/audience → add test user → retry

### Workspace: "setting not available for your account"
Cause: Admin hasn't whitelisted OAuth client
Fix: Send admin handoff (see template above) → wait for policy propagation

## Security Notes

- **Never** store `client_secret.json` or `COMPOSIO_API_KEY` in source code
- Use **dedicated service accounts** for production automations (not personal inbox)
- **Rotate credentials** quarterly or after team member departure
- **Audit logs**: Hermes — local token only; Composio — dashboard audit trail available

## References

- `references/admin_handoff_template.md` — full admin handoff with Client ID extraction
- `references/composio_oauth_troubleshooting.md` — Composio-specific OAuth errors and fixes
- `templates/unified_email_wrapper.py` — provider-agnostic email client starter
- `scripts/create_hermes_oauth.py` — generate OAuth client credentials in GCP (automated)

## Related

- `google-workspace` skill (Hermes native OAuth implementation)
- Composio documentation: https://github.com/ComposioHQ/composio
