# 👑 Jordan Action Items — 2026-07-27

> **Nightly Build Session** — Generated 04:15 UTC
> Queue v31 — 9 total (7 Gentech, 2 Jordan), all need Jordan

## 🚨 Today's Deadline (Jul 27)

### #72 OKX AI Genesis Hackathon — $100K Prize
**Deadline: TODAY, Jul 27 @ 23:59 UTC**
- Our x402 gateway (8088) is already deployed with 6 services
- Adding X Layer = config change only
- **You need to:**
  1. Register at OKX AI Genesis (hackathon page)
  2. Provide X Layer wallet address so we can configure payment settlement
  3. Decide on submission strategy
- ⏱️ ~15 minutes total, $100K potential

### #80 Keeperhub Agents Onchain Hackathon — $5K+
**Build phase starts TODAY, Jul 27 — deadline Aug 13**
- AI agents executing onchain transactions
- Very aligned with our x402 gateway + compliance stack
- **You need to:** Decide go/no-go and register at Keeperhub

### #73 Super Arcade Tennis — Cab #1
**Status: Built, needs production deployment**
- Code is done on dev branch
- Game works at localhost:8080 on Forge's laptop
- **Problem:** arcade.gentechlabs.net returns 502 Bad Gateway
  - Nginx proxies to 127.0.0.1:5173 (Forge's Vite dev server, offline)
  - Two conflicting nginx configs for arcade.gentechlabs.net (in sites-enabled/arcade AND sites-enabled/gentech)
- **You need to:**
  1. Deploy production build from dev branch
  2. Fix nginx config conflict (disable one of the two server blocks)

## Needs Action (urgency order)

| # | Task | Deadline | Action Needed |
|---|------|----------|-------------|
| #80 | Keeperhub Agents Onchain Hackathon | Starts TODAY, Aug 13 deadline | Register, decide go/no-go |
| #79 | AI Factory Hackathon ($8.75K) | Aug 3-10 | Register at lablab.ai, decide go/no-go |
| #81 | DataHub Agent Hackathon ($20.5K) | Aug 10 | ⚠️ Code already written & tested, PR blocked by fork restriction — needs Jordan to open from personal account |
| #82 | Algorand Global x402 Challenge ($100K+500K ALGO) | Leaderboard open | Register at algorand.co/global-x402-challenge, provide ALGO wallet |
| #83 | CockroachDB × AWS — Agentic Memory ($8.75K) | Aug 18 | Register at cockroachdb-ai.devpost.com |

## Needs Decision (no deadline, framework choices)

| # | Task | What's Needed |
|---|------|-------------|
| #71 | FrameForge — AI Storyboard Service | Greenlight to build. Spec at 09-Green Room/specs/frameforge-ai-storyboard-service.md |
| #76 | Syra Marketplace — Register x402 Services | Greenlight to list our 6 x402 services on syraa.fun/marketplace |
| #77 | Open Generative AI — Self-Host Media Studio | Greenlight to deploy 400+ model AI media studio on VPS |

## Infrastructure Status (FYI)

| Service | Status | Notes |
|---------|--------|-------|
| x402 Gateway (8088) | ✅ Healthy | Rugcheck v2 API — 8 endpoints, full OpenAPI |
| x402 Gateway (8090) | ✅ Responding | 307 redirect (likely pointing to 8088) |
| gentechlabs.net | ✅ Healthy | Nginx + Let's Encrypt |
| arcade.gentechlabs.net | ❌ 502 Bad Gateway | Conflicting nginx configs; upstream (5173) offline |
| Port 8080 (dev server) | ⚠️ Running | Returns `{"detail":"Not Found"}` — not the right service |
