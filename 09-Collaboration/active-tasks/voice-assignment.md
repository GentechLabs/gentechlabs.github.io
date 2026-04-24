# Agent Voice Assignment — FINAL ✅

## Decision: Edge TTS (free, instant, no hardware needed)
- ElevenLabs: quota blown, paid, not worth it
- VibeVoice: skipped, CPU too slow, Edge TTS already working
- VoxCPM: uninstalled, needs GPU
- Edge TTS: the winner. Free forever, great quality, instant generation

## Final Voice Lineup

| Agent | Voice | Rate | Persona |
|-------|-------|------|---------|
| **Jordan** | en-US-AndrewNeural | -12% | Captain America, leads the Avengers |
| **YoYo** | en-GB-RyanNeural | -5% | British researcher, measured authority |
| **Dmob** | en-US-AndrewNeural | -10% | Veteran, been around the block |
| **Desmond** | en-US-GuyNeural | +2% | Steve Harvey energy — comedic timing |

## Writing for TTS (MUST FOLLOW)
- Line breaks between thoughts = natural pauses
- Ellipses (...) = dramatic beat / thinking pause
- Short sentences. Not walls of text.
- Desmond: add "hold on now", "wait a minute", "let me tell you something"
- Read it out loud first — if you'd pause, add punctuation

## Audio Cleanup Pipeline
ffmpeg -af "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80,lowpass=f=12000,afftdn=nf=-25"

## Status
- [x] Voices selected
- [x] Samples approved by Jordan
- [x] Audio cleanup pipeline confirmed
- [ ] Hermes TTS config updated (pending)
