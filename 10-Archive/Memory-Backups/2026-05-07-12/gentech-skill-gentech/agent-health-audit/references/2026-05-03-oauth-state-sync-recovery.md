# OAuth State Desynchronization Recovery — 2026-05-03

**Profile**: Gentech (Gentech Labs)  
**Cron job**: Proactive Nous OAuth refresh (`refresh_nous_oauth.py`)  
**Trigger**: Refresh script reported `Hermes is not logged into Nous Portal` despite apparent credentials existing in `auth.json`.

## Incident Timeline

1. **Initial state** (`auth.json`):
   - `providers.nous` — **empty** (singleton provider state missing)
   - `credential_pool.nous[0]` — contains full OAuth entry with `access_token`, `refresh_token`, `expires_at`, `agent_key`, etc.

2. **Refresh attempt** (before sync):
   - `resolve_nous_access_token()` reads only `providers.nous` → empty → raises `AuthError("Hermes is not logged into Nous Portal.")`
   - Exit code 0 (maintenance state), `needs_reauth: true`

3. **Investigation**:
   - Discovered the two-source model: runtime reads from `providers.nous`; `hermes auth`/credential management writes to `credential_pool.nous`.
   - Found that `persist_nous_credentials()` writes to both locations, but some historical paths only wrote to the pool.
   - **Manual sync performed**: copied pool entry fields into `providers.nous` to restore canonical state.

4. **Second refresh attempt** (after sync):
   - `providers.nous` now populated → token refresh logic engaged
   - Refresh token rejected: `"Refresh session has been revoked"` → full OAuth revocation
   - Exit code 0, `needs_reauth: true`

5. **Root cause**: Not a desync bug per se, but a **revoked refresh token**. The desync masked the revocation initially; after normalization, the true failure surfaced.

## Detection Pattern

**Symptoms**:
- Refresh script output: `Hermes is not logged into Nous Portal` (not the usual `Refresh session has been revoked`)
- Manual inspection of `auth.json` reveals:
  ```json
  "providers": { "nous": {} }   // or null/missing
  "credential_pool": {
    "nous": [ { ... access_token, refresh_token, expires_at ... } ]
  }
  ```
- Token in pool appears unexpired (future `expires_at`), yet refresh logic cannot see it.

**Diagnostic command** (shell):
```bash
# Check for state desynchronization
python3 -c "
import json
a = json.load(open('/root/.hermes/profiles/gentech/auth.json'))
prov = a.get('providers', {}).get('nous')
pool = a.get('credential_pool', {}).get('nous', [])
print('providers.nous present:', bool(prov))
print('credential_pool.nous entries:', len(pool))
if not prov and pool:
    print('DESYNC DETECTED: pool has credentials but provider state missing')
"
```

## Recovery Procedure

### Step 1 — Normalize state (only if pool entry exists and appears valid)

```bash
python3 <<'PY'
import json, sys
from datetime import datetime, timezone
HERMES_HOME = '/root/.hermes/profiles/gentech'
AUTH_FILE = f'{HERMES_HOME}/auth.json'
with open(AUTH_FILE) as f:
    auth = json.load(f)
pool = auth.get('credential_pool', {}).get('nous', [])
if not pool:
    print('ERROR: No pool entries to recover from')
    sys.exit(1)
e = pool[0]
# Build provider state
state = {
    "access_token": e["access_token"],
    "refresh_token": e["refresh_token"],
    "token_type": e.get("token_type", "Bearer"),
    "scope": e.get("scope", "inference:mint_agent_key"),
    "obtained_at": e.get("obtained_at", datetime.now(timezone.utc).isoformat()),
    "expires_at": e.get("expires_at", ""),
    "expires_in": e.get("expires_in", 900),
    "client_id": e.get("client_id", "hermes-cli"),
    "portal_base_url": e.get("portal_base_url", "https://portal.nousresearch.com"),
    "inference_base_url": e.get("inference_base_url", "https://inference-api.nousresearch.com/v1"),
    "agent_key": e.get("agent_key", ""),
    "agent_key_expires_at": e.get("agent_key_expires_at", ""),
    "agent_key_obtained_at": e.get("agent_key_obtained_at", ""),
    "agent_key_id": e.get("agent_key_id", ""),
    "agent_key_reused": e.get("agent_key_reused", False),
    "tls": e.get("tls", {"insecure": False, "ca_bundle": None}),
}
auth.setdefault('providers', {})['nous'] = state
with open(AUTH_FILE, 'w') as f:
    json.dump(auth, f, indent=2)
print('✅ Synced credential pool → providers.nous')
PY
```

### Step 2 — Re-run refresh to assess true token status

```bash
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```

**Interpret results**:
- `success: true` → Desync was the only issue; tokens are now fresh.
- `needs_reauth: true` with message `Refresh session has been revoked` → Refresh token invalid; proceed to Step 3.
- Any other error → investigate further (network, portal downtime, etc.)

### Step 3 — Full re-authentication (when refresh token revoked)

**Interactive manual step required**:
```bash
hermes model
```
- This initiates a fresh device-flow OAuth
- Requires browser interaction; cannot run in non-interactive cron context
- After successful login, both `providers.nous` and `credential_pool.nous` will be populated with new tokens

### Prevention

Run the **state sync recovery** as a pre-check inside the refresh script *before* calling `resolve_nous_access_token()`, but **only** if `providers.nous` is empty and `credential_pool.nous` has a valid entry. This would make the refresh job self-healing for desync cases (though not for revocation).

**Proposed wrapper improvement**: Modify `refresh_nous_oauth.py` to attempt auto-recovery from desynchronization before failing, e.g.:

```python
# Pseudo-patch
if not nous_state and pool_entries:
    log.warning("Auth state desync detected — auto-syncing from credential pool")
    persist_nous_credentials(pool_entries[0])  # or direct write like above
    # then re-load state and proceed
```

Until patched, the cron job will continue to emit `needs_reauth: true` for both desync and revocation; operators must inspect `auth.json` to distinguish.

## Key Insight

Hermes maintains **two sources of truth** for Nous credentials:
- **`providers.nous`** — singleton state read by runtime token resolver
- **`credential_pool.nous`** — credential pool entries used by `hermes auth` and selection logic

Historically, `hermes auth add nous` wrote only to the pool; newer code writes to both. When the singleton gets cleared or fails to persist, the pool may still hold valid refresh credentials. Runtime **cannot see** the pool, so it reports "not logged in" even though a refresh token exists. Syncing restores access **if the refresh token itself is still valid**.

## Related

- Existing skill section: **OAuth session state fingerprint** (covers revocation signs)
- This pattern is **pre-revocation**: desync before the refresh token becomes invalid.
- Compound failure: If desync coincides with revocation, recovery requires manual `hermes model` anyway.
- Cron constraint: `hermes model` requires TTY; automation cannot complete device flow without human browser interaction.
