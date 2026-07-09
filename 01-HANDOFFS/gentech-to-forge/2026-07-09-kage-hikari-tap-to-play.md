# 🎵 KAGE & HIKARI — Tap-to-Play Feature (For Forge)

## The Feature

Vanito wants the **character images** on his hub's Artists tab to play songs when tapped.

**Current state as of 2026-07-09:**
- The hub at `hub-vanito.html` has KAGE × HIKARI characters in the Artists tab
- Native HTML5 `<audio>` players are embedded under each bio card (work fine)
- The character images now have `onclick` handlers that trigger `document.getElementById('player-id').play()` — but this **does not work in Telegram's in-app browser** on mobile

**The problem:**
Telegram's in-browser blocks `audio.play()` calls even from direct user gestures. The native `<audio controls>` player works fine (user taps the ▶️ button manually), but programmatic `.play()` on image click gets silently blocked.

**What Vanito wants:**
Tap the character picture → music plays. Simple, reliable, no extra UI.

## Files involved:

- `hub-vanito.html` — main page, look for `#tab-characters`
- `music/vanito/` — MP3 files (fight-forever-never-quit.mp3, mirai-e-hashire.mp3, in-the-darkness-we-rise.mp3)
- `hub-vanito-data.json` — song metadata

## Current approach to try fixing:

Each character card has:
```html
<img src="..." onclick="document.getElementById('kage-player').play()">
<audio id="kage-player" controls preload="none">
  <source src="music/vanito/fight-forever-never-quit.mp3" type="audio/mpeg">
</audio>
```

The audio elements have `preload="none"` — try changing to `preload="auto"` or `preload="metadata"`. Mobile browsers sometimes block play on unloaded audio.

## Alternative approaches to try:

1. **Audio context API** — Use `AudioContext` with `resume()` which works better on mobile
2. **Lazy-load the audio src** — Set `audio.src` in the click handler, then call `play()` 
3. **Service Worker** — Pre-cache the audio file via service worker
4. **WebView-compatible approach** — Use a hidden iframe or WebView-friendly player
5. **Check if iOS vs Android** — The behavior differs

## Deliverable:
- Tap KAGE image → "Fight Forever Never Quit" plays
- Tap HIKARI image → "Mirai e Hashire" plays
- Should work in Telegram's in-app browser on both iOS and Android
- Bonus: a subtle visual cue that tapping works (glow/ripple on the image)
