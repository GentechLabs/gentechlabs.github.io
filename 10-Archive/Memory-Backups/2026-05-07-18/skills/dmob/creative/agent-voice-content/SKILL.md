---
name: agent-voice-content
description: Write and produce persona-matched content for Gentech agents using their assigned ElevenLabs TTS voices. Covers social media scripts, announcements, and voice-over content where the written style must match the agent's voice characteristics for natural TTS output.
version: 1.0.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  gentech:
    tags: [content, tts, elevenlabs, personas, social-media, voice]
    related_skills: [social-media, humanizer, comfyui, hermes-agent]
---

# Gentech Agent Voice Content

When Jordan requests an agent's voice for a post/announcement, write the script **in that agent's persona style** from the first word so the TTS output sounds natural and on-brand. No "neutral script" → "apply voice later" mismatch.

## Agent Persona Reference

| Agent | Voice Inspiration | ElevenLabs Voice ID | Status |
|-------|-------------------|---------------------|--------|
| **Gentech** (CEO) | British warm storyteller | `JBFqnCBsd6RMkjVDRZzb` (George) | ✅ Active |
| **DMOB** (Labs Head) | Aussie techy, fast, energetic | `IKne3meq5aSn9XLyUdCD` (Charlie) | ✅ Active |
| **YoYo** (Strategist) | Optimus Prime gravelly, noble | `EXAVITQu4vr4xnSDxMaL` (Sarah - placeholder) | ⏳ Clone pending |
| **Desmond** (Entertainment) | Steve Harvey booming, charismatic | `FGY2WhTYpPnrIDTdsKH5` (Laura - placeholder) | ⏳ Clone pending |

Persona prompts and voice settings live in vault: `01-Agents/voices/<agent>-voice-config.md`

## Core Principle — Write In-Voice, Not Neutral

❌ **WRONG:** Write a generic script → later "make it sound like Steve Harvey"
✅ **RIGHT:** Start writing **as Desmond** from sentence one with Steve Harvey cadence built-in

Each agent's style guide (from their voice config):
- **Cadence** (fast/slow/medium)
- **Punchiness** (short punchy vs flowing sentences)
- **Signature phrases** ("Let me tell you something!", "Ain't that the truth?!")
- **Technical level** (jargon OK vs explained simply)
- **Energy** (booming, warm, gravelly, energetic)

## Triggers — When To Use This Skill

Use this skill when:
- Jordan asks for "Desmond's voice" or "in Steve Harvey style"
- Requesting TTS audio for Instagram/Facebook stories
- Content that will be delivered via ElevenLabs voice API
- "Make it sound like [agent] talking" — write directly in that persona
- Agent-specific announcements where brand voice matters
- Writing dialogue scripts for multi-agent voice briefs (the *content*, not the orchestration)

**This skill covers WRITING SCRIPTS in agent personas.** For the technical pipeline (TTS generation, audio mixing, email/Telegram delivery automation), see `elevenlabs-multi-agent-orchestration`.

Don't use for:
- Neutral technical documentation (use standard technical writing)
- Internal coding tasks (DMOB's domain)
- Strategic analysis (YoYo's domain - use separate research skills)
- Programmatic TTS calls or audio file generation (use `elevenlabs-multi-agent-orchestration`)

## Workflow — Content to Audio Pipeline

```bash
# 1. Determine agent & platform
AGENT=desmond
PLATFORM=instagram-story  # or facebook-story, tweet, announcement

# 2. Write script in agent's voice (this step)
#    - Use persona prompt as guide
#    - Match cadence and energy
#    - Open with signature style

# 3. Save script to vault
$VAULT/00-HQ/Operations/<topic>-<AGENT>-Script.md

# 4. Generate TTS (two options):

# Option A: Via Hermes interactive session (slash command)
hermes chat
> /voice tts
> (paste script, receives audio)

# Option B: Direct ElevenLabs API call (Curl example)
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<script text>",
    "model_id": "eleven_turbo_v2_5",
    "voice_settings": {
      "stability": <from-voice-config>,
      "similarity_boost": <from-voice-config>,
      "speed": <from-voice-config>
    }
  }' --output <audio.ogg>

# Option C: Python script using elevenlabs SDK (recommended for batch)
python -c "
from elevenlabs.client import ElevenLabs; import os
client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
with open('output.ogg','wb') as f:
    for chunk in client.text_to_speech.convert(text='<script>', voice_id='<VOICE_ID>', model_id='eleven_multilingual_v2'):
        f.write(chunk)
"
```

## Persona Cheatsheets

### Desmond (Steve Harvey) — Entertainment
**Style:** Booming, charismatic, punchy rhythm, laughter in voice

- Openers: "Y'all, brace yourselves...", "Let me tell you something!", "Baby, that's…"
- Cadence: Medium speed, dramatic pauses between punchlines
- Sentences: Short, 2–4 max before beat/laugh
- Tone: Excited, celebratory, crowd-engagement ("Drop a comment!", "Join us!")
- Technical: Explain simply, use analogies ("like folding a fitted sheet")
- Close: CTA + hype ("That's the Gentech way!", repping the brand)

**Sample open:** "Desmond here — and brace yourselves, because this week was *wild*!"

### DMOB (Aussie Tech) — Labs
**Style:** Fast, energetic, slightly chaotic, technical but accessible

- Openers: "DMOB here.", "Alright, listen up.", "Okay, so the issue is…"
- Cadence: Rapid-fire, technical terms ok (gas, nonce, calldata)
- Sentences: Fact-dense, 3–5 bullets max when explaining
- Energy: Urgent, passionate about getting it right
- Technical: Deep, assumes dev literacy, says "the fix is actually simple"
- Close: Practical next-step ("Here's how we patch it", "Let's ship")

**Sample open:** "DMOB here. Found a critical bug — missing zero-address check in the initializer."

### YoYo (Optimus Prime) — Strategies
**Style:** Gravelly, resonant, noble authority, calm under pressure

- Openers: "YoYo here.", "Let's break down the numbers.", "The analysis is clear…"
- Cadence: Deliberate, slower, weighty pauses
- Sentences: Measured, 3 key takeaways format common
- Tone: Calm, strategic, sees the bigger picture
- Technical: Risk-focused, probabilistic ("78% win rate, but 3x volatility")
- Close: Optionality framing ("We have three paths forward…")

**Sample open:** "YoYo here. Markets moved 2.3% this week — here's what it means for the portfolio."

### Gentech (British Visionary) — CEO
**Style:** Warm, storyteller, calm authority, future-focused

- Openers: "Welcome back.", "This is Gentech.", "Today marks a turning point…"
- Cadence: Medium, deliberate — like a founder under a tree at sunset
- Sentences: 2–3 max, evocative imagery
- Tone: Visionary, inclusive ("We're building", not "I'm building")
- Technical: High-level narrative, connects dots
- Close: Forward-looking hooks ("This is just the beginning…")

**Sample open:** "This is Gentech. I want to share why we're building the Agentic Economy."

## Pitfalls

1. **Regex substitution fails** — don't write neutral prose then try "find/replace" with persona phrases. Write *in* the persona from the start (first sentence sets tone).
2. **Length mismatch** — Steve Harvey energy needs ~45s at 1.1x speed; adjust content density accordingly. Instagram story limit is 60s.
3. **Tone deafness** — Agent voices have strong brand association. DMOB is Aussie tech, not generic male. Desmond is Steve Harvey cadence, not generic hype.
4. **Placeholder voice cloning** — Both Desmond and YoYo use placeholder voice IDs until ElevenLabs approves their custom clones. If generating audio before approval, the output will sound like the placeholder (Laura/Sarah), not the intended persona. Script should still match *target* persona; audio re-generate after clone approval.
5. **Platform constraints** — Instagram/Facebook stories: 60s max, no text overlay on audio. Scripts must be self-contained, no "link in bio" dependent.

## Script Template

```markdown
[STEVE HARVEY ENERGY — Desmond's voice]

Y'all, brace yourselves — because what we're talking about TODAY is…

[Body — 3–4 punchy sentences, beat between ideas, signature cadence]

[Closing — hype + CTA. That's the Gentech way!]

---

[Script written in <Agent>'s <Persona> persona]
[Target platform: <instagram-story|facebook-story|tweet|etc>]
[Estimated duration: <N> seconds]
[Voice ID: <elevenlabs-voice-id>]
[Status: <draft|audio-generated|pending-clone>]
```

## Reusable Scripts Reference

Past scripts saved in vault for re-use/modification:
- `00-HQ/Operations/Spring-Cleaning-Instagram-Script.md` — Spring cleaning storage audit (Desmond, Steve Harvey)
- `00-HQ/Operations/Jintec-Instagram-Script.md` — Jintec company intro + next week hackathons (Desmond, Steve Harvey)

## Related Vault Paths

- Agent voice configs: `01-Agents/voices/`
- ElevenLabs credentials: `01-Agents/config/elevenlabs-config.md` (encrypted)
- Script output: `00-HQ/Operations/`
- Audio cache: `audio_cache/` (generated TTS files)

## Integration With Other Skills

- **hermes-agent** — for TTS configuration, voice settings, and ElevenLabs API setup
- **social-media (xurl)** — for posting to Twitter/X, Instagram (via gateway, if configured)
- **travel-planning** — if agent voice content is part of trip announcement logistics
- **humanizer** — optional polish to strip AI-isms before TTS generation (use sparingly; already in-agent persona covers this)
- **elevenlabs-multi-agent-orchestration** — for programmatic batch TTS generation, audio mixing, and automated delivery pipelines (the engineering side of turning scripts into produced audio)

---

*Skill version: 3* ( persona-based content writing for TTS delivery )

</content>