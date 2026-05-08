---
name: social-media-audio-content
description: End-to-end production of audio content for social media platforms (Instagram Stories, TikTok, Reels) — scriptwriting, TTS generation, provider fallback, format compliance, and vault documentation.
trigger: "Creating voice audio for social media posts, stories, or reels — especially when TTS provider issues arise or platform-specific constraints apply."
status: stable
version: 1.0.0
---

# Social Media Audio Content Production

## Purpose
Produce engaging, platform-optimized audio content (primarily voiceovers for Instagram Stories, TikTok, etc.) from script to deliverable file, with robust provider fallback and complete documentation.

## Workflow

### 1. Script Authoring
- Capture key message + requested style (e.g., "Steve Harvey energetic")
- Target length: **~60 seconds** for Instagram Stories (max 60s)
- Structure: hook → body → punchline/CTA
- Write in conversational, high-energy tone if requested
- Save script to vault: `00-HQ/Operations/{Topic}-Instagram-Script.md`

### 2. Voice Selection & Strategy (CRITICAL — STYLE DRIVES PROVIDER)

When a comedic/character voice is requested (e.g., "Steve Harvey energetic"):

**Step A — Determine voice feasibility FIRST:**
1. Check if requested voice is a **celebrity/imitation request**
2. If yes → check ElevenLabs policy: celebrity clones require explicit consent, generally NOT publicly available
3. If celebrity clone is requested but unavailable, **immediately pivot** to:
   - Option 1: Premade voice with comedic flavor (see reference matrix)
   - Option 2: Custom Voice Design creating a new persona inspired by (not identical to) the requested style

**Step B — Research ElevenLabs voice library:**
```bash
# Pull current ElevenLabs premade voice catalog (filter for comedic traits)
curl -s -H "Accept: application/json" -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/voices | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps([v for v in d['voices'] if any(kw in (v.get('name','')+v.get('description','')+str(v.get('labels',{}))).lower() for kw in ['energetic','humor','conv','entertain','storytell','warm','confident'])], indent=2))"
```

**Step C — Select approach based on findings:**
- If premade voice exists with matching energy → use immediately
- If no premade match but budget/time available → custom Voice Design
- If neither viable → fallback to Edge TTS with script adaptation (punctuation for inflection)

### 3. TTS Provider Selection & Validation
**Check current provider:**
```bash
cat /root/.hermes/profiles/gentech/config.yaml | grep -A 3 "tts:"
```

**Validate API key (if using ElevenLabs/OpenAI/etc.):**
- Attempt single generation; if `401 invalid_api_key` → provider down
- Quick test: generate 3-second clip before full script

**Available providers (priority order):**
1. `elevenlabs` — high quality but key-dependent
2. `edge` (Microsoft Edge) — free, no key, good neural voices
3. `openai` — reliable, requires key
4. `xai` / `mistral` / `neutts` — alternatives

### 3. Provider Fallback (Critical Path)
**If primary fails (401/403/limited quota):**

```bash
# 1. Edit config.yaml
hermes config edit  # or manual edit at /root/.hermes/profiles/gentech/config.yaml

# 2. Change provider
# In tts.provider: set to 'edge' (no key needed)
# OR switch voice_id/model if key valid but quota exhausted

# 3. Retry generation
```

**Why Edge TTS as fallback?**
- No API key required
- `en-US-AriaNeural` voice is clear and professional
- Works even when paid services are down/over-limit

### 4. Audio Generation
**Command (via `text_to_speech` tool):**
```python
text_to_speech(
    text="<full script>",
    output_path="/root/.hermes/profiles/gentech/audio_cache/{descriptive-name}.ogg",
    provider="<configured provider>"  # optional override
)
```

**File format:** `.ogg` or `.mp3` — both Instagram-compatible  
**Naming convention:** `topic-style-provider.ogg` (e.g., `spring-cleaning-steve-harvey-edge.ogg`)

### 5. Quality Check
- Listen to output (auto-play via `[[audio_as_voice]]` tag)
- Verify:
  - No robotic artifacts (Edge occasionally has minor issues)
  - Timing ~60s (±10s acceptable)
  - Energy/style matches request

### 6. Delivery & Logging
**Send to appropriate group:**
- Instagram story content → `telegram:Gentech Entertainment`
- Technical/ops content → `telegram:Gentech HQ` or Strategies

**Vault documentation (triple-file pattern):**
1. `00-HQ/Operations/{Topic}-{Date}.md` — technical analysis
2. `00-HQ/Operations/{Topic}-Instagram-Script.md` — script text
3. `00-HQ/Operations/{Topic}-Audio-Delivery-{Date}.md` — delivery log with metadata

**Metadata to include:**
- Provider used + reason for selection/fallback
- Voice characteristics
- Duration
- File path
- Recipient group
- Any issues encountered

## Pitfalls

### API Key Expiry (ElevenLabs etc.)
**Symptom:** `401 invalid_api_key` from TTS API  
**Fix:**
1. Switch to `edge` provider immediately (no key required)
2. Flag key for renewal in `.env` or credential manager
3. Document expiry date if known

### Instagram Duration Overflow
**Symptom:** Script > 70 seconds, audio gets cut off in Story  
**Fix:**
- Count words → ~150 words ≈ 60 seconds at conversational pace
- Use shorter sentences, fewer parentheticals
- Trim before generation

### Edge TTS Voice Mismatch
**Symptom:** Sound too robotic/flat for energetic script  
**Fix:**
- Adjust script punctuation (exclamation marks, em dashes) to force inflection
- Consider switching to ElevenLabs once key restored (voice_id: JBFqnCBsd6RMkjVDRZzb)
- Fallback to `openai` with `onyx` or `nova` voice

### File Format Compatibility
**Symptom:** Instagram rejects audio upload  
**Fix:** Use `.mp3` (universal) instead of `.ogg`. Edge can output MP3 with `--format mp3` flag if supported by hermes tool.

## Verification
After generation:
- `[[audio_as_voice]]` tag should render playable audio in Telegram
- File size < 5 MB (60s audio typically ~1-2 MB)
- No errors in generation output

## References
- **Session 2026-05-02:** Spring Cleaning audio (Steve Harvey style) → `references/spring-cleaning-20260502.md`
- Edge TTS voice: `en-US-AriaNeural` (default)
- ElevenLabs voice_id: `JBFqnCBsd6RMkjVDRZzb` (pending key renewal)

## Support Files
- `references/spring-cleaning-20260502.md` — session-specific details, config changes, provider fallback path
- `templates/instagram-story-script.md` — starter template with timing guide (see below)

## Related
- `note-taking` skill (vault documentation patterns)
- `devops/api-key-rotation` (credential refresh workflows)
- Content scripts: `00-HQ/Operations/*-Instagram-Script.md`
