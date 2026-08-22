# API Docs Page — Live (Aug 18, 2026)

## What was built
The missing `/docs` page for api.gentechlabs.net — the conversion surface for the
11 paid x402 services. It was 404 (FastAPI has docs_url=None + nginx proxied /docs
to the gateway which had no route).

- **Page:** `/var/www/gentechlabs/api-docs.html` (~16KB, dark theme)
- **URL:** `https://api.gentechlabs.net/docs` (now 200)
- **Served via:** nginx `location /docs { alias .../api-docs.html; }` on both
  HTTP + HTTPS server blocks for api.gentechlabs.net

## Contents
- ✅ How x402 payment works (402 → sign → settle → fulfill)
- ✅ Full service catalog table (11 services, prices, endpoints)
- ✅ Per-service cards: endpoint + real copy-paste curl example
- ✅ Dev/agent section (@x402/client, GoPlausible for humans)
- ✅ Verified settlement proof (0.05 USDC on Base)
- ✅ Links to manifest v9.3.0

## Verified
- `https://api.gentechlabs.net/docs` → **200**, HTML balanced, 11 service cards
- Gateway health: `{"status":"ok","gateway":"x402-v2","services":11}`
- Paid endpoint still returns 402 correctly (proxying unaffected)

## Context
This was the #1 API gap Jordan flagged: no docs = no customers. Now a developer
landing on the gateway can learn how to call all 11 services. This is the
conversion surface — the highest-leverage next step after the settlement proof.
