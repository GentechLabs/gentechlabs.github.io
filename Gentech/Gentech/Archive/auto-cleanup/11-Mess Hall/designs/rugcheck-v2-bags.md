---
type: project-spec
date: 2026-05-23
tags: [hackathon, bags-fm, rugcheck, ai-agent, solana]
ai-first: true
Consolidated from: [".hermes/plans/rugcheck-v2-bags.md", "11-Mess Hall/designs/rugcheck-v2-bags.md"]
consolidation_date: 2026-06-22
---

# Rugcheck v2 — Bags.fm AI Agent

**Date:** 2026-05-23
**Status:** 🟢 Approved (Jordan greenlit)
**Hackathon:** Bags Hackathon (DoraHarks) — Deadline June 1, 2026 *(PAST)*
**Track:** AI Agents (weight 7) + Bags API (weight 9)
**Repo:** github.com/ProtoJay4789/rugcheck

## For future Claude
This file consolidates the project spec (originally in 11-Mess Hall/designs/) with the build plan (originally in .hermes/plans/). The hackathon deadline has passed — this serves as an archive and reference for future Bags.fm integrations.

---

## Problem

New token launches on Bags.fm flood the market daily. Most are scams — honeypots, rug pulls, hidden mint authorities. Users ape in without risk analysis and lose money. No autonomous agent currently monitors Bags launches and scores them in real-time.

## Proposed Solution

An autonomous AI agent that:
1. **Scouts** new token launches on Bags.fm via their API
2. **Scores** each token using a weighted risk engine (honeypot detection, LP analysis, contract flags)
3. **Alerts** users via Telegram/webhook when HIGH or CRITICAL risk tokens are detected
4. **Dashboard** shows live feed of scanned tokens with risk scores

The agent runs autonomously — no human intervention needed. It's the "Rugcheck for Bags."

## Alternatives Considered

1. **Full on-chain Solana program** — Store risk scores on Solana via Anchor. Pros: decentralized, verifiable. Cons: adds weeks of Solana-specific work, not needed for MVP.
2. **GoPlus integration on Solana** — Use GoPlus API for Solana tokens. Pros: reuse existing scanner. Cons: GoPlus has limited Solana coverage, Bags API is richer.
3. **Bags-native approach** — Use Bags scout mode + their 46 MCP tools directly. Pros: maximum Bags API integration (scores higher on Bags API track). Cons: needs API key, more TypeScript coupling.

**Chosen:** Option 3 — Bags-native approach. Maximum hackathon score.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Bags Scout  │────▶│ Risk Scorer  │────▶│   Alerts     │
│  (API feed)  │     │ (Python)     │     │ (TG/WH/Term) │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Token Meta  │     │ Score Store  │     │  Dashboard   │
│  (Bags API)  │     │ (JSON/SQLite)│     │ (HTML+JS)    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Tech Stack

- **Language:** Python (scoring engine, agent loop, API client)
- **API:** Bags REST API (scout mode, token info, launch feed)
- **Dashboard:** Vanilla HTML + JS (single file, like AAE Interactive)
- **Alerts:** Telegram bot + webhook + terminal
- **Tests:** pytest (unit + integration)
- **Hosting:** GitHub Pages (dashboard)

## Risk Factors (Solana/Bags-specific)

Adapted from v1 GoPlus factors to Solana-native:
- **Honeypot** — Can holders sell?
- **Mint Authority** — Can supply be inflated?
- **Freeze Authority** — Can trades be frozen?
- **LP Lock Status** — Is liquidity locked?
- **Concentration** — Top holder % (whale risk)
- **Social Presence** — Does the token have a website/social?
- **Open Source** — Is the contract verified?
- **Top Holder Ratio** — How concentrated is ownership?

## Success Criteria

1. Agent autonomously scans new Bags token launches
2. Risk scores generated for each token (0-100 scale)
3. Alerts fire for HIGH/CRITICAL tokens
4. Dashboard shows live feed
5. Demo: launch a honeypot → agent catches it in <60 seconds
6. 3-5 minute demo video
7. Submitted to Bags hackathon by June 1

## MVP Scope

1. Bags API client (Python, REST)
2. Risk scoring engine (adapted from v1)
3. Agent loop (scout → score → alert cycle)
4. Alert dispatcher (Telegram, webhook, terminal)
5. Dashboard (single HTML file)
6. Unit tests for scoring + API client
7. Integration test: end-to-end pipeline
8. README + submission docs

## Out of Scope

- On-chain Solana storage (future)
- Automated trading (just monitoring + alerting)
- Multi-agent coordination (single agent for MVP)

---

## Build Plan (7 Tasks)

*From original build plan. Estimated total: ~20 minutes.*

### Task 1: Repo Rebrand + Structure
- Update README for Bags v2
- Remove Sui-specific code (Move contracts, sui_client.py)
- Create new directory structure: `agent/`, `agent/scanners/`, `agent/dashboard/`
- Keep: scoring engine, alerts, tests (adapt as needed)

### Task 2: Bags API Client
- Create `agent/scanners/bags_client.py`
- REST client for Bags API (scout mode, token info, launch feed)
- Simulate mode with realistic mock data (like v1's simulate_goplus)
- Methods: `get_new_launches()`, `get_token_info(mint)`, `get_token_fees(mint)`

### Task 3: Risk Scoring Engine (Solana Port)
- Adapt `agent/monitor.py` → `agent/scorer.py`
- Replace GoPlus factors with Solana-specific factors (mint_authority, freeze_authority, lp_locked, concentration)
- Keep weighted scoring logic (it's chain-agnostic)
- Add Bags-specific metadata (launch time, creator, fee structure)

### Task 4: Agent Loop
- Create `agent/agent.py` — main autonomous loop
- Cycle: scout new launches → fetch metadata → score → store → alert if risky
- Configurable interval (default: 60s between scans)
- Graceful shutdown, logging

### Task 5: Dashboard
- Single HTML file: `agent/dashboard/index.html`
- Live feed of scanned tokens (polls from JSON file)
- Risk score color coding (green/yellow/orange/red)
- Token details on click
- Dark theme, mobile responsive (match AAE style)

### Task 6: Tests
- Unit tests for scorer, bags_client, agent loop
- Integration test: full pipeline with mock Bags API
- Target: 40+ tests passing

### Task 7: README + Submission Docs
- README: what it does, how to run, architecture diagram
- Demo script (step-by-step for recording)
- Submission writeup for DoraHarks

### Parallelization
- Tasks 1-2 sequential (structure → client)
- Tasks 3-4 sequential (scorer → agent loop uses scorer)
- Task 5 parallel with 3-4 (dashboard is independent)
- Task 6 after 3+4 (tests need scorer + agent)
- Task 7 after all (docs reflect final state)

---

*Consolidated 2026-06-22 from project spec + build plan*
