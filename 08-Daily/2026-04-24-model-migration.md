---
date: 2026-04-24
type: system-update
agents: gentech, yoyo, dmob, desmond
---

# Model Migration — OpenCode Go + Ollama Split

## Changes
- **gentech** → opencode-go / kimi-k2.6
- **yoyo** → opencode-go / kimi-k2.6
- **desmond** → opencode-go / kimi-k2.6
- **dmob (Labs)** → ollama-cloud / qwen2.5-coder:32b

## Why
Ollama Cloud was overloaded with all 4 agents + crons hitting it. Splitting load:
- 3 agents on opencode-go (faster, more reliable)
- 1 agent (Labs) on ollama-cloud with Qwen Coder (better for code tasks)

## Cron Updates
- DMOB-specific crons pinned to `qwen2.5-coder:32b` model explicitly:
  - `860b3336e150` Hermes Agent Daily Sync Check
  - `2b3840f4ec54` Weekly Opportunity Scanner
  - `1c153ade3177` Kite AI Hackathon Submission Check
- All other crons follow global config (opencode-go / kimi-k2.6)

## Fixes Applied
- **Auxiliary vision** switched from `nous` to `opencode-go / kimi-k2.6` (Nous token expired causing 401s)
- **.env corruption** fixed: `OPENCODE_GO_API_KEY` line had comment separator merged into value (`<key> =============================================================================`), causing auth failures in all 4 profiles
- **Gateway PID files** cleaned after stale locks prevented startup
- **Environment injection** added to gateway startup script so each profile loads its own `.env` explicitly

## Gateway PIDs (post-restart)
- gentech: 402952
- yoyo: 402953
- dmob: 402954
- desmond: 402955

## Status
✅ All 4 gateways running clean
✅ Test messages delivered to all groups
✅ No auth errors in logs
⚠️ Stand by for Hermes agent software update
