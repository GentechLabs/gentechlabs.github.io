# FrameForge — AI Storyboard Service

**Status:** Concept → Pending Build
**Lead:** Gentech + Vanito (KAGE pipeline R&D)
**Revenue Model:** Service (now) → API (phase 2)

---

## The Product

A controlled pre-visualization service that turns character reference sheets into camera-ready storyboard frames. Locked character consistency, editable shot lists, studio-grade output. No randomness, no character drift.

Built on the pipeline we proved with Vanito's KAGE film: character sheet → Seedance seed → time-coded prompts → inline character coating every frame → compiled storyboard.

## Why It Sells

Studios spend $50K–$200K on concept art and animatics before a single frame of principal photography. FrameForge delivers a storyboard in an afternoon for $500–$5,000. Same crew, same workflow, faster iteration loop.

The strikes taught Hollywood that "replace the artist" is poison. "Give the director a faster previs tool" is the right pitch. FrameForge doesn't replace storyboard artists — it lets directors iterate on shot composition, camera angles, and pacing before commissioning final art.

## Target Buyers

| Tier | Buyer | Price | Volume |
|------|-------|-------|--------|
| Indie | Filmmakers (<$1M budget) | $500–$1,500/project | High |
| Studio | Production companies | $2,000–$5,000/project | Medium |
| Enterprise | Studios, VFX houses | Custom | Low, high-value |

## Revenue Model

### Phase 1 — Service (Launch Immediately)
- **Flat-rate storyboard:** $1,500 for up to 10 scenes, 3 frames per scene
- **Express (48h):** $2,500
- **Per additional scene:** $150
- **Revenue per project:** $1,500–$5,000
- **Cost per project:** ~$15–$45 in AI inference (FLUX/GPT Image 2)

### Phase 2 — API (Build after demand validation)
- `POST /v1/storyboard` — $3–$5 per frame
- `POST /v1/character/lock` — $10 per character (analyze + produce repeatable seed config)
- `POST /v1/storyboard/compile` — $25 per video export (ffmpeg concat + title overlays)
- **Unit cost per frame:** $0.40–$0.90 (inference)
- **Margin:** ~80%

### Phase 3 — Subscription (Scale)
- **Starter:** 5 scenes/month, $199/mo
- **Studio:** 20 scenes/month, $799/mo
- **Enterprise:** Unlimited, custom pricing

## Tech Stack

**Core Pipeline (already working):**
- Character sheet → FLUX/GPT Image 2 (character consistency)
- Seedance 2.0 (video/generation)
- Inline character coating (proven on KAGE — every prompt includes full character description)
- Time-coded prompt structure (`[0-3s][3-6s][6-9s][9-12s][12-15s]`)
- ffmpeg concat + audio mix + title overlays

**Missing for Product:**
- Landing page / service portal
- Shot list editor (camera angle, lighting, mood selector)
- Character config persistence (store coating + seed once, reuse)
- Batch generator (process N shots from one config)
- Client gallery (shareable storyboard URL)

## MVP Scope (Build in One Session)

### Service Portal (Cloud — Gentech)
1. **Landing page:** What it does, sample output, pricing, "Get a Storyboard" CTA
2. **Order form:** Upload character sheet, describe scenes (shot list), select tier
3. **Delivery page:** Generated storyboard gallery, download links

### Backend (Cloud — Gentech)
4. **Character locker:** Analyze character sheet → store coating + seed + palette config
5. **Storyboard engine:** Character config + scene descriptions → batch generate frames
6. **Compile pipeline:** Frames → animated video (ffmpeg concat + credits overlay)

## Market Positioning

FrameForge sits at the intersection of three trends:
1. **AI previs** — No one has cracked consistent character-for-scene generation at scale
2. **Hollywood 2026** — Post-strike, studios are hungry for AI tools that respect the crew
3. **Remote pre-production** — Directors need to iterate on shots without flying to a studio

**Competition:**
- Midjourney storyboard — No character consistency, no camera control
- Runway Gen-3 — Video-first, no shot list structure
- Wonder Studio — Character replacement, not from-scratch storyboard
- **FrameForge differentiator:** Character reference sheet → locked look → camera-direction-native prompts → consistent output every frame

## Next Steps

1. Jordan decides: build MVP (landing page + basic pipeline) or test demand via service first?
2. If build: estimate effort (~1 session for landing page + character locker)
3. If service first: write the "Get a Storyboard" landing page copy
4. Vanito continues KAGE film — that R&D feeds directly into FrameForge's pipeline
