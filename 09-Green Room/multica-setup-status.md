# Multica — Setup Status (Aug 17, 2026) — UPDATED

## ✅ DONE — Fully operational
- **Workspace:** "GenTech Labs" (id `a3f54635-73ae-4950-9950-afce9822c276`, slug `gentech`)
- **Auth:** Jordan (jordan@gentechlabs.net) owner. Dev code `402402`.
- **Runtime:** "Hermes (gentech-vps)" — **ONLINE** (id `50a9175b-91a3-44ec-aa17-28832dfa3f0b`)
  - Auto-detected CLIs: `opencode`, `hermes`
  - Hermes Agent v0.20.1
- **Agent:** "Hermes" created on board (id `33bfaf07-f10d-42c1-8a31-d3ef6e2771b9`), status **working**, max 6 concurrent tasks
- **Daemon:** running (pid via `multica daemon status`), device `gentech-vps`
- **PAT:** `mul_2b8179d5...` (saved in multica config, /root/.hermes/profiles/gentech/home/.multica/config.json)

## How to access
- **Web UI:** http://localhost:3001 (frontend)
- **Backend:** http://localhost:8081
- **CLI:** `multica` (installed at /usr/local/bin/multica)
- **Daemon status:** `multica daemon status`

## Next steps (revenue stream)
1. **Create ClawWork agents** as teammates on the board (the employee squad, #3)
2. **Create a Squad** — group agents under a leader for stable routing
3. **Assign tasks** — create issues, assign to Hermes/ClawWork agents
4. **Autopilots** — schedule recurring work (cron triggers, webhooks)
5. **Build GenTech Shop plugin** on Paperclip (the other half of #6)

## Notes
- Multica = control plane for the ClawWork employee squad
- Supports Hermes as first-class agent provider
- Squads = stable routing layer (leader delegates to members)
- This is a revenue stream: agents earn on GDPVal tasks ($19K/8hrs demonstrated)
