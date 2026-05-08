# Steve Harvey Style Script Template

**Voice ID:** `Rxk9LQxvNFEplpjjsjuN` (Desmond-SteveHarvey custom clone)  
**Best for:** Social media storytelling, energetic explainers, audience engagement

## Voice Settings (ElevenLabs)

```json
{
  "stability": 0.7,
  "similarity_boost": 0.7,
  "style": 0.2,
  "use_speaker_boost": true
}
```

**Why these settings:**
- `stability 0.7`: Consistent but natural delivery
- `similarity_boost 0.7`: Recognizable Steve Harvey character
- `style 0.2`: Low exaggeration → cleaner, fewer artifacts
- Avoid SSML `<break>` tags → causes choppy artifacts

## Script Structure Template

```text
[OPENING - ENERGETIC]
Y'all, let me tell you... [topic]!

[HOOK - RELATABLE]
I know a lot of y'all be like "[question/joke]" 😂

[EXPLANATION - SIMPLE]
So picture this: [simple analogy]

[DETAILS - CONCRETE]
Here's the breakdown:
- Point one...
- Point two...
- Point three...

[CLOSING - PUNCHY]
That's what's up. Follow along — it's fascinating stuff!
```

## Writing Guidelines

- ✅ **Short sentences** (12–15 words max)
- ✅ **Ellipses for trailing thoughts** (`...`)
- ✅ **Parenthetical asides** `(like this)`
- ✅ **Audience call-outs** ("I know y'all be like...")
- ✅ **Punchy one-liners** ("That's what's up.")
- ❌ **NO SSML breaks** — let TTS natural prosody handle pacing
- ❌ **Avoid over-the-top style** (`style: 0.4+`) → causes artifacts

## Example (GenTech Intro for Non-Tech Friends)

```
Y'all, let me tell you what my brother Jordan is doing — because I know a lot of y'all be like "Jordan, what you DO all day?!" 😂

So picture this: Right now, when you want something done online, you gotta go FIND someone to do it — find a freelancer, find a service, go through apps… Jordan building something different.

He's building AI that works FOR you like an actual employee — but it's digital, it's smart, and it's always on.

Here's the breakdown:
- Need a logo? His AI agents will design it.
- Need research? They'll go dig it up and summarize.
- Need to manage a project? They'll coordinate the whole thing.

Not one AI — a whole TEAM of specialized AI agents that talk to each other and get stuff done. That's GenTech. That's what Jordan building.

And the crazy part? These AI agents have their own little digital wallets. They pay each other. They team up on jobs. They're like a digital workforce that never sleeps.

So when you hear "AI agents" — think "autonomous digital employees" that Jordan's team is building from the ground up.

That's the mission. That's what's up. Follow along — it's fascinating stuff!
```

## Testing Checklist

- [ ] No random noise/pops between sentences
- [ ] Pauses feel natural, not robotic
- [ ] Energy matches Steve Harvey (punchy, audience-engaged)
- [ ] Ending is complete, not truncated
- [ ] Duration ~60s for Instagram Story cut
- [ ] Character count ~1,100–1,300 (fits budget)

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Choppy pauses | SSML `<break>` tags used | Remove SSML, rely on natural prosody |
| Robotic sound | `style` too high (>0.4) | Reduce to 0.2–0.3 |
| Artifacts/pops | `stability` too low (<0.5) | Increase to 0.7 |
| Too fast | Voice settings default | Reduce `style`, increase `stability` |
| Voice not recognizable | `similarity_boost` too low | Increase to 0.8 |

---

*Last updated: 2026-05-02 — discovered SSML pause artifact issue, established natural delivery approach.*