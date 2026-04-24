# RSSHub Setup

## Status: ✅ OPERATIONAL

**Date:** 2026-04-24
**Location:** `/opt/rsshub/`
**Public URL:** `http://[VPS-IP-REDACTED]:1200`
**Local URL:** `http://localhost:1200`

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RSSHub    │────▶│    Redis    │     │ Browserless │
│  (:1200)    │     │  (:6379)    │     │   Chrome    │
│  (chromium  │     │   (cache)   │     │  (:3000)    │
│   bundled)  │     └─────────────┘     └─────────────┘
└─────────────┘
```

---

## Services

| Service | Image | Purpose |
|---------|-------|---------|
| rsshub | `diygod/rsshub:chromium-bundled` | Main RSS feed generator |
| redis | `redis:alpine` | Caching layer |
| browserless | `browserless/chrome` | Headless Chrome for JS-rendered sites |

---

## Commands

```bash
# Start
cd /opt/rsshub && docker compose up -d

# Stop
cd /opt/rsshub && docker compose down

# View logs
cd /opt/rsshub && docker compose logs -f rsshub

# Update to latest
cd /opt/rsshub && docker compose pull && docker compose up -d
```

---

## Working Routes (Tested)

| Route | URL | Status |
|-------|-----|--------|
| RSSHub Routes Feed | `/rsshub/routes` | ✅ |
| GitHub Repo Releases | `/github/release/:user/:repo` | ⚠️ needs auth for high rate limits |
| YouTube Channel | `/youtube/channel/:channelId` | ⚠️ needs yt-dlp or API key |
| Twitter/X User | `/twitter/user/:id` | ❌ requires extra auth setup |
| Reddit | `/reddit/:sort` | ⚠️ requires login since 2024 |

---

## Next Steps

1. **GitHub** — Authenticate `gh` CLI or set `GITHUB_TOKEN` env var in `docker-compose.yml`
2. **YouTube** — Install `yt-dlp` or configure YouTube API key
3. **Reddit** — Login to `rdt-cli` or configure Reddit app credentials
4. **Exa/Web Search** — Set up `mcporter` + Exa MCP integration
5. **Firewall** — Consider restricting `:1200` to VPN/internal only

---

## Notes

- Docker `restart: always` handles boot-time auto-start
- Redis persists data to named volume `rsshub_redis-data`
- Browserless ulimits set to prevent core dumps
- Cache TTL: 300s (5 minutes) default
