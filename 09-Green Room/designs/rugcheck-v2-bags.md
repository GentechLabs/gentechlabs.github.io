# Rugcheck v2 — Bags.fm AI Agent

**Date:** 2026-05-23
**Status:** 🟢 Approved (Jordan greenlit)
**Hackathon:** Bags Hackathon (DoraHacks) — Deadline June 1, 2026
**Track:** AI Agents (weight 7) + Bags API (weight 9)
**Repo:** github.com/ProtoJay4789/rugcheck

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

## MVP Scope (This Build)

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
