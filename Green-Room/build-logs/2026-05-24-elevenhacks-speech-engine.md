# Speech Engine — ElevenHacks #10 Build Log

**Date:** May 24, 2026
**Hackathon:** ElevenHacks #10 — Real-time Voice Agents
**Repo:** github.com/ProtoJay4789/speech-engine
**Status:** Scaffolded + server verified

## What Was Built

### Server (`server.py`) — FastAPI + WebSocket
- Speech Engine WebSocket endpoint at `/ws/{persona}`
- Conversation token endpoint at `/api/token` (ElevenLabs auth)
- Persona listing at `/api/personas`
- Two voice personas with distinct system prompts:
  - **Steve Harvey** (`Rxk9LQxvNFEplpjjsjuN`) — Music critic, tough love
  - **Vanito** (`eMQtaKLvw87ksRqmQVpS`) — Rapper, creative collaborator
- LLM integration via OpenRouter (falls back to demo mode without key)
- Interruption handling
- Verified: compiles clean, boots on port 9090

### Frontend (`static/index.html`) — Vanilla JS
- No build step — pure HTML/CSS/JS
- Animated orb interface (idle → listening → speaking states)
- Real-time transcript display
- Persona selection cards
- WebSocket connection to ElevenLabs
- MediaRecorder API for microphone capture
- Responsive design

### Architecture
```
Browser mic → ElevenLabs STT → Server processes → Response text → ElevenLabs TTS → Browser speaker
```

## What's Next
1. Test with real ElevenLabs API key (end-to-end voice flow)
2. Polish demo mode responses
3. Add more persona-specific behaviors
4. Record demo video for submission
5. Deploy to a public URL for judges

## Blockers
- None — server verified, deps available
- ELEVENLABS_API_KEY is set and working
- OPENROUTER_API_KEY available for LLM responses

## Dependencies
- fastapi, uvicorn, python-dotenv (all pre-installed)
- ElevenLabs API key (configured)
