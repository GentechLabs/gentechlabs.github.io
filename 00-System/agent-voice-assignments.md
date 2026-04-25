# Agent Voice Assignments

**Last Updated:** April 25, 2026
**TTS Provider:** ElevenLabs
**Model:** eleven_multilingual_v2

---

## Active Voices

| Agent | Persona | Voice Name | Voice ID | Notes |
|---|---|---|---|---|
| **Gentech** | Orchestrator, decisive leader | **Gentech-Mako** | `TkEJnN27nf5BsX1xwrLB` | Mako Iwamatsu style — commanding, wise |
| **DMOB** | Technical, precise, coder | **D-Mob** | `n2icbiwmCen7udwM65GS` | Deep, resonant, analytical |
| **YoYo** | Strategist, finance-focused | **YoYo** | `xQbwtCgzouB5QdCSd0Z7` | Peter Cullen / Optimus Prime style — authoritative, calm |
| **Desmond** | Creative, brand, expressive | **Desmond-SteveHarvey** | `Rxk9LQxvNFEplpjjsjuN` | Charismatic, energetic, showman |

---

## Spare / Backup Voices

| Voice Name | Voice ID | Potential Use |
|---|---|---|
| Gentech-Iroh | `NqA7ncEPGGt1nDbCrDex` | Alternative leader persona (softer, mentor-like) |
| IvanOnTech | `ToA54GQ3jBRB2zt0fBXj` | Crypto-native technical narrator |

---

## Config Locations

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

---

## API Key

Stored in `/root/.hermes/.env`:
```
ELEVENLABS_API_KEY=sk_c8766565d4c76cf2917dbb21b88f20b7bbd5717d088e739d
```

**Security:** Old key `ff52c5...` revoked (returned 401). Ensure current key is rotated if shared.

---

## Creating New Voices

### Voice Design (Recommended)
Describe the persona in ElevenLabs Voice Design. Example prompts:
- "Charismatic game show host, energetic, warm, laughs easily"
- "Deep authoritative leader, calm under pressure, transformer-like resonance"
- "Wise elderly mentor, patient, measured speech, slight rasp"

### Voice Cloning
Requires consent for real people. ElevenLabs policy:
- Instant Voice Cloning: ~30s audio sample, requires consent
- Professional Voice Cloning: Signed consent + identity verification

---

*If adding a new agent, clone this row and assign a unique voice. Never reuse another agent's voice_id.*
