# 🎭 Vanito's Hub — Full Theme Overhaul + Rain + Lighting

## Task 1: Rain Effect — Canvas-Based

The current rain effect uses JavaScript canvas with 150 raindrops, wind, splash particles, and a wet glass overlay on cards. **Vanito wants it improved:**

**Current implementation in `hub-vanito.html`:**
- `<canvas id="rain-canvas">` right before `<body>` end
- CSS for the canvas and water sheen overlay in `<style>` under `/* ═══ RAIN EFFECT ═══ */`
- JavaScript rain engine under `/* ═══ RAIN EFFECT ═══ */` in the script section
- Rain starts on `DOMContentLoaded` via `startRain()`

**Vanito's feedback:**
- Still not looking right — needs to look more **watery**
- Rain should **drip down onto the content** like it's actually getting wet
- Water droplets forming and dripping off the edges of cards
- Needs to feel like you're looking through a rain-streaked window

**Things to try:**
- Make rain streaks thicker/whiter
- Add actual water droplets that form on top edges of cards and drip down
- Add a subtle fog/mist layer behind the rain
- Water ripple animation when drops "hit" card surfaces
- Maybe use a shader-like gradient animation for water on glass look

## Task 2: Lighting Effects Check

Vanito has lighting effects CSS but they need a full audit:
- Pulse glow on banner (currently targets `#tab-characters > video:first-child` and `img:first-child`)
- Border glow on KAGE card (`.card-kage`) and HIKARI card (`.card-hikari`)
- Text pulse on KAGEKŌ title
- Light sweep across album card
- Floating ember particles (`.card-together::before`)
- Fade-slide-up on entering the tab

**Fix checklist:**
- Check if all animations fire when switching to Artists tab
- Banner uses `<video>` now, not `<img>` — ensure animations target `video`
- Album section uses `<video>` too
- Ensure animations don't conflict with rain canvas

## Task 3: Full Site Audit

- Check everything on the hub:
  - Audio players (KAGE, HIKARI, Together) — do all play?
  - Animated banner video loop
  - Animated album cover video
  - Epilogue video in story section
  - Settings modal saves default tab
  - Bottom nav switches correctly
  - All tabs load (Gaming, Profile, Travel, Music, Chat, Artists)
- Fix any console errors
- Test on mobile (Telegram in-app browser)

## Task 4: Theme Redesign

Vanito wants the hub theme redesigned to match the KAGEKŌ album cover aesthetic:
- Deep crimson red (primary)
- Bone white text
- Charcoal black backgrounds
- Dark red/black header (already done — no more orange)
- No "Wyvern" subtitle in header
- Dark premium feel

## Files
- `hub-vanito.html` — everything's in this single file
- Reference: `music/vanito/kage-hikari-album-cover.png` or the animated `kage-hikari-album-loop.mp4`
