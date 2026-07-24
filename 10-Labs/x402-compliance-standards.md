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

## 6. Incident Log

| Date | Issue | Cause | Fix | Documented |
|------|-------|-------|-----|------------|
| 2026-07-24 | OKX listing rejected | No A2A node running | Installed `@okxweb3/a2a-node`, ran `okx-a2a doctor --fix` | ✅ This file |
| 2026-07-24 | Agentic Market validator failed | Manifest at wrong path, no `.well-known/` in `api.*` nginx config, Cloudflare WAF blocking | Created `x402-bazaar` file, added nginx `location /.well-known/` block | ✅ This file |
| 2026-07-24 | Port 8090 API gateway down for 77k+ restarts | `server.py` missing from agent-kit-q402 repo, systemd misconfigured | Built new x402 gateway at `10-Labs/x402-gateway/server.py`, updated systemd service | ✅ This file |
| 2026-07-24 | PAYMENT-REQUIRED header missing | Old implementation only returned 402 in response body | New gateway returns proper base64-encoded `PAYMENT-REQUIRED` header per v2 spec | ✅ This file |
| 2026-07-24 | Cloudflare WAF blocking api.gentechlabs.net | Cloudflare error 1003 on `/.well-known/` and `/v1/` paths; `/health` works | **Fix requires dashboard:** Cloudflare → Security → WAF → allow `api.gentechlabs.net/.well-known/*` and `/v1/*` | ⏸️ Needs Jordan |

---

*Last updated: 2026-07-24*
