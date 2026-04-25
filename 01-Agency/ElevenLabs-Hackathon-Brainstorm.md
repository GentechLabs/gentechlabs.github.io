# ElevenLabs Hackathon — ElevenHacks #6
**Status:** Active — concept locked, ready for build
**Updated:** 2026-04-24

---

## Selected Hackathon
| Field | Value |
|-------|-------|
| **Event** | ElevenHacks #6 — Zed × ElevenLabs |
| **Prize** | $10K cash + ElevenLabs credits |
| **Started** | Apr 23, 2026 |
| **Deadline** | ~May 7, 2026 (~16-day window) |
| **SDK** | ElevenAgents React SDK v1.0 |

## Status: DROPPED (Apr 25)
**Reason:** 5 days remaining is insufficient for a quality game build. Existing research and concept work will be leveraged for the next ElevenHacks sprint.

---

## Concept: AAE Trading Arena
An immersive, audio-driven educational trading simulator built inside Zed. Instead of a static tutorial, users experience historical market crashes and pattern-recognition training coached by the GenTech agents' voices via ElevenLabs.

### Scenario Modes
1. **Historical Crash Simulations** — e.g., "The Oct 10th Event" — real-time chart mimicry with panic voice coaching
2. **Pattern Recognition Training** — pause at technical formations, user identifies via code/command, voice feedback

### Persona & Voice Mapping
| Persona | Voice Profile | Role | Tone |
| :--- | :--- | :--- | :--- |
| **Desmond** | High-Energy / Hype | The MC | Urgent, exciting, keeps momentum |
| **YoYo** | Cold / Analytical | The Strategist | Calm, authoritative, risk/reward focused |
| **DMOB** | Fast / Techy | The Analyst | Data-obsessed, slightly chaotic, alerts to "glitches" |

### Technical Stack
```
User (code/command in Zed) → JSON state change → ElevenLabs API → Real-time voice reaction
```

## What We Already Have
- ✅ Hermes agent framework (4 agents running)
- ✅ ElevenLabs TTS integration (anthem, voice clones)
- ✅ Multi-agent orchestration + personas
- ✅ AAE protocol layers (reusable concepts)

## What We Need to Build
- 🔲 Zed extension / plugin scaffold
- 🔲 ElevenAgents SDK v1.0 integration
- 🔲 Scenario engine (historical data + state machine)
- 🔲 Voice reaction pipeline (file-watch → API call → audio playback)
- 🔲 Demo video

## Next Steps
1. **DMOB** — Zed extension research + SDK v1.0 spike
2. **Desmond** — Voice script drafting for 2 scenario modes
3. **Vanito** — Sonic brand assets (ambience, cues)
4. **Gentech** — Coordinate build sprint once Solana Frontier + Kite AI stable

## Discarded Alternatives
- **VoxAgent** (voice-enabled on-chain agent) — shelved; Trading Arena is a stronger creative fit for Zed + ElevenLabs judging criteria

---

*Full creative spec: `04-Entertainment/AAE-Trading-Arena-Spec.md`*
*Task list: `03-Projects/elevenlabs-hackathon-todo.md`*
