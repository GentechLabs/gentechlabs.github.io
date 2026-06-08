# 🎙️ Agent Voice Assignments (Kokoro TTS)

**Date:** 2026-04-17
**Updated:** 2026-04-17 (evening)
**TTS Engine:** Kokoro-82M (Apache 2.0, open source)
**Replaces:** ElevenLabs

## Voice Map

| Agent | Voice ID | Character | Status |
|-------|----------|-----------|--------|
| **Dmob** | `🇺🇸 🚹 Onyx` (speed 1.15) | Bodyguard — heavy, dark, energetic | ✅ LOCKED |
| **YoYo** | `🇬🇧 🚹 Daniel` | Columbus/explorer — experienced, been around the block | ✅ LOCKED |
| **Desmond** | `🇺🇸 🚹 Michael` | Steve Harvey — warm, comedic timing, serious when needed | 🔄 TESTING |
| **Gentech** | `🇺🇸 🚹 Eric` (speed 0.85) | Captain America — leads from the front, inspiring | ✅ LOCKED |

## Character Dynamic
- **YoYo = Columbus** — the pioneer, charting new territory in markets
- **Dmob = Columbus' bodyguard** — tough, protective, "don't touch my guy"

## Text Prompt Rules (Natural Sounding)
- Use commas (`,`) for short breath pauses
- Use periods (`.`) for natural sentence stops
- Use ellipses (`...`) for dramatic/thinking pauses
- Use em dashes (`—`) for mid-thought pivots
- Use semicolons (`;`) for slight beats between ideas
- Use `!` for energy lifts, `?` for curiosity/upward tone
- NEVER run sentences together without punctuation — it sounds robotic
- Write like you're talking, not reading

## Local Setup
- **Engine:** Kokoro-82M via `kokoro-tts` Python package
- **Location:** `/opt/kokoro-voices/`
- **Server:** Running on our VPS (CPU, no GPU needed)
- **Sample rate:** 24kHz

## Files
- `/opt/kokoro-voices/dmob-onyx.ogg`
- `/opt/kokoro-voices/yoyo-daniel.ogg`
- `/opt/kokoro-voices/desmond-michael.ogg`
- `/opt/kokoro-voices/gentech-eric.ogg`

## Notes
- Kokoro runs on CPU — no GPU needed for production
- 82M params, Apache 2.0 license
- ~$0.80/M chars via API, free self-hosted
- Demo: https://hf.co/spaces/hexgrad/Kokoro-TTS
- GitHub: https://github.com/hexgrad/kokoro
