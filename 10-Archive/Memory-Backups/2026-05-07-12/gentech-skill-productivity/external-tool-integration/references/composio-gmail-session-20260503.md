# Composio Gmail Integration — Session Notes (May 03, 2026)

## Context
Goal: Set up Gmail access via Composio as a workaround for blocked Google Workspace OAuth consent. Need to link a personal Gmail account for testing while Workspace admin resolution is pending.

## Setup Summary
- **Composio API Key**: `ak_sDnTqs_zYC06AnIoQ-RJ` (stored in session, NOT committed)
- **Python SDK**: `composio` 1.0.0-rc2
- **Target Toolkit**: Gmail (slug: `gmail`)
- **Auth Config ID**: `ac_98QwD-Yyqe3y` (pre-existing, name: `gmail-m742vi`)
- **Toolkit ID** (from deprecated_params): `a90e7d79-4f7a-4ff2-bd7d-19c78640b8f8`

## Key Discoveries

### 1. Auth Config Structure — Toolkit ID Location
The `auth_configs.list()` returns `AuthConfigListResponse` with `items`. Each item has:
- `id` — the auth config ID (use for initiate)
- `toolkit` — nested object with `slug` (e.g., `'gmail'`)
- `deprecated_params.toolkit_id` — the actual toolkit GUID used in some API calls

**Common mistake**: Using `toolkit.id` doesn't exist; toolkit doesn't have an `id` attribute. Use `config.id` for `auth_config_id` parameter.

```python
auth_configs = client.auth_configs.list()
configs_dict = dict(auth_configs)
configs = configs_dict['items']

gmail_config = [c for c in configs if c.toolkit.slug == 'gmail'][0]
print(gmail_config.id)  # → 'ac_98QwD-Yyqe3y' (use this)
```

### 2. Toolkits List Response Format
`client.toolkits.list()` returns `ToolkitListResponse`, a Pydantic model with fields:
```python
{
  'current_page': 1.0,
  'items': [Item, ...],  # list of toolkit items
  'total_items': 1033.0,
  'total_pages': 2.0,
  'next_cursor': 'Mi0xMDAw'
}
```

Access items: `items = dict(resp)['items']`

Each `Item` has:
- `slug` — e.g., `'gmail'`
- `name` — e.g., `'Gmail'`
- `meta` — description, categories, logo
- `deprecated.toolkit_id` — GUID of toolkit

### 3. Connected Accounts Object Attributes
`client.connected_accounts.list()` returns `ConnectedAccountListResponse`. Each account item attributes:
- `id` — connection ID (use with `client.use(connection_id=...)`)
- `status` — `'INITIATED'`, `'ACTIVE'`, `'DISABLED'`, `'ERROR'`
- `toolkit` — nested toolkit info (slug available)
- `created_at`, `last_used_at`

**Note**: No `.type` attribute; that raised `AttributeError` in early exploration.

### 4. OAuth Initiation and URL Retrieval
```python
conn_req = client.connected_accounts.initiate(
    user_id="default",
    auth_config_id=gmail_config.id,
    allow_multiple=True  # allow multiple accounts for same tool
)
redirect_url = conn_req.redirect_url  # or .url
# In our session: https://backend.composio.dev/api/v3/s/OadKH8UW
```

The ConnectionRequest object:
- `redirect_url` — the OAuth URL to open
- `status` — initial `'INITIATED'`
- `wait_for_connection(timeout)` — poll until completion (returns account)

### 5. Existing Connection State
On first check, the Gmail auth config reported `no_of_connections = 3` but listing accounts showed:
- 3 accounts total
- 1 with status `INITIATED` (stale, never completed)
- Likely 2 `ACTIVE` from previous sessions

**Cleanup recommended before new OAuth**:
```python
for acc in client.connected_accounts.list():
    if acc.status in ['INITIATED', 'ERROR']:
        client.connected_accounts.delete(acc.id)
```

## Session Sequence

1. **Explore SDK**: Checked `client.tools`, `client.toolkits`, discovered Gmail toolkit available
2. **Auth Config Discovery**: Found pre-existing Gmail auth config with ID `ac_98QwD-Yyqe3y`
3. **Response Format Troubleshooting**: Had to convert wrapper objects to dicts to access `.items`
4. **Toolkit ID Extraction**: Found toolkit GUID in `deprecated_params.toolkit_id`
5. **OAuth Initiation**: Successfully called `initiate()`, got redirect URL
6. **Browser Open**: Called `webbrowser.open()` to present OAuth URL (headless workaround)

## Code Snippets

### List Gmail Tool Methods (for documentation)
```python
session = client.use(connection_id=active_account.id)
tools = session.tools  # ToolRouterSession
# Enumerate Gmail methods
for tool in tools:
    print(tool.name)  # e.g., 'gmail_send_email', 'gmail_fetch_emails'
```

### Poll for OAuth Completion
```python
# After user completes OAuth in browser
completed_account = conn_req.wait_for_connection(timeout=120)
print(f"Connected: {completed_account.id}, status: {completed_account.status}")
```

## Admin Handoff — Workspace Gmail
See `external-tool-integration` skill Section "⚠️ OAuth Consent Blocked by Admin (Google Workspace)".

Action: Route to Google Workspace admin with:
- OAuth client ID from Composio auth config credentials (redacted in logs)
- Required scopes: `https://mail.google.com/`, `userinfo.email`, etc.
- Location: Admin Console → Security → API controls → Manage Third-Party App Access

## Next Steps (Pending User Action)
1. User completes OAuth at `https://backend.composio.dev/api/v3/s/OadKH8UW`
2. Upon confirmation ("done"), poll `wait_for_connection()` to verify `ACTIVE`
3. Test Gmail operations: fetch inbox, send test email
4. Create unified wrapper script that routes between:
   - Direct Workspace API (when admin consent resolved)
   - Composio personal Gmail (current workaround)

## Files Referenced
- `00-HQ/Approvals/` — for any future admin approval tracking
- `03-Projects/AAE/` — agent automation engineering notes
- Vault sync: `cd /root/vaults/gentech && ob sync`
