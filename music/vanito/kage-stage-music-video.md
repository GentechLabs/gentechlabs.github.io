# KAGE Stage Music Video — Church of the Dead (NEXT WEEK)

**Status:** IN PROGRESS · **PAUSED Aug 16 — weekly LLM usage at 82%, resume after reset** · 45s built (v7)
**Owner:** Vanito + Gentech

## ✅ CURRENT STATE — 45s STAGE VIDEO (v7, the rapping beat, APPROVED)
- **`music/vanito/kage-cotd-stage-v7.mp4`** (45s) — the current best cut, scored contiguously with the stage edition song (0-45s). Vault + VPS ✅.
- VPS: `https://vanito.gentechlabs.net/music/vanito/kage-cotd-stage-v7.mp4` (200 verified)
- **Sequence (45s, one continuous stage-edition track):**
  1. **0-20s** — stitched opening (`kage-cotd-opening.mp4`): cathedral establishing + KAGE's first power chord
  2. **20-25s** — brief flashback: KAGE fighting shadow creatures (reused `kage-church-sb6.mp4`, zero cost)
  3. **25-30s** — back to guitar: head thrown back, guitar on fire (`kage-stage-chorus-shred.mp4`)
  4. **30-35s** — camera orbits the stage (`kage-camera-orbit.mp4`)
  5. **35-40s** — breakdown solo (`kage-breakdown-solo.mp4`)
  6. **40-45s** — **KAGE RAPS while playing guitar** (`kage-rapping.mp4`) — NO microphone, mouth moves like rapping (NOT screaming), hands only on guitar. This was the fix Vanito requested (the earlier singing clip had a mic + screaming mouth — rejected).
- **Budget:** ~$0.50 USDC left on Base (needs ~$1.50 top-up for next clip)

## ✅ DONE — CINEMATIC OPENING + CATHEDRAL STAGE (saved, don't forget)
- `music/vanito/kage-cotd-opening.mp4` (20s) — CHAINED + SCORED opening sequence: (1) cinematic establishing shot of cathedral + blood moon with "GEN TECH PRODUCTION" + "VANITO FILM" dispersing (0-10s), (2) KAGE shredding the electric guitar at the cathedral stage (10-20s). Scored contiguously with the stage edition (0-20s). 1280p, 14M. Vault + repo + VPS ✅.
- `music/vanito/kage-cathedral-stage.png` — approved cathedral-stage keyframe (KAGE at church, blood moon + rose window, fog, crowd).
- `music/vanito/kage-cathedral-stage-clip.mp4` — raw 10s performance clip (approved).
- `music/vanito/kage-cathedral-stage-scored.mp4` — 10s clip scored to stage edition (10-20s).
- VPS: `https://vanito.gentechlabs.net/music/vanito/kage-cotd-opening.mp4`
- Generators: `gen-cathedral-stage-keyframe.mjs` + `gen-cathedral-stage-clip.mjs` + `gen-cinematic-open.mjs` in `/root/.hermes/blockrun-mcp/`
- Earlier: `kage-stage-intro.mp4` (old plain-concert-stage 10s clip) — SUPERSEDED by cathedral-stage clip. Keep for reference.

## ✅ DONE — CREATIVE 10s INTRO (saved, don't forget)
- `music/vanito/kage-stage-intro.mp4` (10s) — KAGE center stage, electric guitar, strikes first power chord, crimson lights + smoke + crowd erupt. Low-angle hero shot. Saved to vault + hub repo + VPS.
- `music/vanito/kage-stage-intro.png` — the approved keyframe (1536×1024).
- VPS: `https://vanito.gentechlabs.net/music/vanito/kage-stage-intro.mp4`
- Generators: `gen-stage-intro-keyframe.mjs` + `gen-stage-intro-clip.mjs` in `/root/.hermes/blockrun-mcp/`
- NOT YET scored to the stage edition song — next step is syncing the chord strike to the song's opening.

## NEXT BEATS (resume after weekly reset)
- **Guitar rev** — KAGE revving the guitar like a throttle
- **Finale** — the big ending moment
- Keep the show going — Vanito wants it to keep building, get fancy, KAGE rapping/singing to the music
- **Budget:** top up ~$1.50 before the next clip
- **LLM:** weekly usage was 82% when paused — resume when it drops (or route to Z.AI/OpenCode Go)

## 🎬 NEXT SCENE (LOCKED — Vanito's idea, 5s, 45-50s of song)
**Scene 7 — "The Shadows Appear"** (5s, scored to 45-50s)
- **0-2s:** KAGE keeps rapping while playing the guitar (continues from v7's rapping beat)
- **2-5s:** KAGE STOPS playing, looks around SHOCKED — shadows start appearing and flying around him, multiple shadow figures circling him
- He looks around at the shadows, wondering what's about to happen — "oh my god, where did they come from" energy
- **Camera:** rotate in circles around him IF it doesn't break the scene; otherwise KAGE just looks around at the flying shadows
- **Chain from:** last frame of `kage-rapping.mp4` (verified clean — KAGE mid-performance, cathedral stage, blood moon)
- **Budget needed:** ~$1.50 top-up (wallet at $0.49)
- **Generator:** `gen-stage-shadows.mjs` (to create on resume)

## The Task
Produce a **stage music video** of KAGE performing "Church of the Dead" live on stage.

## KEY CHANGE: GUITAR, NOT GUNS
KAGE performs with an **electric guitar** (NOT his Desert Eagles) — he rocks/revs the guitar to the music. The guns are replaced by the guitar for this stage performance.

## STAGE LOCATION (LOCKED)
The stage is **inside / before the gothic cathedral** — the same "Church of the Dead" world as the cinematic opening (blood-red moon, rose window, fog, graveyard crosses). Flow:
1. 🏛️ Cinematic opening — slow push toward the cathedral under the blood-red moon, "GEN TECH PRODUCTION" + "VANITO FILM" disperse. (KAGE `kage-cotd-open-scored.mp4`)
2. 🎸 KAGE performs on a stage **inside/before the cathedral** — rose window and blood moon behind him, fog and crimson light on stage, electric guitar.
3. 🎵 Scored with the stage edition ONLY. Update the LOOK string + keyframes accordingly: KAGE holding/playing a dark electric guitar, shredding to the beat, no guns in frame.

## SONG: STAGE EDITION
The stage music video is scored with the **stage edition** of Church of the Dead (`audio_43a5d51700ef.mp3`, 279s, title "Church Of The Dead stage edition"). Use this, NOT the 165s original. Sync the performance to the stage edition's most energetic stretch.

## What We Have (reusable)
- **Song:** `music/vanito/church-of-the-dead-song.mp3` — Church of the Dead (165s) + **stage edition (279s)** both in vault. **Stage edition is the one for this video.**
- **Character:** KAGE — locked LOOK string + canonical seed (`kage-church-scene-final.png`) + character sheet
- **Cover:** `church-of-the-dead-cover.png` (KAGE, dual gunmetal-black Desert Eagles, red phoenix)
- **Skills:** `beat-based-film-pipeline` (build) + `seedance-prompt-fixes` (fix) — both saved to brain
- **Film:** `church-of-the-dead-final.mp4` (61s, scored + SFX) — the fight film this is a companion to

## Approach (from the saved skills)
- Keyframe-first: cheap GPT Image 2 keyframes (~$0.06) to lock the stage + KAGE's performance look BEFORE animating
- One approved clip at a time — Vanito directs the choreography
- Stage beats: entrance with guitar, shredding to the chorus, guitar revs, breakdown solo, finale
- Score with the Church of the Dead song, sync to the most energetic stretch
- Branded intro (GenTech Production / A Vanito Film) + copyright outro
- Deploy to Vanito hub artist page

## Notes
- Wallet check before each generation (`node bal.mjs`)
- Audit every clip before showing (extract frames → vision_analyze)
- User-provided clips = zero cost option
