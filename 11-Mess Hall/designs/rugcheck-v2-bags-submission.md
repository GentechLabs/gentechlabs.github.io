# Rugcheck v2 — Bags.fm Hackathon Submission

**Date:** 2026-05-23
**Status:** ✅ BUILT — Ready for submission
**Hackathon:** Bags Hackathon (DoraHacks) — Deadline June 1, 2026
**Track:** AI Agents (weight 7) + Bags API (weight 9)
**Repo:** github.com/ProtoJay4789/rugcheck (branch: bags-hackathon)

## What Was Built

### Core Components
1. **Bags API Client** (`agent/bags_scanner.py`)
   - Scans new token launches via Bags REST API
   - Fetches token metadata, holders, LP info
   - Simulation mode for demos

2. **Risk Scoring Engine** (`agent/bags_scanner.py`)
   - 11 weighted risk factors (Solana-specific)
   - 0-100 scoring scale
   - Classification: LOW/MEDIUM/HIGH/CRITICAL

3. **Agent Loop** (`agent/agent_loop.py`)
   - Continuous monitoring (configurable interval)
   - Deduplication (skips already-scanned tokens)
   - Webhook + Telegram alerts
   - Stats tracking (uptime, scans, alerts)

4. **Dashboard** (`frontend/dashboard.html`)
   - Live feed of scanned tokens
   - Filter by risk level
   - Alert banners for HIGH/CRITICAL
   - Stats cards (scans, alerts, distribution)

5. **Tests** (`agent/tests/test_bags_scanner.py`)
   - 21/21 tests passing
   - Coverage: risk factors, scoring, simulation, edge cases

## Demo Flow

1. Run agent: `python3 agent/agent_loop.py --simulate`
2. Dashboard shows live feed of scanned tokens
3. When HIGH/CRITICAL detected → alert banner + webhook
4. Click token row → see full risk report

## Why This Wins

- **Real utility:** Protects Bags users from rugs
- **Autonomous:** Runs without human intervention
- **Deep integration:** Bags API + Solana RPC
- **Production ready:** Tests passing, clean architecture
- **Clear demo:** Honeypot → agent catches live

## Next Steps

- [ ] Record 3-5 min demo video
- [ ] Submit to DoraHacks
- [ ] Post on X/Twitter with demo
- [ ] Monitor for feedback/judging
