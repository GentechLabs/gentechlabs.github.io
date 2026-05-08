# Composio OAuth Troubleshooting

## Error: `Error 403: access_denied` during Gmail OAuth

**Symptom**: OAuth consent screen shows "The setting you are looking for is not available for your account" and refuses to proceed.

**Root causes** (in order of likelihood):
1. **OAuth app in Testing mode** → user not added as Test User
2. **Google Workspace admin policy** → third-party app access blocked at org level
3. **Advanced Protection Program** enrolled → hardware key required for all OAuth

### Fix Path

#### If using **Personal Gmail** (not Workspace):
```
1. Go to: https://console.cloud.google.com/auth/audience
2. Under "Test users", add your Gmail address
3. Save
4. Retry OAuth flow
```

#### If using **Workspace Gmail**:
```
1. Forward this error to your Google Workspace admin
2. Admin must: Security → API controls → Manage Third-Party App Access → Add OAuth Client ID
3. Wait 5–15 minutes → retry
```

#### If **Advanced Protection** is enabled:
```
Admin must: Admin Console → Security → Advanced Protection → Allowlisted apps → Add Composio OAuth client
```

---

## Error: `COMPOSIO_API_KEY not set`

**Symptom**: `NameError: name 'COMPOSIO_API_KEY' is not defined` or similar when running Composio scripts.

**Fix**:
```bash
# Option 1: Temporary (session only)
export COMPOSIO_API_KEY='your_key_here'

# Option 2: Persistent (add to ~/.hermes/.env)
echo "export COMPOSIO_API_KEY='your_key_here'" >> ~/.hermes/.env
source ~/.hermes/.env

# Option 3: Pass explicitly in code
import os
os.environ['COMPOSIO_API_KEY'] = 'your_key_here'
```

---

## Error: `composio.tools.execute() returns empty or None`

**Symptom**: Tool call succeeds but returns no email data.

**Likely causes**:
1. **Gmail connection not linked** — run linking flow first
2. **Wrong `connection_id`** — default is `gmail` unless you renamed it
3. **Personal Gmail has no messages matching query** — test with broader query

**Diagnostic**:
```python
from composio import Composio
c = Composio()
conns = c.integrations.list()
for conn in conns:
    print(f"{conn.appName}: {conn.connectionStatus} (ID: {conn.connectionId})")
```

If `connectionStatus != 'connected'`, re-link: `c.integrations.link('gmail')`

---

## Error: `pip install composio fails with "No matching distribution"`

**Symptom**: `ERROR: Could not find a version that satisfies the requirement composio-py`

**Fix**: Package name is `composio`, not `composio-py`:
```bash
pip install composio
```

If that fails (version conflicts), install from GitHub:
```bash
pip install git+https://github.com/ComposioHQ/composio.git
```

---

## OAuth Redirect Fails (localhost:8080 not responding)

**Symptom**: After approving OAuth consent, browser redirects to `http://localhost:8080` and shows "Site can't be reached".

**This is expected** — the redirect URI is just a mechanism to extract the auth code. Hermes/Composio doesn't actually run a server.

**Correct steps**:
1. After approval, **copy the entire URL** from browser address bar (it contains `?code=...`)
2. **Paste it back** into the terminal/CLI prompt
3. The OAuth code is extracted from the URL automatically

If the URL is cut off or blank, add yourself as a **Test User** (see above).

---

## Known Quirks (Documented May 2026)

- Composio SDK version `0.12.0` has a bug where `GMAIL_BATCH_DELETE_MESSAGES` times out on batches > 50 messages. Workaround: chunk batches to 25 msg/batch.
- OAuth tokens from Composio expire after 90 days of inactivity — schedule a weekly ping to keep alive if using for long-running agents.
- Gmail API `maxResults` parameter is ignored on some queries (Composio passes it through but Gmail caps at 100). Always paginate if you need >100.
