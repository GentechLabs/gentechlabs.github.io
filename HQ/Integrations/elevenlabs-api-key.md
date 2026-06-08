# ElevenLabs API Key — Managed by Gentech HQ

**Date:** 2026-05-02
**Owner:** Jordan (CEO)
**Custodian:** Desmond (Entertainment) — for demo voiceover work
**Integration:** Kite AI demo + Solana Frontier demo narration

---

## Credentials

| Field | Value |
|-------|-------|
| **API Key** | `bb158b2f8063a7d10519ffb3a349d168195f67c9fe5698532e5c191d70298674` |
| **Storage** | EMV — `ELEVENLABS_API_KEY` in Desmond profile (`.env`) |
| **Voices** | 29 total — Laura (FGY2WhTYpPnrIDTdsKH5) configured as default |
| **Model** | `eleven_multilingual_v2` |

---

## Usage

**Desmond — Quick Commands:**
```bash
# Test voice
echo "Test voice for Kite AI demo." | hermes tts --provider elevenlabs

# Full demo script (once storyboard ready)
hermes tts --provider elevenlabs --voice-id FGY2WhTYpPnrIDTdsKH5 --file demo-narration.mp3
```

---

## Quota Monitoring

Check remaining characters:
```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user
```

**Alert threshold:** <10,000 characters remaining → notify Jordan

---

## Change Log
- 2026-05-02: Key added, voices switched to Laura (quirky/enthusiast) per Jordan
- 2026-05-02: Persisted to vault, routed to Desmond
