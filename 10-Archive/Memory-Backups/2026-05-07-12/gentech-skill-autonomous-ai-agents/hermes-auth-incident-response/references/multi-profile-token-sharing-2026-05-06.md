# Multi-Profile Token Sharing Vulnerability

**Discovered:** 2026-05-06 during Nous OAuth incident  
**Impact:** Single point of failure across entire agent fleet  
**Affected:** gentech, yoyo, dmob, desmond profiles  

## Problem

All four Hermes profiles share the same Nous token instance. When the primary token expires, **all profiles become unavailable simultaneously**, creating a system-wide outage.

### Root Causes

1. **Token provisioning:** All profiles were configured using the same device flow or re-authentication process
2. **Lack of isolation:** No per-profile token management strategy
3. **Missing refresh scheduling:** Not all profiles had refresh cron jobs configured

## Detection

### Check Token Expiration Across Profiles

```bash
for profile in gentech yoyo dmob desmond; do
  if [ -f "/root/.hermes/profiles/$profile/auth.json" ]; then
    expires=$(jq -r '.providers.nous.expires_at' "/root/.hermes/profiles/$profile/auth.json" 2>/dev/null)
    if [ "$expires" != "null" ]; then
      echo "$profile: expires at $expires"
    fi
  fi
done
```

**Expected output (problem indicator):**
```
gentech: expires at 2026-05-06T12:38:54.268608+00:00
yoyo: expires at 2026-05-06T12:38:54.268608+00:00
dmob: expires at 2026-05-06T12:38:54.268608+00:00
desmond: expires at 2026-05-06T12:38:54.268608+00:00
```

### Check Refresh Scheduling

```bash
# Check which profiles have refresh cron jobs
for profile in gentech yoyo dmob desmond; do
  if [ -f "/root/.hermes/profiles/$profile/cron/jobs.json" ]; then
    has_job=$(jq '.jobs[] | select(.script | contains("nous") or contains("refresh"))' "/root/.hermes/profiles/$profile/cron/jobs.json")
    if [ -z "$has_job" ]; then
      echo "$profile: NO refresh cron job"
    else
      echo "$profile: has refresh cron job"
    fi
  else
    echo "$profile: no cron configuration"
  fi
done
```

## Impact Assessment

### Single Point of Failure
- When shared token expires, **entire agent fleet goes offline**
- No fallback capability during recovery
- Rate limiting affects all profiles simultaneously

### Rate Limit Exacerbation
- Multiple profiles attempting device flow → higher chance of HTTP 429
- Concurrent attempts can trigger cascading failures
- Recovery time increases for all services

## Mitigation Strategies

### Immediate Actions (P0)
1. **Schedule refresh for all profiles** — ensure each profile has its own refresh cron job
2. **Add fallback providers** to all profiles' config.yaml
3. **Document shared token risk** in incident response procedures

### Medium-Term Solutions
1. **Implement staggered refresh schedules** — avoid concurrent refresh attempts
   ```bash
   # Example: gentech every 10min, yoyo every 10min at :20, :50, dmob at :40, :10
   gentech: */10 * * * *
   yoyo: 20,50 * * * *
   dmob: 40,10 * * * *
   desmond: 0,30 * * * *
   ```
2. **Create per-profile tokens** — isolate token expiration times
3. **Implement global rate limit semaphore** — prevent concurrent device flow attempts

### Long-Term Architectural Changes
1. **Profile-specific OAuth flows** — each profile should have independent token lifecycle
2. **Centralized auth monitoring** — track all profiles' token states
3. **Automated cross-profile health checks** — detect shared tokens and scheduling gaps

## Prevention

### Configuration Management
Ensure each profile has:
- ✅ Independent OAuth token (or at least staggered expiration)
- ✅ Scheduled refresh cron job
- ✅ Fallback providers configured
- ✅ Monitoring alerts for auth failures

### Monitoring Alerts
Set up alerts for:
- Multiple profiles with identical token expiration times
- Profiles missing refresh cron jobs
- Auth failures across multiple profiles simultaneously
- Rate limit errors on device code endpoint

### Incident Response Updates
- Add cross-profile impact assessment to incident declaration checklist
- Include multi-profile verification in post-recovery checklist
- Create specific templates for multi-profile incidents

## Lessons Learned

**2026-05-06 Incident Summary:**
- Shared tokens create systemic risk
- Rate limiting can block automated recovery
- Cross-profile dependencies must be documented
- Fallback providers are not optional — they're critical infrastructure

**Key Takeaway:** Treat OAuth tokens as single points of failure. Isolate them across services or implement robust fallback mechanisms.