# Vanito's Travel Companion — Meta Ray-Ban AR Experience

**Owner:** Vanito
**Engine:** Forge (GenTech Labs)
**Platform:** Meta Ray-Ban Display (600×600px)
**Theme:** Japan travel
**Status:** 🟢 Active development

---

## Identity

This is **Vanito's project**. Not GenTech's. He owns the vision, the content, the creative direction. We build the engine, he drives what goes in it.

## The Product

An AR travel companion for Meta Ray-Ban glasses. Walk into a neighborhood in Tokyo and the HUD shows you:
- Ramen spots nearby
- History of the street
- Currency conversion (¥ → $)
- Key phrases in Japanese
- Saved memories with location stamps

## Why It's Different From GenTech

| Vanito's Travel Companion | GenTech Labs |
|--------------------------|--------------|
| Consumer AR experience | B2B agent infrastructure |
| Free / ad-supported | x402 micropayments |
| Vanito's creative vision | Jordan's business |
| Japan-first, then global | Agent economy first |
| Open source engine | Open source tools → paid APIs |

## Architecture

```
vanito-travel-companion/
├── index.html          # Main HUD (600×600)
├── styles.css          # Dark theme, animations
├── app.js              # Engine (shared with GenTech)
├── cities/
│   ├── tokyo.json      # Vanito's content
│   ├── osaka.json
│   └── kyoto.json
├── modes/
│   ├── explorer.js     # POI discovery
│   ├── food.js         # Restaurant finder
│   ├── phrases.js      # Language helper
│   └── memories.js     # Photo journal
└── server.js           # Dev server
```

## Build Plan

1. **Engine** — Port Manila Explorer engine to Japan data (Forge)
2. **Tokyo data** — Vanito picks the spots (Vanito)
3. **Deploy** — GitHub Pages so Vanito can test on glasses (Forge)
4. **Iterate** — Vanito plays, tells us what to change (Vanito + Forge)

## Deployment

URL: `https://ProtoJay4789.github.io/Games/Vanito-Travel/`

---

*Vanito's world. We just build the tools.*
