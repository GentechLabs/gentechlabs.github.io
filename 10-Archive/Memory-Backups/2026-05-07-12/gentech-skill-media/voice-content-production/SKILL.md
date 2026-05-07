---
name: voice-content-production
description: "Generate voice audio content across multiple agent personas using TTS/elevenlabs, with credit budgeting and style-preservation workflows."
version: 1.0.0
author: Gentech (Desmond — Audio Producer)
license: MIT
metadata:
  hermes:
    tags: [media, tts, voice, audio, elevenlabs, social-media, content-production]
    related_skills: [social-media-audio-content, text-to-speech, hermes-agent]
---

# Voice Content Production

Generating audio content (social media posts, explainers, narratives) using TTS engines (ElevenLabs, Edge TTS) while preserving **agent voice identity** and managing **credit budgets**.

## When to Use This Skill

- Creating Instagram/Facebook Story audio
- Producing explainer audio for non-technical audiences
- Recording agent-specific narration (each agent speaks in their own voice)
- Multi-voice compositions (stitching different agent voices into one track)
- Credit-constrained TTS usage (switch between premium and fallback providers)

---

## Core Principle: Agent-Voice Consistency

Each agent has an assigned voice ID. When generating content **as** that agent, use their voice — not a generic one.

**Current Voice Assignments (GenTech):**

| Agent | Profile | ElevenLabs Voice ID | Voice Name | Style |
|---|---|---|---|---|
| Gentech | CEO | `JBFqnCBsd6RMkjVDRZzb` | George | Warm, Captivating Storyteller |
| YoYo | Growth Hacker | `EXAVITQu4vr4xnSDxMaL` | Sarah | Mature, Reassuring, Confident |
| DMOB | Tech Lead | `IKne3meq5aSn9XLyUdCD` | Charlie | Deep, Confident, Energetic |
| Desmond | Creative Director | `FGY2WhTYpPnrIDTdsKH5` | Laura | Enthusiast, Quirky |

**Special Custom Voices (pre-cloned, ready):**
- `Rxk9LQxvNFEplpjjsjuN` — **Desmond-SteveHarvey** (for energetic social storytelling)
- `TkEJnN27nf5BsX1xwrLB` — Gentech-Mako
- `NqA7ncEPGGt1nDbCrDex` — Gentech-Iroh
- `xQbwtCgzouB5QdCSd0Z7` — YoYo (Optimus sample)
- `n2icbiwmCen7udwM65GS` — D-Mob

**⚠️ CRITICAL DISCOVERY (2026-05-02):** These custom agent voices were **already cloned and active** in the ElevenLabs account — no approval needed. Always check for existing custom voices before requesting new clones. Use `curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/voices` to inventory.

---

## Workflow: Premium + Fallback Strategy

### Step 1: Check Credit Budget (ElevenLabs)

## Credit Budget Management

**Monthly quota:** Check via `curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user`

**Decision thresholds (Jordan's preferred strategy):**
- **> 15,000 chars remaining** → use ElevenLabs for all high-impact social content
- **5,000–15,000 chars** → reserve for **hero assets only** (company intro, flagship explainer, key campaign pieces)
- **< 5,000 chars** → switch entirely to Edge TTS for all new content
- **< 1,000 chars** → stop premium generation, reuse existing assets

**Character budget per asset (estimate before generating):**
- 60s Instagram Story: ~1,200–1,500 chars
- 70s Facebook Story: ~1,400–1,800 chars
- 90s extended explainer: ~2,000–2,500 chars

**Always pre-trim script text** to target duration BEFORE calling API to avoid burning excess chars.

**Log usage per asset** in vault `00-HQ/Marketing/<campaign>-Audio-Delivery-<date>.md`:

```markdown
| Asset | Characters Used | Platform | Voice |
|-------|-----------------|----------|-------|
| GenTech intro (66s) | ~1,400 | Instagram | SteveHarvey |
| Hackathon explainer (60s) | ~1,700 | Instagram | SteveHarvey |
```

---

## ⚠️ Pitfalls & Gotchas

### Step 3: Generate Audio

#### Option A: ElevenLabs (premium, while credits last)

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your script here",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.8,
      "style": 0.4,
      "use_speaker_boost": true
    }
  }' --output output.mp3
```

**Recommended settings for social storytelling:**
- `stability: 0.5` — consistent but natural
- `similarity_boost: 0.8` — recognizable voice character
- `style: 0.4` — expressive (higher for Steve Harvey style)
- `use_speaker_boost: true` — clarity

#### Option B: Edge TTS (fallback, unlimited)

No API key needed. Uses `en-US-AriaNeural` voice. Modulate **rate/pitch** via SSML to mimic agent style:

```python
import edge_tts

# Example: slower, measured for Gentech
ssml = '<speak><prosody rate="slow" pitch="low">Your script</prosody></speak>'
await edge_tts.Communicate(ssml, voice="en-US-AriaNeural").save("output.mp3")
```

**SSML cheat sheet for agent styles:**
- Gentech: `rate="slow" pitch="low"` → deliberate, visionary
- YoYo: `rate="fast" pitch="high"` → energetic, upbeat
- DMOB: `rate="medium" pitch="0%"` → steady, factual
- Desmond: `rate="slow" pitch="-5%"` → smooth, lingering

### Step 4: Trim for Platform

Instagram Story: max 60s → trim to `0:00–1:00`.

```bash
ffmpeg -i input.mp3 -t 60 -c:a libmp3lame -b:a 192k output-60s.mp3
```

Facebook/Extended: keep full version (up to 90s typical).

### Step 5: File Naming Convention

```
<content-label>-<voice>-<duration>.<ext>
Examples:
  gentech-intro-steveharvey.mp3      (full version)
  hackathon-steveharvey-60sec.mp3    (Instagram cut)
  jintec-desmond-elevenlabs.mp3      (premium, no cut)
```

Store in: `/root/.hermes/profiles/gentech/audio_cache/`

---

## Content Style: Agent-Voice Scriptwriting

Each agent's script **must match** their voice character. Don't write a Steve Harvey script and feed it to Laura's voice.

**Style Guides:**

- **Gentech (George):** Warm storyteller. Big-picture vision, measured pacing, inspirational but not hype-y. Use metaphors about infrastructure, foundations, long-term building.
- **YoYo (Sarah):** Confident, reassuring. Data-driven optimism, growth metrics, "here's what it means" framing. Energetic but trustable.
- **DMOB (Charlie):** Deep, confident, energetic. Technical clarity, "let me give you the actual fix list" pragmatism. No fluff, just facts.
- **Desmond (Laura / SteveHarvey):** Enthusiast, quirky → Steve Harvey: punchy "Y'ALL!" open, audience call-outs, exaggerated emphasis, rhythm with breaks. Cultural fluency, connection to real-world impact.

**Script format:** Write in SSML-friendly chunks with natural pause points (`<break time="0.3s"/>`) for natural TTS rhythm.

---

## 🎯 Two-Audience Script Strategy

For explaining complex technical work to **non-technical audiences**, use a different script than for technical audiences — but **same voice**:

### For Non-Technical Friends/Family
- **Hook:** Relatable question ("Jordan, what you DO all day?!")
- **Analogy:** Compare to everyday experiences (hiring a freelancer, finding a service)
- **Concrete examples:** Logo design, research dig-up, project coordination
- **Avoid:** Jargon (agents, protocols, capital allocation)
- **Frame:** "AI that works for you like an actual employee"
- **Voice:** Same Steve Harvey energy, simpler vocabulary

### For Technical/Hackathon Audiences
- **Hook:** Forward-looking ("building the autonomous economy")
- **Details:** Agent escrow, reputation scoring, production deployment
- **Terminology:** Protocols, capital, transactions, simulations
- **Frame:** "Infrastructure for autonomous AI agents"
- **Voice:** Same Steve Harvey energy, technical precision

**Same voice, different script depth.** This preserves brand consistency while maximizing comprehension per audience.

---

## Pitfalls & Gotchas

**Monthly quota:** Check via `curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user`

**Decision thresholds:**
- > 15,000 chars remaining → use ElevenLabs for all high-impact content
- 5,000–15,000 → reserve for hero assets only (company intro, flagship explainer)
- < 5,000 → switch entirely to Edge TTS for all new content
- < 1,000 → stop premium generation, use existing assets

**Log usage per asset** in vault `00-HQ/Marketing/<campaign>-Audio-Delivery-<date>.md`:

```markdown
| Asset | Characters Used | Platform |
|-------|-----------------|----------|
| GenTech intro (66s) | ~1,400 | Instagram |
| Hackathon explainer (60s) | ~1,700 | Instagram |
```

---

## Pitfalls & Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| Voice sounds robotic | `stability` too high (0.9+) or `similarity_boost` too low | Use `stability: 0.5`, `similarity_boost: 0.8` |
| SSML stripped | Using `text` field instead of `ssml` field | Edge TTS only — wrap in `<speak>` tags |
| Wrong voice used | Copied script from another agent | Always check `VOICE_ID` matches agent assignment |
| Too many chars burned | Generating full-length then trimming later | Trim script text to target duration BEFORE API call |
| File too big for Telegram | MP3 > 2 MB | Use lower bitrate (`-b:a 128k`) or shorten duration |
| ElevenLabs 401 | API key wrong/expired | Refresh key in `.env`, update profile |
| ElevenLabs DNS fail | Server can't resolve API host | Fall back to Edge TTS temporarily |

### ElevenLabs Quota Exhausted

When API returns 402/Payment Required or character limit reached:
1. **Immediate:** Switch to Edge TTS for all remaining content
2. **Log:** Note quota status in vault delivery doc
3. **Alert:** Notify Jordan (`@Jordan` in Gentech HQ) that premium voice quota is depleted
4. **Restore:** When new quota acquired (new month or plan upgrade), regenerate hero assets with premium voice

---

## 🎯 Critical Pitfall: SSML Pauses vs Natural Flow

**Problem:** Using SSML `<break time="Xs"/>` tags to force pauses in ElevenLabs TTS creates **choppy, artificial silences** that sound robotic, not conversational.

**Symptoms:**
- ❌ "Dead air" that feels unnatural, not like a real storyteller pausing for effect
- ❌ Pauses sound like playback errors, not intentional beats
- ❌ Breaks the Steve Harvey authentic energy vibe

**Root cause:** ElevenLabs' TTS engine already includes natural micro-pauses. Adding explicit SSML breaks creates double-pauses or truncated silence artifacts.

**✅ Solution: Natural Delivery Settings Approach**

Instead of SSML breaks, **adjust voice settings** and **write natural script rhythm**:

1. **Voice Settings for Slower Pacing:**
```json
{
  "stability": 0.7,       // slightly higher = more deliberate
  "similarity_boost": 0.8,
  "style": 0.2,           // lower = less exaggerated, clearer
  "use_speaker_boost": true
}
```

2. **Script Writing for Natural Pauses:**
- Write short sentences (12–15 words max)
- Use ellipses (`...`) for trailing thoughts
- Use parentheticals `(…)` for asides
- Let the TTS engine's natural prosody handle rhythm
- **DO NOT** add `<break>` tags — trust the model's timing

3. **If Pauses Are Still Too Fast:**
- Reduce `style` further (0.1 or 0.0)
- Increase `stability` to 0.8
- Manually add `.` (period) between thoughts instead of SSML

**Example:**
```text
❌ SSML approach (choppy):
<speak>Y'all...<break time="1.5s"/>let me tell you...</speak>

✅ Natural approach (smooth):
Y'all... let me tell you...
```
The TTS engine naturally pauses at punctuation.

**When SSML IS Appropriate:**
- Edge TTS only (ElevenLabs supports SSML but it causes artifacts)
- For dramatic single pauses (1–3s) in otherwise natural flow
- Use sparingly: max 1–2 breaks per 60s audio

**Rule of thumb:** If your audio sounds like a robot hitting pause button, **remove SSML** and adjust script + voice settings instead.

---

## Multi-Voice Composition

To stitch multiple agent voices into one audio track:

1. Generate each agent segment separately (with their voice ID)
2. Concatenate with `ffmpeg`:

```bash
ffmpeg -f concat -safe 0 -i <(for f in seg*.mp3; do echo "file '$PWD/$f'"; done) \
  -c copy combined.mp3
```

3. Add crossfade transitions (300–500ms) for smooth flow:

```bash
# Use pydub if available, else manual fade
ffmpeg -i seg1.mp3 -i seg2.mp3 -i seg3.mp3 \
  -filter_complex "[0:a][1:a]acrossfade=d=0.5[out1]; \
                   [out1][2:a]acrossfade=d=0.5[out]" \
  -map "[out]" combined.mp3
```

---

## Vault Integration

All voice content assets reference these vault paths:

- **Scripts:** `00-HQ/Marketing/<Campaign>-Instagram-Script-<date>.md`
- **Delivery logs:** `00-HQ/Marketing/<Campaign>-Audio-Delivery-<date>.md`
- **Voice catalog:** `00-HQ/Integrations/ElevenLabs-Voice-Catalog-<date>.md`
- **Audio cache:** `/root/.hermes/profiles/gentech/audio_cache/` (not vault-synced, ephemeral)

**Reference templates:**
- `references/steve-harvey-script-template.md` — ready-to-use template for Steve Harvey-style social content with proven voice settings and script structure

Delivery log must include:
- Voice ID used
- Character count (if ElevenLabs)
- Duration & file size
- Platform destination
- Script path in vault

---

## Quick Reference Commands

```bash
# Check ElevenLabs quota
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user | jq '.subscription'

# Generate with specific voice (premium)
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"...","model_id":"eleven_multilingual_v2","voice_settings":{...}}' \
  --output file.mp3

# Edge TTS with style modulation (free)
python3 -c "import edge_tts; import asyncio; \
async def gen(): \
  await edge_tts.Communicate('<speak><prosody rate=\"fast\" pitch=\"high\">text</prosody></speak>', \
  voice='en-US-AriaNeural').save('out.mp3') \
asyncio.run(gen())"

# Trim to 60s
ffmpeg -i input.mp3 -t 60 -c:a libmp3lame -b:a 192k output-60s.mp3

# Get duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 file.mp3
```

---

## Change Log

- **2026-05-02:** Initial skill — captured voice assignments, Steve Harvey style generation, credit budgeting workflow, fallback strategy
- **2026-05-02:** Discovered pre-cloned custom agent voices (Desmond-SteveHarvey, Gentech-Mako, etc.)
- **2026-05-02:** Established Edge TTS SSML modulation for agent style differentiation when ElevenLabs unavailable