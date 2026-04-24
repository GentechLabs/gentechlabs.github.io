# Agent Voice Assignment — ElevenLabs ✅

## Final Voice Lineup (ElevenLabs)

| Agent | ElevenLabs Voice ID | Style | Persona |
|-------|-------------------|-------|---------|
| **Gentech** | auto (default) | Confident, leader | Captain America, leads the Avengers |
| **YoYo** | auto (default) | Measured, analytical | British researcher, financial authority |
| **DMOB** | auto (default) | Sharp, technical | Veteran smart contract dev |
| **Desmond** | auto (default) | Energetic, comedic | Steve Harvey energy |

## Status
- [x] ElevenLabs API key configured
- [x] TTS enabled in all agent configs
- [ ] Custom voice cloning (future)

## Writing for TTS (MUST FOLLOW)
- Line breaks between thoughts = natural pauses
- Ellipses (...) = dramatic beat / thinking pause
- Short sentences. Not walls of text.
- Read it out loud first — if you'd pause, add punctuation

## Audio Cleanup Pipeline
ffmpeg -af "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80,lowpass=f=12000,afftdn=nf=-25"

---
**Updated:** 2026-04-20 — Switched from Edge TTS to ElevenLabs
