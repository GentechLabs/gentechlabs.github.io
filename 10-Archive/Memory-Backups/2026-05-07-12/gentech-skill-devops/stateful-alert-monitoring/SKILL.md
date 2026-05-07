---
name: stateful-alert-monitoring
description: "Stateful cron-based monitoring with debounced confirmation and tiered alerts — prevents alert spam while ensuring critical conditions are caught. Covers state persistence, multi-threshold logic (immediate/watch/confirmed), and integration patterns for any periodic health/event checker."
tags: ["devops", "monitoring", "alerts", "cron", "state-machine", "debounce"]
trigger: "When building or enhancing periodic monitoring scripts that need false-positive filtering via delayed confirmation, or when different condition severities require different alert urgency levels. Applies to price breakouts, efficiency thresholds, health checks, or any recurring poller where immediate reaction causes noise."
related_skills:
  - defi-lp-monitoring  # for LP-specific logic (efficiency, fees, ranges)
  - agent-coordination  # for vault logging and handoff protocols
  - system-health       # for cron health and failure alerts
version: 1.0.0
author: Gentech
---

# Stateful Alert Monitoring (Umbrella)

Reusable pattern for cron-based detectors that need **confidence confirmation** before escalating, plus **tiered urgency** based on condition severity. Prevents noise from transient spikes while ensuring real breakouts get noticed.

> **Why this exists:** Simple threshold alerts fire on every tick — painful when price ping-pongs across a boundary. This skill adds a state layer: first detection → wait N minutes → confirm → alert. Different severities get different treatment (immediate vs debounced).

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Alert only if condition persists for 5min" | [Debounce Pattern](#1-core-debounce-pattern) |
| "Different alert levels for mild vs severe" | [Tiered Alert Matrix](#2-tiered-alert-matrix) |
| "Persist state across cron runs" | [State File Schema](#3-state-file-schema) |
| "Integrate with existing script" | [Implementation Checklist](#4-implementation-checklist) |
| "Avoid duplicate alerts" | [Deduplication Rules](#5-deduplication-rules) |

---

## 1. Core Debounce Pattern

### When to Use

- **Transient noise** expected (price wicks, brief API hiccups, temporary IL spikes)
- **Cost of false positive** > cost of delayed detection (rebasing penalties, notification fatigue)
- Condition is **discrete** (in/out of range) OR **continuous but thresholded** (efficiency below X%)
- Cron interval is shorter than desired confirmation window (e.g., script runs every 15min, want 5min confirmation)

### When NOT to Use

- **Continuous decay** metrics (efficiency trending down) — use immediate alerts with rate-limiting instead
- **High-frequency trading** contexts where 5min is too slow
- **One-shot events** (contract deployed, milestone hit) — fire once, mark done
- **Safety-critical** systems needing instant reaction (use both immediate + confirmed pathways)

### State Machine

```
          ┌─────────────┐
          │ First       │
          │ Detection   │
          └──────┬──────┘
                 │ set pending=true, timestamp=now
                 ▼
          ┌─────────────┐
          │ Pending     │◄────┐
          │ (waiting)   │     │ condition still true
          └──────┬──────┘     │ after delay?
                 │ elapsed ≥ DELAY_MIN?
                 ▼             │
          ┌─────────────┐     │
          │ Re-check    │─────┘
          │ Condition   │
          └──────┬──────┘
                 │ condition true?
         ┌───────┴───────┐
         │               │
    YES  ▼               ▼  NO
         │               │
    ┌─────────────┐ ┌─────────────┐
    │ Confirmed   │ │ Cancelled   │
    │ → ALERT     │ │ → clear     │
    └─────────────┘ └─────────────┘
         │
    stay confirmed until
    condition clears → reset
```

**Key fields:**
- `pending: boolean` — waiting for confirmation?
- `first_seen: ISO timestamp` — when condition first appeared
- `confirmed: boolean` — has condition survived delay?
- `last_alert_sent: ISO timestamp` — deduplication guard

### Timing Rules

| Metric | Recommendation |
|--------|----------------|
| `CONFIRMATION_DELAY_MIN` | 5 (balance: noise filter vs responsiveness) |
| `MAX_ALERT_INTERVAL_MIN` | 60 (rate-limit repeat alerts on persistent condition) |
| Cron frequency | Should divide evenly into delay (e.g., 15min cron → 5min delay fits) |

---

## 2. Tiered Alert Matrix

Not all conditions deserve the same urgency. Split into **three tiers**:

| Tier | Condition Type | Response | Example |
|------|---------------|----------|---------|
| **IMMEDIATE** | Continuous decay crossing threshold OR safety-critical | Alert now, no wait | Efficiency ≤30%, gas below minimum, contract paused |
| **WATCH** | Discrete boundary crossing with noise potential | Debounce (5min), then alert | Price out of range, efficiency drops below 50% |
| **INFO** | Routine state changes | Log only, no Telegram | Daily snapshot, within-range update |

**Implementation:** Two parallel checks in `should_alert()`:
```python
def should_alert(state, metrics):
    # Tier 1: Immediate (bypass debounce)
    if metrics['efficiency'] <= IMMEDIATE_THRESHOLD:
        return True, "IMMEDIATE"

    # Tier 2: Watch (go through debounce)
    if metrics['out_of_range']:
        return check_debounce(state), "WATCH"

    return False, None
```

---

## 3. State File Schema

Store in JSON at fixed path (e.g., `~/.hermes/scripts/.<script>-state.json`):

```json
{
  "last_run": "2026-05-02T14:10:00-04:00",
  "pending_breakout": {
    "condition": "out_of_range" | "efficiency_low",
    "first_seen": "2026-05-02T14:05:00-04:00",
    "price": 9.02,
    "efficiency": 28.5,
    "confirmed": false
  },
  "last_alert_sent": "2026-05-02T13:55:00-04:00",
  "counters": {
    "total_runs": 142,
    "alerts_sent": 7,
    "false_positives_cancelled": 3
  }
}
```

**Atomic writes:** Write to temp file then `os.replace()` to avoid corruption on interruption.

**Migration:** On script start, call `migrate_state(old_schema)` if version key missing.

---

## 4. Implementation Checklist

### Phase 1 — State Infrastructure
- [ ] Choose state file path (absolute, in `~/.hermes/scripts/` or script dir)
- [ ] Define `load_state()` / `save_state()` helpers with atomic write
- [ ] Add `last_run` timestamp on every execution
- [ ] Initialize `pending_*` keys as empty dicts on first run

### Phase 2 — Debounce Logic
- [ ] In main condition check, detect **first crossing** (condition true AND `pending` not set)
- [ ] Set `pending = {condition, first_seen=now, confirmed=false}`
- [ ] On subsequent runs: if `pending.confirmed == false` AND `now - first_seen ≥ DELAY`:
  - Re-evaluate condition
  - If **still true**: `confirmed = true`, send confirmed alert
  - If **false**: `pending = {}` (false positive resolved)
- [ ] Once `confirmed == true`, keep sending alerts on every run until condition clears
- [ ] On condition clear: `pending = {}`, `confirmed = false`

### Phase 3 — Tiered Alert Routing
- [ ] Define threshold constants at top of script:
  ```python
  IMMEDIATE_THRESHOLD = 30  # efficiency
  WATCH_THRESHOLD = 50
  CONFIRMATION_DELAY_MIN = 5
  ```
- [ ] Build `format_alert(metrics, tier)` → returns two Telegrams:
  - Mini-warning (pending): `"⚠️ Monitoring: condition detected — confirming..."`
  - Confirmed: `"🚨 ACTION REQUIRED: ... — Rebalance suggested"`
- [ ] Route mini-warning to same channel or separate "monitor" channel if spam critical

### Phase 4 — Deduplication
- [ ] Store `last_alert_sent` timestamp
- [ ] Before sending ANY alert, check `now - last_alert_sent < MIN_ALERT_INTERVAL_MIN`
- [ ] If too soon, skip (but keep pending state ticking)
- [ ] After sending, update `last_alert_sent = now`

### Phase 5 — Vault Logging (Optional but Recommended)
- [ ] Create daily log file in appropriate vault folder (e.g., `03-Strategies/Defi-Monitor/YYYY-MM-DD-update.md`)
- [ ] Write first entry of day even if silent (date marker)
- [ ] On every confirmed alert, append detailed entry (price, metrics, action)
- [ ] Use template from `defi-lp-monitoring` skill if applicable

---

## 5. Deduplication Rules

**Problem:** Script runs every 15min; condition persists across 4+ runs → spam.

**Solution:** Three guards:

1. **Pending escalation throttle** — once `pending.confirmed == true`, send **one** confirmed alert per condition lifetime (until reset)
2. **Global rate limit** — `MIN_ALERT_INTERVAL_MIN = 60` prevents rapid successive alerts even if multiple conditions trigger
3. **Same-day suppression** — If today's alert already sent for same condition type, add "update" footer instead of new header

**Alert journal** in state:
```json
{
  "alert_history": [
    {"condition": "out_of_range", "sent_at": "2026-05-02T14:15:00-04:00", "tier": "CONFIRMED"}
  ]
}
```
Prune entries >24h old to keep file small.

---

## 6. Testing Protocol

**Unit tests** (script-level):
```python
def test_pending_escalation():
    state = {}
    metrics = {'out_of_range': True, ...}
    # Run 1: set pending
    alert, tier = should_alert(state, metrics)
    assert tier == "PENDING"
    # Fast-forward time 5min
    state['pending']['first_seen'] = now - 6min
    alert, tier = should_alert(state, metrics)
    assert tier == "CONFIRMED"
```

**Integration tests** (real data):
1. **False positive simulation** — price crosses boundary at t0, crosses back at t+3min → expect no confirmed alert
2. **True breakout** — out-of-range at t0, still out at t+6min → expect one confirmed alert
3. **Efficiency immediate** — eff=28% → alert immediately, no pending
4. **Recovery** — condition clears → pending resets; re-trigger starts new cycle

**Smoke test** on devnet/prod:
- Force condition via mock (patch `fetch_*` functions)
- Verify Telegram delivers exactly one message per escalation
- Verify state file updates correctly
- Verify vault entry created

---

## 7. Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| State file not writable | Silent failures, no persistence | Check `os.access(state_path, os.W_OK)` on startup |
| Timezone drift | first_seen in UTC but cron in local → delay mis-calculated | Use UTC everywhere, convert only for display |
| Cron overlap | Two instances run concurrently, race condition on state file | Use file lock (`fcntl` or lockfile) or ensure cron spacing > script runtime |
| Midnight rollover | Pending state from previous day never clears | Reset `pending_*` on date change (compare `last_run.date()` vs `now.date()`) |
| Memory leak | State file grows unbounded | Prune `alert_history` to last 24h on each run |
| False negative on rebound | Condition true at t0, false at t+5min, true again at t+10min → missed alert | On condition clear, reset pending; on re-trigger, start new cycle (correct behavior) |
| Timezone mismatch in Telegram messages | Timestamps wrong | Use `now_eastern()` helper only for display; store UTC in state |

---

## 8. Integration Guide

**Step 1 — Load this skill** at the top of your monitoring script:
```python
# skill: stateful-alert-monitoring
CONFIRMATION_DELAY_MIN = 5
IMMEDIATE_THRESHOLD = 30
# ... rest of config
```

**Step 2 — Add state helpers** (copy from `references/state-helpers-template.py`):
```python
def load_state(path):
    ...
def save_state(path, state):
    ...
```

**Step 3 — Wrap condition checks:**
```python
def check_conditions(metrics):
    alerts = []
    if metrics['eff'] <= IMMEDIATE_THRESHOLD:
        alerts.append(('IMMEDIATE', 'efficiency critical'))
    if metrics['out_of_range']:
        tier = 'WATCH'
        # debounce handled in should_alert()
        alerts.append((tier, 'price out of range'))
    return alerts
```

**Step 4 — Replace `print()` with `send_telegram(message, tier)`** that respects rate limits.

**Step 5 — Add vault logging** (optional): call `log_to_vault(metrics, tier)` using templates from `defi-lp-monitoring`.

---

## 9. Extensions & Variations

- **Adaptive delay:** If false positive rate high, auto-increase `CONFIRMATION_DELAY_MIN` (max 15min)
- **Multi-condition AND:** Only confirm if BOTH efficiency low AND out-of-range (reduces false positives further)
- **Escalation ladder:** Pending → Confirmed → Critical (if persists >2h) → page Jordan
- **Histogram bins:** For continuous metrics, bucket into bins and confirm bin movement (e.g., efficiency dropped from 55% → 42% → 28%, confirm each step)
- **Cross-validation:** require second data source agreement before confirming (DexScreener + on-chain reader)

---

## 10. Related Skills

- `defi-lp-monitoring` — LP-specific metrics (efficiency, IL, fees) that feed into this pattern
- `agent-coordination` — vault logging, handoff protocols, Mess Hall notes
- `system-health` — cron job health check, failure alerts, gateway monitoring

---

## References (Session-Specific Detail)

**Linked files** — use `skill_view(name='stateful-alert-monitoring', file_path='...')` to read:
**Linked files** — use `skill_view(name='stateful-alert-monitoring', file_path='...')` to read:

- `references/state-helpers-template.py` — boilerplate `load_state()` / `save_state()` with atomic write + time helpers
- `references/d5-milestone-case-2026-05-02.md` — ⚠️ case study: D5 Master Cron enhancement, Jordan's voice-approved rules (5-min debounce, efficiency≤30% immediate, bid-ask edge), implementation handoffs to DMOB + YoYo
- `templates/state-schema.json` — JSON schema for state file (pending_breakout, last_alert_sent, alert_history)
- `templates/telegram-alert-template.md` — mini-warning vs confirmed alert markdown templates for all three tiers

**Implementation example in production:**  
`03-Strategies/scripts/d5-master-cron.py` (post-enhancement) — watch for this file to appear with stateful debounce logic.

*Last updated: 2026-05-02 — created after D5 milestone cron enhancement directive; captures debounce pattern, tiered alerts, and stateful cron orchestration principles.*
