# Gentech-Branded Dashboard

**Status:** 🟡 Queued — Dmob development pending
**Priority:** Medium

## Vision
Replace Hermes Workspace with custom-branded dashboard built by Dmob.

## Design Spec
- **Theme:** Dark charcoal base
- **Accents:** Red + cyan neon
- **Logo:** GT hexagonal shield (Afro-tech aesthetic)
- **Layout:** Agent panels, cron status, DeFi ticker

## Features
- Live agent status (YoYo, Dmob, Desmond, Gentech)
- Cron job monitoring and logs
- DeFi ticker (AVAX, BTC, key tokens)
- Session viewer with group attribution
- Mobile-responsive (PWA)

## Technical
- **Current:** Hermes Workspace on port 3001 (systemd)
- **Target:** Custom React app, same port or 3002
- **Backend:** Hermes API (/api/sessions, /api/config, /api/cron/jobs)

## Next Steps
- [ ] Dmob starts development
- [ ] Finalize design mockups with Desmond's branding assets
- [ ] API integration with Hermes backend
- [ ] Deploy alongside existing workspace

## Tags
#project:dashboard #agent:dmob #agent:desmond #status:queued
