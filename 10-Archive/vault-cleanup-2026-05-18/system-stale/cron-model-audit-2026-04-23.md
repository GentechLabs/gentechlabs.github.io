---
title: Cron Job Model Audit
date: 2026-04-23
type: audit
status: active
tags: [cron, models, infrastructure]
---

# Cron Job Model Audit — 2026-04-23

## Findings
- **31 total cron jobs** (29 active, 2 paused)
- **Only 1 job** has an explicit model override: "YoYo Crypto Watchlist + LP" → `gemma4:31b`
- **30 jobs** inherit the default model from `~/.hermes/config.yaml` → `gemma4:31b`
- All 4 agent profiles (yoyo, dmob, desmond, gentech) also have `model.default: gemma4:31b`

## By Group

### HQ (-1003863540828) — 7 jobs
All inherit default (gemma4:31b)
- Gentech LLC Reminder
- The Brain Review
- Mess Hall Agent Check-in
- End of Shift Wrap-Up
- Vault Maintenance Weekly
- Weekly Skills Update
- Omni-Summary Master Brief

### Strategies (-1002916759037) — 5 jobs (3 paused)
- YoYo Crypto Watchlist + LP → **gemma4:31b** (explicit)
- Protocol Due Diligence → inherits
- x402 Ecosystem Monitor → inherits
- social-briefing → inherits [PAUSED]
- social-monitor → inherits [PAUSED]

### Labs (-1003872552815) — 4 jobs (DMOB's group)
All inherit default
- Hermes Agent Daily Sync
- Weekly Opportunity Scanner
- PentAGI-Nous-Weekly-Monitor
- Kite AI Hackathon Check

### Entertainment (-1003893562036) — 2 jobs (Desmond's group)
All inherit default
- Security Content Pipeline
- Gentech X Content Extractor

### local/origin — 12 jobs
All inherit default (various maintenance, Mess Hall, brain ops)

## Action Items
- [ ] When switching models tonight, decide: should Labs jobs run on `qwen3-coder-next`?
- [ ] Should Strategies jobs run on `glm-5.1` explicitly?
- [ ] Update cron jobs with explicit model overrides after terminal config is set
- [ ] Jordan noted: Telegram model switch ≠ terminal config — must use `hermes setup`