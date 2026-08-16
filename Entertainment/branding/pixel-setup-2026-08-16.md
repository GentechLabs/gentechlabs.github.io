# Pixel — Entertainment Worker (LIVE 2026-08-16)

## Identity
- **Name**: Pixel
- **Bot**: @Enterthebrainsbot (token 8918283925:... stored `/root/.bot-tokens/pixel.token` + `pixel/.env`)
- **Profile**: `/root/.hermes/profiles/pixel` (cloned light from gentech)
- **Role**: Entertainment specialist — arcade, films (Seedance/vanito), social/X, on-ramp energy
- **Group**: Gentech Entertainment (`-1003893562036`) — bot is ADMINISTRATOR there
- **Gateway**: systemd `hermes-gateway-pixel.service` — active, NRestarts=0
- **Avatar**: `Entertainment/branding/pixel-avatar.png` (+512)
- **SOUL**: `Entertainment/branding/pixel-SOUL.md` (applied to `pixel/SOUL.md`)
- **Description set**: "Pixel — GenTech Entertainment. Arcade, films, social."

## Cron jobs migrated from gentech → pixel (5)
1. [Jordan] GenTech Shop — Weekly Sales Sweep (80fd54684d86)
2. [Jordan] GenTech Shop — Game Release Intelligence (41f8e6d0e24b)
3. [Jordan] POE2 Build Health — Gaming Hub Sync (02461aa0a77b)
4. [Vanito] GenTech Shop — Weekly Sales Sweep (1c25463fc281)
5. Social Media Engine — Gentech + Forge Drafts (e7b632043e30)

All 5 **paused in gentech profile** (80fd, 41f8, 02461, 1c25, e7b6) to prevent double-fire.
Pixel gateway runs these via `pixel/cron/jobs.json`.

## Notes
- Setup script: `/root/.hermes/profiles/gentech/scripts/setup-pixel-worker.sh` (re-runnable)
- Profile picture must be set by Jordan via BotFather (bots can't set own photo via API)
- Follows V4 full-mesh: writes `01-HANDOFFS/entertainment-to-gentech/` + `entertainment-completions.md`
