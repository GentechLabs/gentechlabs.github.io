# RomM + AI Companion — Research & Architecture

**Date:** July 11, 2026
**Status:** Scoping
**Stack:** RomM (self-hosted) + EmulatorJS + Vision AI + Ollama Cloud

---

## What is RomM?

RomM (11.1k ★) is a self-hosted ROM manager that:
- Scans, enriches, and browses game collections
- Plays games in-browser via **EmulatorJS** (RetroArch cores → WebAssembly)
- Supports 25+ platforms (NES, SNES, GB, GBA, N64, PS1, PSP, etc.)
- Netplay for up to 4 players over WebRTC
- Saves/states auto-sync to server
- Python backend + Vue frontend

## The AI Companion Vision

An AI agent that:
1. **Watches** the game screen via screenshots/streaming
2. **Understands** game state (health, position, objectives)
3. **Plays** as a co-op partner (AI Player 2)
4. **Talks** to the human player via voice

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    RomM Server                       │
│  (Docker: backend + frontend + EmulatorJS)           │
└─────────────────────┬───────────────────────────────┘
                      │ EmulatorJS runs in browser
                      ▼
┌─────────────────────────────────────────────────────┐
│              AI Companion Agent (Forge)               │
│                                                      │
│  1. Screenshot Capture ──► Vision Model (qwen3-vl)   │
│  2. Game State Parser  ──► Understands game context   │
│  3. Decision Engine    ──► What to do next            │
│  4. Input Emulation    ──► Keyboard/gamepad inputs     │
│  5. Voice Output      ──► TTS (Gepard / ElevenLabs)  │
└─────────────────────────────────────────────────────┘
```

## Technical Approach

### Phase 1: Screen Capture + Vision (Week 1-2)
- Capture EmulatorJS canvas via browser automation
- Feed screenshots to qwen3-vl:235b-instruct (Ollama Cloud)
- Parse game state: health, score, position, enemies

### Phase 2: Decision Engine (Week 2-3)
- Map game state → actions
- Simple: follow player, attack enemies, collect items
- Complex: learn game-specific strategies

### Phase 3: Input Emulation (Week 3-4)
- Emulate keyboard/gamepad inputs
- Send to EmulatorJS via JavaScript API
- Co-op mode: AI controls Player 2

### Phase 4: Voice (Week 4-5)
- Gepard TTS for voice output
- Whisper STT for voice commands
- "Hey, cover me!" → AI responds

## Key Challenges

1. **Latency** — Vision model needs to be fast enough for real-time play
2. **Game-specific knowledge** — Each game needs different state parsing
3. **Input synchronization** — AI inputs must not conflict with human inputs
4. **EmulatorJS API** — Need to understand how to inject inputs programmatically

## EmulatorJS Input API

EmulatorJS exposes a JavaScript API:
- `window.emulator` — emulator instance
- `window.emulator.pressKey(key)` — simulate key press
- `window.emulator.releaseKey(key)` — release key
- Gamepad API via browser's standard Gamepad API

## Next Steps

1. [ ] Set up RomM locally (Docker)
2. [ ] Test EmulatorJS with a ROM
3. [ ] Build screen capture pipeline
4. [ ] Test vision model on game screenshots
5. [ ] Build input emulation module
6. [ ] MVP: AI plays a simple NES game (co-op mode)
