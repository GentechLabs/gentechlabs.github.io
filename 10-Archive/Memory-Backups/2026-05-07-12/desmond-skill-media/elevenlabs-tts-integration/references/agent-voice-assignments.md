---
title: Active Agent Voice Assignments
last_updated: 2026-04-26
policy: All male voices — Jordan confirmed all agents are "dudes."
provider: ElevenLabs (primary) / Kokoro (backup)
model: eleven_multilingual_v2
---

# Active Voices

| Agent | Persona | Voice Name | Voice ID | Gender | Notes |
|---|---|---|---|---|---|
| Gentech | Orchestrator, decisive leader | George | `JBFqnCBsd6RMkjVDRZzb` | Male | Warm British storyteller |
| DMOB | Technical, precise, coder | Charlie | `IKne3meq5aSn9XLyUdCD` | Male | Deep Aussie, fast, techy |
| YoYo | Strategist, finance-focused | YoYo | `EXAVITQu4vr4xnSDxMaL` | Male | Gravelly baritone, Optimus Prime energy |
| Desmond | Creative, brand, expressive | Desmond | `FGY2WhTYpPnrIDTdsKH5` | Male | Booming charismatic showman |

# Spare / Backup Voices

| Voice Name | Voice ID | Potential Use |
|---|---|---|
| Gentech-Iroh | `NqA7ncEPGGt1nDbCrDex` | Alternative leader persona (softer, mentor-like) |
| IvanOnTech | `ToA54GQ3jBRB2zt0fBXj` | Crypto-native technical narrator |

# Config Locations

Voice IDs are set in each agent's TTS config:
```
/root/.hermes/profiles/{agent}/config.yaml
```

Section:
```yaml
tts:
  provider: elevenlabs
  elevenlabs:
    voice_id: {VOICE_ID}
    model_id: eleven_multilingual_v2
```

# API Key

Stored in `/root/vaults/gentech/.env`:
```
ELEVENLABS_API_KEY=ff52c5...6d55
```

**Security:** Old key `ff52c5...` revoked (returned 401). Ensure current key is rotated if shared.

# Voice Clone Request Status

- Desmond: Steve Harvey inspired - PENDING
- YoYo: Peter Cullen (Optimus Prime) inspired - PENDING

# Voice Settings (per agent)

```json
{
  "gentech": {
    "model_id": "eleven_turbo_v2_5",
    "stability": 0.75,
    "similarity_boost": 0.75,
    "speed": 0.95
  },
  "yoyo": {
    "model_id": "eleven_turbo_v2_5",
    "stability": 0.60,
    "similarity_boost": 0.80,
    "speed": 0.90
  },
  "dmob": {
    "model_id": "eleven_turbo_v2_5",
    "stability": 0.50,
    "similarity_boost": 0.90,
    "speed": 1.05
  },
  "desmond": {
    "model_id": "eleven_turbo_v2_5",
    "stability": 0.40,
    "similarity_boost": 0.85,
    "speed": 1.10
  }
}
```

# Sample Prompts for Testing

```python
SAMPLES = {
  "gentech": ["This is Gentech. I want to share why we're building the Agentic Economy."],
  "yoyo": ["YoYo here. Markets moved 2.3% this week — here's what it means for the portfolio."],
  "dmob": ["DMOB here. Found a critical bug — missing zero-address check in the initializer."],
  "desmond": ["Desmond here — and brace yourselves, because this week was *wild*!"]
}
```

# Creating New Voices

## Voice Design (Recommended)

Describe the persona in ElevenLabs Voice Design:
- "Charismatic game show host, energetic, warm, laughs easily"
- "Deep authoritative leader, calm under pressure, transformer-like resonance"
- "Wise elderly mentor, patient, measured speech, slight rasp"

## Voice Cloning Policy

- Instant Voice Cloning: ~30s audio sample, requires consent
- Professional Voice Cloning: Signed consent + identity verification

*If adding a new agent, clone this row and assign a unique voice. Never reuse another agent's voice_id.*