# Device Code Rate Limiting — 2026-05-06 Incident

**Incident:** HTTP 429 from Nous device code endpoint during OAuth recovery  
**Impact:** Automated recovery blocked, required manual intervention  
**Root Cause:** Multiple concurrent device flow attempts triggered rate limiting

## Problem

The Nous OAuth device code endpoint (`/oauth/device/code`) enforces rate limits. When multiple Hermes profiles attempt to initiate device flow simultaneously (e.g., during a shared token expiration event), the endpoint returns HTTP 429, blocking automated recovery.

### Observed Behavior

- **gentech** refresh script attempted device flow initiation
- **yoyo, dmob, desmond** profiles also needed recovery but lacked scheduled refresh
- Concurrent attempts from multiple profiles (or even multiple attempts from one profile) triggered rate limiting
- Non-interactive device flow became unavailable
- Manual `hermes model` path required as fallback

## Detection

### Identify Rate Limit Errors

```python
import httpx

def is_rate_limit_error(response):
    """Detect HTTP 429 or rate limit errors"""
    if response.status_code == 429:
        return True
    # Some APIs return 403 with rate limit headers
    if response.status_code == 403 and "rate-limit" in response.text.lower():
        return True
    # Check for rate limit headers
    if response.headers.get("X-RateLimit-Remaining") == "0":
        return True
    return False
```

### Monitor Device Code Endpoint Health

```bash
# Check recent gateway logs for rate limit patterns
tail -50 ~/.hermes/profiles/gentech/logs/gateway.log | grep -i "rate\|429\|throttle"

# Monitor auth script errors
grep -i "rate\|429" ~/.hermes/profiles/gentech/logs/cron/*.log
```

## Enhanced Handling Procedures

### 1. Immediate Response to Rate Limiting

When device code endpoint returns 429:

1. **Abort further automated attempts** — additional retries will worsen throttling
2. **Escalate to manual `hermes model`** — bypasses rate-limited endpoint entirely
3. **Document the rate limit** in incident log with timestamp
4. **Implement cooldown period** (5-10 minutes) before retrying
5. **After cooldown, retry device flow once** — if still 429, continue with manual path

### 2. Proactive Rate Limit Prevention

**Stagger Refresh Schedules:** Prevent concurrent device flow attempts by spacing out refresh times across profiles.

```bash
# gentech: every 10 minutes (baseline)
gentech: */10 * * * *

# yoyo: every 10 minutes, offset by 20 minutes
yoyo: 20,50 * * * *

# dmob: every 10 minutes, offset by 40 minutes
dmob: 40,10 * * * *

# desmond: every 10 minutes, offset by 0 and 30 minutes
desmond: 0,30 * * * *
```

**Implement Global Rate Limit Semaphore:**

```python
import threading
import time

# Global semaphore to prevent concurrent device flow attempts
device_flow_semaphore = threading.Semaphore(1)

def safe_device_flow_initiation():
    """Acquire semaphore before attempting device flow"""
    if not device_flow_semaphore.acquire(blocking=False):
        print("Device flow already in progress — skipping attempt")
        return None
    
    try:
        # Perform device flow initiation
        result = _nous_device_code_login(open_browser=False, timeout_seconds=5.0)
        return result
    finally:
        device_flow_semaphore.release()
```

### 3. Enhanced Error Handling

Update refresh scripts to:

- Detect rate limit errors explicitly
- Implement exponential backoff with jitter
- Escalate to manual path after threshold
- Log rate limit occurrences for analysis

```python
import time
import random
from hermes_cli.auth import _nous_device_code_login

def initiate_with_rate_limit_protection(max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            # 30-second timeout to prevent hanging
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Device flow initiation timed out")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            result = _nous_device_code_login(
                open_browser=False,
                timeout_seconds=5.0,
                min_key_ttl_seconds=300
            )
            signal.alarm(0)
            return result
            
        except TimeoutError:
            raise RuntimeError("Device flow initiation timed out after 30 seconds")
            
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                if attempt < max_retries:
                    cooldown = 300  # 5 minutes
                    print(f"Rate limited — waiting {cooldown} seconds before retry...")
                    time.sleep(cooldown + random.uniform(0, 60))  # Add jitter
                    continue
                else:
                    raise RuntimeError(
                        "Device code endpoint rate-limited after retries. "
                        "Switch to manual `hermes model` re-authentication."
                    )
            else:
                raise
```

## Production Recommendations

### 1. Monitoring & Alerting
- Set up alerts for HTTP 429 errors from device code endpoint
- Monitor concurrent device flow attempts across profiles
- Track token expiration times for all profiles
- Alert when multiple profiles share identical expiration times

### 2. Infrastructure Changes
- **Implement per-profile token isolation** — ensure each profile has independent token lifecycle
- **Add rate limit headers** to device code endpoint responses for better detection
- **Consider token vending service** — centralize OAuth management with better rate limit handling

### 3. Operational Procedures
- **Always check for rate limiting** when device flow fails
- **Default to manual `hermes model`** when rate limits are detected
- **Document rate limit fallback procedures** in incident response playbooks
- **Regularly audit** cross-profile dependencies and refresh schedules

## Lessons Learned

**Key Takeaways:**
- Shared tokens create systemic risk and rate limit amplification
- Automated recovery paths can be blocked by the same failures they're trying to fix
- Manual intervention paths are essential safety nets
- Proactive rate limit prevention is better than reactive handling

**Action Items from 2026-05-06 Incident:**
- [ ] Stagger refresh schedules across all profiles
- [ ] Implement global rate limit semaphore
- [ ] Add fallback providers to all config.yaml
- [ ] Create cross-profile monitoring dashboard
- [ ] Document rate limit handling procedures

## References

- Original incident: 2026-05-06 Nous OAuth revocation
- Affected profiles: gentech, yoyo, dmob, desmond
- Endpoint: `https://portal.nousresearch.com/oauth/device/code`
- Error code: HTTP 429 (Too Many Requests)