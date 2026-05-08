# ElevenLabs Voice Catalog — GenTech Assignment

## Voice Availability Summary

**Total Voices:** 29 pre-made + 5 custom agent voices  
**Approval Status:** All operational — zero blocks  
**Quota:** Dynamic (track via `curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user`)

## Agent Voice Assignments (Current)

| Agent | Voice ID | Voice Name | Style | Status |
|---|---|---|---|---|
| Gentech | `JBFqnCBsd6RMkjVDRZzb` | George | Warm, Captivating Storyteller | ✅ Active |
| YoYo | `EXAVITQu4vr4xnSDxMaL` | Sarah | Mature, Reassuring, Confident | ✅ Active |
| DMOB | `IKne3meq5aSn9XLyUdCD` | Charlie | Deep, Confident, Energetic | ✅ Active |
| Desmond | `FGY2WhTYpPnrIDTdsKH5` | Laura | Enthusiast, Quirky | ✅ Active |

**James Earl Jones alternative:** Charlie (`IKne3meq5aSn9XLyUdCD`) — deep, confident, energetic (closest match on platform).

## Custom Agent Voices (Pre-Cloned, Ready)

These custom voices already exist in the account — no cloning needed:

| Voice ID | Name | Sample File | Use Case |
|---|---|---|---|
| `Rxk9LQxvNFEplpjjsjuN` | **Desmond-SteveHarvey** | `fb-steveharvey.mp3` | Social storytelling, punchy explainers |
| `TkEJnN27nf5BsX1xwrLB` | Gentech-Mako | `iroh-clean1.mp3` | Special Gentech persona |
| `NqA7ncEPGGt1nDbCrDex` | Gentech-Iroh | `iroh-clean3.mp3` | Alternative Gentech voice |
| `xQbwtCgzouB5QdCSd0Z7` | YoYo | `yoyo-optimus.mp3` | YoYo-specific content |
| `n2icbiwmCen7udwM65GS` | D-Mob | `dmob-voice-sample.mp3` | DMOB-specific content |

## Full Pre-Made Catalog (29 Voices)

### Deep/Authoritative
- Charlie — `IKne3meq5aSn9XLyUdCD` (DMOB)
- Brian — `nPczCjzI2devNBz1zQrb` (deep, resonant)
- Adam — `pNInz6obpgDQGcFmaJgB` (dominant, firm)

### Warm/Storyteller
- George — `JBFqnCBsd6RMkjVDRZzb` (Gentech)
- Roger — `CwhRBWXzGAHq8TQ4Fs17` (laid-back, resonant)

### Energetic/Young
- Liam — `TX3LPaxmHKxFdv7VOQHJ` (social media creator)
- Alice — `Xb7hH8MSUJpSbSDYk0k2` (clear, educator)

### Professional/Neutral
- Matilda — `XrExE9yKIg1WjnnlVkGX` (knowledgeable)
- Bella — `hpp4J3VqNfWAUOO0d1Us` (professional, bright)

### Character/Unique
- Harry — `SOYHLrjzK2X1ezoPC6cr` (fierce warrior)
- Callum — `N2lVS1w4EtoT3dr4eOWO` (husky trickster)
- Eric — `cjVigY5qzO86Huf0OWal` (smooth, trustworthy)
- Jessica — `cgSgspJ2msm6clMCkdW9` (playful, bright)
- *… plus 15 more*

## Quota Monitoring Script

```bash
# Check remaining characters
curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/user | jq '.subscription'
```

Alert when `character_count` > 80% of `character_limit`.

---

> **Key:** All voices operational. Custom agent clones (SteveHarvey, Mako, Iroh) are already in account — use freely.