# ElevenHacks #10: Speech Engine — Build Brief

**Status:** 🔴 ACTIVE — Jordan greenlit May 23
**Route:** → Labs (execution)
**Skill:** speech-engine (loaded ✅)

## What We're Building
Real-time voice agent using ElevenLabs Speech Engine. Server-side WebSocket endpoint that handles voice conversations — STT → LLM → TTS, interruption-aware.

## Why It's Perfect for Us
- **Steve Harvey voice clone** — already built, Voice ID: Rxk9LQxvNFEplpjjsjuN
- **Vanito voice** — collaborator, can add to roster
- **Speech Engine skill** — loaded and ready
- **Agent Arena angle** — voice interface for agent hiring/interaction
- **Fast build** — "we have most of it already ready" (Jordan)

## Architecture
1. **Server** — Python WebSocket endpoint (Speech Engine SDK)
2. **Browser client** — React with `@elevenlabs/react` hook
3. **Token endpoint** — `/api/token` for conversation auth
4. **LLM backend** — Route voice input to agent logic
5. **Voice selection** — Steve Harvey as default agent voice

## Build Steps
1. Scaffold Python Speech Engine server (WebSocket at `/ws`)
2. Create `/api/token` endpoint for browser auth
3. Wire React browser client with `useConversation` hook
4. Connect LLM processing pipeline (voice → text → agent → text → voice)
5. Test interruption handling
6. Deploy + demo

## Demo Plan
Live voice conversation with an agent powered by Steve Harvey's voice. User speaks → agent processes → Steve Harvey responds in real-time. Interruption mid-response shows the awareness.

## References
- Skill: `speech-engine` (SKILL.md loaded)
- Voice inventory: `references/voice-inventory.md`
- ElevenLabs API key: check env
