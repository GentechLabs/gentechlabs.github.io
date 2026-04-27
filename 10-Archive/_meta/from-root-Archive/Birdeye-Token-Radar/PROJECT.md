# Birdeye Token Radar — Project Tracker

**Status:** 🟡 Scaffold complete, awaiting API key
**Sprint:** BIP Competition Sprint 1 (deadline Apr 25)
**Repo:** TBD (GitHub auth needed)

## What's Built
- [x] Core radar script (`src/radar.py`) — Birdeye API client + safety scorer
- [x] Health check script (`src/healthcheck.py`) — API connectivity test
- [x] Safety scoring engine (5 factors, 0-100 scale)
- [x] Telegram alert formatter
- [x] README with architecture diagram
- [x] `.env.example` config

## What's Needed
- [ ] Birdeye API key (get at bds.birdeye.so)
- [ ] Telegram bot token + chat ID (for alerts)
- [ ] Push to GitHub (need GH auth)
- [ ] Test with live API (healthcheck.py)
- [ ] Run --watch mode to accumulate 50+ API calls
- [ ] Demo video for BIP submission
- [ ] X thread: build in public with @birdeye_data #BirdeyeAPI

## API Call Budget
BIP requires minimum 50 API calls. Each scan makes ~3 calls per token:
- 1x new_listing (per scan)
- 1x token_security (per token)
- 1x token_overview (per token)

20 tokens × 3 calls = 60 calls per scan. One scan exceeds minimum.

## Judging Alignment
- **Technical Depth (25%):** Safety scoring algorithm, multi-endpoint chaining
- **Product Utility (25%):** Solves real problem — catching safe early tokens
- **Presentation (25%):** Clean README, demo video
- **Community (25%):** Build-in-public X thread

## Files
```
Birdeye-Token-Radar/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── .env.example
├── src/
│   ├── radar.py          # Main script (500+ lines)
│   └── healthcheck.py    # API test
└── output/               # Alert logs (gitignored)
```
