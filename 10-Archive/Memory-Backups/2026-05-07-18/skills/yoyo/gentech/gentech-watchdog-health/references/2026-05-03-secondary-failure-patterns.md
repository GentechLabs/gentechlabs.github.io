
# Secondary Failure Patterns — 2026-05-03 Fleet Degradation

## Overview

This reference documents four systemic failure patterns observed during the May 3, 2026 fleet-wide degradation event. These patterns co-occurred with the primary Nous OAuth cascade but represent independent, recurring fault modes that future watchdog runs should detect and flag separately.

All patterns were observed across multiple agents within a 30-minute window (23:00–23:30 UTC) and produced correlated error bursts.

---

## 1. Firecrawl Tool Initialization Failure

**Error signature:**
```
ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth
```
Appears repeatedly in `errors.log` (YoYo: 5+ in <1 minute; Gentech: 7+).

**Root causes:**
- `FIRECRAWL_API_KEY` missing from agent `.env` file
- Tool-gateway permission binding not established (tool registry entry lacks `auth_scope: tool-gateway`)
- Firecrawl provider endpoint unreachable or misconfigured

**Diagnostic checklist:**
```bash
# 1. Check for Firecrawl errors in last 100 lines
grep -i "firecrawl" /root/.hermes/profiles/*/logs/errors.log | tail -20

# 2. Verify environment variable presence (in running process)
for p in yoyo dmob desmond gentech; do
  PID=$(pgrep -f "hermes_cli.main --profile $p")
  if [ -n "$PID" ]; then
    echo "[$p] FIRECRAWL_API_KEY=$(tr '\0' '\n' < /proc/$PID/environ | grep FIRECRAWL_API_KEY || echo 'NOT SET')"
  fi
done

# 3. Check config.yaml for provider config
grep -A2 -B2 "firecrawl" /root/.hermes/profiles/*/config.yaml
```

**Remediation:**
- If missing: add `FIRECRAWL_API_KEY=<valid-key>` to agent `.env` and restart gateway
- If present but still failing: verify tool-gateway binding in tool registry (`/usr/local/lib/hermes-agent/tools/registry.json` or equivalent)
- If endpoint unreachable: check network egress to `api.firecrawl.dev` and token validity

**Watchdog alert phrasing:** `🚨 Watchdog Alert: Firecrawl tool failing fleet-wide — missing API credentials` or agent-specific: `🚨 Watchdog Alert: YoYo Firecrawl config missing`

---

## 2. Vision Tool 404 Errors

**Error signature:**
```
ERROR tools.vision_tools: Error analyzing image: Error code: 404 - {'status': 404, 'message': "Couldn't find that, sorry."}
```
Followed by traceback through `auxiliary_client.py` and `openai` SDK. Affected all agents (YoYo, Desmond, Gentech).

**Root causes:**
- Vision model (e.g., `gpt-4-vision-preview`) unavailable in the configured OpenAI organization
- Provider `openai` not registered in `auth.json` `providers` mapping
- OPENAI_API_KEY valid but lacks vision model access (quota or plan restriction)
- Fallback provider not configured; default provider lookup fails with 404

**Diagnostic checklist:**
```bash
# 1. Count vision errors per agent (last 200 lines)
for p in yoyo dmob desmond gentech; do
  count=$(grep -c "vision_tools.*404" /root/.hermes/profiles/$p/logs/errors.log)
  echo "[$p] Vision 404 count: $count"
done

# 2. Check active provider in auth.json
python3 -c "
import json, glob
for p in ['yoyo','dmob','desmond','gentech']:
  d=json.load(open(f'/root/.hermes/profiles/{p}/auth.json'))
  print(p, 'active:', d.get('active_provider'), 'providers:', list(d.get('providers',{}).keys()))
"

# 3. Verify OPENAI_API_KEY in process environment
for p in yoyo dmob desmond gentech; do
  PID=$(pgrep -f "hermes_cli.main --profile $p")
  [ -n "$PID" ] && echo "[$p] OPENAI_API_KEY set: $(tr '\0' '\n' < /proc/$PID/environ | grep -c OPENAI_API_KEY)"
done
```

**Remediation:**
- Confirm OpenAI organization has vision API access; upgrade plan or request quota if needed
- Add `openai` to `auth.json` providers with valid token if missing
- Set `OPENAI_API_KEY` in agent `.env` and restart
- As temporary mitigation, disable vision tool in agent config (`disabled_tools: [vision_analyze]`) to stop error flood

**Watchdog alert phrasing:** `🚨 Watchdog Alert: Vision tool failing fleet-wide — provider misconfigured`

---

## 3. Interpreter Shutdown Race

**Error signature:**
```
RuntimeError: cannot schedule new futures after interpreter shutdown
```
Observed in DMOB and Gentech cron delivery failures: `⚠ Delivery failed: delivery error: Telegram send failed: Unknown error in HTTP implementation: RuntimeError('cannot schedule new futures after interpreter shutdown')`.

**Root causes:**
- Gateway shutdown sequence initiated while background tasks (Telegram send, tool calls) still pending
- Event loop teardown raced with futures submission; common during coordinated multi-agent restarts
- Worker thread pool explicitly closed before all work completed

**Diagnostic checklist:**
```bash
# 1. Search for shutdown-related errors in gateway.log
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  grep -i "shutdown\|interpreter" /root/.hermes/profiles/$p/logs/gateway.log | tail -10
done

# 2. Check for rapid restart loops (multiple SIGTERM within 5 minutes)
for p in yoyo dmob desmond gentech; do
  count=$(grep -c "SIGTERM" /root/.hermes/profiles/$p/logs/gateway.log)
  echo "[$p] SIGTERM count (last 200 lines): $count"
done

# 3. Verify graceful shutdown timeout settings
grep -E "shutdown|timeout" /root/.hermes/profiles/*/config.yaml
```

**Remediation:**
- Ensure gateways are not being triggered to restart while jobs are mid-execution; add a debounce (e.g., `systemctl --user restart` with `sleep` between agents)
- Increase shutdown grace period in gateway config (`shutdown_timeout: 120` or higher)
- If using coordinated restart scripts (like `snap-*.sh`), insert a `sleep 10` between each `systemctl restart` to let each gateway fully exit before starting the next
- Check for external orchestration (cron or monitoring) that may be triggering simultaneous restarts; serialize restarts

**Watchdog alert phrasing:** `🚨 Watchdog Alert: Interpreter shutdown race causing cron delivery failures` (if cron output shows this error pattern)

---

## 4. Telegram Delivery — Chat Not Found

**Error signature:**
```
⚠ Delivery failed: delivery error: Telegram send failed: Chat not found
```
Observed in Gentech cron delivery (Watchdog, HQ Update). Indicates Telegram bot is not a member of the target chat or chat ID changed.

**Root causes:**
- Bot removed from group/channel
- Chat ID stale (group recreated, old ID invalid)
- Bot's `chat_id` configuration in cron job (`deliver: "telegram:-100XXXXX"`) no longer valid

**Diagnostic checklist:**
```bash
# 1. Find failing Telegram deliveries in cron output or errors.log
grep -i "chat not found" /root/.hermes/profiles/*/logs/*.log

# 2. Identify the cron job name and target chat
grep -B5 "Chat not found" /root/.hermes/cron/output/*.json 2>/dev/null | head -20

# 3. Verify bot still in target group: use Telegram CLI or manually check
#    The bot must be an active member; reinvite if necessary
```

**Remediation:**
- Re-invite the bot to the target Telegram group/channel using the bot's invite link
- Update the `deliver` field in affected cron jobs with the correct `-100` chat ID
- If using a personal chat (user ID), ensure the bot has messaged that user first (Telegram restriction)

**Watchdog alert phrasing:** `🚨 Watchdog Alert: Telegram bot not in target chat — delivery failing for <agent>`

---

## Cross-Cutting Notes

### Error Velocity Thresholds

When counting repeated errors to distinguish loops from bursts:
- **10+ identical errors** within 200 lines = **looping/stuck** (agent-specific)
- **>50 errors** fleet-wide in 10 minutes = **systemic third-party failure** (e.g., ElevenLabs, OpenAI vision outage)
- **<5 errors** across all agents = noise; ignore

### Cron DB Parser Error

If `hermes cron list` or internal code raises:
```
AttributeError: 'str' object has no attribute 'get'
```
This indicates `jobs.json` contains array elements that are JSON **strings** rather than objects. Cause: previous write failure that serialized stringified JSON into the array.

**Fix:** Stop all gateways → edit `jobs.json` → replace string entries with proper objects (copy from backup or vault `00-HQ/Operations/cron-registry.json`) → restart gateways. If unrecoverable, rebuild from canonical job definitions in vault.

### No Recovery Without TTY

The `hermes model` re-authentication requires an interactive TTY session. Cron-based auto-recovery cannot proceed without manual intervention. The watchdog should flag any `needs_reauth: true` state as requiring **human attention**, not automated fix.

---

## Related

- Primary failure mode: `2026-05-03-nous-oauth-cascade-failure.md`
- Cron repair: `cron-repair-procedure.md`
- Bytecode corruption: `detect_bytecode_corruption.py`
