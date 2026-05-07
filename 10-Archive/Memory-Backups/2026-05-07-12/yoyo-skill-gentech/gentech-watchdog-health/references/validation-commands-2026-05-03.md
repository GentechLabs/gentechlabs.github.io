# Validation Commands — 2026-05-03 Fleet Failure

Run these to reproduce the diagnostic steps from the May 3 OAuth cascade incident.

## Quick health triage (one-liners)

```bash
# 1. Verify all 4 gateways are running
ps aux | grep 'hermes_cli.main --profile' | grep -v grep

# 2. Check recent Telegram responses (last 10 lines per agent)
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  tail -20 /root/.hermes/profiles/$p/logs/gateway.log | grep 'Sending response' | tail -5
done

# 3. Count errors in last 200 lines (high velocity = active degradation)
for p in yoyo dmob desmond gentech; do
  err=$(tail -200 /root/.hermes/profiles/$p/logs/agent.log 2>/dev/null | grep -ci ' error ')
  warn=$(tail -200 /root/.hermes/profiles/$p/logs/agent.log 2>/dev/null | grep -ci ' warning ')
  echo "[$p] ERRORS: $err | WARNINGS: $warn"
done
```

## OAuth token validation (DMOB critical)

```bash
# Check refresh script status (returns JSON)
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# Expected healthy output:
#   {"success": true, "message": "...", "needs_reauth": false, ...}
#
# Failure output (requires manual intervention):
#   {"success": false, "message": "No access token found...", "needs_reauth": true}

# Direct auth check (read expiry timestamp)
for p in yoyo dmob desmond gentech; do
  echo "[$p] $(cat /root/.hermes/profiles/$p/auth.json 2>/dev/null | jq -r '.nous_credentials?.access_token_expiry // "missing"')"
done
```

## Error pattern extraction

```bash
# Find all ERROR lines with context (last 50)
tail -50 /root/.hermes/profiles/gentech/logs/agent.log | grep -E ' ERROR ' | head -10

# Check for specific OAuth/credential failure patterns
grep -rni 'Refresh session has been revoked' /root/.hermes/profiles/*/logs/ 2>/dev/null | head
grep -rni 'needs_reauth' /root/.hermes/profiles/*/logs/ 2>/dev/null | head
grep -rni 'Firecrawl.*missing.*auth' /root/.hermes/profiles/*/logs/ 2>/dev/null | head
```

## Cron job health

```bash
# List all Gentech cron jobs with last run status
jq '.jobs[] | "\(.name) | schedule=\(.schedule.display) | enabled=\(.enabled) | last=\(.last_run_at // "never") | status=\(.last_status // "unknown")"' /root/.hermes/cron/jobs.json

# Filter to failed jobs
jq '.jobs[] | select(.last_status != "ok") | "\(.name): \(.last_error // "no error message")"' /root/.hermes/cron/jobs.json
```

## Coordination board sanity check

```bash
# The coordination board may show OFFLINE even when gateways run.
# Always cross-check with process list:
echo "=== Coordination board status ==="
grep -A3 'Agent.*Status' /root/vaults/gentech/11-Mess\ Hall/agent-coordination-board.md

echo -e "\n=== Actual process status ==="
ps aux | grep 'hermes_cli.main --profile' | grep -v grep | awk '{print $11" "$12" "$13" "$14}'
```

## Watchdog self-degradation check

```bash
# Check latest watchdog session for empty responses
latest=$(ls -t /root/.hermes/profiles/yoyo/sessions/session_cron_9ecfada01952_*.json 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  echo "Latest watchdog session: $latest"
  echo "Messages total: $(grep -c '"role":' "$latest")"
  echo "Empty assistant responses: $(grep -c '"content": ""' "$latest" 2>/dev/null || echo 0)"
  echo "Tool calls made: $(grep -o '"tool_calls_made": [0-9]*' "$latest" | tail -1 | cut -d: -f2)"
fi
```

## Recovery verification

After running `hermes model` to re-authenticate:

```bash
# 1. Verify refresh script succeeds
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py | jq '.success'

# 2. Check gateway logs for new successful calls
tail -30 /root/.hermes/profiles/gentech/logs/gateway.log | grep -E 'response ready|Sending response'

# 3. Verify cron jobs resume
jq '.jobs[] | select(.name | test("Mess Hall|Pre-Shift|Post-Shift")) | "\(.name) last=\(.last_run_at) status=\(.last_status)"' /root/.hermes/cron/jobs.json
```

## File locations reference

- Agent logs: `/root/.hermes/profiles/<yoyo|dmob|desmond|gentech>/logs/`
  - `agent.log` — Agent execution errors
  - `gateway.log` — Telegram message handling
  - `errors.log` — Aggregated error stream
- Cron jobs: `/root/.hermes/cron/jobs.json` (config) and `jobs.db` (runtime state)
- Refresh script: `/root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`
- Auth state: `/root/.hermes/profiles/<profile>/auth.json`
- Coordination board: `/root/vaults/gentech/11-Mess Hall/agent-coordination-board.md`
