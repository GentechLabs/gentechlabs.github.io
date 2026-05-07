---
name: hermes-auth-incident-response
description: "Handle Hermes OAuth token expiry and authentication failures proactively"
version: 1.0.0
author: Gentech Labs
license: MIT
metadata:
  hermes:
    tags: [hermes, auth, oauth, maintenance, incident-response]
    homepage: https://github.com/NousResearch/hermes-agent
related_skills: ["hermes-agent", "hermes-maintenance-scripts"]
---

# Hermes Authentication Incident Response

When Hermes OAuth tokens expire or authentication fails, follow this playbook to diagnose, document, delegate, and verify recovery.

## When This Skill Applies

Trigger conditions (any one):
- Any script or agent returns JSON with `"needs_reauth": true`
- Refresh script prints or logs `"Refresh session has been revoked"` (HTTP 400 from OAuth token endpoint indicating refresh token is no longer valid)
- `hermes doctor` shows providers as "not logged in" that should be active
- Cron jobs fail with auth-related errors (check `last_error` in `cron/jobs.json`)
- Gateway logs show "Primary provider auth failed" messages
- Access token `expires_at` in `auth.json` is in the past and refresh fails with `AuthError(relogin_required=True)`

**Does NOT apply:** API key misconfiguration (that's a `config.yaml`/`.env` issue, not OAuth).

---

## Quick Diagnostic

Run these checks in order:

```bash
# 0. Resolve canonical HERMES_HOME (avoids nested-path confusion)
# See: references/hermes-home-path-quirk-2026-05-03.md
HERMES_HOME=$(realpath "${HERMES_HOME:-~/.hermes/profiles/gentech}")
echo "Using HERMES_HOME: $HERMES_HOME"
```

**Pre-step A: Mandatory stale device flow cleanup** (observed 2026-05-04: pending flow file aged ~342 min)
```bash
# Remove any stale pending flow before initiating new auth
if [ -f "$HERMES_HOME/auth_pending_device_flow.json" ]; then
    echo "Found stale pending flow — removing"
    rm -f "$HERMES_HOME/auth_pending_device_flow.json"
fi
# Also remove symlink in scripts dir if present
if [ -L "$HERMES_HOME/scripts/pending_nous_device_flow_latest.json" ]; then
    echo "Removing stale symlink"
    rm -f "$HERMES_HOME/scripts/pending_nous_device_flow_latest.json"
fi
```

# 1. Check auth state (granular)
cat "$HERMES_HOME/auth.json" | jq '.providers.nous'

# 1a. Distinguish token state:
#   - If .providers.nous is {} or null → tokens completely missing/revoked
#   - If .providers.nous exists but .access_token missing → corrupted state
#   - If .access_token present but .expires_at in past → expired, refresh token may be valid
#   - If .refresh_token missing entirely → must re-auth even if access_token present

# 2. Look for expires_at (if provider entry exists)
# If missing while access_token present → token state damaged
# If in the past → access token expired; check if refresh_token exists to determine if refresh can proceed

# 3. Check refresh script exists and is scheduled
ls "$HERMES_HOME/scripts/refresh_nous_oauth.py"
grep -A5 "Nous OAuth" "$HERMES_HOME/cron/jobs.json"

# 4. Check for stale pending device flow (clean up if expired)
# Use helper script: scripts/cleanup_stale_nous_flows.py
if [ -f "$HERMES_HOME/scripts/pending_nous_device_flow_latest.json" ]; then
    echo "Pending flow file exists — running cleanup check..."
    "$HERMES_HOME/scripts/cleanup_stale_nous_flows.py" --dry-run  # remove --dry-run to actually delete
fi

# 5. Test refresh manually
"$HERMES_HOME/scripts/refresh_nous_oauth.py"
```

Expected manual refresh output: `"success": true` with `access_token_preview`, `refresh_token_present: true`, and `remaining_seconds` > 300.

If refresh script returns `needs_reauth: true` or `success: false` with relogin_required, OAuth session is fully revoked — proceed to Incident Declaration.

---

## Incident Declaration Checklist

- [ ] Token truly expired (`expires_at` < now) or refresh fails with `relogin_required`
- [ ] Verify refresh script is deployed and scheduled (every 5–10 min is typical)
- [ ] Confirm affected data sources: which scripts/cron jobs depend on this auth?
- [ ] Check gateway logs for recent auth failures: `tail -20 ~/.hermes/profiles/<profile>/logs/gateway.log | grep -i auth`
- [ ] Ensure no other provider can fall in (check `config.yaml` provider priority)
- [ ] **Non-interactive check:** If running in cron/agent context and `hermes model` is required, use device flow path instead (see Non-Interactive Recovery)
- [ ] **Cron environment check:** If this is a scheduled cron job with no TTY, `hermes model` **cannot be executed** due to terminal requirements. When device flow is unavailable (rate-limited, endpoint down, or manual flow fails), the only recovery path is manual intervention by a user with interactive terminal access. The job will remain failed until such intervention occurs.

---

## Non-Interactive Recovery Path (Cron/Headless Environments)

When `hermes model` cannot run due to non-TTY constraints (cron jobs, SSH without a terminal, automated agents), and the refresh token is fully revoked (`relogin_required: true`), use the device authorization flow programmatically. This path initiated the OAuth flow without a browser, captures the verification URL and user code, and creates a completion helper for the human operator.

### Step 1: Initiate Device Flow (No Browser)

Call the private auth function with `open_browser=False` and a short timeout to only perform the initiation (not the blocking poll):

```python
import sys
sys.path.insert(0, '/usr/local/lib/hermes-agent')
from hermes_cli.auth import _nous_device_code_login

result = _nous_device_code_login(
    portal_base_url=None,      # uses default from PROVIDER_REGISTRY
    inference_base_url=None,
    client_id=None,            # falls back to provider config client_id
    scope=None,                # falls back to provider config scope
    open_browser=False,        # critical — do not try to open browser
    timeout_seconds=5.0,       # short — only for initiation, not completion
    insecure=False,
    ca_bundle=None,
    min_key_ttl_seconds=300,
)

print(result)
# → { device_code, user_code, verification_uri, verification_uri_complete, expires_in, interval, ... }
```

**Production note:** This minimal example omits the outer timeout guard that prevents hanging when the device code endpoint is rate-limited or unresponsive. The `timeout_seconds` parameter only guards the initial HTTP request; the subsequent polling loop can block for up to `expires_in` (typically 10 minutes). In production automation, always wrap the call in an outer timeout (e.g., 30 seconds) and fall back to manual `hermes model` if it expires. A reusable, production-hardened template is provided in the skill's `scripts/` directory: `initiate_nous_device_flow_with_timeout.py`.

**Important:** The `timeout_seconds` parameter applies only to the initial device code request. A separate polling loop waits for user approval and can block up to the code's `expires_in` (typically 10 minutes). Even with a small timeout, the function may hang; wrap the call in an outer timeout (e.g., `timeout 30s`) and if it exceeds ~30 seconds, abort and fall back to `hermes model`. The return value contains the verification URL and user code.

### Step 2: Save Flow State & Alert Human

Save the `result` dict to a well-known location and communicate the verification URL to the responsible human (DMOB) via your chosen channel (Telegram group, Mess Hall, email).

Example:

```python
import json, os
from datetime import datetime, timezone
flow = result
flow['initiated_at'] = datetime.now(timezone.utc).isoformat()
flow_path = f"/root/.hermes/profiles/gentech/scripts/pending_nous_device_flow_{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M')}.json"
with open(flow_path, 'w') as f:
    json.dump(flow, f, indent=2)
# Symlink as "latest"
latest = os.path.join(os.path.dirname(flow_path), "pending_nous_device_flow_latest.json")
if os.path.exists(latest) or os.path.islink(latest):
    os.remove(latest)
os.symlink(flow_path, latest)
```

Then delegate with the verification URL included (see Delegation section below).

### Step 3: Human Completes Browser Auth

1. Human opens `verification_uri_complete` in a browser
2. Approves the OAuth consent screen
3. Runs the completion helper script (provided in `scripts/` of this skill):
   ```bash
   ~/.hermes/profiles/gentech/scripts/complete_nous_device_flow.sh
   ```
   or
   ```bash
   python3 ~/.hermes/profiles/gentech/scripts/complete_nous_device_flow.py
   ```

The completion script polls for the token endpoint using `device_code`, then writes the tokens to `auth.json` and cleans up the pending flow file.

### Step 4: Rate Limit Detection & Fallback

**Observed behavior:** The device code endpoint (`/oauth/device/code`) may return HTTP 429 when the refresh script has been polling frequently or multiple agents attempt flows concurrently. When this happens, the non-interactive programmatic path is unavailable and `_nous_device_code_login()` will fail immediately.

**Detection:**
```python
resp = httpx.post(f"{portal_url}/oauth/device/code", ...)
if resp.status_code == 429:
    # Device code endpoint is rate-limited
    raise RuntimeError("Device code endpoint rate-limited (429) — manual hermes model path required")
```

**Fallback strategy:**
1. Abort further device flow attempts for 5–10 minutes (rate limit window)
2. Escalate to owner (`@DMOB`) with explicit instruction: **"Device code endpoint is rate-limited. Run `hermes model` for interactive re-authentication instead."**
3. Document the rate limit condition in the incident log with timestamp for post-mortem correlation
4. After cooldown, retry device flow once; if still 429, continue with manual path

**Why this matters:** Automated retries during rate limits aggravate the throttle and delay recovery. Escalating to manual `hermes model` is faster and bypasses the rate-limited endpoint entirely.

### Step 5: Configuration Vulnerability Check (NEW — 2026-05-03 Incident)

When the primary OAuth provider fails, **an empty `fallback_providers` list creates a single point of failure**. During incident assessment, verify the provider chain:

```bash
# Check current provider and fallback chain
grep -A2 "^model:" ~/.hermes/profiles/gentech/config.yaml
grep -A5 "^fallback_providers:" ~/.hermes/profiles/gentech/config.yaml
```

**If `fallback_providers` is empty or all entries are unhealthy**, the agent will fail when the primary provider goes offline. Before declaring resolution, **add at least one healthy API-key-based provider** to the fallback chain:

```yaml
model:
  provider: auto   # Use 'auto' to enable fallback chain
fallback_providers:
  - ollama-cloud   # Requires working API key in .env
  - opencode-go    # May have quota limits
```

**How to assess provider health** (check `auth.json` credential pool):

```bash
# List all providers and their last status
python3 -c "
import json
d = json.load(open('/root/.hermes/profiles/gentech/auth.json'))
for prov, creds in d.get('credential_pool', {}).items():
    for c in creds:
        print(f'{prov}: {c.get(\"last_status\")} — {c.get(\"last_error_message\", \"OK\")}')
"
```

Look for:
- `last_status: \"ok\"` — healthy
- `last_status: \"exhausted\"` — quota exceeded, not usable
- `last_error_code: 429` — rate-limited, may recover later

**Mandatory post-recovery check:** After OAuth re-authentication, **update `config.yaml` to include at least one API-key fallback provider** to prevent future single-point failures. Document the change in the incident log.

### Step 6: Cross-Profile Token Sharing Risk Assessment (NEW)

**Critical Discovery:** Multiple Hermes profiles (gentech, yoyo, dmob, desmond) may share the same Nous token instance. When one profile's token expires, all profiles become unavailable simultaneously.

**Detection:**
```bash
# Check token expiration across profiles
for profile in gentech yoyo dmob desmond; do
  if [ -f "/root/.hermes/profiles/$profile/auth.json" ]; then
    expires=$(jq -r '.providers.nous.expires_at' "/root/.hermes/profiles/$profile/auth.json" 2>/dev/null)
    if [ "$expires" != "null" ]; then
      echo "$profile: expires at $expires"
    fi
  fi
done
```

**Impact:**
- Single point of failure across entire agent fleet
- Rate limiting during recovery may be exacerbated by multiple profiles attempting device flow concurrently
- If one profile lacks scheduled refresh, it won't attempt recovery automatically

**Mitigation:**
1. **Stagger refresh schedules** across profiles (e.g., gentech: */10, yoyo: */10 at 20min offset)
2. **Ensure all profiles have refresh scripts scheduled**
3. **Implement coordinated recovery** to avoid concurrent device flow attempts
4. **Add fallback providers** to all profiles' config.yaml

### Step 7: Enhanced Rate Limit Handling (NEW)

**Observed Behavior:** Device code endpoint may return HTTP 429 when multiple profiles attempt recovery concurrently or refresh script has been polling frequently.

**Enhanced Detection & Fallback:**
```python
import time
from hermes_cli.auth import _nous_device_code_login

def initiate_device_flow_with_rate_limit_protection(max_retries=1, cooldown=300):
    for attempt in range(max_retries + 1):
        try:
            # Wrap in outer timeout to prevent hanging
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Device flow initiation timed out")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout
            
            result = _nous_device_code_login(
                open_browser=False,
                timeout_seconds=5.0,
                min_key_ttl_seconds=300
            )
            signal.alarm(0)  # Reset alarm
            return result
            
        except TimeoutError:
            print("Device flow initiation timed out — falling back to manual hermes model")
            raise
            
        except Exception as e:
            # Check if this is a rate limit error
            if "429" in str(e) or "rate limit" in str(e).lower():
                if attempt < max_retries:
                    print(f"Rate limited — waiting {cooldown} seconds before retry...")
                    time.sleep(cooldown)
                    continue
                else:
                    raise RuntimeError(
                        f"Device code endpoint rate-limited after {max_retries + 1} attempts. "
                        "Manual `hermes model` re-authentication required."
                    )
            else:
                raise
```

**Production Recommendation:**
- When rate limit detected, **escalate immediately** to manual `hermes model` instead of retrying
- Document rate limit occurrence in incident log with timestamp
- After cooldown, retry device flow **once**; if still 429, continue with manual path
- Consider implementing a **global rate limit semaphore** across profiles to prevent concurrent attempts

### Step 8: Expanded Verification & Monitoring (NEW)

**Post-Recovery Verification Expanded:**
1. ✅ Verify refresh script returns success for **all affected profiles**
2. ✅ Check token TTL is ~30 days for **each profile**
3. ✅ Test affected cron jobs manually for **each profile**
4. ✅ **Update all profiles' config.yaml** to add fallback providers
5. ✅ Schedule refresh cron jobs for profiles that lack them
6. ✅ Document completion in incident log with cross-profile impact assessment

**Proactive Monitoring Enhancements:**
- Extend Gentech Watchdog to monitor **all profiles' auth state**
- Check for `needs_reauth: true` in cron script output (not just exit codes)
- Monitor `auth.json` for expired tokens across all profiles
- Alert when multiple profiles share the same token expiration time

**Healthy Output Shape Reminder:**
```json
{
  "success": true,
  "message": "Tokens are fresh",
  "tokens": {
    "access_token_preview": "eyJhbG...fOtU",
    "refresh_token_present": true,
    "expires_at": "2026-05-06T12:38:54.268608+00:00",
    "agent_key_expires_at": "2026-05-07T12:33:05.021Z"
  },
  "needs_reauth": false,
  "critical": false,
  "hermes_home": "/root/.hermes/profiles/gentech",
  "remaining_seconds": 244
}
```

**Key indicators of health:**
- `success: true` — script executed without error
- `needs_reauth: false` — refresh token still valid
- `remaining_seconds` > 0 — time until access token expiry
- `refresh_token_present: true` — recovery mechanism intact

### Step 9: Documentation Templates (NEW)

**Cross-Profile Incident Log Entry:**
```markdown
## Incident: Multi-Profile OAuth Failure — <Provider>

**Status:** 🔴 ACTIVE  
**Detected:** <YYYY-MM-DD HH:MM UTC>  
**Impact:** Entire agent fleet affected (gentech, yoyo, dmob, desmond)

### Root Cause
- Shared token expiration across all profiles
- gentech had refresh scheduled; other profiles did not
- Rate limiting blocked automated recovery

### Resolution
- [ ] @DMOB: Run `hermes model` for manual re-authentication
- [ ] Schedule refresh for all profiles
- [ ] Add fallback providers to all config.yaml
- [ ] Implement staggered refresh schedules

### Follow-Up
- [ ] Verify recovery for each profile
- [ ] Update monitoring to detect multi-profile issues
- [ ] Document lessons learned
```

**Mess Hall Alert Template:**
```markdown
🔴 **CRITICAL: Multi-Profile OAuth Failure** 🔴

**Issue:** All Hermes profiles (gentech, yoyo, dmob, desmond) share the same <Provider> token which has expired.  
**Action:** @DMOB must run `hermes model` to re-authenticate **immediately**.  
**Why manual:** Device code endpoint rate-limited (429) — automated recovery blocked.  
**Incident log:** 00-HQ/Operations/Infrastructure-Issues.md  
**Priority:** P0 — Entire agent fleet offline.
```

### Step 6: Exit Code Semantics Reminder

The refresh script returns exit code `0` for both `success: true` (tokens fresh) **and** `needs_reauth: true` (manual intervention required). This is by design to avoid automated incident alerts for expected maintenance states.

**Monitoring implication:** Do NOT rely on exit code alone. Cron job monitoring must parse the JSON output and raise an alert when `needs_reauth: true` appears. If your monitoring only checks exit codes, update it to parse stdout/stderr JSON and flag `needs_reauth` as a P0 condition.

---

### Step 7: Verify

### Pitfalls

| Pitfall | How to avoid |
|---------|--------------|
| `_nous_device_code_login` blocks despite `timeout_seconds=5` | The `timeout_seconds` parameter controls only the initial HTTP request; a separate polling loop waits for user approval and can block up to the device code's `expires_in` (typically 10 minutes). Even with `timeout_seconds=5`, the function may hang for minutes. Wrap the call in an outer timeout (e.g., `timeout 30s`) and if it exceeds ~30 seconds, abort and fall back to `hermes model`. |
| Completion script runs before browser approval | It will poll with dots until the user approves or the code expires (10 min). Safe to run early. |
| Device code expires before completion | The completion script detects expiry and exits with code 1, printing a clear error. Re-initiate the flow. |
| Multiple concurrent device flows | Only one pending flow is tracked via `pending_nous_device_flow_latest.json`. Re-initiation overwrites previous. Coordinate with DMOB to avoid confusion. |
| Device code endpoint rate-limited (HTTP 429) | Automated device flow attempts trigger throttling when refresh script has been failing repeatedly. **Abort programmatic retries.** Escalate to manual `hermes model` re-authentication. Document 429 occurrence in incident log. |
| Device flow call hangs or times out (no explicit 429) | The `_nous_device_code_login` function may not immediately surface rate-limit errors; instead it can hang during polling. If the call exceeds 30 seconds despite `timeout_seconds=5`, treat as unavailable and fall back to `hermes model`. |
| Stale pending device flow files accumulate | If a device flow is initiated but never completed (no human action), the `pending_nous_device_flow_latest.json` file remains and may be very old. When `needs_reauth: true` is detected, proactively check and **remove expired pending flow files** before attempting any new device flow initiation (see Quick Diagnostic step 4). | **NEW (2026-05-04):** Mandatory pre-clean discovered stale flow aged ~342 min. Add explicit pre-step A in Quick Diagnostic. |
| HERMES_HOME path structure quirks | Some Hermes installations resolve HERMES_HOME to a nested path like `/root/.hermes/profiles/gentech/home/.hermes/profiles/gentech`. When constructing script paths, **use `realpath "$HERMES_HOME"`** first to get the canonical location, or directly use the known canonical path `/root/.hermes/profiles/gentech`. Never trust `$HERMES_HOME` blindly without validation. | Observed in this session: canonical path resolved to nested structure. Always run `realpath` first. |
| Refresh script exit code 0 trap | The refresh script returns exit code `0` for both `success: true` (tokens fresh) **and** `needs_reauth: true` (manual intervention required). **Monitoring systems that only check exit codes will miss auth failures.** Cron job `last_status` will show `ok` despite `needs_reauth: true` in JSON payload. Always parse stdout JSON; flag `needs_reauth: true` as P0. | Confirmed 2026-05-04: `refresh_nous_oauth.py` exited 0 while returning `{"needs_reauth": true}`. Update Gentech Watchdog to parse cron script output. |
| **Credential pool status is stale** | `auth.json` may show `credential_pool.nous.status=ok` while `providers.nous` is `{}` or tokens are expired/revoked. **Credential pool status reflects last successful authentication, not current state.** Always inspect `.providers.<name>` directly (presence of `access_token`, `expires_at` in future); do NOT rely on `credential_pool` health as a proxy for token availability. | Observed 2026-05-04: credential_pool.nous[0].last_status='ok' but providers.nous had tokens with `expires_at` in past and refresh failed with `relogin_required`. |
| Refresh script not deployed | Verify: `ls ~/.hermes/profiles/<profile>/scripts/refresh_nous_oauth.py`. If missing, copy from vault: `/root/vaults/gentech/00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py` |
| Cron job not scheduled | Check `cron/jobs.json` for `"Nous OAuth Proactive Refresh"` entry with `"script": "refresh_nous_oauth.py"` and `"enabled": true`. |
| Wrong HERMES_HOME in cron | Cron sets HERMES_HOME to profile directory. Script uses `os.environ.get("HERMES_HOME")` — never hardcode paths inside cron scripts. |
| Gateway still using stale token | Gateway process picks up new token on next request automatically (auth module reloads from `auth.json`). No restart needed. |
| Multiple profiles affected | Repeat this playbook for each profile (yoyo, dmob, desmond) if they share the same OAuth provider. |
| "Tokens are fresh" false positive | Refresh script returns `success: true` even when no refresh occurred (token still valid, not in 2-min skew window). Verify renewal by checking `obtained_at` timestamp advanced; do NOT rely on `"Tokens are fresh"` message alone. |
**Provider Support:** Currently implemented for Nous Portal (`_nous_device_code_login`). For other OAuth providers (Google, GitHub, Minimax, etc.), `hermes model` remains the primary path; the device flow pattern may be applied if the provider supports it and the CLI exposes a non-blocking initiation function.

---

## Documentation & Delegation

### 1. Incident Log (00-HQ/Operations)

Create or update `00-HQ/Operations/Infrastructure-Issues.md`:

```markdown
## Incident: <Provider> OAuth <Status> — <Impact>

**Status:** 🔴 ACTIVE / ✅ RESOLVED
**Detected:** <YYYY-MM-DD HH:MM UTC>
**Impact:** <What's broken>

### Timeline
- <time>: Token expired / refresh failed / first script failure

### Resolution Steps
- Assigned: @<Team Lead>
- Action: `hermes model` → re-authenticate <Provider>
- Verify: <script path> returns success

### Follow-Up
- [ ] Re-auth complete
- [ ] Refresh script verified
- [ ] Affected jobs tested
```

### 2. Mess Hall Alert (11-Mess Hall/YYYY/W##/today)

Add to `today-context.md` under Flags Raised:

```markdown
🔴 **CRITICAL: <Provider> OAuth session revoked** — <impact>
  - Token expired at HH:MM UTC; refresh script cannot recover
  - **Action:** <Team Lead> must run `hermes model` to re-authenticate
  - Incident logged in `00-HQ/Operations/Infrastructure-Issues.md`
```

Create a dedicated alert file ` nous-oauth-revoked-alert.md` (or provider-equivalent) with:
- Executive summary
- Affected components table
- Immediate action block
- Monitoring status

### 3. Delegate to Team Lead

Route via Telegram group (NOT DM):
- **Gentech (Nous/Hermes infra):** → @DMOB
- **External service OAuth:** → appropriate department head

Message template (standard):
```
@DMOB — Hermes auth incident requiring manual intervention.

Issue: <Provider> OAuth token expired, refresh script failing.
Action required: Run `hermes model` and re-authenticate <Provider>.
Details: 00-HQ/Operations/Infrastructure-Issues.md
Incident alert posted in today's Mess Hall context.
Priority: P0 — data collection offline.
```

**Non-interactive variant (cron/headless):** If `hermes model` cannot run and device flow was initiated, extend the message with:
```
Device verification URL (complete within 10 minutes):
  <verification_uri_complete>
User code: <user_code>
After browser approval, run:
  ~/.hermes/profiles/gentech/scripts/complete_nous_device_flow.sh
```

---

## Verification After Re-Auth

1. Run the refresh script manually:
   ```bash
   ~/.hermes/profiles/<profile>/scripts/refresh_nous_oauth.py
   ```
   Should print JSON with `"success": true`.

2. Check token TTL:
   ```bash
   python3 -c "import json; d=json.load(open('~/.hermes/profiles/<profile>/auth.json')); exp=d['providers']['nous']['expires_at']; print(f'Expires: {exp}')"
   ```
   `expires_at` should be ~30 days from now (Nous tokens are long-lived).

3. Trigger one affected cron job manually:
   ```bash
   hermes cron run <job-id>
   ```
   Or run the underlying script directly from `~/.hermes/profiles/<profile>/scripts/`.

4. Confirm no new `needs_reauth` errors in subsequent cron runs (watch next 2–3 cycles).

---

## Prevention & Monitoring

The `Nous OAuth Proactive Refresh` cron job runs every 10 minutes (`*/10 * * * *`). That cadence is sufficient for a ~30-day TTL token. What matters is **escalation visibility**:

- ✅ Refresh script surfaces clear error with `needs_reauth: true` when recovery is impossible
- ⚠️ Silent mode: refresh script exits `0` on both success and `needs_reauth`; monitoring must parse JSON to detect auth issues (exit code alone insufficient)
- ⚠️ Gentech Watchdog currently monitors agent session errors only — it does NOT catch cron script auth failures
- **Recommendation:** Extend Watchdog prompt to include auth-state checks (query `auth.json` for expired tokens, check `last_error` fields in cron jobs for `needs_reauth`)

---

## Proactive Maintenance Confirmation

When the refresh script runs and tokens are already valid (within the 2-minute skew window), it returns a **success status** with no actual refresh performed. This is expected and healthy.

### Healthy Output Shape

```json
{
  "success": true,
  "message": "Tokens are fresh",
  "tokens": {
    "access_token_preview": "eyJhbG...NiIs...",
    "refresh_token_present": true,
    "expires_at": "2026-05-03T17:45:12.198597+00:00",
    "agent_key_expires_at": "2026-05-04T13:16:13.569Z"
  },
  "needs_reauth": false,
  "critical": false,
  "hermes_home": "/root/.hermes/profiles/gentech",
  "remaining_seconds": 244
}
```

**Key indicators of health:**
- `success: true` — script executed without error
- `needs_reauth: false` — refresh token still valid
- `remaining_seconds` > 0 — time until access token expiry (use this, not `obtained_at`, for TTL calculations)
- `refresh_token_present: true` — recovery mechanism intact

### Quick Verification

```bash
# Run refresh manually
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# Parse remaining TTL (requires jq)
python3 -c "import json; d=json.load(open('/root/.hermes/profiles/gentech/auth.json')); from datetime import datetime, timezone; exp=datetime.fromisoformat(d['providers']['nous']['expires_at'].replace('Z','+00:00')); print(f'Remaining: {int((exp - datetime.now(timezone.utc)).total_seconds())}s')"
```

**Expected:** `remaining_seconds` should be > 300 (5+ minutes) on a healthy run. If it's < 60 and decreasing on successive runs, the token is approaching expiry and refresh should trigger soon.

**Note:** The refresh script uses `resolve_nous_access_token()` which automatically refreshes only when `expires_at` is within the 2-minute skew window. Seeing `"Tokens are fresh"` with `remaining_seconds` still high means the pre-emptive refresh check determined no action was needed — that's correct behavior.

### Cron Job Location

- **Script:** `~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`
- **Cron registry:** `~/.hermes/profiles/gentech/cron/jobs.json` (look for `"Nous OAuth Proactive Refresh"`)
- **Schedule:** `*/10 * * * *` (every 10 minutes)
- **Delivery:** `local` (no Telegram noise on success)

If the job disappears from `jobs.json` or `enabled` flips to `false`, re-add it via `hermes cron` commands or direct JSON edit.

---

## Common Pitfalls

| Pitfall | How to avoid |
|---------|---------------|
| Refresh token also expired | The refresh script will detect this (`relogin_required: true`). Manual `hermes model` is the only fix. |
| Refresh script not deployed | Verify: `ls ~/.hermes/profiles/<profile>/scripts/refresh_nous_oauth.py`. If missing, copy from vault: `/root/vaults/gentech/00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py` |
| Cron job not scheduled | Check `cron/jobs.json` for `"Nous OAuth Proactive Refresh"` entry with `"script": "refresh_nous_oauth.py"` and `"enabled": true`. |
| Wrong HERMES_HOME in cron | Cron sets `HERMES_HOME` to profile dir. Script uses `os.environ.get("HERMES_HOME")` — never hardcode paths inside cron scripts. |
| Gateway still using stale token | Gateway process picks up new token on next request automatically (auth module reloads from `auth.json`). No restart needed. |
| Multiple profiles affected | Repeat this playbook for each profile (yoyo, dmob, desmond) if they share the same OAuth provider. |
| "Tokens are fresh" false positive | Refresh script returns `success: true` even when no refresh occurred (token still valid, not in 2-min skew window). Verify renewal by checking `obtained_at` timestamp advanced; do NOT rely on `"Tokens are fresh"` message alone. |

---

## Knowledge Base References

- Hermes Agent OAuth docs: `hermes login`, `hermes auth`, `hermes logout` commands
- Auth state file: `~/.hermes/profiles/<profile>/auth.json` (JSON with `providers.<name>.access_token`, `refresh_token`, `expires_at`)
- Refresh script logic: uses `hermes_cli.auth.resolve_nous_access_token()` — catches `AuthError` with `relogin_required` flag
- Provider token TTL: Nous access tokens ~30 days, refresh tokens similar. Plan re-auth before expiry if refresh fails.
- Rate-limit behavior: `references/nous-oauth-rate-limit-2026-05-03.md` — observed HTTP 429 on device code initiation during cascading revocation; fallback to manual `hermes model`
- **Auth state edge case:** `references/auth-empty-providers-with-stale-credential-pool-2026-05-03.md` — when `providers.<name>` is empty but `credential_pool` shows healthy; how to detect and recover
- **Post-mortem 2026-05-04:** `references/auth-incident-post-mortem-2026-05-04.md` — refresh script exit code 0 trap, stale pending flow cleanup, credential pool staleness verification, affected jobs inventory, HERMES_HOME path quirk, empty fallback_providers vulnerability

---

## Session Template (for future incidents)

When documenting a new auth incident:
1. Copy `00-HQ/Operations/Infrastructure-Issues.md` template block
2. Fill: provider, expiry time, script names, job IDs
3. Link to affected vault files (scripts, cron config)
4. Add Mess Hall flag with action + deadline if urgent
5. Delegate with `@<role>` and explicit command

---

**Skill version:** 1.0.0  
**Last updated:** 2026-05-03 (initial compile from Nous OAuth revocation incident)
