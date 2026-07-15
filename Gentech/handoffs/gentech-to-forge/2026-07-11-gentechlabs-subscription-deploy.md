# Forge — Deploy Subscription Hub to gentechlabs.net 🚀

## Overview
Deploy the new subscription hub page to `gentechlabs.net`. This turns the site into a commercial storefront with Q402/x402 payment tiers for Jordan and Vanito.

## What's Ready

| File | Purpose |
|------|---------|
| `gentech-ops/gentechlabs-subscription-hub.html` | Full subscription hub page (Jordan + Vanito tiers, live products) |

## Tiers
| Tier | Price | Audience |
|------|-------|----------|
| Basic | $3/mo | LP alerts, Atlas packs, journal |
| Pro | $10/mo | API access, signals, registrations |
| Max | $25/mo | Build requests, early access, direct line |
| Vanito Music | $3/mo | Tracks + early releases |
| Vanito Vault | $10/mo | Music + anime + exclusives |

## Deploy Options (pick whichever works)

### Option A — New subdomain route (recommended)
Add to `wrangler.toml`:
```
[[routes]]
pattern = "https://subscribe.gentechlabs.net/*"
zone_name = "gentechlabs.net"
```
Update `src/worker.ts` to serve the HTML for that hostname.

### Option B — Replace main landing page
Replace the existing `gentechlabs.net` HTML with the subscription hub. Keeps the API catalog as a separate page at `/api/`.

### Option C — Add as `/subscribe` path
Add route to worker for `gentechlabs.net/subscribe`, serve inline HTML.

## What Forge Does
1. Read the HTML from `gentech-ops/gentechlabs-subscription-hub.html`
2. Decide the route (A, B, or C above)
3. Update `wrangler.toml` + `src/worker.ts`
4. Run `npx wrangler deploy`
5. Verify: `curl -s https://subscribe.gentechlabs.net/` or chosen route

## Credentials
- **Cloudflare Account ID**: `a618b777aff85c5360bd847629385b4d`
- **CF_API_TOKEN**: (Forge has this from prior setup)
- **Worker name**: `gentechlabs-api`
- **Vault source**: `src/worker.ts`, `wrangler.toml`

## Post-Deploy Verification
- [ ] Page loads at chosen URL
- [ ] All subscription tiers render correctly
- [ ] Existing API routes still work (`api.gentechlabs.net`, `/api/*`, `/v1/*`)
- [ ] Mobile responsive
- [ ] Q402 payment links resolve

## Notes
- The subscription page uses Q402 payment links (placeholder URLs). Update them with real Q402 recurring payment links when ready.
- x402 gateway stays as-is — subscriptions add a recurring layer on top.
- Vanito's vault tier is optional until he gives the green light.
