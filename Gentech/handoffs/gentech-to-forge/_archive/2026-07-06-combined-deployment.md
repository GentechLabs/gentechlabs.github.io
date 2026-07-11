# Forge Handoff — Combined Deployment (Error Fix + Rate Limiting)

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Created:** July 6, 2026
**Priority:** HIGH

---

## What Needs Done

**Deploy TWO fixes to x402 gateway:**

1. **Error handling fix** — Returns 402 instead of 500 for payment errors
2. **Rate limiting middleware** — Per-wallet limits (10/min free, 100/min paid)

---

## Changes Made

### 1. Error Handling (worker.js, line 142-164)

Added try-catch middleware to gracefully handle x402/CDP payment errors and return proper HTTP status codes.

### 2. Rate Limiting (worker.js, line 142-233)

Added KV-based rate limiting:
- **Free tier:** 10 calls/minute, 50 calls/day
- **Paid tier:** 100 calls/minute, 1,000 calls/day
- **Bypasses:** `/health`, `/pricing`, `/openapi.json`, `/.well-known/*`
- **Storage:** Cloudflare KV with 2min (minute) and 24h (day) TTL

### 3. KV Configuration (wrangler.toml, line 25-27)

Added `[[kv_namespaces]]` binding for rate limiting storage.

---

## Commands to Run

```bash
cd /root/vaults/gentech/10-Labs/x402-gateway

# Verify changes
grep -A 10 "Rate limiting" worker.js
grep "kv_namespaces" wrangler.toml

# Deploy to Cloudflare
npx wrangler deploy

# Verify KV namespace created (if needed)
npx wrangler kv:namespace list
```

---

## Expected Results

After deployment:

### Error Handling Test
```bash
curl -I https://api.gentechlabs.net/api/games/search?q=cyberpunk
# Should return: 402 (not 500)
# Response includes: "payment_required" + helpful message
```

### Rate Limiting Test
```bash
# Test free tier (no payment headers)
for i in {1..12}; do
  curl -s https://api.gentechlabs.net/api/games/search?q=cyberpunk | jq '.error'
done
# First 10: 402 (payment required)
# 11th+: 429 (rate limit exceeded)
```

### Bypass Test
```bash
curl https://api.gentechlabs.net/health | jq '.status'
# Should work unlimited times (no rate limit)
```

---

## Verification Script

After deployment, run:

```bash
cd /root/vaults/gentech
python3 scripts/test-x402-enforcement.py
```

Expected result:
- ✅ Health: PASS
- ✅ Pricing: PASS
- ✅ Paid without payment: PASS (402 status)
- ❌ Paid with payment: FAIL (expected — no real payment yet)

---

## What Gentech Is Doing Next

While Forge deploys, Gentech will:
1. Build revenue tracking dashboard (Day 2)
2. Prepare end-to-end payment test plan

---

## Deployment Checklist

- [ ] Deploy worker.js with error handling + rate limiting
- [ ] Verify KV namespace created (or create manually)
- [ ] Test error handling (402 response)
- [ ] Test rate limiting (429 response after 10 calls)
- [ ] Test bypass endpoints (health/pricing unlimited)
- [ ] Update handoff with deployment status

---

**Status:** Ready for Forge to deploy.
**Estimated time:** 10-15 minutes to deploy and verify.
**Dependencies:** Requires Cloudflare API token (already configured).