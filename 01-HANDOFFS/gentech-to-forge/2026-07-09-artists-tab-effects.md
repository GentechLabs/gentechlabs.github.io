# 🎭 Vanito's Hub — Full Theme Overhaul + Effects

## Task 1: Full Site Audit

- Check **everything** on the hub (`hub-vanito.html`):
  - **Lighting effects** on Artists tab (pulsing glow, border animations, light sweep, ember particles)
  - **Audio players** — do all 3 work? (KAGE, HIKARI, Together)
  - **Animations** — smooth on mobile, Telegram in-app browser, and desktop?
  - **Banner video** — does the animated loop play correctly?
  - **Album video** — does the animated KAGEKŌ cover loop work?
  - **Dynamic header** — does it toggle correctly between tabs?
  - **Settings modal** — does it save default tab?
  - **All tabs** — Gaming, Profile, Travel, Music, Chat, Artists — do they all load and function?
- Fix anything broken
- Ensure no console errors on mobile

## Task 2: Rain Effect (All Pages, Not Just Artists)

Vanito wants the **entire hub** to have a dripping water/rain effect. Think:

- Cinematic rain streaks falling down the whole page (not just Artists tab)
- Water droplets running down the screen like glass
- Subtle water ripple when drops hit cards or surfaces
- Theme should look **wet** — like you're looking through a rain-streaked window

**Make sure:**
- Rain works on ALL tabs (Gaming, Profile, Travel, Music, Chat, Artists)
- Doesn't block any buttons or audio players (pointer-events: none on rain layer)
- Lightweight enough for mobile
- Stops/restarts cleanly when switching tabs
- Dark atmospheric vibe matching the crimson/black/bone-white theme

## Task 3: Theme Redesign — Match the Picture

Vanito wants the **entire hub theme** redesigned to match the KAGEKŌ album cover aesthetic.

The picture (reference: `music/vanito/kage-hikari-album-cover.png` or the animated `kage-hikari-album-loop.mp4`) features:
- **Deep crimson red** (primary)
- **Bone white** (text, highlights)
- **Charcoal black** (backgrounds, panels)
- **Ember gold/amber** (accents, HIKARI side)
- **Dark shadow gradients**
- **Gritty, apocalyptic, cinematic feel**

### Requirements for the theme change:

**Header:**
- Dark gradient background (charcoal → deep crimson)
- White/bone-white text
- Maybe a subtle red glow behind the title
- The header subtitle "Wyvern · Warrior of GenTech" should pop

**Background:**
- Dark charcoal/almost black (`#0d0d0d` or darker)
- Maybe a subtle dark gradient instead of solid

**Cards:**
- Dark panels with crimson/reddish borders
- Red glow on hover
- Bone white text
- Semi-transparent background (`rgba(20,5,5,0.8)` or similar)

**Text colors:**
- Primary: white/bone-white
- Secondary: crimson red accents
- Subtitle/dim text: gray with reddish tint

**Bottom nav:**
- Dark with red active indicator
- Active tab should glow red
- Non-active: dim white/gray

**Settings modal:**
- Dark red/black theme
- White text

**Overall vibe:**
- Dark, atmospheric, wet, cinematic
- Looks like it belongs to the KAGEKŌ world
- Premium feel, not just a generic dark theme

## Files involved:
- `hub-vanito.html` — the main file (CSS vars, all tabs, header, nav, modals)
- `music/vanito/` — reference images and video for the theme
- No external CSS files — everything is inline in `<style>`

## Design reference:
The KAGEKŌ album cover has a dark, gritty, apocalyptic feel with:
- Red sun glow
- Dark stormy sky
- Japanese street aesthetic
- Blood/crimson accents
- Charcoal and ash tones
- Cinematic lighting

The rain effect should feel like standing in a dark alley during a storm, looking at neon reflections on wet pavement.
