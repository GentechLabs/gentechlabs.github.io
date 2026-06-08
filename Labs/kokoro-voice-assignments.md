# Kokoro TTS — Voice Assignments

> Testing Kokoro-82M as ElevenLabs replacement. 82M params, Apache 2.0, runs on CPU.

**Policy:** ALL MALE VOICES — Jordan confirmed all agents are "dudes."

## Status: IN PROGRESS

Need male voices for all 4 agents.

## Tested & Liked

| Agent | Voice | Gender | Status | Notes |
|-------|-------|--------|--------|-------|
| **Dmob** | 🇺🇸 Onyx | Male | ✅ APPROVED | Dark, heavy, authoritative — bodyguard energy |
| **YoYo** | 🇬🇧 Daniel | Male | ✅ APPROVED | Experienced, "been around the block," old man wisdom |
| **Desmond** | 🇺🇸 Puck | Male | 🔄 PENDING | Playful, mischievous, creative energy |
| **Gentech** | 🇺🇸 Adam | Male | 🔄 PENDING | Commanding, professional, orchestrator energy |

## Still Need Approval

| Agent | Candidate | Gender | Notes |
|-------|-----------|--------|-------|
| **Desmond** | 🇺🇸 Echo | Male | Lighter, friendly alternative to Puck |
| **Gentech** | 🇺🇸 Michael | Male | Deeper, more authoritative than Adam |

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

1. ✅ All agents confirmed male voices (Jordan policy)
2. Generate Desmond samples (Puck, Echo) for approval
3. Generate Gentech samples (Adam, Michael) for approval
4. Set up Kokoro locally if replacing ElevenLabs
5. Update all agent configs with approved male voices
