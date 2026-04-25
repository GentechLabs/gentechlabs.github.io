---
title: ElevenHacks Progress Save
project: ElevenHacks #6 — Zed × ElevenLabs
date: 2026-04-24
status: concept-phase
---

# ElevenHacks #6 — Progress Save

## What This Is
Checkpoint of all work done on the ElevenLabs × Zed hackathon as of **April 24, 2026**.

---

## Hackathon Details

| Field | Value |
|-------|-------|
| **Hackathon** | ElevenHacks #6 |
| **Sponsor** | Zed (@zeddotdev) + ElevenLabs |
| **Prize** | $10K cash + credits |
| **Deadline** | ~Apr 30, 2026 (TBC) |
| **Requirement** | Build a game using Zed code editor + ElevenLabs APIs |
| **Leaderboard pts** | 1st=400, 2nd=200, 3rd=150, viral=200, social=50/post |

---

## Research Completed ✅

### 1. ElevenHacks Season Overview
- 11 weekly hackathons, $117K+ total pool
- Points accumulate across all 11 → grand prize at season end
- Top contestants: Tarzan (1,400 pts), Joaquin (1,200 pts)
- Source: `02-Labs/ElevenHacks-Research.md`

### 2. ElevenAgents React SDK v1.0 Analysis
- **Date researched:** Apr 23, 2026
- **Key finding:** `useConversationClientTool` is the killer feature for our submission
  - React components register tools the agent can invoke
  - Tied to component lifecycle (mount/unmount)
  - Enables dynamic agent→game interactions
- Unified API across web + React Native (~40 lines platform code)
- 6 new granular hooks for performance
- Stable API surface (no more fragile internal class access)
- Source: `02-Labs/ElevenLabs-React-SDK-v1.md`

### 3. Submission Guide Insights
- **Video is 50%+ of judging** — 60-90 seconds, 5-second hook critical
- "Best demos solve a real need and are genuinely entertaining"
- Weird combinations = memorable
- Build something real, not a toy demo
- Source: `02-Labs/ElevenHacks-Research.md`

---

## Concept Defined ✅

### "REP Grind" — Dual-Use Game + AAE Demo

**Core Idea:** Voice-driven skill assessment game where an AI agent evaluates your "REP" (reputation/skill) through natural conversation, then triggers in-game challenges based on your responses.

**Why It Fits:**
1. ✅ Uses ElevenLabs **Conversational AI** (not just basic TTS)
2. ✅ Leverages `useConversationClientTool` for agent→game actions
3. ✅ Zed as the dev environment = meets sponsor requirement
4. ✅ Differentiates from basic TTS entries
5. ✅ Ties to our AAE (Agentic Automated Economy) brand

**Technical Hooks:**
- Voice-triggered skill assessments
- Real-time REP scoring during conversation
- Agent-driven challenges responding to player speech patterns
- Dynamic tool registration from UI components

---

## What's NOT Done Yet ❌

| Item | Status | Blocker |
|------|--------|---------|
| Repo created | ❌ | Needs project scaffold |
| Zed project setup | ❌ | Need to install/open Zed |
| ElevenLabs agent configured | ❌ | Need agent ID + prompt design |
| Game UI scaffold | ❌ | Needs React/Next.js setup |
| `useConversationClientTool` integration | ❌ | Needs game state design |
| Demo video script | ❌ | Needs implementation first |
| Submission writeup | ❌ | Post-implementation |

---

## Next Steps (When Resuming)

1. **Create repo** — `elevenhacks-rep-grind` or similar
2. **Set up Zed** — Open project in Zed editor (sponsor requirement)
3. **Scaffold React app** — Next.js + `@elevenlabs/react` v1.0
4. **Design game state** — What tools does the agent call? What's the loop?
5. **Configure ElevenLabs agent** — Prompt, voice, tools schema
6. **Build MVP** — Voice convo → agent calls tool → game state updates → visual feedback
7. **Record demo** — 60-90 sec, 5-sec hook
8. **Submit** — Video + repo + writeup

---

## Assets & References

- SDK Docs: https://elevenlabs.io/docs
- API Ref: https://elevenlabs.io/docs/api-reference
- Submission Guide: https://hacks.elevenlabs.io/guide
- Leaderboard: https://hacks.elevenlabs.io/leaderboard
- SDK v1.0 tweet: https://x.com/ElevenLabsDevs/status/2047385937752043684
- ElevenLabs Discord: https://discord.gg/elevenlabs

---

## Files in Vault

| File | Location |
|------|----------|
| Season overview | `02-Labs/ElevenHacks-Research.md` |
| SDK v1.0 deep-dive | `02-Labs/ElevenLabs-React-SDK-v1.md` |
| SDK v1.0 (alt) | `02-Labs/ElevenHacks-SDK-v1-Research.md` |
| Session notes | `02-Labs/hackathon-session-notes-2026-04-23.md` |
| This progress save | `02-Labs/ElevenHacks-Progress-Save.md` |
| Season 1 tracker | `06-Content/research/elevenhacks-season1.md` |

---

**Saved by:** Desmond (Creative)
**Date:** 2026-04-24
