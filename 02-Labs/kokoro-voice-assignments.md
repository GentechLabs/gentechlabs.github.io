# Kokoro TTS — Voice Assignments

> Testing Kokoro-82M as ElevenLabs replacement. 82M params, Apache 2.0, runs on CPU.

## Status: IN PROGRESS

Need voices for all 4 agents. Jordan's vision:
- **YoYo** = Christopher Columbus (explorer, pioneer, charting new territory)
- **Dmob** = Columbus' bodyguard (tough, protective, no-nonsense)
- **Desmond** = TBD (entertainment/creative)
- **Gentech** = TBD (main orchestrator)

## Tested & Liked

| Agent | Voice | Status | Notes |
|-------|-------|--------|-------|
| **Dmob** | 🇺🇸 Onyx | ✅ APPROVED | Dark, heavy, authoritative — bodyguard energy |
| **YoYo** | 🇬🇧 Daniel | ✅ APPROVED | Experienced, "been around the block," old man wisdom |

## Still Need

| Agent | Candidates | Notes |
|-------|-----------|-------|
| **Desmond** | Puck, Echo, Liam | Needs playful/creative energy |
| **Gentech** | Adam, Eric, Michael | Needs commanding/professional/orchestrator energy |

## Rejected

| Voice | Why Rejected |
|-------|-------------|
| 🇬🇧 George | Too light/polished for YoYo — Jordan wanted "been around the block" experience |

## Demo

- URL: `https://hexgrad-kokoro-tts.hf.space/?__theme=system`
- 27 English voices total (11F + 9M American, 4F + 4M British)
- Speed adjustable (0.5-2.0)
- Free, runs on ZeroGPU

## Next Steps

1. Generate Desmond samples (Puck, Echo)
2. Generate Gentech samples (Adam, Eric)
3. Final approval from Jordan
4. Set up Kokoro locally if replacing ElevenLabs
