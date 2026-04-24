---
name: agent-health-check
description: Systematic health check for Hermes agent instances across tmux sessions, journalctl, and process monitoring.
category: devops
---

# Agent Health Check

Systematic approach to diagnosing health issues across Hermes agent instances (YoYo, DMOB, Desmond, Gentech, etc).

## Trigger Conditions
- Scheduled watchdog cron job
- Reports of agent misbehavior
- Silent/stuck agents

## Steps

### 1. Check journalctl for system-wide errors
```bash
journalctl --user -u "hermes*" --since "1 hour ago" --no-pager 2>/dev/null | grep -E "(ERROR|CRITICAL|Failed to send|NotFoundError|404)" | tail -30
```

### 2. Identify running processes and their PIDs
```bash
ps aux | grep hermes | grep -v grep
pgrep -f "hermes.*yoyo"
pqrep -f "hermes.*dmob"
pgrep -f "hermes.*desmond"
```
Maps PIDs to gateway instances. Each `hermes gateway run` is one agent. Current deployment runs as background processes with stable PIDs (no tmux).

### 3. Check agent logs for recent activity
```bash
tail -50 /root/.hermes/profiles/yoyo/logs/errors.log
tail -50 /root/.hermes/profiles/dmob/logs/errors.log
tail -50 /root/.hermes/profiles/desmond/logs/errors.log
```
Also check agent.log for successful cron completions:
```bash
grep -E 'cron.*completed|cron.*success' /root/.hermes/profiles/yoyo/logs/agent.log | tail -5
```

### 4. Count error frequency
```bash
journalctl --user -u "hermes*" --since "1 hour ago" --no-pager | grep -c "ERROR"
journalctl --user -u "hermes*" --since "1 hour ago" --no-pager | grep -c "WARNING"
```

### 5. Correlate PIDs to profiles
Multiple `hermes gateway run` processes (pts/0, pts/1, pts/3) map to different agents. Identify which by checking environment:
```bash
for pid in $(ps aux | grep "hermes gateway run" | grep -v grep | awk '{print $2}'); do
  echo "PID $pid: $(cat /proc/$pid/environ 2>/dev/null | tr '\0' '\n' | grep HERMES_HOME)"
done
```
Profiles live under `/root/.hermes/profiles/` (yoyo, dmob, desmond). **Gentech is a vault name, not an agent profile** — it has no profile directory or dedicated gateway.

### 6. Verify agent liveness via log timestamps
```bash
stat -c "%Y" /root/.hermes/profiles/<name>/logs/agent.log 2>/dev/null
```
Compare epoch to current `date +%s` — if within last few minutes, agent is active.

### 7. Diagnose syntax/corruption issues
If you see `'{‘ was never closed (auxiliary_client.py, line N)`:
1. Check if source is actually valid: `python3 -c "import ast; ast.parse(open('/root/.hermes/hermes-agent/agent/auxiliary_client.py').read())"`
2. Compare .py vs .pyc timestamps: `ls -la /root/.hermes/hermes-agent/agent/__pycache__/auxiliary_client*.pyc`
3. If .py is valid but errors persist, cached .pyc is stale — **this can affect some agents but not others** (depends on when each gateway last imported the module)
4. Fix: delete stale .pyc and restart affected gateway: `rm /root/.hermes/hermes-agent/agent/__pycache__/auxiliary_client*.pyc && tmux kill-session -t bot-<name> && tmux new-session -d -s bot-<name> ...`
5. Impact scope: blocks 5 tools (browser, session_search, vision, web, mixture_of_agents) + cron job processing

## Agent Inventory (2026-04-20)
| Agent | Profile Dir | tmux Session | Status |
|-------|-------------|--------------|--------|
| YoYo | `/root/.hermes/profiles/yoyo` | `bot-yoyo` | Active |
| DMob | `/root/.hermes/profiles/dmob` | `bot-dmob` | Active |
| Desmond | `/root/.hermes/profiles/desmond` | `bot-desmond` | Active |
| Gentech | *none* | *none* | **Vault only** — no agent profile. Only `ob sync` runs. |

## Common Error Patterns

| Pattern | Meaning |
|---------|---------|
| `vision_tool 404` | Vision model endpoint returning 404 — check provider/model config |
| `'{‘ was never closed` (auxiliary_client.py) | Stale .pyc cache — blocks tool imports (browser, session_search, vision, web, mixture_of_agents) AND cron job processing. Can affect some agents but not others. Fix: delete `__pycache__/auxiliary_client*.pyc` and restart affected gateway |
| `Could not import tool module tools.web_tools` | Web tools dependency missing or broken |
| `TTS configuration error (elevenlabs)` | Missing ELEVENLABS_API_KEY — non-critical if TTS not needed |
| `Model 404 (step-3.5-flash not found)` | Provider/model mismatch — `config.yaml` specifies `stepfun/step-3.5-flash` but `providers: {}` empty or Nous OAuth expired. Fix: configure `STEPFUN_API_KEY` or revert to valid Nous model |
| `Failed to send media` on Telegram | Broken file path or missing media file |
| Unknown tool 'X' | Tool not registered in current gateway instance — may resolve on next import |
| `Telegram flood control` | Normal rate limiting — not an error, auto-retries |

## 8. Check session transcripts for error patterns
Session files live at `/root/.hermes/profiles/<name>/sessions/`. Use Python to scan for real errors (not just the word "error" in tool descriptions):
```bash
python3 -c "
import json, os, glob, re
agents = {'yoyo': '/root/.hermes/profiles/yoyo/sessions/', 'dmob': '/root/.hermes/profiles/dmob/sessions/', 'desmond': '/root/.hermes/profiles/desmond/sessions/'}
for name, path in agents.items():
    files = sorted(glob.glob(path + '*.jsonl'), key=os.path.getmtime, reverse=True)[:1]
    for f in files:
        lines = open(f).readlines()
        for line in lines[-100:]:
            if any(kw in line for kw in ['Traceback', 'CRITICAL', 'flood control', 'HTTP 401', 'Rate Limit Exceeded']):
                print(f'{name}: {line.strip()[:200]}')
"
```
**Pitfall**: Don't grep for just "error" — tool descriptions contain the word, inflating counts. Target specific error signatures like `Traceback`, `CRITICAL`, `flood control`, `HTTP 401`.

## 9. Verify cron job health
Read `/root/.hermes/cron/jobs.json` and check each job for:
- `last_error` — should be `null`
- `last_status` — should be `"ok"` (or `null` if never run)
- `last_delivery_error` — should be `null`
- `enabled` — should be `true`
- `state` — should be `"scheduled"`

**Note**: Jobs with `last_status: null` and `last_run_at: never` are expected for daily/weekly/monthly jobs that haven't had their first trigger yet.

## 10. Verify Gentech vault sync
Gentech is a vault, not an agent. Verify sync is running:
```bash
ps aux | grep -E 'ob sync|obsidian' | grep -v grep
```
Look for `npm exec obsidian-headless sync --path /root/vaults/gentech --continuous`.

## Pitfall: execute_code cannot import session_search
`session_search` is a standalone tool, NOT available via `from hermes_tools import ...`. Use it as a direct tool call, not inside `execute_code`.

## Silence Rules
- If all agents healthy → `STATUS:OK`
- Only report on actual errors, crashes, or anomalies

## Pitfalls
- `journalctl --user` requires systemd user services; may return nothing if agents run outside systemd
- tmux capture only shows visible pane content; use `-S -200` for history
- Some errors are transient (e.g., API 404s during model switching); count frequency before alerting
- Multiple gateway processes (pts/0, pts/1, pts/3) may be cron job instances, not persistent agents
