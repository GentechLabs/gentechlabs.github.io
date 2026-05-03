# Agent Log Query Cheatsheet — One-Liners for Fast Triage

## Per-Agent Quick Status

```bash
for agent in yoyo dmob desmond gentech; do
  errs=$(grep -icE "(error|exception|failed)" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  boots=$(grep -c "Starting Hermes Gateway" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  disc=$(grep -c "Telegram.*Disconnected" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  echo "$agent: errors=$errs boots=$boots disconnects=$disc"
done
```

## Credential Gap Detection (All Agents)

```bash
# Anthropic missing (DMOB)
grep -i "No Anthropic credentials" /root/.hermes/profiles/*/logs/agent.log

# ElevenLabs 401 (Desmond)
grep -i "elevenlabs.*401" /root/.hermes/profiles/desmond/logs/agent.log | wc -l

# Provider key missing (Gentech/YoYo)
grep -E "Provider '.*' is set in config.yaml but no API key" /root/.hermes/profiles/*/logs/gateway.log
```

## Gateway Stability Check

```bash
# Count abnormal exits per agent
for a in yoyo dmob desmond gentech; do
  exits=$(grep -c "Exiting with code 1" /root/.hermes/profiles/$a/logs/gateway.log 2>/dev/null || echo 0)
  echo "$a abnormal exits: $exits"
done

# Get last crash traceback (per agent)
agent=gentech
tac /root/.hermes/profiles/$agent/logs/gateway.log | grep -m1 -B40 "Exiting with code 1" | tail -45
```

## Cron Job Health

```bash
# Find all cron failures across agents
grep -i "Job '.*' failed" /root/.hermes/profiles/*/logs/agent.log

# Check cron ticker stopped without restart (orphaned)
grep "Cron ticker stopped" /root/.hermes/profiles/*/logs/gateway.log | grep -v "Stopping gateway for restart"
```

## Connection Fallback Storms

```bash
# Count "connection error on auto" fallbacks (auxiliary client failures)
for a in yoyo dmob desmond gentech; do
  falls=$(grep -c "connection error on auto" /root/.hermes/profiles/$a/logs/agent.log 2>/dev/null || echo 0)
  echo "$a connection fallbacks: $falls"
done

# If >1000 in 2h, provider endpoint is unreachable or misconfigured
```

## Telegram Platform Issues

```bash
# Disconnect count per agent
for a in yoyo dmob desmond gentech; do
  disc=$(grep -c "Telegram.*Disconnected" /root/.hermes/profiles/$a/logs/gateway.log 2>/dev/null || echo 0)
  echo "$agent Telegram disconnects: $disc"
done

# Network error reconnection attempts
grep "Telegram network error" /root/.hermes/profiles/*/logs/gateway.log | tail -10
```

## Log Volume Summary

```bash
for a in yoyo dmob desmond gentech; do
  lines=$(wc -l < /root/.hermes/profiles/$a/logs/agent.log 2>/dev/null || echo 0)
  errors=$(grep -icE "(error|exception|failed)" /root/.hermes/profiles/$a/logs/agent.log 2>/dev/null || echo 0)
  ratio=$(awk "BEGIN {printf \"%.2f\", $errors/$lines}")
  echo "$agent: $lines total lines, $errors errors, error_rate=$ratio"
done
```

**Interpretation:** error_rate > 0.10 (10%) = critically degraded.

## Process & Environment Check

```bash
# Running gateway processes
ps aux | grep hermes | grep -v grep | grep "gateway run"

# .env existence matrix
for a in yoyo dmob desmond gentech; do
  printf "%-8s .env=%-5s config=%-5s\n" "$a" \
    "$(test -f /root/.hermes/profiles/$a/home/.env && echo YES || echo NO)" \
    "$(test -f /root/.hermes/profiles/$a/home/.config/hermes/config.yaml && echo YES || echo NO)"
done
```

## Session Timeline Reconstruction

For a given agent, get the last 30 minutes of activity to understand recent behavior:

```bash
agent=gentech
now=$(date +%s)
find /root/.hermes/profiles/$agent/logs -name "*.log" -exec grep -H . {} \; | \
  awk -v now=$now '$1 ~ /[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}/ {
    cmd="date -d \""$1"\" +%s"
    cmd | getline ts; close(cmd)
    if (now - ts < 1800) print
  }'
```

Use this after a recent restart to see what errors immediately preceded the crash.
