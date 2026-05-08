# Nous OAuth Rate Limit Observations

**Date observed:** 2026-05-03  
**Session:** `nous-oauth-revoked-2026-05-03-1917`  
**Profile:** gentech

## Endpoint Behavior

| Endpoint | Method | Purpose | Rate Limit Observed |
|----------|--------|---------|---------------------|
| `POST /oauth/device/code` | POST | Initiate device authorization flow | **429** after repeated refresh script failures (~every 10 min) |
| `POST /oauth/token` (device flow completion) | POST | Poll for tokens with device_code | Unknown (not reached due to 429 on initiation) |

## Trigger Conditions

The rate limit was hit when:
1. Refresh token was revoked (`needs_reauth: true`)
2. `refresh_nous_oauth.py` cron job ran every 10 minutes and failed repeatedly
3. A manual attempt to initiate device flow (`_nous_device_code_login` with `open_browser=False`) was made ~27 minutes after initial failure
4. Multiple concurrent automated agents were likely invoking refresh

**Hypothesis:** Nous Portal rate-limits device code initiation per IP/client when the underlying refresh token is invalid and attempts are frequent. This is a protection mechanism preventing brute-force or runaway renewal loops.

## Recovery Path

When 429 is encountered:
1. **STOP** all automated device flow attempts immediately
2. **ESCALATE** to manual intervention: `hermes model` interactive flow
3. **WAIT** 5–10 minutes before any retry if attempting programmatic path again
4. **DOCUMENT** the 429 occurrence in incident log with timestamp

The interactive `hermes model` path uses a different endpoint flow (browser-based OAuth consent) and is not subject to the same device code rate limits.

## Code Recast

```python
import httpx

def initiate_device_code_safe():
    """Initiate device flow with rate-limit detection."""
    resp = httpx.post(
        "https://portal.nousresearch.com/oauth/device/code",
        data={"client_id": "hermes-cli", "scope": "inference:mint_agent_key"},
        timeout=10.0
    )
    if resp.status_code == 429:
        raise RuntimeError(
            "Device code endpoint rate-limited (HTTP 429). "
            "Fallback to manual 'hermes model' re-authentication required."
        )
    resp.raise_for_status()
    return resp.json()
```

## Impact on `hermes-auth-incident-response` Skill

This observation was integrated into the skill as:
- **New Step 4** in Non-Interactive Recovery: "Rate Limit Detection & Fallback"
- **New pitfall** in the Pitfalls table: "Device code endpoint rate-limited (HTTP 429)"

**Rule:** When `_nous_device_code_login()` or direct POST to `/oauth/device/code` returns 429, do not retry programmatically. Escalate to manual `hermes model`.
