---
name: elevenlabs-multi-agent-orchestration
description: Orchestrate multi-agent voice dialogues using ElevenLabs TTS — generate per-agent audio tracks, mix/concatenate with transitions, and deliver via email/Telegram. Covers the ElevenLabs Python SDK, voice ID assignment management, audio mixing with ffmpeg/pydub, and automated daily briefs.
version: 1.0.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  gentech:
    tags: [elevenlabs, tts, multi-agent, voice-orchestration, audio-mixing, automation]
    related_skills: [agent-voice-content, hermes-agent, blockchain-operations]
---

# ElevenLabs Multi-Agent Voice Orchestration

## Overview

This skill covers the **technical orchestration layer** for multi-agent voice content: programmatically calling ElevenLabs TTS for multiple agents, mixing/concatening audio tracks, automating delivery (email/Telegram), and managing voice ID assignments. It complements `agent-voice-content`, which focuses on persona-based scriptwriting.

**Typical use cases:**
- Daily standup audio brief (each agent records 30s voice update → auto-mixed → delivered to Gmail)
- Multi-agent dialogues/debates (YoYo vs DMOB market analysis)
- Automated weekly recap podcasts
- Hackathon demo narration pipelines

**What this skill does NOT cover:**
- Writing scripts in agent personas (see `agent-voice-content`)
- Voice cloning/character design (use ElevenLabs VoiceLab directly)
- Manual one-off TTS via Hermes CLI (`hermes chat` with `/voice tts` mode)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Script Template (in agent persona)                        │
│  → saved to vault: 00-HQ/Operations/<topic>-Script.md      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator (this skill)                                  │
│  • generate_agent_audio(agent, script) → .mp3/.ogg          │
│  • mix_tracks(tracks, output_path, transitions?)            │
│  • deliver_email(audio_file, recipients)                    │
│  • deliver_telegram(audio_file, chat_id)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │Gentech │  │ DMOB    │  │ YoYo     │
    │Voice   │  │ Voice   │  │ Voice    │
    │ID:     │  │ ID:     │  │ ID:      │
    │George  │  │ Charlie │  │ Optimus  │
    └────────┘  └─────────┘  └──────────┘
         │            │            │
         └────────────┼────────────┘
                      ▼
            Mixed Dialogue Audio
            (standup-brief-MM-DD.ogg)
```

---

## ElevenLabs Python SDK — Core Pattern

### Installation
```bash
pip install elevenlabs  # Already installed: v1.59.0
```

### Basic Usage
```python
from elevenlabs.client import ElevenLabs
import os

# Initialize client (reads ELEVENLABS_API_KEY from env)
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Generate audio for an agent
def generate_agent_audio(agent_name: str, script_text: str, output_path: str):
    voice_id = get_voice_id(agent_name)  # See Voice Assignment Table below
    model_id = "eleven_multilingual_v2"
    
    audio_stream = client.text_to_speech.convert(
        text=script_text,
        voice_id=voice_id,
        model_id=model_id,
        # Per-agent voice settings (from 01-Agents/config/elevenlabs-config.md)
        voice_settings={
            "stability": get_voice_setting(agent_name, "stability"),
            "similarity_boost": get_voice_setting(agent_name, "similarity_boost"),
            "style": 0.4,  # Optional, for expressive models
            "speed": get_voice_setting(agent_name, "speed"),
        }
    )
    
    # Save to file
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    
    return output_path
```

**Important:** ElevenLabs returns a streaming generator; you must iterate and write chunks to file. Do NOT pass the stream directly to audio libraries without consumption.

---

## Voice Assignment Management

### Source of Truth
Voice IDs are maintained in two places (keep in sync):

1. **Vault canonical**: `00-System/agent-voice-assignments.md`
2. **ElevenLabs config (encrypted)**: `01-Agents/config/elevenlabs-config.md`

### Current Voice Assignment Table

| Agent | Persona | ElevenLabs Voice Name | Voice ID | Status |
|-------|---------|----------------------|----------|--------|
| Gentech | CEO, British visionary | George | `JBFqnCBsd6RMkjVDRZzb` | ✅ Active |
| DMOB | Labs head, Aussie tech | Charlie | `IKne3meq5aSn9XLyUdCD` | ✅ Active |
| YoYo | Strategist, Optimus Prime | YoYo (placeholder) | `EXAVITQu4vr4xnSDxMaL` | ⏳ **Clone pending** |
| Desmond | Creative, Steve Harvey | Desmond (Steve Harvey clone) | `Rxk9LQxvNFEplpjjsjuN` | ✅ Active |

### Per-Agent Voice Settings (from `elevenlabs-config.md`)
```json
{
  "gentech": {"stability": 0.75, "similarity_boost": 0.75, "speed": 0.95},
  "yoyo":    {"stability": 0.60, "similarity_boost": 0.80, "speed": 0.90},
  "dmob":    {"stability": 0.50, "similarity_boost": 0.90, "speed": 1.05},
  "desmond": {"stability": 0.40, "similarity_boost": 0.85, "speed": 1.10}
}
```

### Critical Pitfall — Placeholder Voices
- **YoYo currently uses placeholder voice** (`Sarah` — `EXAVITQu4vr4xnSDxMaL`) until Peter Cullen–inspired clone is approved by ElevenLabs.
- Generated audio for YoYo will **not sound like Optimus Prime** until clone is active.
- Scripts should still be written to YoYo's target persona (see `agent-voice-content`); re-generate audio after clone approval.

---

## Audio Mixing & Concatenation

### Using pydub (recommended)
```bash
pip install pydub  # Not currently installed — see setup section
```

```python
from pydub import AudioSegment
from pydub.effects import normalize

def concatenate_tracks(track_paths: list[str], output_path: str, 
                      crossfade_ms: int = 300, gaps_ms: int = 0):
    """Concatenate audio tracks with optional crossfade."""
    tracks = [AudioSegment.from_file(p) for p in track_paths]
    
    # Normalize all tracks to same dB level
    normalized = [normalize(t, headroom=0.1) for t in tracks]
    
    # Concatenate with crossfade
    if len(normalized) == 1:
        final = normalized[0]
    else:
        final = normalized[0]
        for track in normalized[1:]:
            final = final.append(track, crossfade=crossfade_ms)
    
    # Export
    final.export(output_path, format="ogg", bitrate="128k")
    return output_path
```

### Using ffmpeg directly (no pydub dependency)
```python
import subprocess

def concat_ffmpeg(track_paths: list[str], output_path: str):
    """Use ffmpeg concat demuxer (requires all tracks same codec)."""
    # Create file list
    list_path = "/tmp/tracklist.txt"
    with open(list_path, "w") as f:
        for p in track_paths:
            f.write(f"file '{p}'\n")
    
    # Run ffmpeg
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy", output_path
    ], check=True, capture_output=True)
    
    return output_path
```

**Recommendation:** Use pydub when available; fall back to ffmpeg only if pydub not installed. pydub gives better crossfade control and normalization.

---

## Daily Standup Brief Pipeline

### Script Template Location
Save daily scripts to: `00-HQ/Operations/<date>-MultiAgent-Script.md`

Example format (from `Spring-Cleaning-MultiAgent-Script.md`):
```markdown
# <Topic> — Multi-Agent Voice Script
**Date:** YYYY-MM-DD
**Format:** Instagram Story (60-90 seconds)
**Concept:** Each agent "checks in" with their voice/perspective

## [SCENE 1 — GENTECH (CEO)]
*[Calm, measured, visionary tone]*
"..."

## [SCENE 2 — YOYO (GROWTH)]
*[Upbeat, rapid-fire, data-optimistic]*
"..."

## [SCENE 3 — DMOB (TECH LEAD)]
*[Pragmatic, systems-focused]*
"..."

## [SCENE 4 — DESMOND (CREATIVE)]
*[Smooth, cultural, visionary]*
"..."

## Voice Assignment Matrix
| Agent | TTS Voice ID | Fallback |
|---|---|---|
| Gentech | `JBFqnCBsd6RMkjVDRZzb` | Edge AriaNeural |
| YoYo | `EXAVITQu4vr4xnSDxMaL` | Edge AriaNeural |
| DMOB | `IKne3meq5aSn9XLyUdCD` | Edge AriaNeural |
| Desmond | `FGY2WhTYpPnrIDTdsKH5` | Edge AriaNeural |
```

### End-to-End Script (`02-Labs/scripts/multi_agent_voice.py`)

**Features:**
- Parse multi-agent script markdown
- Extract per-agent scenes and voice IDs
- Generate TTS audio via ElevenLabs SDK
- Mix tracks with 300ms crossfade
- Output final `.ogg` ready for delivery
- Archive to `00-HQ/Operations/audio/<date>/`

**CLI:**
```bash
python multi_agent_voice.py --script 00-HQ/Operations/today-script.md \
                           --output 00-HQ/Operations/audio/standup-YYYY-MM-DD.ogg
```

---

## Delivery Integration

### Email (Gmail)
Use Gmail API or `smtplib` to send audio file as attachment to both Jordan accounts:
- `jordan@get_gentech.com`
- `j.sir58@gmail.com`

**Pattern:** Generate MIME message with `audio/ogg` attachment, send via SMTP (OAuth2 or app password).

### Telegram
Use Telegram Bot API (`python-telegram-bot` or direct HTTP) to post audio to:
- `@GentechHQ` (main channel) — for quick preview
- `@GentechEntertainment` (if content is social media ready)

---

## Automation (Cron)

Schedule daily generation at 09:00 UTC:

```bash
# ~/.hermes/cronjobs/standup-voice.yml
schedule: "0 9 * * *"
prompt: "Generate yesterday's standup audio from script vault"
delivery:
  - email: ["jordan@get_gentech.com", "j.sir58@gmail.com"]
  - telegram: "@GentechHQ"
```

**Note:** Hermes cron currently focuses on chat prompts; for file-based pipelines, use system cron (`crontab -e`) until Hermes supports file-triggered jobs.

---

## Setup Checklist

- [ ] Set `ELEVENLABS_API_KEY` in `~/.hermes/.env` (currently missing from DMOB profile)
- [ ] Install pydub: `pip install pydub`
- [ ] Verify ElevenLabs SDK import: `python -c "import elevenlabs; print(elevenlabs.__version__)"` → expect `1.59.0+`
- [ ] Ensure ffmpeg installed: `which ffmpeg` → already present v6.1.1
- [ ] Create Hermes profile for Gentech (if different from dmob's `.env`)
- [ ] Submit voice clone request for YoYo (Peter Cullen style) — currently using placeholder
- [ ] Test single-agent TTS generation before multi-agent pipeline

---

## Voice Assignment Reference

See `01-Agents/voices/<agent>-voice-config.md` for persona prompts, cadence guides, and sample openers.

**Per-agent voice style match is critical** — write scripts *in* persona (see `agent-voice-content` skill), then generate TTS with correct voice ID and settings. Substitution fails.

---

## Reusable Resources

- **Script examples:** `00-HQ/Operations/Spring-Cleaning-MultiAgent-Script.md`
- **Audio delivery examples:** `00-HQ/Marketing/Hackathon-Audio-Delivery-20260502.md`
- **Voice catalogs:** `00-HQ/Integrations/ElevenLabs-Voice-Catalog-20260502.md`
- **API key (encrypted):** `00-HQ/Integrations/elevenlabs-api-key.md`

---

## Related Skills

- `agent-voice-content` — persona-based scriptwriting for TTS delivery
- `hermes-agent` — Hermes TTS tool configuration and usage (note: TTS is a **tool within Hermes sessions**, not a standalone CLI subcommand)
- `blockchain-operations` — DeFi strategy engines (relevant for YoYo market brief scripts)

---

*Skill version: 1* —十一度 multi-agent TTS orchestration pipeline

</content>