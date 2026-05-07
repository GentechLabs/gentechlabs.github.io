# Slow Response Investigation Methodology (Gentech Agents, May 2026)

## Observed Degradation

All 4 agents exhibiting severe latency (May 2 snapshot):

| Agent | Avg (last 20) | Max | Status |
|-------|--------------|-----|--------|
| Yoyo  | 103.6s       | 305s | 🟡 Degraded |
| DMOB  | 121.2s       | 877s | 🔴 Critical |
| Desmond | 98.7s      | 550s | 🟡 Degraded |
| Gentech | 156.9s     | 646s | 🔴 Critical |

**Expected baseline:** < 60s average for typical queries.

## Investigation Steps

### Step 1: Extract response timeline from gateway.log

```python
import re
from datetime import datetime

responses = []
with open('/root/.hermes/profiles/<agent>/logs/gateway.log') as f:
    for line in f:
        if 'response ready:' in line:
            ts = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
            dur = float(re.search(r'time=([\d.]+)s', line).group(1))
            responses.append((ts, dur))
```

Plot `dur` over time to identify:
- Gradual creep (resource exhaustion)
- Sudden spike (incident onset)
- Periodic spikes (cron job interference)

### Step 2: Identify longest response session

Take slowest response (max duration), extract session ID from log line:

```
2026-05-02 12:04:52,179 INFO gateway.run: response ready: ... session=agent:main:telegram:group:-1003863540828:355efc09 ...
```

Session ID: `355efc09` (last part after `:`)

Find session file:
```bash
ls -lt /root/.hermes/profiles/<agent>/sessions/ | grep 355efc09
```

### Step 3: Analyze slow session transcript

Read session JSONL; count tool calls and identify churn:

```python
import json

tool_calls = []
with open(session_file) as f:
    for line in f:
        entry = json.loads(line)
        if entry.get('role') == 'assistant' and entry.get('tool_calls'):
            tool_calls.extend(entry['tool_calls'])

print(f"Total tool calls: {len(tool_calls)}")
for call in tool_calls[-10:]:  # tail
    print(call['function']['name'])
```

**Red flags:**
- > 30 tool calls in one turn → likely recursive/looping behavior
- Repeated same tool (e.g., `session_search` 20x) → missing context or stuck
- Alternating `tool`/`tool_result` without assistant text → back-and-forth storm

### Step 4: Cross-check LLM provider latency

If session shows minimal tool use but still slow → LLM generation latency.

Check concurrent load:
```bash
# Count all Hermes processes sharing same model provider
ps aux | grep hermes | wc -l  # multiple agents = concurrent API calls
```

Inspect model config:
```bash
cat /root/.hermes/profiles/<agent>/config.yaml | grep -A3 'model:'
```

**If using OpenRouter:** Check `openrouter:usage` endpoint for rate-limit headers.

### Step 5: Check for external tool stalls

Common culprits:
- `web` tool: slow/scraping-protected sites
- `terminal` tool: long-running subprocess (check gateway.log for `tool started` → `tool finished` gaps)
- `delegation` tool: subagent not returning (check subagent's own logs)

Search log for long tool executions:
```
grep "tool started" gateway.log | awk '{print $1,$2}' > starts.txt
grep "tool finished" gateway.log | awk '{print $1,$2}' > finishes.txt
# Join and compute gaps
```

### Step 6: Check for cascading error retries

If a tool fails and is retried automatically (e.g., network timeout), each retry adds latency.

Pattern in session:
```
tool_call: web_search(...)
tool_result: {"error": "Timeout", "retry": 1}
tool_call: web_search(...)  # same query
tool_result: {"error": "Timeout", "retry": 2}
...
```

**Mitigation:** Increase tool timeout in config or disable flaky tool.

### Step 7: Verify cron job interference

Long-running cron jobs (e.g., Brain Review, Watchdog) can starve interactive sessions if they occupy LLM capacity or disk I/O.

Check for concurrent cron execution in gateway.log:
```bash
grep "cron job" gateway.log | grep "$(date +%Y-%m-%d)"
```

If cron jobs overlap with slow responses, stagger schedules.

## Common Root Causes (Observed)

| Cause | Evidence | Fix |
|-------|----------|-----|
| LLM provider rate-limit/slowdown | All agents slow simultaneously; no tool errors; `api_calls=N` high | Switch provider or reduce parallel agents |
| kanban dispatcher deadlock (DMOB/Desmond) | Errors in log; kanban.db stale; tasks=0 | Restart gateway; replace kanban.db |
| Telegram flood control | `Flood control exceeded` in log; response after flood clears | Reduce notification frequency; batch messages |
| Disk I/O pressure (May 1) | `disk I/O error` in kanban and channel directory logs; `iowait` elevated | Clear disk space; check inode exhaustion; restart affected services |
| Recursive tool loops | 50+ `tool_result` entries in single session; repetitive pattern | Identify looping function; patch skill to add loop guard |

## Quick Fix Order

1. **Restart slowest agent** — often clears transient LLM or connection backlog
2. **Check kanban DB** — if stale, restart gateway immediately (dispatcher freeze blocks kanban-dependent workflows)
3. **Verify Telegram bot** — "Chat not found" interrupts response finalization (message send step)
4. **Review concurrent cron load** — pause non-essential jobs during peak hours
5. **Switch LLM provider temporarily** — if provider-wide slowdown confirmed

## Monitoring

Add to daily health check:
```bash
# Response time trend (last 50 responses)
python3 -c "
import re, glob, json
log = '/root/.hermes/profiles/yoyo/logs/gateway.log'
with open(log) as f: lines = f.readlines()
durs = [float(re.search(r'time=([\d.]+)s', l).group(1))
        for l in lines[-5000:] if 'response ready:' in l]
if durs:
    avg = sum(durs[-50:])/50
    print(f'Yoyo recent avg: {avg:.1f}s')
"
```

Alert if avg > 90s.

</content>