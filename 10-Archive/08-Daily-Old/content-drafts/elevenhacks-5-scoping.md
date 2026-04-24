# ElevenHacks #5 — Zed + ElevenLabs (Scoping Notes)

**Status:** PREP — opens Apr 23, 2026
**Prize:** $11,980
**Deadline:** ~Apr 30 (7-day hackathon)

---

## What We Know
- **Sponsor:** Zed (high-performance code editor) + ElevenLabs (voice AI)
- **Format:** Likely build something creative combining Zed + ElevenLabs
- **Judging:** Video demo (60-90 sec), virality matters, real use case > toy

## Project Ideas for Gentech

### 1. 🎯 "Voice-First Agent Briefings" (Highest confidence)
**Concept:** Zed extension that converts complex DeFi/contract analysis into 30-second voice briefings via ElevenLabs.
- Agent monitors on-chain data → generates summary → Zed plays it as voice
- "Your LP position is out of range" → spoken, not read
- Fits ElevenLabs perfectly, uses our existing TTS infrastructure

### 2. "Multi-Agent Voice Debate"
**Concept:** Multiple agents with different personalities (our 4 voices) debate a trading decision.
- Conservative agent says "wait," aggressive agent says "buy," auditor says "check the contract first"
- User listens to the debate in voice, makes decision
- Very shareable, viral potential

### 3. "Agent Marketplace Voice Browser"
**Concept:** Browse and evaluate AI agents through voice commands in Zed.
- "Tell me about the top yield farming agents" → voice response
- Agent introductions in their own cloned voices
- Novel but more complex to build

## Recommendation
**Idea #1** is the fastest build — we already have the ElevenLabs voices configured, the monitoring logic from our LP system, and it solves a real pain point. Build it as a Zed extension or CLI tool.

## Build Time Estimate
- **Idea #1:** 2-3 days (we have most pieces)
- **Idea #2:** 3-4 days (need debate orchestration)
- **Idea #3:** 5+ days (full marketplace UI)

## Decision: Pursue alongside ETHGlobal or skip?
- If ETHGlobal submission is on track by Apr 23 → pursue Idea #1 (quick win)
- If ETHGlobal is behind → skip, focus on May 3 deadline
