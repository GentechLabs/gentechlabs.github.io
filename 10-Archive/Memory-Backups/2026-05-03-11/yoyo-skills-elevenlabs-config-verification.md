# ElevenLabs Configuration Verification

**Skill**: `hermes-agent-environment-debugging` — extension for TTS service-specific audits

**Scope**: Verify ElevenLabs API key presence + voice assignment + provider alignment across vault, Hermes profiles, and agent configs.

---

## Quick Check Commands

```bash
# 1. Verify API key in active locations
grep -h "ELEVENLABS_API_KEY" \
  /root/vaults/gentech/.env \
  /root/.hermes/profiles/gentech/.env \
  /root/.hermes/profiles/yoyo/.env 2>/dev/null

# 2. Extract voice IDs from all agent configs
grep -rh "voice_id:" /root/vaults/gentech/00-System/agent-profiles/*/config.yaml | sort -u

# 3. Check active TTS provider per agent
grep -A2 "tts:" /root/vaults/gentech/00-System/agent-profiles/yoyo/config.yaml
```

---

## Verification Matrix

| Check | Location | What to look for |
|-------|----------|------------------|
| **API key existence** | `vault .env` + `~/.hermes/.env` | `ELEVENLABS_API_KEY=xi-...` format |
| **Key value consistency** | All .env files | Same key across files (sync needed if different) |
| **Agent voice_id** | `agent-profiles/<agent>/config.yaml` → `tts.elevenlabs.voice_id` | UUID-like string; compare against ElevenLabs dashboard |
| **Fallback voice_id** | Same file → often `c69964a6...` (Mistral test voice) | Should be valid or removed |
| **Active provider** | `tts.provider` field | `edge` (Microsoft) vs `elevenlabs` — if `edge`, ElevenLabs config ignored |
| **Voice cloning status** | Agent voice config markdown files | `01-Agents/voices/<agent>-voice-config.md` — check "voice clone pending" flags |

---

## Common Misalignment Patterns

### Pattern A: Provider Mismatch
**Symptom**: `tts.provider: edge` but `tts.elevenlabs.voice_id` populated
**Fix**: Change provider to `elevenlabs` OR clear elevenlabs block to avoid confusion
**Impact**: ElevenLabs voice IDs sit idle; Edge TTS uses Microsoft voices instead

### Pattern B: Pending Voice Clone
**Symptom**: Voice config file says "voice clone pending" but voice_id points to placeholder (e.g., `EXAVITQu4vr4xnSDxMaL` — Sarah)
**Fix**: Update voice_id after cloning completes in ElevenLabs dashboard; archive old config as `*-pending.md`
**Impact**: Agent speaks with wrong voice until updated

### Pattern C: Key Present but Not Loaded
**Symptom**: `.env` file has correct key but gateway returns 401
**Cause**: Key in profile `.env` but not in `~/.hermes/.env` (global) → not in process environment
**Fix**: Copy/append key to `~/.hermes/.env` and restart gateways
**See**: `hermes-agent-environment-debugging` skill for full env_loader precedence

### Pattern D: Fallback Voice Pollution
**Symptom**: Multiple agents share same fallback `c69964a6...` (Mistral test voice) — may be deprecated/deleted in ElevenLabs
**Fix**: Replace with agent-specific fallback or remove if not used
**Impact**: If that voice ID gets removed from ElevenLabs, all agents with that fallback break simultaneously

---

## Session Log: May 2, 2026 Verification

**Trigger**: User asked to "check the brain for contacts, but check to see if the 11 labs API key is in the EMV."

**Findings**:
- ✅ **API key present** in vault `.env` and Hermes global `.env`: `ff52c5f015c3490da49adf12513a6d55`
- ⚠️ **Active provider**: All agents use `edge` (Microsoft Edge TTS) — ElevenLabs configs dormant
- ⚠️ **Voice ID assignments**:
  - YoYo: `xQbwtCgzouB5QdCSd0Z7` (active in config, unused by provider) + fallback `c69964a6...`
  - Gentech: `TkEJnN27nf5BsX1xwrLB` + fallback
  - Desmond: `Rxk9LQxvNFEplpjjsjuN` + fallback
  - D-Mob: `n2icbiwmCen7udwM65GS` + fallback
- ⚠️ **Voice cloning target**: YoYo config voice file (`01-Agents/voices/yoyo-voice-config.md`) shows placeholder Sarah voice (`EXAVITQu4vr4xnSDxMaL`) with "voice clone pending" — suggests Peter Cullen/Optimus Prime clone not yet activated in agent config

**Recommendation**: If voice cloning completed, update `voice_id` fields in agent configs and switch `tts.provider` to `elevenlabs`.

---

## Reference: ElevenLabs Voice ID Format

- Standard voice ID: 32-char hex-like string (e.g., `xQbwtCgzouB5QdCSd0Z7`)
- UUID format with dashes also valid (e.g., `c69964a6-ab8b-4f8a-9465-ec0925096ec8`)
- Can verify existence via API: `GET /v1/voices` with API key

---

## Related Skills

- `hermes-agent-environment-debugging` — general credential/env loading diagnostics
- `autonomous-ai-agents/hermes-agent` — Hermes agent configuration patterns
