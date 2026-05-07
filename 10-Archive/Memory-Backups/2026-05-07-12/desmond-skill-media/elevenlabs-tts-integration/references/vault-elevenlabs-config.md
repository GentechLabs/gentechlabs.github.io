# ElevenLabs Agent Configuration (Vault Copy)

**Source**: `/root/vaults/gentech/01-Agents/config/elevenlabs-config.md`
**Status**: Encrypted config — DO NOT SHARE
**Last synced**: 2026-04-26

## API Configuration

```
XI_API_KEY=***
API_VERSION=v1
```

## Agent Voice Configs (Current IDs - Clone Pending)

```
VOICE_ID_GENTECH=JBFqnCBsd6RMkjVDRZzb
VOICE_ID_YOYO=EXAVITQu4vr4xnSDxMaL
VOICE_ID_DMOB=IKne3meq5aSn9XLyUdCD
VOICE_ID_DESMOND=FGY2WhTYpPnrIDTdsKH5
```

## Voice Clone Request Status

- Desmond: Steve Harvey inspired - PENDING
- YoYo: Peter Cullen (Optimus Prime) inspired - PENDING

## Voice Settings (per agent)

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

**Note**: Profile configs use `eleven_multilingual_v2` but this JSON uses `eleven_turbo_v2_5`. Divergence intentional? Reconcile if customizing voice parameters.

## Sample Prompts for Testing

```python
SAMPLES = {
  "gentech": ["This is Gentech. I want to share why we're building the Agentic Economy."],
  "yoyo": ["YoYo here. Markets moved 2.3% this week — here's what it means for the portfolio."],
  "dmob": ["DMOB here. Found a critical bug — missing zero-address check in the initializer."],
  "desmond": ["Desmond here — and brace yourselves, because this week was *wild*!"]
}
```

## Next Actions

- [ ] Submit voice cloning request for Desmond (Steve Harvey)
- [ ] Submit voice cloning request for YoYo (Peter Cullen)
- [ ] Test generated voices with curl
- [ ] Update VOICE_IDs in config once clones approved
- [ ] Rotate API key if still returning 401