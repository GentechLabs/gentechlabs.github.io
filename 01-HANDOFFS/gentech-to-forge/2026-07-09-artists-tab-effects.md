# 🎭 Vanito's Hub — Artists Tab Enhancement

## Task 1: Lighting Effects Audit

Vanito already has lighting effects on the Artists tab (`hub-vanito.html` > `#tab-characters`). He wants them reviewed and optimized:

- **Pulsing glow** on the banner and album section (red/crimson glow breathing effect)
- **Pulse animations** on KAGE and HIKARI card borders
- **Light sweep** across the album card
- **Text pulse** on the KAGEKŌ title
- **Fade-slide-up** on tab entry
- **Floating ember particles** in album section (`::before` ember rise animation)

**Checklist for audit:**
- Animations smooth on mobile (Telegram in-app browser)?
- Performance issues on lower-end devices?
- Any unnecessary repaints/layouts?
- CSS animation properties optimized?

## Task 2: Rain Effect

Vanito wants an **animated raining effect** on the Artists tab — like the layout is getting wet. Think cinematic rain, not just simple drops.

**Desired effect:**
- Semi-transparent rain streaks falling across the entire tab
- Subtle water ripple/streak effect when rain hits the "surface" of cards
- Rain should feel dark and atmospheric, matching the crimson/black theme
- Raindrops hitting the banner image could have tiny splash animations

**Constraints:**
- Must work on mobile (Telegram in-app browser)
- Must not block tap/click on audio players
- Should auto-play when switching to Artists tab
- Performance: keep it lightweight (canvas or CSS, not heavy JS)

**Files involved:**
- `hub-vanito.html` — all characters tab content in `#tab-characters`
- CSS in the `<style>` section under `CHARACTERS THEME` and `CHARACTERS LIGHTING EFFECTS`

**Design reference:** The KAGEKŌ album cover has a dark, gritty, apocalyptic feel with ash/embers. Rain would add to that atmosphere.
