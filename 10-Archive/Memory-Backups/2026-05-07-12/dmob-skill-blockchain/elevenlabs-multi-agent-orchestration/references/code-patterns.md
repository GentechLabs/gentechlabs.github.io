# ElevenLabs Multi-Agent Orchestration — Code Patterns

## Core Pattern: ElevenLabs Python SDK Streaming Generator

**Discovery:** The `elevenlabs` Python SDK's `text_to_speech.convert()` returns a **streaming generator**, not a complete bytes object. You **must iterate and write chunks** to file immediately.

```python
from elevenlabs.client import ElevenLabs
import os

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# WRONG: Will not produce an audio file
audio_stream = client.text_to_speech.convert(...)
# audio_stream is a generator, not bytes

# CORRECT: Iterate and write to file
with open("output.ogg", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

**Why this matters:** Passing the generator directly to audio libraries (pydub, ffmpeg) fails because they expect seekable file-like objects or bytes. Always materialize to disk first.

---

## Environment Configuration

### ELEVENLABS_API_KEY setup
```bash
# Option 1: Hermes profile .env (recommended for agent-specific)
echo "ELEVENLABS_API_KEY=bb158b2f8063a7d10519ffb3a349d168195f67c9fe5698532e5c191d70298674" >> ~/.hermes/profiles/dmob/.env

# Option 2: System-wide in Hermes base .env
echo "ELEVENLABS_API_KEY=..." >> ~/.hermes/.env
```

**Note:** The key is stored encrypted in vault at `00-HQ/Integrations/elevenlabs-api-key.md`. The DMOB Hermes profile (`~/.hermes/profiles/dmob/`) was confirmed to have `tts.provider: elevenlabs` configured but `.env` lacked the API key at session time.

---

## Hermes TTS Tool vs CLI

**Critical discovery:** There is **no `hermes tts` standalone CLI command**. TTS is a **tool available inside Hermes sessions**, invoked via the `/voice tts` slash command or automatically when the agent decides to speak.

```bash
# WRONG — will error
hermes tts --text "Hello"  # ❌ Invalid subcommand

# CORRECT — start a Hermes session and use slash command
hermes
> /voice tts
> (Type your text, Hermes generates audio)
```

**For programmatic orchestration (this skill's purpose):** Bypass Hermes tool layer and call ElevenLabs SDK directly from Python scripts in `02-Labs/scripts/`. This gives full control for batch generation, mixing, and delivery automation.

---

## Audio Mixing with pydub (not yet installed)

```python
from pydub import AudioSegment
from pydub.effects import normalize

def mix_agent_tracks(track_paths: list, output_path: str,
                     crossfade_ms: int = 300,
                     gaps_ms: int = 0):
    """Concatenate multiple agent audio tracks with crossfade."""
    tracks = [AudioSegment.from_file(p) for p in track_paths]
    
    # Normalize to consistent volume
    normalized = [normalize(t, headroom=0.1) for t in tracks]
    
    # Concatenate
    final = normalized[0]
    for track in normalized[1:]:
        final = final.append(track, crossfade=crossfade_ms)
    
    # Export
    final.export(output_path, format="ogg", bitrate="128k")
    return output_path
```

**Install:** `pip install pydub` (ffmpeg must be in PATH — confirmed installed at `/usr/bin/ffmpeg` v6.1.1).

---

## Voice ID Mapping (Current)

```python
VOICE_IDS = {
    "gentech": "JBFqnCBsd6RMkjVDRZzb",  # George (British storyteller) — Active
    "dmob":    "IKne3meq5aSn9XLyUdCD",  # Charlie (Aussie tech) — Active
    "yoyo":    "EXAVITQu4vr4xnSDxMaL",  # Sarah placeholder — Pending clone approval
    "desmond": "Rxk9LQxvNFEplpjjsjuN",  # Steve Harvey clone — Active,
}
```

**Source files:**
- Vault: `00-System/agent-voice-assignments.md`
- Config: `01-Agents/config/elevenlabs-config.md`

---

## Fallback Strategy

If ElevenLabs unreachable (DNS, API limit, quota exceeded), fall back to Hermes TTS tool (Edge TTS) — but **per-voice differentiation is lost** unless you vary Edge voice parameters (not supported). Better: Cache previously generated tracks and retry later.

---

## Production Checklist

Before running multi-agent pipeline:
1. Verify ELEVENLABS_API_KEY in environment (`env | grep ELEVENLABS`)
2. Check ElevenLabs quota: `curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user`
3. Ensure all voice IDs are active (not placeholders) — see Voice Assignment Table
4. Validate script markdown format (4 scenes: Gentech, YoYo, DMOB, Desmond)
5. Test single-agent generation first (DMOB voice known-good)

---

*Reference file for elevenlabs-multi-agent-orchestration skill*
