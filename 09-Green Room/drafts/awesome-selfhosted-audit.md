# Awesome-Selfhosted Audit — GenTech Stack Gaps

**Queue item:** #26 (labs)
**Date:** 2026-08-06
**Status:** ✅ SHIPPED (Nightly Build Session)
**Scope:** Scan awesome-selfhosted (311K ⭐) for self-hosted tools we're missing that could replace paid services or close real gaps. Low priority — we already self-host most of our stack.

---

## Current GenTech self-hosted stack (verified Aug 6)

| Layer | Tool | Notes |
|-------|------|-------|
| Reverse proxy | **nginx** | systemd, serves gentechlabs.net + api.gentechlabs.net |
| Container runtime | **docker** | DataHub, Hummingbot, Multica, Rota, Trek |
| Data lineage | **DataHub** | 8 containers (GMS, frontend, MySQL, ES, Neo4j, broker, zookeeper, schema-registry) |
| Trading | **Hummingbot** | api + postgres + broker + tailscale |
| Agent squad | **Multica** | backend + frontend + postgres |
| Dashboards | **Rota** | core + timescaledb |
| x402 gateway | **custom FastAPI** | 8 services on ports 8080-8096 |
| APIs | **custom FastAPI** | crypto-price, gas-price, token-security, deal-tracker, defi-dashboard, code-audit, gentech-intel |

---

## Gaps worth closing (ranked by value)

### 🟢 HIGH VALUE — recommend adding

1. **Uptime Kuma** (self-hosted uptime monitoring)
   - **Why:** We have 8+ live services + 8 x402 backends but NO uptime monitoring. The infra playbook (Issue #4, #5) shows services silently breaking. Uptime Kuma gives status pages + alerts for free.
   - **Replaces:** Statuspage.io, Better Uptime (paid)
   - **Effort:** 1 docker container + nginx alias. ~15 min.
   - **License:** MIT

2. **Beszel** (lightweight server monitoring, ~2K ⭐)
   - **Why:** We run a VPS with 20+ containers and no resource monitoring. Beszel is a single binary, ~1MB, gives CPU/RAM/disk/network graphs + alerts.
   - **Replaces:** Grafana + Prometheus stack (heavy for our scale), Netdata (heavier)
   - **Effort:** 1 binary + 1 agent. ~10 min.
   - **License:** MIT

3. **Listmonk** (self-hosted newsletter/mailing list, 22.6K ⭐)
   - **Why:** We have a website + blog ambitions (clarity-act-announcement-blog.md, ghost drafts). Listmonk is the standard self-hosted newsletter tool — replaces Mailchimp/Buttondown.
   - **Replaces:** Mailchimp, Buttondown (paid)
   - **Effort:** 1 docker container + SMTP config. ~20 min.
   - **License:** AGPL-3.0

### 🟡 MEDIUM VALUE — nice to have

4. **PostHog** (self-hosted product analytics, 37.5K ⭐)
   - **Why:** We have 10K+ website visitors/week (per infra playbook) but no analytics. PostHog gives product analytics + session recording + feature flags, self-hosted.
   - **Replaces:** Mixpanel, Amplitude, Hotjar (all paid)
   - **Effort:** 1 docker container. ~20 min.
   - **License:** MIT

5. **Forgejo** (self-hosted git forge, Gitea fork)
   - **Why:** We push to GitHub (ProtoJay4789) but a local mirror would give us a private backup + self-hosted CI (Woodpecker). The Colosseum GitHub-account blocker (from session handoff) makes a local forge a useful fallback.
   - **Replaces:** GitHub (for private repos / backup)
   - **Effort:** 1 docker container. ~15 min.
   - **License:** MIT

6. **Karakeep** (self-hosted bookmark/read-it-later, modern)
   - **Why:** We clip lots of research (specs, references). Karakeep gives full-text search + tagging + browser extension.
   - **Replaces:** Pocket, Raindrop (paid)
   - **Effort:** 1 docker container. ~15 min.
   - **License:** AGPL-3.0

### 🔴 LOW VALUE — skip for now

- **Jellyfin / Immich / Nextcloud / Vaultwarden** — media/photos/file/password management, not relevant to our agent-infra stack.
- **Home Assistant / Pi-hole** — home automation / ad-block, not relevant to a VPS.
- **Grafana + Prometheus** — overkill for our scale; Beszel covers it.
- **n8n / Huginn** — workflow automation; we already have Hermes cron + custom scripts.
- **Supabase / Appsmith / ToolJet** — low-code; we build custom FastAPI + React.
- **Ghost / Discourse** — blog/forum; we have gentechlabs.net + drafts, Listmonk covers newsletter.

---

## Recommendation

**Ship Uptime Kuma + Beszel this week** — they close the two real gaps (no uptime monitoring, no resource monitoring) for ~25 min total and zero recurring cost. Listmonk + PostHog are worth adding when we launch the blog/newsletter push.

**Not a paid-service replacement priority:** we already self-host the core (nginx, docker, DataHub, Hummingbot, custom APIs). The audit confirms we're lean — the gaps are monitoring + analytics, not core infra.

---

*Verified: current stack enumerated from systemd + docker ps (Aug 6). awesome-selfhosted data from github.com/awesome-selfhosted (311K ⭐, Aug 4 2026).*
