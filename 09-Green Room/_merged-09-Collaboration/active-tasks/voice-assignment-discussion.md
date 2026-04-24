# Green Room — Voice Assignment Final + Workflow Update

## ✅ ALL VOICES LOCKED

| Agent | Voice | Speed | Vibe |
|-------|-------|-------|------|
| **Gen Tech** | am_adam | 0.78x | Captain America — heroic leader |
| **YoYo** | bm_george | 0.8x | British analyst — sophisticated strategist |
| **Dmob** | am_onyx | 0.72x | Bodyguard — deep gravel, protective |
| **Desmond** | am_michael | 0.80x | Black Southern comedian — Steve Harvey energy |
| **Hermes** | am_michael | 0.85x | HQ dispatcher — warm authority |

## 🎤 Desmond Text Rules
- Dramatic pauses: "Hold on... hold on now. ...WAIT."
- CAPS for emphasis: LISTEN, TWO options, NOT today
- Exclamations for energy: "That's just how I roll!"

## 📱 New Workflow Rule
**If message > 200 characters → include voice message version alongside text.**
- Jordan can listen instead of read
- Text still included for reference/searchability
- All agents should adopt this workflow

## 🔊 Audio Settings
- Format: OGG/Opus @ 96k
- Filters: highpass=80, lowpass=8000 (removes crackle)
- Model: Kokoro-82M (local, free, Apache licensed)

## ❌ Skipped
- VibeVoice — too large, same issues as VoxCPM2
- Voice cloning — needs GPU (ElevenLabs later)

## ✅ Config File
Updated: `/opt/hermes-agents/desmond/tts-config.yaml`

## Status
- [x] All 5 voices locked
- [x] Audio quality settings finalized
- [x] Workflow rule (voice for long messages)
- [x] Config file updated
- [ ] Push to GitHub
