---
title: Deadline Validation — Common Pitfalls
skill: hackathon-lifecycle
date: 2026-05-02
author: YoYo (Strategies)
---

# Hackathon Deadline Validation Pattern

## Problem

Vault deadline files often become stale. Discovered 2026-05-02:
- `03-Strategies/DEADLINES-April-2026.md` lists:
  - ETHGlobal Open Agents: **Apr 23**
  - Kite AI Hackathon: **Apr 26**
- **Actual date**: May 2, 2026 — both dates appear passed or very close
- File title says "April 2026 Sprint" but we're in May → stale file not updated

## Root Causes

1. **Monthly deadline files not rotated**: Created for April, never renamed/updated for May
2. **Cross-file inconsistency**: Multiple strategy files (`Kite-AI-Strategic-Watch.md`, `KiteAI_Strategy.md`) may list different dates
3. **No automated validation**: Cron jobs don't check if deadline file is stale relative to current date


4. **Single-source drift**: `01-Agency/active-hackathons.md` intended as canonical but may not be updated either

## Validation Checklist

Run this when checking any hackathon deadline:

- [ ] **Read canonical source**: `01-Agency/active-hackathons.md` — what does it list?
- [ ] **Cross-check platform**: Visit official hackathon page (Encode Club, lablab.ai, ETHGlobal) — look for:
  - "Submit by" date on landing page
  - Countdown timer
  - "Registration closed" banner
  - Winners/finalists already announced
- [ ] **Detect stale monthly files**: If filename contains a past month (e.g., `DEADLINES-April-2026.md` in May), assume stale until verified
- [ ] **Flag date inconsistency**: If vault files disagree (e.g., KiteAI says May 6 vs May 11), investigate immediately
- [ ] **Check timezone**: Deadline times often UTC-12 or PST — convert to local (ET) for comparison
- [ ] **Look for submission evidence**: Even if deadline passed, check `03-Projects/Hackathons/` for submission artifacts to determine if we entered

## Red Flags

| Symptom | Likely Issue | Action |
|---------|--------------|--------|
| File named `DEADLINES-April-*.md` in May | Not rotated | Check `01-Agency/active-hackathons.md` instead |
| Two strategy files have different dates | Cross-file drift | Use earliest date as hard deadline |
| Platform page says "Closed" but vault says "active" | Vault outdated | Mark as submitted/closed, update vault |
| No activity in Mess Hall for 5+ days about it | Project deprioritized | Move to `10-Archive/` with note |
| Deadline in past but no submission evidence | Likely missed | Flag urgent, notify coordination |

## Automation (Future Cron Enhancement)

Add to daily briefing cron job:
```python
from datetime import datetime, timedelta
import re

# Parse DEADLINES file
with open('03-Strategies/DEADLINES-*.md') as f:
    content = f.read()
    deadlines = re.findall(r'\*\*Deadline:\*\* ([A-Za-z]+ \d+)', content)

# Check if any deadline < today - 3 days
for dl in deadlines:
    parsed = date_parse(dl)
    if parsed < today - timedelta(days=3):
        send_alert(f"Stale deadline detected: {dl} — verify or archive")
```

---

*Session reference: 2026-05-02 — discovered April deadlines in May, created handoff to verify ETHGlobal/Kite AI actual dates*