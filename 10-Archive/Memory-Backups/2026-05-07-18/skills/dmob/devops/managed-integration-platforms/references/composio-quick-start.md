# Composio Quick Start — Gentech Labs

This is the canonical setup sequence for getting Composio operational in our environment. Reference this when onboarding new agents or rebuilding the Hermes instance.

---

## Prerequisites

- Python 3.10+
- Hermes Agent installed (`~/.hermes/`)
- API key from [composio.dev](https://composio.dev) (free tier available)

---

## Installation

```bash
# SDK
pip install composio-core

# Verify
python -c "from composio import Composio; print('OK')"
```

---

## Environment Configuration

**Add to `~/.hermes/.env`:**
```bash
COMPOSIO_API_KEY=your_key_here
```

**Ensure Hermes picks it up:**
```bash
hermes config set security.redact_secrets true   # protect the key
```

**Restart any active Hermes sessions** → new env vars apply on process start.

---

## First-Time Auth Flow (Google example)

### Step 1: Link account
```bash
python -c "from composio import Composio; Composio().integrations.link('gmail')"
```
- Browser opens → Google OAuth consent
- Select scopes: Gmail + Calendar (or full Workspace)
- Approve

### Step 2: Verify linkage
```python
from composio import Composio
c = Composio()
conns = c.integrations.list(connection_id="gmail")
print(conns)  # should show status: "connected"
```

Or CLI:
```bash
python -c "from composio import Composio; print(Composio().integrations.list())"
```

### Step 3: Test an action
```python
from composio import Composio
c = Composio()
result = c.tools.exec(
    action="GMAIL_SEARCH_EMAILS",
    params={"query": "is:unread", "max_results": 5}
)
print(result)  # JSON array of messages
```

---

## Common Tool Calls

### Gmail
```python
c.tools.exec("GMAIL_SEARCH_EMAILS", {"query": "from:boss@company.com", "max_results": 10})
c.tools.exec("GMAIL_SEND_EMAIL", {"to": "user@example.com", "subject": "Report", "body": "See attached", "html": False})
c.tools.exec("GMAIL_REPLY_TO_THREAD", {"thread_id": "xxx", "body": "Confirming"})
```

### Calendar
```python
c.tools.exec("CALENDAR_LIST_EVENTS", {"time_min": "2026-05-01T00:00:00Z", "time_max": "2026-05-07T23:59:59Z"})
c.tools.exec("CALENDAR_CREATE_EVENT", {"summary": "Standup", "start": "2026-05-03T10:00:00-07:00", "end": "2026-05-03T10:30:00-07:00"})
```

### Slack
```python
c.tools.exec("SLACK_POST_MESSAGE", {"channel": "general", "text": "Deploy complete ✅"})
c.tools.exec("SLACK_UPDATE_THREAD", {"channel": "general", "thread_ts": "xxx", "text": "Update"})
```

### GitHub
```python
c.tools.exec("GITHUB_CREATE_ISSUE", {"owner": "gentech", "repo": "agent-escrow", "title": "Bug: milestone timeout", "body": "..."})
c.tools.exec("GITHUB_ADD_LABELS", {"owner": "gentech", "repo": "agent-escrow", "issue_number": 42, "labels": ["bug", "p1"]})
```

---

## Error Handling Pattern

```python
try:
    result = c.tools.exec(action, params)
    if result.get('error'):
        raise Exception(result['error'])
    return result['data']
except Exception as e:
    # Fallback: log to vault, queue for retry, or use backup method
    print(f"Composio failed: {e}")
    raise
```

**Common errors:**
- `401 Unauthorized` → Re-run link flow (token expired)
- `429 Too Many Requests` → Backoff 60s, retry (Composio enforces rate limits)
- `403 Scope Insufficient` → Re-link with broader scopes
- `404 Action not found` → Tool not enabled in your plan tier

---

## Enabling Tools in Your Plan

1. Dashboard → Integrations → toggle each service ON
2. For each, click "Connect" and complete OAuth
3. Return to CLI, actions are immediately available

**Note**: Unconnected integrations return `ConnectionRequiredError` even if the tool is enabled.

---

## Cost Monitoring

Composio pricing is per-invocation after free tier (typically ~$0.0001–0.001/call).

**Track usage in-script:**
```python
import json
from datetime import datetime

def log_composio(action, params, result):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "params_summary": str(params)[:200],
        "success": "error" not in result,
        "cost_est_usd": estimate_cost(action)  # lookup table from their pricing doc
    }
    # Append to /root/vaults/gentech/02-Labs/Audits/Composio-Usage-YYYY-MM.md
```

---

## Wrapper Script Pattern

Store in `02-Labs/scripts/composio_client.py` for consistent usage across agents:

```python
#!/usr/bin/env python3
"""Gentech Labs — Composio thin wrapper with logging + retry."""
import os, sys, json, time
from composio import Composio

API = Composio()

def exec(action: str, params: dict, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            result = API.tools.exec(action=action, params=params)
            if result.get("error"):
                raise RuntimeError(result["error"])
            return result.get("data")
        except Exception as e:
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)  # exponential backoff

if __name__ == "__main__":
    # CLI: python composio_client.py GMAIL_SEARCH_EMAILS '{"query":"is:unread"}'
    action = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(exec(action, params)))
```

---

## Deprecating Old Skills

Once Composio is live for a service, archive the custom skill:

```bash
# Example: google-workspace (custom OAuth) → Composio managed
mv ~/.hermes/skills/productivity/google-workspace ~/.hermes/skills/productivity/google-workspace.DISABLED-$(date +%Y%m%d)
hermes skills config  # confirm it's disabled
```

Update any agent system prompts to load `managed-integration-platforms` first.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ConnectionRequiredError` | OAuth not completed | Re-run link flow for that service |
| `Action not found` | Tool not enabled in dashboard | Enable integration in Composio UI |
| `401 Unauthorized` after days | Token expired/revoked | Re-link account |
| Rate limit errors | Too many calls too fast | Add `time.sleep(1)` between sequential calls |
| Empty result set | Query params wrong (e.g., date format) | Check action schema in dashboard |

---

## Security Notes

- **Hermes redaction**: `security.redact_secrets = true` masks the COMPOSIO_API_KEY in all logs
- **Token storage**: Composio stores OAuth tokens; our code never sees refresh tokens
- **Least privilege**: Link only the scopes needed per service (e.g., Gmail read-only if no send required)
- **Audit**: All tool invocations are logged in Composio dashboard; mirror to vault for compliance

---

When in doubt, read the official docs: https://docs.composio.dev
