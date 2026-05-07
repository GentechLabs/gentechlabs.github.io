---
name: auth-bypass-patterns
description: Systematic patterns for bypassing or working around OAuth/auth blocks during time-constrained development (hackathons, debugging, production incidents).
version: 1.0.0
author: Desmond (Gentech Creative)
license: MIT
---

# Auth Bypass Patterns

## When to Use

Use these patterns when you hit an auth blocker that would stall development and:
- **Hackathon/Time-boxed build** — Can't wait days for admin approval
- **Production incident** — Authentication failure blocking critical path
- **Testing/Dev environment** — Need to test flows without full OAuth setup
- **Third-party dependency delays** — Vendor hasn't approved your OAuth client yet

**Golden rule:** Auth debt should never block product logic validation. Use bypass patterns to keep building, then circle back to proper auth later.

---

## Pattern 1: Parallel Dual-Account (The Composable Workaround)

**Scenario:** Your primary account (Workspace, Enterprise, Org) has OAuth restrictions that require admin approval. Timeline: 2–5 business days. You need to test auth-dependent features immediately.

**Solution:** Run two accounts in parallel:
1. **Primary account** — Target production account (may be blocked). File the admin request, but don't wait.
2. **Secondary account** — Personal/test account with no restrictions. Connect through a managed OAuth provider (Composio, Clerk, Supabase Auth) or direct API if unrestricted.

**Implementation:** See `templates/service-dual-account-template.py` for a complete ready-to-copy implementation.

```python
class ServiceFactory:
    @staticmethod
    def create_gmail(mode: str = "auto"):
        """
        mode: "workspace" | "composio" | "auto"
        auto: try workspace first, fall back to composio
        """
        if mode == "auto":
            try:
                return GmailWorkspace()  # may raise auth error
            except AuthBlockedError:
                log("Workspace blocked — falling back to Composio")
                return GmailComposio()

        elif mode == "workspace":
            return GmailWorkspace()
        elif mode == "composio":
            return GmailComposio()
```

**Benefits:**
- ✅ Test immediately without waiting
- ✅ Keep primary account integration code path intact
- ✅ Easy switch-over when admin approves
- ✅ Documented fallback for production resilience

**Risks:**
- ⚠️ Data segregation — test emails won't match production account
- ⚠️ Scope differences — personal accounts may have different permissions
- ⚠️ Cost — managed providers may charge for parallel usage

**Mitigations:**
- Add metadata tagging: `X-Test-Account: true` header/flag
- Document scope differences in README
- Use test data, not real user data, in dev

**Real example from AgentEscrow:**
- Workspace (blocked): Direct Google API, admin consent pending
- Personal (working): Composio managed OAuth, fully functional
- Decision: Ship MVP with Composio, defer Workspace integration

---

## Pattern 2: Mocked Auth Layer

**Scenario:** You need to test auth-dependent logic but the actual OAuth provider is down, slow, or has rate limits.

**Solution:** Abstract auth behind an interface and inject a mock implementation for development.

```python
class AuthProvider(Protocol):
    def get_user_email(self) -> str: ...
    def verify_token(self, token: str) -> bool: ...

class GoogleWorkspaceAuth(AuthProvider):
    # Real implementation
    pass

class MockAuth(AuthProvider):
    def __init__(self, test_user="test@example.com"):
        self.test_user = test_user

    def get_user_email(self) -> str:
        return self.test_user

    def verify_token(self, token: str) -> bool:
        return True  # Accept all tokens in dev
```

**Configuration:**
```bash
# .env.development
AUTH_PROVIDER=mock
MOCK_AUTH_EMAIL=dev@example.com

# .env.production
AUTH_PROVIDER=google-workspace
```

**Benefits:** No external dependencies during development; deterministic; fast.

**Caveat:** Must have at least one integration test against real provider before shipping.

---

## Pattern 3: Service Token Bypass (Service Accounts)

**Scenario:** OAuth user consent flow is blocked, but your use case is server-to-server (no user interaction). Common for cron jobs, batch processing, CI/CD.

**Solution:** Use service account credentials instead of user OAuth.

```python
# Instead of user OAuth with consent screen:
creds = Credentials.from_authorized_user_file("token.json")

# Use service account (no user consent needed):
from google.oauth2 import service_account
creds = service_account.Credentials.from_service_account_file(
    "service-account.json",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"]
)
```

**Prerequisites:**
- Service account must be created in Google Cloud Console
- Domain-wide delegation may be needed for Workspace (admin must grant scopes to service account)
- Still requires admin action in Workspace, but different path: Security → API Controls → Domain-wide Delegation

**When it fails:** If admin has disabled API access entirely, service accounts won't work either.

---

## Pattern 4: Local Proxy / Tunnel

**Scenario:** External API is blocked by corporate firewall, geo-restriction, or IP allowlist.

**Solution:** Route through a proxy server or tunnel that has access.

```python
# Before (blocked):
requests.get("https://api.service.com/data")

# After (proxied):
proxies = {"https": "http://localhost:8080"}  # local tunnel
requests.get("https://api.service.com/data", proxies=proxies)
```

**Tools:**
- `ngrok` — Expose local server to internet
- `cloudflared` — Cloudflare Tunnel
- Self-hosted squid proxy

**Use case:** Testing webhook delivery from external service to localhost.

---

## Pattern 5: Temporary Scope Narrowing

**Scenario:** Your OAuth client requested broad scopes (e.g., `gmail.modify`), triggering admin review. You need *any* access now, full access later.

**Solution:** Re-register OAuth client with minimal scopes that still let you test core flow.

Example:
- Original scopes: `gmail.readonly gmail.modify gmail.send` → triggers review
- Narrowed scopes: `gmail.readonly` → may auto-approve

**Trade-off:** Can only test read operations until scopes expanded. But that's often enough to validate architecture.

**Process:**
1. Create separate OAuth client ID for development
2. Request only `gmail.readonly`
3. Once approved, request scope expansion for production client

---

## Decision Tree

```
OAuth Blocked?
│
├─ Is this a hackathon/time-critical? ──YES─▶ Use Pattern 1 (Dual-Account)
│                                            │
│                                            └─▶ Use managed OAuth (Composio/Clerk) for dev account
│
├─ Is this for testing/CI only? ──YES─▶ Use Pattern 2 (Mock Auth)
│
├─ Is this server-to-server (no user)? ──YES─▶ Use Pattern 3 (Service Account)
│
├─ Is this a network/firewall block? ──YES─▶ Use Pattern 4 (Proxy/Tunnel)
│
└─ Are scopes too broad triggering review? ──YES─▶ Use Pattern 5 (Scope Narrowing)
```

---

## Pitfalls & Gotchas

### Pitfall 1: Forgetting to Switch Back
**Symptom:** Production deploys with mock auth or test credentials.

**Fix:** Enforce environment-based configuration with CI check:
```yaml
# .github/workflows/deploy.yml
- name: Verify auth config
  run: |
    if [ "$ENVIRONMENT" = "production" ] && [ "$AUTH_PROVIDER" = "mock" ]; then
      echo "❌ Mock auth in production!"
      exit 1
    fi
```

### Pitfall 2: Data Contamination
**Symptom:** Test data from personal account leaks into production reports.

**Fix:** Tag all test-account data with metadata and filter in aggregations:
```python
def is_test_account(email: str) -> bool:
    return email in settings.TEST_ACCOUNTS

# In reporting:
results = db.query("SELECT * FROM transactions WHERE is_test = false")
```

### Pitfall 3: Rate Limit Cross-Contamination
**Symptom:** Personal account exhausts shared rate limit pool (Composio, etc.), blocking primary account operations.

**Fix:** Monitor rate limit headers separately per account; implement exponential backoff per credential set.

### Pitfall 4: Scope Mismatch
**Symptom:** Code works on personal account but fails on Workspace because scopes differ.

**Fix:** Write integration tests that validate against both account types; fail CI if behavior diverges.

### Pitfall 5: Security Regression
**Symptom:** Bypass pattern becomes permanent, credentials left in repo.

**Fix:** Add pre-commit hook scanning for auth-related env vars; run `git-secrets` scan in CI.

---

## Verification

Use `scripts/verify_auth_bypass.py` to test that the dual-account pattern is working correctly. It checks:

- Direct API attempts (expect blocked or healthy)
- Managed provider connection
- Fallback logic (auto mode)

```bash
python scripts/verify_auth_bypass.py --mode auto
```

See the template script for the exact checks to implement for your service.

---

## References

- AgentEscrow dual Gmail implementation: `02-Labs/Hackathons/Colosseum-Frontier/gmail-setup-dual.md`
- Architecture diagram: `02-Labs/Hackathons/Colosseum-Frontier/architecture-dual-gmail.html`
- Composio managed OAuth: `tool-infrastructure-composio.md`
- Google Workspace admin consent docs: (link when available)

---

## Related Skills

- `google-workspace` — Direct Gmail API usage (may be blocked by admin)
- `composio-integration` — Managed OAuth provider patterns
- `service-accounts` — Server-to-server auth bypass
- `environment-config` — Switching between auth backends
