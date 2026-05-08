# ElevenLabs Agents — Pricing & Access

**Date evaluated:** 2026-05-03
**Source:** https://elevenlabs.io/pricing (ElevenAgents tab)

## Quick Answer
ElevenLabs Agents is a **separate product** from standard ElevenLabs TTS/Creator subscriptions. It does NOT come with your existing ElevenLabs plan.

## Pricing Model

**Base rate:** $0.08 per minute of agent conversation time

**Monthly plans with bundled minutes:**
- Free: $0/mo → 15 minutes included
- Starter: $6/mo → 75 minutes
- Creator: $22/mo → 275 minutes (popular)
- Pro: $99/mo → 1,238 minutes
- Scale: $330/mo → 3,738 minutes
- Business: $1,320/mo → 12,375 minutes
- Enterprise: custom pricing

All plans include:
- Workflow Builder
- 70+ languages
- Low-latency voice
- Knowledge base integration
- Tool/API connections

## Implications for GenTech

- **Hackathon prototypes:** Free tier (15 min) is sufficient for demos
- **AAE/Travel premium tier:** Would need to budget for runtime costs if we offer voice agents as a feature
- **Local vs cloud:** Agents run on ElevenLabs cloud; we pay per minute
- **Alternative path:** If we want fully local voice agents, we need a different stack (Bark/Parler + local LLM)

## Decision
🔧 **Integrate** for hackathon demos (use free tier).  
🅿️ **Park** for production deployment until we validate revenue model.

## Related
- `skill: elevenlabs` ( ElevenLabs TTS integration already in vault)
- Travel Agent Premium Tier idea (`07-Ideas/travel-agent-crypto-layer.md`)
