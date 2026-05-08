# Local vs Cloud TTS Tradeoffs (Session 2026-05-03)

## Context
User (Jordan) wants multi-agent conversations but is Avoiding Voice Agent subscription fees. Instead, using batch TTS generation with existing ElevenLabs subscription and free Edge TTS fallback.

## Alternatives Compared

| Provider | Cost (per minute) | Quality | Latency | Offline | GPU Required |
|---|---|---|---|---|---|
| ElevenLabs Cloud (current) | ~$0.30 | High (emotional) | ~5s/stem | ❌ | ❌ |
| Microsoft Edge TTS | Free | Medium (robotic) | ~1s/stem | ✅ (Windows only) | ❌ |
| Coqui XTTS (local) | Free (compute) | Medium-High | ~3-10s/stem | ✅ | ✅ (GPU speeds up) |
| OpenAI Realtime API | ~$0.50/min | High | <1s streaming | ❌ | ❌ |

## Decision Rules Used

- **Production/hackathon demos:** ElevenLabs (quality matters)
- **Internal drafts/test:** Edge TTS (free, instant)
- **Long-form (>10 min) content:** Hybrid model (ElevenLabs for main speakers, Edge for crowd voices)
- **Offline requirement:** Edge TTS (when no internet) or local Coqui if GPU available

## User Constraints
- Home PC has 32GB RAM (can cache models)
- Local GPU available for acceleration (unspecified model)
- Priority: accessibility (no subscription per-minute fees)

## Implication for Batch Workflow
Since batch generation doesn't require streaming latency, even slow local inference (Coqui on CPU) is acceptable for non-critical paths. The tradeoff becomes cost vs quality, not time.
