# Rugcheck v2 — Bags.fm Hackathon Build Log

**Date:** 2026-05-23
**Status:** ✅ COMPLETE (code pushed)
**Repo:** github.com/ProtoJay4789/rugcheck
**Commit:** 70e7dd1
**Hackathon:** Bags Hackathon (DoraHacks) — Deadline June 1, 2026

## What Was Built

Transformed the Sui-based "Agent Catcher" into **Rugcheck v2** — a Bags.fm Solana-native AI agent that monitors new token launches and scores them for rug/honeypot risk.

### New Files
- `agent/scorer.py` — Solana-native risk scoring engine (10 weighted factors)
- `agent/scanners/bags_client.py` — Bags.fm REST API client (simulate + live mode)
- `agent/agent.py` — Autonomous polling agent (scout → score → alert loop)
- `agent/config.py` — Config from env vars or config.yaml
- `agent/__main__.py` — Package entry point
- `agent/dashboard/index.html` — Live monitoring dashboard (851 lines, dark theme)
- `agent/tests/test_bags_client.py` — 13 API client tests
- `agent/tests/test_agent.py` — 12 agent loop tests

### Updated Files
- `agent/alerts.py` — Rebranded from "Agent Catcher" to "Rugcheck"
- `agent/tests/conftest.py` — Solana-native fixtures
- `agent/tests/test_scoring.py` — Solana-specific risk factors
- `.github/workflows/tests.yml` — Python 3.11 + lint job
- `README.md` — Full docs with architecture, quick start, config

### Removed (Sui-specific)
- `agent/monitor.py` — GoPlus/EVM scanner
- `agent/sui_client.py` — Sui RPC client
- `contracts/` — Sui Move contracts
- `frontend/` — Old HTML frontend

## Test Results

| Suite | Tests | Status |
|-------|-------|--------|
| test_scoring.py | 20 | ✅ |
| test_bags_client.py | 13 | ✅ |
| test_alerts.py | 17 | ✅ |
| test_agent.py | 12 | ✅ |
| test_e2e.py | 8 | ✅ |
| test_integration.py | 15 | ✅ |
| **Total** | **85** | **✅ ALL PASSING** |

## Architecture

```
Bags Scout API → Risk Scorer → Alert Dispatcher
     ↓                ↓               ↓
 Token Feed      0-100 Score      Telegram/Webhook
     ↓                ↓               ↓
  Dashboard      Score Store      Terminal Log
```

## Risk Factors (Solana-native)

1. LP Locked (18%) — Is liquidity locked?
2. Mint Authority (15%) — Can supply be inflated?
3. Freeze Authority (12%) — Can trades be frozen?
4. Top Holder % (12%) — Is ownership concentrated?
5. Open Source (10%) — Is the program verified?
6. Creator History (10%) — Has this creator rugged?
7. Rug History (10%) — Known scam patterns?
8. Social Presence (8%) — Website/twitter?
9. Liquidity Depth (8%) — Meaningful liquidity?
10. Trading Volume (5%) — Anyone trading?

## Remaining Work

1. **Demo video** (3-5 min) — Record with simulate mode
2. **DoraHacks registration** — Jordan needs to register + submit
3. **Bags API key** — Required for live mode (simulate works for demo)
4. **GitHub Pages** — Deploy dashboard

## Time

- Subagent build: ~6 min (parallel Python + dashboard)
- Review + cleanup + push: ~3 min
- Total: ~9 minutes
