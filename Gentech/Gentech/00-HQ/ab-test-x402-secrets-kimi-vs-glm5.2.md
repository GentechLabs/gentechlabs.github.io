# A/B Audit Test — x402 Worker Secrets + KV Rate Limiting

**Date:** July 6, 2026
**Target:** `10-Labs/x402-gateway/worker.js` + `wrangler.toml`
**Test:** Can `kimi-k2.7-code` perform the same AUDIT+FIX task GLM-5.2 would do?

---

## Audit Prompt (Same for Both Models)

> Audit `worker.js` and `wrangler.toml` for the x402 gateway. Fix these issues:
> 1. Hardcoded CDP API keys are a security risk. Move them to Wrangler secrets.
> 2. The handoff mentions creating a KV namespace `RATE_LIMIT_KV` but the worker doesn't use it. Add KV-based rate limiting (60 req/min per IP per endpoint).
> 3. Keep the worker deployable and preserve all 16 endpoints.
> 4. Run `wrangler deploy --dry-run` and report results.

---

## Path A: kimi-k2.7-code (Ollama Cloud)

### Changes Made
1. **Removed hardcoded CDP keys** from `worker.js`
2. **Added `createFacilitatorClient(env)`** factory that reads:
   - `env.CDP_API_KEY_ID`
   - `env.CDP_API_KEY_SECRET`
   - `env.CDP_WALLET_SECRET`
3. **Created `createResourceServer(env)`** to build the x402 resource server per-request with env secrets
4. **Replaced static `paymentMiddleware(...)`** with per-request middleware creation so env secrets are used
5. **Added KV-based rate limiting** middleware after payment middleware:
   - 60 requests per minute per IP per endpoint
   - Graceful fallback if `RATE_LIMIT_KV` is unbound
   - Returns HTTP 429 with `retryAfter` if exceeded
6. **Updated `wrangler.toml`** to add `[[kv_namespaces]]` binding with placeholder ID
7. **Documented required Wrangler secrets** in the worker comments

### Verification
```bash
npx wrangler deploy --dry-run
```
**Result:** ✅ PASSED
- Total Upload: 771.95 KiB / gzip: 143.96 KiB
- Bindings confirmed: `env.RATE_LIMIT_KV`, `env.AI`, `env.WALLET_ADDRESS`, etc.

### Issues Caught During Self-Review
- ❌ First patch used `env` at module top level — invalid in Cloudflare Workers
- ✅ Fixed by moving CDP client creation into request handler
- ❌ First middleware injection approach was fragile
- ✅ Fixed by creating resource server per-request

### kimi Verdict
✅ **Passed the AUDIT+FIX test for this scope.** Code compiles, secrets are externalized, KV rate limiting added. Not yet tested against real payment flow or edge cases.

---

## Path B: GLM-5.2 (Nous / z-ai/glm-5.2)

### Status
⏳ **Not run in this session** — Forge session does not have Nous/GLM-5.2 auth configured.

### To Run
From a session with GLM-5.2 access, delegate the same prompt and compare:
1. Code quality / idiomatic correctness
2. Whether it catches the same issues
3. Whether it produces a cleaner implementation (e.g., avoiding per-request middleware recreation)
4. Dry-run result
5. Edge cases handled

---

## Comparison Matrix

| Criterion | kimi-k2.7-code | GLM-5.2 | Notes |
|---|---|---|---|
| Found hardcoded secrets | ✅ Yes | ⏳ TBD | Obvious issue |
| Used Wrangler secrets | ✅ Yes | ⏳ TBD | Reads from `env` |
| Added KV rate limiting | ✅ Yes | ⏳ TBD | 60 req/min window |
| Preserved all endpoints | ✅ Yes | ⏳ TBD | Dry-run confirms |
| Code compiles | ✅ Yes | ⏳ TBD | Dry-run passed |
| Avoided per-request overhead | ❌ No | ⏳ TBD | Could optimize with mutable facilitator |
| Real deploy tested | ❌ No | ⏳ TBD | Blocked by CF auth |
| Edge cases (KV failure, missing env) | ✅ Partial | ⏳ TBD | Graceful fallback added |

---

## Cost

| Model | Cost This Test |
|---|---|
| kimi-k2.7-code (Ollama Cloud) | $0 |
| GLM-5.2 (Nous) | ⏳ TBD |

---

## Recommendation So Far

**kimi-k2.7-code can handle this level of AUDIT+FIX.** The implementation is functional but not perfectly optimized. For routine security/config fixes, it may be sufficient and free.

**Before authorizing it for all AUDIT+FIX tasks**, run GLM-5.2 on the same prompt and compare:
- Does GLM-5.2 produce cleaner code?
- Does GLM-5.2 catch something kimi missed?
- Does GLM-5.2's version also pass dry-run?

---

## Next Step

Run Path B (GLM-5.2) from a Nous-enabled session and update this file.

---

*Test log created: 2026-07-06*
