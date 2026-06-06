# GenTech Pals — Project Scope

**Status:** 🟡 SCOPING
**Started:** May 29, 2026
**Priority:** Active queue (after hackathon sprint)
**Type:** Product (not hackathon submission)

---

## Vision
AI gaming companions that know YOUR build, speak in real voices, and talk about ANY game — no guardrails, no lectures.

## The Problem
- Mainstream AI (ChatGPT, Claude, Gemini) blocks M-rated game content
- Gamers can't get AI help for the games they ACTUALLY play
- Static wiki pages don't know your build or playstyle
- Existing AI companions (Character.AI, Replika) have zero game integration

## The Solution
An uncensored gaming companion agent that:
1. **Knows your build** — reads vault files, tracks your progress
2. **Speaks with personality** — cloned voices (Steve Harvey, Vanito, custom)
3. **Talks about ANY game** — no content filters, no refusals
4. **Gives real-time advice** — passive tree routing, gear recommendations, strategy
5. **Learns from you** — the more you use it, the better it gets

## Target Audience
- Core gamers (POE2, Diablo, WoW, FFXIV)
- M-rated game players (GTA, Cyberpunk, Schedule I)
- Build-crafters who want personalized advice
- Crypto-native gamers (web3 gaming overlap)

## Revenue Model
- **Free tier:** Basic companion, limited queries
- **Pro tier ($5/mo):** Unlimited queries, voice personalities, patch alerts
- **Ultimate tier ($15/mo):** All voices, live gameplay advice, multi-game support
- **Seasonal rental:** Per-league pricing (3-4 months)

## MVP Scope (Phase 1 — POE2 Only)
1. **Build file parser** — reads `15-Gaming/POE-2/Jordan Monk build.md`
2. **Patch notes scanner** — cron job flags relevant changes
3. **Passive tree advisor** — text-based routing guide
4. **Gear recommender** — analyzes build needs, suggests upgrades
5. **Voice integration** — Steve Harvey roasts your bad gear
6. **Telegram bot interface** — ask questions, get answers

## Technical Stack
- **Agent:** Hermes skill (build context + game knowledge)
- **Memory:** Vault files (`15-Gaming/POE-2/`)
- **Voice:** ElevenLabs TTS (Steve Harvey, Vanito)
- **Data:** Patch notes, wiki APIs, poe.ninja
- **Interface:** Telegram bot (MVP), web UI (later)

## Competitive Landscape
| Competitor | What They Do | Gap |
|-----------|-------------|-----|
| Maxroll.gg | Static build guides | No personalization, no voice |
| poe.ninja | Build tracking | No advice, no conversation |
| Character.AI | Chat companions | No game integration |
| ChatGPT/Claude | General AI | Blocks M-rated content |
| **GenTech Pals** | **Uncensored gaming companion** | **Knows YOUR build, talks about ANY game** |

## Hackathon Fit
- **Qwen Cloud Track 3 (Agent Society)** — multi-agent gaming companions
- **Somnia Agentathon** — on-chain memory for companions
- **ElevenHacks** — voice-powered gaming NPCs

## Next Steps
- [ ] Confirm POE2 passive tree API access
- [ ] Build MVP skill (build parser + advisor)
- [ ] Test with Jordan's Monk build
- [ ] Add voice personality (Steve Harvey)
- [ ] Deploy to Telegram as bot
- [ ] Expand to other games

---

*Created: May 29, 2026 | Status: Scoping*
