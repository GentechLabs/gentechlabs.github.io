# GenTech x402 Compliance Standards

> **Purpose:** Every time we discover a marketplace requirement, fix a deployment issue, or learn something new about x402 compliance, we document it here. After every mistake, we fix it and write down how so nobody makes the same error twice.

---

## 1. Bazaar Manifest Serving Standard

### The Requirement
The x402 Bazaar spec requires the service manifest at `/.well-known/x402-bazaar`. This is how marketplaces (Agentic Market, Coinbase Bazaar, etc.) discover your services.

### The Mistake (2026-07-24)
- Manifest file was named `x402.json` instead of `x402-bazaar`
- No `location /.well-known/` block existed for `api.gentechlabs.net` — requests went to a dead backend port
- Result: Agentic Market validator returned "No x402 Setup Detected"

### The Fix
1. Manifest file must be at `/.well-known/x402-bazaar` (not `.json`, not any other name)
2. Every server block in nginx that serves API traffic must have:
   ```nginx
   location /.well-known/ {
       root /var/www/gentechlabs;
       default_type application/json;
       add_header Access-Control-Allow-Origin *;
   }
   ```
3. This `location` block must come BEFORE the catch-all `location /` block
4. Static files are fine — no live backend needed for discovery

### Verification
```bash
curl -s -o /dev/null -w "HTTP %{http_code}" https://gentechlabs.net/.well-known/x402-bazaar
# Expected: HTTP 200
```

### Rationale
Marketplaces crawl the Bazaar manifest to auto-discover services. If the endpoint returns anything other than 200 (403, 404, 502, timeout), the marketplace treats the service as unavailable and won't list it.

---

## 2. x402 Middleware Ordering

### The Requirement
Per the x402 v2 spec, paid API endpoints MUST return HTTP 402 (Payment Required) to unauthenticated requests — not 401, 403, or any other status. The `PAYMENT-REQUIRED` response header must carry the base64-encoded payment payload.

### The Mistake (2026-07-24)
Validator detected that our endpoints return 403 instead of 402. This means auth middleware runs before x402 middleware in the request pipeline.

### The Fix
Middleware ordering must be:
1. CORS
2. x402 payment interceptor (catches unauthenticated requests → returns 402)
3. Auth middleware (verifies payment token)
4. Business logic

In FastAPI/Python:
```python
# WRONG: auth before payment
@app.post("/api/endpoint")
async def endpoint(x_api_key: str = Header(...), x_402_token: str = Header(...)):
    verify_auth(x_api_key)  # Returns 403 if missing
    verify_payment(x_402_token)  # Never reached

# RIGHT: payment before auth
@app.post("/api/endpoint")
async def endpoint(x_402_token: str = Header(...), x_api_key: str = Header(...)):
    verify_payment(x_402_token)  # Returns 402 if missing
    verify_auth(x_api_key)  # Only reached if paid
```

### The PAYMENT-REQUIRED Header
Per x402 v2 spec, the payment payload must be delivered via:
- **Required:** `PAYMENT-REQUIRED` response header (base64-encoded)
- **Optional:** Response body fallback

Our implementation was body-only. This causes Bazaar discovery to reject the endpoint.

### Verification
```bash
curl -s -D - https://api.gentechlabs.net/v1/security/score/0x... | head -20
# Expected: HTTP 402 with PAYMENT-REQUIRED header
# NOT:       HTTP 403
```

---

## 3. Cloudflare / Reverse Proxy Compatibility

### The Requirement
x402 and Bazaar endpoints must be accessible to programmatic clients (other agents, marketplace crawlers, CI/CD). Cloudflare WAF rules that block non-browser traffic will prevent marketplace discovery.

### The Mistake (2026-07-24)
Cloudflare returned `error code: 1003` for requests to `api.gentechlabs.net/.well-known/x402-bazaar`. The WAF was blocking programmatic access while allowing browser traffic.

### Diagnostics
```
# Cloudflare error 1003 = Access Denied / Direct IP Access Not Allowed
# Check: Cloudflare Dashboard → Security → WAF → Custom Rules
# The rule blocking non-browser User-Agent or missing Cloudflare headers
```

### The Fix
1. Add a WAF bypass rule for `/.well-known/x402-bazaar` (allow all methods, all user-agents)
2. Or add a Cloudflare Access service token for API clients
3. Or route x402 traffic through a subdomain with relaxed WAF rules

### Verification
```bash
# Must work from any network, any user-agent
curl -s -o /dev/null -w "HTTP %{http_code}" -A "Grok/1.0" https://api.gentechlabs.net/.well-known/x402-bazaar
# Expected: HTTP 200
```

---

## 4. Pre-Deployment Checklist

Before submitting any x402 service to a marketplace:

- [ ] `/.well-known/x402-bazaar` returns HTTP 200 from external (not just localhost)
- [ ] Response is valid JSON with `name`, `description`, `url`, `payment`, `services`
- [ ] CORS headers (`Access-Control-Allow-Origin: *`) are present
- [ ] Paid endpoints return HTTP 402 (not 403) to unauthenticated requests
- [ ] `PAYMENT-REQUIRED` header is present in 402 responses
- [ ] Validated with agentic.market/validate
- [ ] Validated from a non-browser user-agent (simulates agent traffic)
- [ ] All subdomains serving API traffic have `/.well-known/` configured

---

## 5. Marketplace-Specific Requirements

| Marketplace | Requirements | Check |
|-------------|-------------|-------|
| OKX AI | 24/7 A2A node, Node 22.14.0+, review process | ✅ Documented |
| Agentic Market | x402 manifest, no review, auto-indexed | ✅ Fixed 2026-07-24 |
| x402 Bazaar | Stateless HTTP manifest, auto-indexed | ✅ No action |
| Swarms | Manual edit, x402 toggle | ⏸️ Pending |
| Atelier | API key, Solana native | ⏸️ Pending |

---

## 5b. Facilitator Reference — by Network (Jordan directive, 2026-08-07)

> **Why this matters:** A facilitator is the payment rail that settles x402 payments. Without one, an x402 service can *advertise* but cannot *receive money*. The registry (AgentScan) makes us findable; the facilitator makes us payable. They go together — pick the right facilitator for the network you're deploying on.

**Rule:** Before deploying an x402 service on any network, confirm a facilitator is available for that network and wire it in. Don't ship a service that can't settle.

| Network | Recommended Facilitator | Notes / Install |
|---------|------------------------|-----------------|
| **Avalanche (C-Chain)** | **PayAI** (`facilitator.payai.network`) | Avalanche-native x402. Network string `avalanche` (mainnet) / `avalanche-fuji` (testnet). SDKs: TypeScript + Python. Free tier $0/mo up to 10K settlements/mo, then $0.001/tx. Install: `x402-express` middleware with `FACILITATOR_URL=https://facilitator.payai.network`, `NETWORK=avalanche`, `ADDRESS=<payTo>`. |
| **Solana** | **PayAI** | Native Solana settlement, no API key. We already integrate via `payai_facilitator.py` (Jun 25) — our Solana leg. Also the facilitator behind our WURK flow. |
| **Base** | **Q402** / **Coinbase CDP** | Q402 = gasless EIP-7702 (USDC+USDT). Coinbase CDP = x402 facilitator. Both documented in gateway README. |
| **X Layer** | **PayAI** | PayAI supports X Layer (16 networks incl. X Layer). Natural fit — our ERC-8004 identities live on XLayer. |
| **Multi-network** | **PayAI `@payai/agentic-payments`** | Dual-protocol SDK (x402 + MPP) — one Express middleware serves both rails. 16 networks. See `11-Mess Hall/payai-mpp-dual-rail.md` (build-queue #47). |

**Key facts (from `payai-mpp-dual-rail.md`, 2026-08-06):**
- PayAI is the **#2 x402 facilitator by volume**, native Solana settlement, no API key needed.
- Free tier: $0/mo, up to 10,000 settlements/mo. Beyond: $0.001/tx (min tx $0.001).
- **16 networks:** Solana, Base, X Layer, Avalanche, Arbitrum, Polygon, Sei, SKALE (+ testnets).
- **No license on PayAI repos** — borrow the mechanism, not the code. TypeScript-only SDK (we're Python-first).

**Install pattern (Avalanche, from PayAI docs):**
```bash
# .env
FACILITATOR_URL=https://facilitator.payai.network
NETWORK=avalanche        # or avalanche-fuji for testnet
ADDRESS=0x...            # wallet that receives payments
```
```js
// Express middleware
import { paymentMiddleware } from "x402-express";
app.use(paymentMiddleware(payTo, { "GET /weather": { price: "$0.001", network: "avalanche" } }, { url: facilitatorUrl }));
```

---

## 6. Incident Log

| Date | Issue | Cause | Fix | Documented |
|------|-------|-------|-----|------------|
| 2026-07-24 | OKX listing rejected | No A2A node running | Installed `@okxweb3/a2a-node`, ran `okx-a2a doctor --fix` | ✅ This file |
| 2026-07-24 | Agentic Market validator failed | Manifest at wrong path, no `.well-known/` in `api.*` nginx config, Cloudflare WAF blocking | Created `x402-bazaar` file, added nginx `location /.well-known/` block | ✅ This file |
| 2026-07-24 | Port 8090 API gateway down for 77k+ restarts | `server.py` missing from agent-kit-q402 repo, systemd misconfigured | Built new x402 gateway at `10-Labs/x402-gateway/server.py`, updated systemd service | ✅ This file |
| 2026-07-24 | PAYMENT-REQUIRED header missing | Old implementation only returned 402 in response body | New gateway returns proper base64-encoded `PAYMENT-REQUIRED` header per v2 spec | ✅ This file |
| 2026-07-24 | Cloudflare WAF blocking api.gentechlabs.net | Cloudflare error 1003 on `/.well-known/` and `/v1/` paths; `/health` works | **Fix requires dashboard:** Cloudflare → Security → WAF → allow `api.gentechlabs.net/.well-known/*` and `/v1/*` | ⏸️ Needs Jordan |
| 2026-08-07 | **No revenue despite traffic — Avalanche rail missing** | Gateway only advertised Base + Algorand; Avalanche-listed services (AgentScan #1770) had **no settlement rail** — clients on Avalanche literally could not pay. Likely a major cause of traffic-without-revenue. | Added **Avalanche rail** (`eip155:43114`, native USDC `0xB97EF9...`) to `NETWORKS`, wired **PayAI facilitator** (`facilitator.payai.network`) verify+settle path, set `X402_PAYTO_AVALANCHE=0x7ebff...`, enabled `X402_NETWORKS="base,algorand,avalanche"`. Gateway now advertises 3 rails. 24 tests pass. | ✅ This file |

---

*Last updated: 2026-07-24*
