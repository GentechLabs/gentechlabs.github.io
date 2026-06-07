# GenTech Pals — Gaming Companion Agents

## Concept
AI agents that serve as personalized strategy guides for games. Not static wiki pages — living, breathing companions that know your build, watch your progress, and give contextual advice.

## Core Value Proposition
**"The uncensored gaming companion. Ask about ANY game, ANY build, ANY strategy — no guardrails, no lectures."**

Mainstream AI (ChatGPT, Claude, Gemini) blocks M-rated game content — crime sims, violence, drugs, adult themes. GenTech Pals fills this gap. Gamers want AI help for the games they ACTUALLY play, not just family-friendly titles.

### Market Gap
- Schedule I (drug sim) — massive Steam player base, zero AI tools
- GTA, Cyberpunk, POE2 — mainstream AI gives generic/watered-down advice
- Any M-rated game — mainstream AI either blocks it or refuses engagement
- **Positioning:** Mainstream AI is for work. GenTech Pals is for play.

## Core Features
1. **Build Advisor** — Reads your build file, identifies weaknesses, suggests improvements
2. **Passive Tree Guide** — Visual + textual routing for skill trees based on your build
3. **Gear Recommender** — Analyzes current gear, suggests upgrades, tells you what to farm
4. **Patch Notes Scanner** — Auto-scans new patches, flags changes relevant to YOUR build
5. **Live Companion** — Real-time advice during gameplay (voice-enabled via TTS)
6. **Death Analyzer** — "You died because X. Here's how to fix it."

## Technical Architecture
- **Build Context:** Vault files (`15-Gaming/POE-2/Jordan Monk build.md`)
- **Data Source:** Patch notes, wiki APIs, community builds (poe.ninja, maxroll)
- **Agent:** Hermes skill that loads build context + current game state
- **Voice:** Steve Harvey / Vanito personalities for roasts and advice
- **Cron:** Daily patch note scanner, weekly build health check

## MVP Scope (POE2 Only)
1. Build file parser (read vault, extract skills/gear/passives)
2. Patch notes diff scanner (flag relevant changes)
3. Passive tree routing guide (text-based, expandable to visual)
4. Gear recommendation engine (based on build needs)
5. Integration with existing `15-Gaming/POE-2/` vault structure

## Future Expansion
- Support multiple games (POE2, D4, LE, etc.)
- Voice companions (Steve Harvey roasting your gear)
- Community builds database
- Live gameplay analysis via screen capture
- Multiplayer: "GenTech Pals" squad where agents advise different players

## Status
- **Concept:** Approved (May 29, 2026)
- **MVP:** Not started
- **Priority:** After hackathon sprint
- **Vault:** `15-Gaming/POE-2/` (existing build files)
