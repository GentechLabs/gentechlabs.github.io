# ElevenLabs Config Template for New Agent

**File**: `~/.hermes/profiles/{agent}/config.yaml`

Add to the `tts:` section:

```yaml
tts:
  provider: elevenlabs
  edge:
    voice: en-US-AriaNeural
  elevenlabs:
    voice_id: {YOUR_VOICE_ID_HERE}
    model_id: eleven_multilingual_v2
  openai:
    model: gpt-4o-mini-tts
    voice: alloy
  xai:
    voice_id: eve
    language: en
    sample_rate: 24000
    bit_rate: 128000
  mistral:
    model: voxtral-mini-tts-2603
    voice_id: c69964a6-ab8b-4f8a-9465-ec0925096ec8
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

**Then update:**
1. `/root/vaults/gentech/.env` — add to runtime copies if needed
2. `/root/vaults/gentech/00-System/agent-voice-assignments.md` — add row to voice table
3. `/root/repos/hermes-brain/config.yaml` — update brain TTS section if overriding defaults

**Sample test prompt** (add to SAMPLES in `elevenlabs-config.md`):
```python
"{agent}": ["Your agent's signature test phrase here"]
```