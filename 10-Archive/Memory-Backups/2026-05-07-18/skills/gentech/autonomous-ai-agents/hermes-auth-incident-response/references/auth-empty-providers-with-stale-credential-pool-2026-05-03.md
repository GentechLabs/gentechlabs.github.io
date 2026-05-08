# Auth State Edge Case: Empty Providers with Stale Credential Pool

**Observed:** 2026-05-03 — Gentech profile Nous OAuth incident  
**Skill:** `hermes-auth-incident-response`  
**Related:** `references/hermes-home-path-quirk-2026-05-03.md`

## Symptom

`refresh_nous_oauth.py` returns `needs_reauth: true` with message *"Hermes is not logged into Nous Portal"*, yet:

```json
{
  "credential_pool": {
    "nous": [{ "last_status": "ok", "last_error_code": null }]
  },
  "providers": {}
}
```

The credential pool shows `status=ok` (healthy), but the `providers` dict is empty — no tokens cached.

## Root Cause

The OAuth tokens were completely removed from `providers.nous` (manual revocation, cache clear, or profile corruption), while the credential pool metadata remained from a prior successful auth. The credential pool is **not** a real-time reflection of current token availability; it's a historical record of credential health.

## Diagnostic Differentiation

| Check | If token merely expired | If tokens completely missing |
|-------|------------------------|----------------------------|
| `providers.nous` exists? | ✅ Yes (object with fields) | ❌ No (`{}` or `null`) |
| `providers.nous.access_token` present? | ✅ Yes | ❌ No |
| `providers.nous.expires_at` in past? | ✅ Yes | N/A (no token) |
| `providers.nous.refresh_token` present? | ✅ Yes (usually) | ❌ No |
| `credential_pool.nous[0].last_status` | "ok" | "ok" (stale) |
| Refresh script `needs_reauth` | ✅ true | ✅ true |
| Recovery path | Auto-refresh possible if refresh_token valid | Manual `hermes model` required |

## Key Rule

**Never use `credential_pool.*.last_status` to judge current token availability.** It only tells you the last time a credential *worked*, not whether tokens are presently cached.

Always inspect `.providers.<name>` directly:
- `providers.<name>` missing/empty → no tokens at all
- `providers.<name>.access_token` missing → corrupted/incomplete token cache
- `providers.<name>.expires_at` past → token expired (check refresh_token presence)

## Recovery

Both cases require action, but timing differs:
- **Expired but tokens present:** Refresh script may auto-recover within 2-min skew window; if not, `needs_reauth: true` still means manual `hermes model`.
- **Tokens missing:** Immediate manual `hermes model` — refresh token cannot be used because it's not cached.

In this incident (empty providers), the refresh script could not proceed because there was no refresh_token to present to the token endpoint.

## Prevention

Ensure `fallback_providers` is non-empty in `config.yaml` so a single provider's token loss doesn't block all inference. After any OAuth re-auth, verify fallback chain includes at least one healthy API-key provider (e.g., `ollama-cloud`, `opencode-go`, `local`).
