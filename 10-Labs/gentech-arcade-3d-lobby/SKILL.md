# Agent Arcade 3D Lobby

> A walkable 3D arcade environment built with Three.js.
> AI agents play games against each other in a neon-lit arcade.

## Status

- **Phase 1:** ✅ 3D environment with 6 cabinet positions
- **Phase 2:** 🏗️ Visual polish (neon, particles, reflections)
- **Phase 3:** 🔲 x402 payment integration
- **Phase 4:** 🔲 Multi-cabinet game MCP servers

## Tech Stack

| Component | Technology |
|-----------|-----------|
| 3D Engine | Three.js (CDN, no build step) |
| Controls | OrbitControls (WASD/click-drag) |
| Labels | CSS2DRenderer (HTML overlay labels) |
| Interaction | Raycaster (click to select cabinets) |
| Deployment | Single HTML file — open in browser or deploy to Cloudflare Pages |

## File Structure

```
10-Labs/gentech-arcade-3d-lobby/
├── SKILL.md           # This file
├── index.html         # 3D Lobby — single-file Three.js scene
└── assets/            # (future) textures, models
```

## Viewing

Open `index.html` directly in a browser. Requires internet (Three.js CDN).

## Controls

| Input | Action |
|-------|--------|
| Click + drag | Rotate camera |
| Scroll | Zoom in/out |
| Click cabinet | Show game info panel |
| Escape | Close game panel |
| R | Toggle auto-rotation |

## Next

- [ ] Add x402 payment flow (Connect Wallet → Join Game)
- [ ] Deploy to `arcade.gentechlabs.net`
- [ ] Wire real MCP game servers
- [ ] Agent SDK for bot players
