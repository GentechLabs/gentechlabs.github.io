# Fleet-Wide Nous Portal OAuth Revocation — May 4, 2026

**Detection time:** 2026-05-04 00:50 UTC  
**Agents affected:** YoYo, DMOB, Desmond, Gentech (100% of fleet)  
**Severity:** CRITICAL — blocks all LLM-dependent cron jobs and Telegram responses requiring model inference

## Symptom Summary

| Indicator | Observation | Expected |
|-----------|-------------|----------|
| `auth.json` access_token | `MISSING` (all 4 agents) | Valid JWT (~20-30 char base64) |
| `auth.json` refresh_token | `MISSING` (all 4 agents) | Long-lived refresh credential |
| Proactive refresh job output | `"success": false, "message": "Refresh session has been revoked"` | `"success": true, "needs_reauth": false` |
| Error log errors (last ~200 lines) | 32–38 ERROR entries per agent | Sporadic, not flood |\n| TTS 401 errors | 110–356 per agent (quota exceeded) | 0 or occasional transient |\n| Gateway log freshness | All agents show last write <65s ago (healthy) | — |\n| Cron output freshness | YoYo fresh (27 outputs/2h), DMOB stale (1 output 1.9h), Desmond 1 output 0.9h) | All should produce per-schedule outputs |\n| Active provider | `nous` configured but tokens missing | Nous operational |\n| `hermes model` status | Interactive auth required | Already authenticated |\n\n## Root Cause

All four agents' Nous Portal refresh tokens were revoked simultaneously. The cause is not definitively known but likely one of:
- **Shared Nous account credential rotation** — token rotated/revoked on Nous side
- **Session expiry policy change** — refresh tokens have max lifetime (observed: expiry 2026-05-03 22:11:54 UTC)
- **Portal-side security action** — suspicious activity or forced revocation
- **Hermes OAuth implementation bug** — tokens not persisted or refreshed correctly across all profiles

**Key observation:** The Gentech "Nous OAuth Proactive Refresh" cron job (ID: `286d9b3925b4`, schedule `*/10 * * * *`) explicitly reported `"needs_reauth": true` and `"Refresh session has been revoked"`. This confirms the refresh endpoint is still reachable but refuses to issue new access tokens.

## Impact

1. **Model API calls blocked** — Any cron job or skill that calls `llm_tool` or similar fails with "No access token found" or "Refresh session has been revoked"
2. **Cron jobs degrade** — Jobs dependent on LLM fail; only non-LLM jobs (e.g., raw scraping, metric collection) may succeed
3. **No automatic recovery** — The refresh script cannot recover; requires manual interactive `hermes model` re-authentication per agent profile
4. **Fleet-wide dependency** — Since all agents share the same Nous Portal identity, revival must happen across **all four profiles** individually

## Detection Pattern (Watchdog Routine)

```python
import json, os, re
from datetime import datetime

agents = ['yoyo', 'dmob', 'desmond', 'gentech']
fleet_oauth_status = {}

for agent in agents:
    auth_file = f'/root/.hermes/profiles/{agent}/auth.json'
    
    # Primary signal: auth.json missing tokens
    try:
        with open(auth_file) as f:
            auth = json.load(f)
        nous_data = auth.get('nous', {}) or auth.get('nous_tokens', {})
        access = nous_data.get('access_token', 'MISSING')
        refresh = nous_data.get('refresh_token', 'MISSING')
        has_access = access != 'MISSING' and len(access) > 10
        has_refresh = refresh != 'MISSING' and len(refresh) > 10
    except Exception as e:
        has_access = has_refresh = False
    
    # Secondary signal: OAuth refresh job latest output
    out_dir = f'/root/.hermes/profiles/{agent}/cron/output/'
    refresh_failed = False
    try:
        for root, dirs, files in os.walk(out_dir):
            for d in dirs:
                if 'oauth' in d.lower() or 'refresh' in d.lower():
                    dir_path = os.path.join(root, d)
                    md_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
                    if md_files:
                        latest = sorted(md_files)[-1]
                        with open(os.path.join(dir_path, latest)) as f:
                            content = f.read()
                        if '"success": false' in content or 'revoked' in content.lower():
                            refresh_failed = True
    except: pass
    
    fleet_oauth_status[agent] = {
        'access_token': has_access,
        'refresh_token': has_refresh,
        'refresh_job_failed': refresh_failed
    }

# Cross-agent correlation
revoked_count = sum(1 for v in fleet_oauth_status.values() if not v['access_token'])
if revoked_count == len(agents):
    print(f"🚨 FLEET-WIDE OAUTH REVOCATION — all {len(agents)} agents lack Nous tokens")
    print("   Immediate action: run `hermes model` in each agent profile to re-authenticate")
else:
    print(f"Partial OAuth failure: {revoked_count}/{len(agents)} agents affected")
```

## Required Remediation

**Manual intervention required (cannot be automated via cron):**

```bash
# For each agent (run sequentially in interactive shell):
for agent in yoyo dmob desmond gentech; do
    echo "=== Re-authenticating $agent ==="
    hermes --profile $agent model  # Follow OAuth flow in browser/device
done
```

**Post-recovery verification steps:**
```bash
# 1. Verify tokens persisted to auth.json
for agent in yoyo dmob desmond gentech; do
    python3 -c "import json; a=json.load(open('/root/.hermes/profiles/$agent/auth.json')); \
                print('$agent:', 'nous_tokens' in a and 'access_token' in a.get('nous_tokens',{}))"
done

# 2. Run proactive refresh script and expect success
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
# Expected output: {"success": true, "needs_reauth": false}

# 3. Verify a sample Nous-dependent cron job executes
hermes --profile yoyo cron run 682e9597b8d6  # Gentech LLC Reminder (non-LLM fallback possible)
```

## Historical Timeline (Incident Context)

- **2026-05-03 22:11:54 UTC** — Access token expires (observed in Gentech refresh job output)
- **2026-05-03 22:47–23:00** — Multiple agents show TTS 401 floods (secondary symptom as ElevenLabs also quota-exceeded)
- **2026-05-04 00:20–00:50** — Gateway logs show healthy Telegram activity (agents still responding to messages)
- **2026-05-04 00:50:51** — Gentech proactive refresh job runs and explicitly reports `Refresh session has been revoked`
- **2026-05-04 00:52–01:10** — Watchdog health check confirms all 4 agents have `MISSING` tokens in `auth.json`

**Note:** Agents may still respond to Telegram messages **if the request does not require LLM inference** (e.g., simple commands, cached responses). However, any skill invoking `llm_tool` will fail.

## Related Failures Masked by OAuth Issue

- **ElevenLabs TTS 401** — Likely correlated; both provider credentials expired around same window
- **Missing Anthropic credentials** — DMOB/Desmond jobs requiring Claude fail independently (unrelated configuration debt)
- **Cron output staleness** — DMOB/Desmond showing 1.9h/0.9h lag may be due to LLM-dependent jobs failing early in pipeline

## Prevention & Early Warning

**Add to Watchdog (gentech-agent-health):**

1. Include auth.json token presence check in every health scan
2. Alert when **any** agent shows `access_token: MISSING`
3. Escalate to **fleet-wide** when ≥3/4 agents show same pattern within 1 hour
4. Trigger proactive refresh job and parse its `needs_reauth` flag

**Scheduled pre-emptive refresh:** Current `*/10 * * * *` proactive refresh is too frequent and still fails. Consider:
- Reducing to `*/30 * * * *` to avoid noise
- Adding alert to Telegram if refresh fails
- Auto-escalation to Jordan if all agents show `needs_reauth: true`

---

**Last updated:** 2026-05-04 01:52 UTC (watchdog session `cron_9ecfada01952_20260504_005235`)  
**Incident ID:** I-2026-05-04-OAUTH-REVOKE  
**Status:** UNRESOLVED — manual re-authentication pending
