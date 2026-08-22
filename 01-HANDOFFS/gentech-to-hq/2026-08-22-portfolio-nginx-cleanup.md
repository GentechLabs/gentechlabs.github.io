# Handoff to HQ (Jintek) — portfolio.gentechlabs.net nginx cleanup (Aug 22, 2026)

**From:** Treasury → **To:** HQ (Jintek)

## Task
The `portfolio.gentechlabs.net` subdomain nginx config is **incomplete / dead weight**.
Please finish or remove it.

## What I found
`/etc/nginx/sites-enabled/portfolio`:
```nginx
server {
    listen 8089;
    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
- **No `server_name`** — so it never matches `portfolio.gentechlabs.net`.
- **No SSL** (no 443 block, no cert).
- **Proxies to 8090**, which is actually the **x402 gateway** (`uvicorn server:app --port 8090`), NOT the portfolio.

## The correct setup (already live)
The portfolio works fine at **`gentechlabs.net/portfolio/`** — served by the main site's
nginx alias to `/var/www/portfolio/` (index.html, personal/career page). That's the correct
URL per the site routing rule (main=story, portfolio=person, demo=proof).

## Options
1. **Remove** the stale `portfolio` site config (recommended — the subdomain isn't used; the
   portfolio lives at `gentechlabs.net/portfolio/`).
2. **Or** properly wire `portfolio.gentechlabs.net` → `/var/www/portfolio/` with SSL if
   Jordan wants the subdomain live.

## Context
- Site routing rule (Aug 16): main=story, portfolio=person, demo=proof, internal=never public.
- GitHub Pages retired — live site is VPS + Cloudflare (gentechlabs.net).
- Three pages: `gentechlabs.net` (main), `gentechlabs.net/portfolio/` (person), `demo.gentechlabs.net` (proof).
