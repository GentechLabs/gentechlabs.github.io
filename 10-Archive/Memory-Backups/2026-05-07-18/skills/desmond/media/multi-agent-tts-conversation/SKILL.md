---
name: multi-agent-tts-conversation
description: "Generate batch multi-agent dialogues using TTS: script authoring, per-voice generation, mixing, and distribution patterns."
intent: Create realistic agent conversations as pre-recorded audio clips using TTS providers (no streaming required)
category: media
primary_tools:
  - elevenlabs-tts-integration
  - ffmpeg
secondary_tools: []
critical_dependencies:
  - ELEVENLABS_API_KEY (if using ElevenLabs)
  - agent-voice-assignments (canonical voice IDs)
common_patterns:
  - batch-generation
  - voice-consistency
  - audio-mixing
  - local-over-cloud
fragments: []
setup_needed: false
---

# Multi-Agent TTS Conversation Generation

## Purpose

Produce **pre-recorded multi-agent dialogues** as a single audio file using existing TTS tools. This is a **batch workflow** — not real-time streaming — suitable for:
- Daily standup audio briefs
- Hackathon pitch practice recordings
- Demo narration tracks
- Agent debate recordings
- Travel journal voiceovers

**Why batch vs streaming:** Avoids expensive Voice Agent subscriptions; runs locally; fully controllable post-production.

---

## Workflow Overview

```
Script → Voice Assignment → TTS Generation → Audio Mixing → Distribution
(1)     (2)               (3)              (4)             (5)
```

### Step 1 — Script Authoring
Write a dialogue script in markdown:
```markdown
# Daily Standup — May 03 2026

**Desmond:** "Hey team, finish the hackathon writeup today."
**DMOB:** "I'm debugging the escrow state machine. ETA 4 hours."
**YoYo:** "Marketwatch says AVAX is pumping. Should we adjust LP positions?"
```

**Rules:**
- One speaker per line
- Format: `**Agent Name:** "dialogue text"`
- Keep lines < 30s spoken (avoid long monologues)
- End with a clear speaker transition or fade-out

### Step 2 — Voice Assignment
Map each agent name → voice ID using the **canonical voice assignment table** (from `elevenlabs-tts-integration` skill):

| Agent | Voice Name | Voice ID |
|---|---|---|
| Gentech | George | JBFqnCBsd6RMkjVDRZzb |
| DMOB | Charlie | IKne3meq5aSn9XLyUdCD |
| YoYo | YoYo | EXAVITQu4vr4xnSDxMaL |
| Desmond | Desmond | FGY2WhTYpPnrIDTdsKH5 |

**If a new agent appears:** Request voice clone via `elevenlabs-config.md` before generating.

### Step 3 — TTS Generation (Batch)
For each speaker line, generate an audio file using the assigned voice.

**Preferred tool:** `elevenlabs-tts-integration` skill (CLI wrapper around ElevenLabs API).

**Script:**
```bash
# Generate per-line audio (stems)
for line in "$(grep -E '^\*\*.*\*\*:' script.md | sed 's/...//')"; do
  agent=$(echo "$line" | grep -o '^\*\*.*\*\*' | tr -d '*')
  text=$(echo "$line" | sed "s/^\*\*.*\*\*:\s*//")
  voice_id=$(get_voice_id "$agent")  # from assignment table
  curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/${voice_id}" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"text":"'"${text}"'","model_id":"eleven_multilingual_v2"}' \
    --output "stems/${agent}_$(date +%s).mp3"
done
```

**Alternative (CPU-friendly, free):** Use `edge-tts` (Microsoft) — lower quality but zero cost:
```bash
echo "$text" | edge-tts --voice "en-US-ChristopherNeural" --write "stems/${agent}.mp3"
```

**File naming:** `stems/<agent>_<timestamp>.mp3` (preserves order, allows multiple lines per agent).

### Step 4 — Audio Mixing
Concatenate stems in script order into a single track with optional gaps.

**Using ffmpeg:**
```bash
# Create file list in order
ls stems/*.mp3 | sort > files.txt
# Concatenate with 0.5s silence between speakers
ffmpeg -f concat -safe 0 -i <(sed 's/^/file /' files.txt) -c copy output_raw.mp3
# Add short crossfade (optional)
ffmpeg -i output_raw.mp3 -af "afade=t=in:st=0:d=0.5,afade=t=out:st=-0.5:d=0.5" output_mixed.mp3
```

**Tip:** Keep raw stems in `stems/` — allows remixing without regenerating TTS.

### Step 5 — Distribution
Options:
1. **Vault note:** Attach audio to vault entry (copy to `06-Content/Audio/`)
2. **Telegram upload:** Use Telegram Bot API or manual upload
3. **GitHub release:** Attach to latest hackathon commit
4. **Email:** Send to both Gmail accounts as voice note

---

## Voice Consistency Rules

**Never improvise voices** — always use the assignment table. If you need a new voice:
1. Create a clone request in `/root/vaults/gentech/01-Agents/config/elevenlabs-config.md`
2. Wait for approval (Jordan)
3. Update `agent-voice-assignments.md` table
4. THEN generate audio

**Pitfall:** Mixing voice providers mid-conversation (Edge TTS for one agent, ElevenLabs for another) sounds jarring. Decide provider per-project, not per-line.

---

## Project Templates

### Daily Standup Audio Brief
- **Source:** `00-HQ/01-Projects/Daily-Standup.md`
- **Schedule:** Auto-run at 8:30 AM via cron
- **Output:** `06-Content/Audio/standup-YYYY-MM-DD.mp3`
- **Distribution:** Upload to Telegram group + vault note

### Hackathon Pitch Practice
- **Source:** `02-Labs/Hackathons/<Project>/DemoScript.md`
- **Runtime:** On-demand before submission deadline
- **Output:** `06-Content/Audio/pitch-<project>.mp3`
- **Distribution:** Embed in README, submit as bonus asset

### Agent Debate Recording
- **Source:** Green Room discussion transcript
- **Goal:** Capture differing perspectives for HQ review
- **Output:** `06-Content/Audio/debate-<topic>.mp3`

---

## Local vs Cloud Trade-offs

| Aspect | ElevenLabs Cloud | Edge TTS (Local) | Audio Unit |
|---|---|---|---|
| **Quality** | Premium, emotional | Robotic, monotone | ElevenLabs wins |
| **Cost** | ~$0.30/min | Free | Edge wins |
| **Latency** | ~5s per line (API) | ~1s per line (subprocess) | Edge wins |
| **Voice variety** | 100+ | ~30 | ElevenLabs wins |
| **Offline** | ❌ | ✅ | Edge wins |

**Rule of thumb:**
- Production/hackathon demos → ElevenLabs
- Internal test/draft → Edge TTS
- Long-form (10+ min) → Hybrid (ElevenLabs key speakers, Edge for crowd/extra voices)

---

## Automation Opportunities

**Cron job:** Nightly regeneration of the latest standup brief (if script updated) → auto-upload to shared folder.

**GitHub Action:** On PR merge to `main`, regenerate pitch audio for that project and attach to release.

**Vault hook:** New note in `00-HQ/05-Configs/` with `#audio` tag triggers TTS generation.

---

## Pitfalls & Mitigations

| Pitfall | Impact | Mitigation |
|---|---|---|
| **API key 401** | All generations fail | Check key validity before batch; fallback to Edge TTS if critical |
| **Wrong voice assigned** | Inconsistent character | Double-check `agent-voice-assignments.md` before running |
| **Overlong lines** (>60s audio) | Unwieldy files | Split lines; add natural pauses in script with `...` |
| **Silence gaps too short** | Speech overlap, unlistenable | Add 0.7s gap between speakers minimum |
| **Missing stem files** | Broken concatenation | Keep stems in version control; regenerate missing ones automatically |
| **Wrong order** | Jumbled conversation | Sort stems by numeric sequence in filename; embed sequence in filename |

---

## Quality Checklist

Before distributing a generated conversation:
- [ ] All speakers present in assignment table
- [ ] Stems generated for every line (no missing audio)
- [ ] Final mix has 0.5–1.0s gap between speaker changes
- [ ] Volume normalized across stems (use `ffmpeg -af 'loudnorm'`)
- [ ] No API error artifacts (truncated audio, error voice)
- [ ] Filename encodes date/project for easy retrieval

---

## Support Files

- `references/voice-assignment-table.md` — canonical voice ID mapping (copy from elevenlabs skill)
- `templates/script-template.md` — markdown dialogue template with speaker formatting
- `scripts/generate-tts-batch.sh` — end-to-end stem generation from script
- `scripts/mix-audio.sh` — ffmpeg concatenation + normalization
- `scripts/validate-conversation.sh` — pre-flight check (all voices present, stems exist)

---

## Related Skills

- `elevenlabs-tts-integration` — API key management, voice cloning workflow
- `comfyui` — if you later want to add ambient background music/atmosphere
- `obsidian` — where scripts and final audio notes live
- `notion` — optional distribution target

---

## Quick Reference Commands

```bash
# Generate all stems from script
./scripts/generate-tts-batch.sh --script "Daily-Standup.md" --output-dir "stems/"

# Mix stems into final audio
./scripts/mix-audio.sh --stems-dir "stems/" --output "standup-today.mp3"

# Validate before distribution
./scripts/validate-conversation.sh --script "Daily-Standup.md" --stems-dir "stems/"
```

---

*Session discovery (2026-05-03): User wants multi-agent conversations without Voice Agent subscription; batch TTS workflow sufficient; 32GB RAM local machine can handle generation; mapcn and Understand-Anything identified as relevant to travel viz and knowledge graph respectively; local Hermes agent deferred to Wednesday.*
