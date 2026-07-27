## For Forge — 2026-07-27

### Priority items

**HIGH:**
- **#84** Agent Warfare — Agent Archetypes/Classes (Sniper, Scout, Heavy, Medic, Engineer) — Subclass the 8,193 lines of AI behavior into 5 archetypes with unique speed, health, weapons, AI decision trees. Gentech designs, Forge builds AI behavior, Gentech deploys.
- **#85** Agent Warfare — Procedural Map Generation via text-to-cad — Use build123d → STEP → GLB pipeline to generate playable FPS maps. Gentech designs, Forge builds heavy GPU work (Modly), Gentech integrates into Three.js.
- **#86** ClawWork Integration — GenTech Employee Squad — Spin up ClawWork agents as autonomous freelancers. Needs nanobot config with API key. Cloned at /root/ClawWork/, deps installed, CLI working.
- **#87** Paymenter x402 Gateway — Submit to Marketplace + Discord — Repo live at github.com/ProtoJay4789/paymenter-x402. Marketplace listing and Discord post drafted in vault 10-Labs/paymenter-x402/.
- **#88** Paymenter x402 — Pterodactyl Community Outreach — Post in Pterodactyl community about first crypto gateway for game server hosts.

**MEDIUM:**
- **#89** Paymenter x402 — WHMCS/Blesta Extension Port — Port the Paymenter extension pattern to larger hosting billing platforms.
- **#76** Syra Marketplace — Register GenTech x402 Services
- **#77** Open Generative AI — Self-Host AI Media Studio (24.7k ⭐, MIT)
- **#82** Algorand Global x402 Challenge — $100K + 500K ALGO prize pool
- **#83** CockroachDB × AWS — Build with Agentic Memory ($8.75K)

**LOW:**
- **#90** Hippocratic AI Residency — Evaluate Fit

### Updates since last handoff
- Agent Warfare rebranded + deployed at arcade.gentechlabs.net/cabinet/agent-warfare/
- Gamepad + touch controls coded in (415-line touch.js)
- text-to-cad pipeline proven — 5 arcade lobby models generated in ~2s each
- CAD Viewer live at cad.gentechlabs.net
- ClawWork cloned + installed (needs API key config to run)
- Paymenter x402 Gateway Extension built + pushed to GitHub
- Build queue v35 — 16 total, 15 active, 1 cancelled

### Full queue
See `scripts/build_queue.json` for details.
