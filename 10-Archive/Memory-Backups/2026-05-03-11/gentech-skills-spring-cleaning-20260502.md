# Session Reference: Spring Cleaning Audio — 2026-05-02

## Task
Generate Steve Harvey-style audio about GenTech's storage bloat analysis for Jordan's Instagram Story.

## Script Highlights
- Hook: "Y'all, we did some SERIOUS spring cleaning today at GenTech!"
- Key stats: 152 GB total bloat → 56 GB Hermes backups (recursive loops) + 75 GB VideoAgent tools
- Punchline: "Diagnosed, planned, and ready to act — BOOM we executing after hackathon crunch!"

## Provider Journey
| Attempt | Provider | Result | Notes |
|---|---|---|---|
| 1 | ElevenLabs | ❌ 401 invalid_api_key | Key in `.env` but rejected; likely expired or wrong |
| 2 | Edge TTS | ✅ Success | Env var switch: `config['tts']['provider']='edge'`; voice: en-US-AriaNeural |

## Config Change
```yaml
# Before
tts:
  provider: elevenlabs
  elevenlabs:
    voice_id: JBFqnCBsd6RMkjVDRZzb

# After
tts:
  provider: edge
  edge:
    voice: en-US-AriaNeural
```

## Output
- File: `audio_cache/spring-cleaning-steve-harvey.ogg`
- Duration: ~60 seconds
- Delivered to: `telegram:Gentech Entertainment` (for Instagram upload)
- Vault logs:
  - `00-HQ/Operations/Spring-Cleaning-20260502.md` (technical analysis)
  - `00-HQ/Operations/Spring-Cleaning-Instagram-Script.md` (script text)
  - `00-HQ/Operations/Spring-Cleaning-Audio-Delivery-20260502.md` (delivery record)

## Key Learnings
- Always validate TTS provider with 3-second test before full generation
- Edge TTS is reliable fallback; no key, decent quality
- Instagram Stories audio must be ≤60s — script accordingly
- Vault triple-file pattern ensures traceability

## Next Actions
- Renew ElevenLabs key if high-quality voice needed
- Consider shorter 30s cut for Stories format (future enhancement)
- Execute actual cleanup post-hackathon (May 11/17)