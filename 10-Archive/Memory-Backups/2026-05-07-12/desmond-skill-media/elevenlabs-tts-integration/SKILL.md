---
name: elevenlabs-tts-integration
description: Manage ElevenLabs TTS integration - API key location, voice ID assignments, cloning workflows, provider fallback, and cross-agent voice consistency
intent: Integrate and maintain ElevenLabs text-to-speech across Hermes agents
category: media
primary_tools: []
secondary_tools: []
critical_dependencies: []
common_patterns: []
fragments: []
linked_files: []
setup_needed: false
---

# ElevenLabs TTS Integration

**Hermes Agent — Media Skills Division**

## Identity
- **Category**: media / text-to-speech
- **Vault References**: `00-System/agent-voice-assignments.md`, `01-Agents/config/elevenlabs-config.md`
- **Brain Config**: `/root/repos/hermes-brain/config.yaml` (tts section)
- **Related Skills**: `media` (parent category), `hermes-agent` (for env loading)

---

## Purpose

Manage ElevenLabs TTS integration across all Hermes agents:
- API key storage locations and rotation
- Voice ID assignments per agent
- Voice cloning request workflow
- Provider fallback chain logic
- Cross-system consistency (brain ↔ profiles ↔ vault docs)

This is the **single source of truth** for voice configuration.

---

## Quick Reference

### API Key Location
```
Primary vault: /root/vaults/gentech/.env
  ELEVENLABS_API_KEY=ff52c5...6d55 (masked value)

Runtime copies: ~/.hermes/profiles/{agent}/.env (all 4 agents)
System hermes env: ~/.hermes/.env (holds other keys, not 11Labs)

⚠️  Key status note: Old key ff52c5... revoked (401). May need rotation.
```

### Active Voice Assignments
| Agent | Voice Name | Voice ID | Model | Provider |
|---|---|---|---|---|
| Gentech | George | JBFqnCBsd6RMkjVDRZzb | eleven_multilingual_v2 | elevenlabs |
| DMOB | Charlie | IKne3meq5aSn9XLyUdCD | eleven_multilingual_v2 | elevenlabs |
| YoYo | YoYo | EXAVITQu4vr4xnSDxMaL | eleven_multilingual_v2 | elevenlabs |
| Desmond | Desmond | FGY2WhTYpPnrIDTdsKH5 | eleven_multilingual_v2 | elevenlabs |

**Backup voices:**
- Gentech-Iroh: NqA7ncEPGGt1nDbCrDex (softer mentor)
- IvanOnTech: ToA54GQ3jBRB2zt0fBXj (crypto-native narrator)

### Agent Profile TTS Config (YAML)
```yaml
tts:
  provider: elevenlabs
  edge:
    voice: en-US-AriaNeural
  elevenlabs:
    voice_id: {VOICE_ID}
    model_id: eleven_multilingual_v2
  openai:
    model: gpt-4o-mini-tts
    voice: alloy
```
Fallback chain: elevenlabs → edge → openai → xai → mistral → neutts

---

## Workflow: Voice Cloning & Updates

### 1. New Voice Request
- **File**: `/root/vaults/gentech/01-Agents/config/elevenlabs-config.md`
- Mark status: `# Desmond: Steve Harvey inspired - PENDING`
- **Design prompt**: Use ElevenLabs Voice Design
  - `"Charismatic game show host, energetic, warm, laughs easily"`
  - `"Deep authoritative leader, calm under pressure, transformer-like resonance"`

### 2. Instant Voice Cloning
- Requires consent for real people (policy)
- ~30s audio sample minimum
- Professional: signed consent + identity verification

### 3. Update Assignments (after approval)
1. Update `VOICE_ID_{AGENT}` in `elevenlabs-config.md`
2. Update `agent-voice-assignments.md` table
3. Update each agent's `~/.hermes/profiles/{agent}/config.yaml`
4. Test with sample from `SAMPLES` section

### 4. API Key Rotation (on 401)
1. Generate new key in ElevenLabs dashboard
2. Update **all 5 locations**:
   - `/root/vaults/gentech/.env`
   - `~/.hermes/profiles/desmond/.env`
   - `~/.hermes/profiles/dmob/.env`
   - `~/.hermes/profiles/yoyo/.env`
   - `~/.hermes/profiles/gentech/.env`
3. Update vault note with new key fingerprint
4. Restart Hermes agents

---

## Common Tasks

### Check Active Voice for Agent
```bash
cat ~/.hermes/profiles/{agent}/config.yaml | awk '/tts:/,/^[^ ]/ {print}'
grep -A 3 'voice_id:' /root/repos/hermes-brain/config.yaml
```

### Generate Test Audio
```bash
curl -X POST https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID} \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"Sample","model_id":"eleven_multilingual_v2"}'
```

### List All Voices in Account
```bash
curl -X GET https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### Validate API Key
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/voices
# 200 = valid, 401 = rotate key
```

---

## Pitfalls

| # | Pitfall | Mitigation |
|---|---|---|
| 1 | **API key expired** — 401 → fallback to Edge TTS | Check dashboard; rotate key across all 5 env files |
| 2 | **Voice ID mismatch** — brain config ≠ agent profile | Always update brain + profile + vault docs together |
| 3 | **Key masked in vault** — full value not visible in `.env` | Retrieve from ElevenLabs dashboard; never commit unmasked |
| 4 | **Wrong provider active** — agent `provider: edge` not `elevenlabs` | Verify `tts.provider` in agent config.yaml |
| 5 | **Model ID drift** — profiles use `eleven_multilingual_v2`, voice settings JSON uses `eleven_turbo_v2_5` | Reconcile or document divergence when customizing |
| 6 | **Silent fallback** — agent switches to backup TTS silently | Check audio output; verify provider in profile if 11Labs unused |
| 7 | **Batch conversation mixing fails** — stems missing or order scrambled | Use `multi-agent-tts-conversation` skill's validation script before mixing |

---

## Reference Material

### Voice Settings JSON (elevenlabs-config.md lines 20-45)
```json
{
  "gentech": {
    "model_id": "eleven_turbo_v2_5",
    "stability": 0.75,
    "similarity_boost": 0.75,
    "speed": 0.95
  }
}
```
**Note**: Profile configs use `eleven_multilingual_v2` but voice settings JSON uses `eleven_turbo_v2_5`. Divergence exists; reconcile if customizing parameters.

### Policy: All Male Voices
Jordan confirmed (agent-voice-assignments.md line 4): all agent voices are male. New clones must respect this constraint.

---

## How to Debug

### Symptom: Audio uses Edge TTS instead of ElevenLabs
1. Check `tts.provider` in agent profile
2. If `edge` → change to `elevenlabs`
3. Verify `ELEVENLABS_API_KEY` in agent's `.env`
4. Restart agent session

### Symptom: 401 Unauthorized from ElevenLabs API
1. Run key validation curl
2. If 401 → rotate key across **all 5 locations**
3. Check ElevenLabs dashboard for key status
4. Update vault note with new key fingerprint

### Symptom: Wrong voice playing
1. Verify `voice_id` matches assignment table
2. Check brain config for overrides
3. Confirm no voice settings JSON overriding profile

---

## Support Files

- `references/agent-voice-assignments.md` — canonical voice ID table (from vault)
- `references/elevenlabs-config-template.md` — full config template for new agents
- `scripts/test-elevenlabs-key.sh` — key validation script (HTTP 200 check)

---

## Related

- **Brain**: `/root/repos/hermes-brain/config.yaml` — central TTS provider config
- **Vault**: `00-System/agent-voice-assignments.md` — canonical voice assignments
- **Config**: `/root/vaults/gentech/01-Agents/config/elevenlabs-config.md` — clone requests & settings
- **Skill**: `media` — other TTS providers (OpenAI, XAI, Mistral, Kokoro)

---

*Session discovery (2026-05-02): API key stored masked in vault with note "old key revoked"; voice clone requests for Desmond (Steve Harvey) and YoYo (Peter Cullen) pending; active agent profiles use eleven_multilingual_v2; brain config contains provider-agnostic TTS routing with multi-provider fallback chain.*