# GenTech Infrastructure Issues Playbook

**Purpose:** Every gateway/connection/compliance issue we hit gets logged here — symptom, diagnosis, fix, verification. When we help other teams get compliant (x402, ERC-8004, gateways), this is our fast-path reference. If we've seen it, we diagnose it in minutes, not days.

**How to use:**
- New issue → append an entry in this file (date-first, newest at bottom)
- Same issue again → link to the original entry, note what's different
- Before asking Jordan about any infra problem → check here first

---



## Issue #5 — 4 of 6 advertised services had no backend (phantom endpoints)
- **Date:** 2026-08-02
- **Symptom:** Manifest advertised 6 x402 services; only 2 (token_security, market_intelligence) had real backends. The other 4 (agent_discovery, defi_lp_analytics, wallet_analysis, nft_search) returned stubs — a bot that paid got no data. Trust/reputation risk.
- **Root cause:** Manifest was written aspirationally; backends never built.
- **Fix:** Built all 4 as FastAPI services (ports 8091-8094) with keyless data sources:
  - agent_discovery → 8004scan.io ERC-8004 registry (fields are snake_case: agent_id, chain_id, x402_supported; API returns {items,total,...})
  - defi_lp_analytics → DexScreener tokens endpoint + efficiency scoring
  - wallet_analysis → Solana RPC getTokenAccountsByOwner + DexScreener prices
  - nft_search → Magic Eden v2 collections (NO search param — fetch 100, filter client-side; offset/limit must be multiples of 20)
  - Systemd template x402-backend@.service; wired into gateway BACKEND_ROUTES + URL_TO_SERVICE; manifest bumped to 8.0.0
- **Verification:** Full matrix — every service: correct payment → 200 real data; unpaid → 402; underpaid → 402. All 6 confirmed live.
- **Lesson:** The manifest is a promise. Only list services with live, correctly-routed backends. Test the FULL payment loop (discovery → 402 → pay → proof → 200) for every advertised service, at every price point.

## Issue #4 — Gateway could not accept standard x402 payments (THE customer blocker)
- **Date:** 2026-08-02
- **Symptom:** $0 traction despite 10K+ website visitors/week. x402-list showed "no on-chain settlement recorded", 0 buyers. Bots could discover us but never complete a payment.
- **Root cause (3 stacked bugs):**
  1. **Wrong payment header** — gateway only read the private `x-402-token` header. Standard x402 clients send `Authorization: x402 <proof>` (v2) or `X-Payment`. Every real client's proof was ignored → always 402.
  2. **Proxy path mangling** — even with a valid token, the proxy stripped `/v1/` and forwarded wrong paths → backend 404.
  3. **Routing table mismatch** — manifest advertised 6 services but BACKEND_ROUTES only mapped old keys (security/deals/prices/gas/tokens) to wrong paths. Only 2 of 6 services had real backends at all (token_security→8088, market_intelligence→8082).
- **Fix:**
  1. `extract_proof()` — accept `Authorization: x402 <json>`, `X-Payment`, legacy `x-402-token`
  2. `verify_proof_via_cdp()` — production path via CDP facilitator `api.cdp.coinbase.com/platform/v2/x402/verify`; `verify_proof_simulation()` — local HMAC for dev (matches our SDK)
  3. `PAYMENT_VERIFY_MODE=simulation` in .env until real CDP key:secret wired
  4. Reworked `BACKEND_ROUTES` as (base, public_prefix, backend_prefix) tuples; added `URL_TO_SERVICE` map
  5. Forward `X-Payment-Proof` header to backends (rugcheck MVP gate accepts any non-empty)
- **Verification:** standard proof → security score 200 (real risk data), market price 200; no proof → 402; bad proof → 402. All 4 cases correct.
- **Lesson:** A gateway that returns a spec-perfect 402 but can't RECEIVE a standard payment is a wall, not a door. Always test the full loop: discovery → 402 → pay → proof header → 200. Also: the manifest must list only services with live, correctly-routed backends. 4 of 6 listed services (wallet_analysis, agent_discovery, defi_lp_analytics, nft_search) have NO backend — they should be removed from the manifest or built before claiming them. x402-list re-scans ~5h; traction will only move when a real on-chain settlement lands.

## Issue #3 — x402-list.com "route not signable" + compliance C (13/14)
- **Date:** 2026-08-02
- **Source:** x402-list.com listing (gentech-labs-x402-gateway)
- **Symptom:** Signability chip = "route not signable"; compliance grade capped at C with 13/14 checks passing, failing: "EIP-712 domain parameters present on every EVM entry"
- **Root cause:** The 402 envelope's `accepts[]` entry was missing the EIP-712 domain parameters (`extra.name` + `extra.version`). A standard x402 client needs these to build the signature for EIP-3009 settlement — without them it literally cannot construct the payment. Everything else in the envelope was correct (scheme, network, asset, amount, payTo, maxTimeout).
- **Fix:**
  1. `server.py` `build_payment_required()`: added `"extra": {"name": "USD Coin", "version": "2"}` inside `accepts[0]` (USDC on Base — name "USD Coin", version "2")
  2. `/.well-known/x402` was 404 (only `x402.json` and `x402-bazaar` existed) — copied `x402.json` → `x402` in `/var/www/gentechlabs/.well-known/` and chown www-data
- **Verification:** `curl https://api.gentechlabs.net/v1/security/score?...` → `accepts[0].extra == {name: "USD Coin", version: "2"}`; `/.well-known/x402` → 200
- **Spec reference:** Binance x402 v2 verify-payment docs + Monad x402 guide show `extra.name`/`extra.version` mandatory on every EVM entry; the exact EIP-712 domain must match the token's actual domain (USDC = "USD Coin"/"2"), hardcoding a wrong name breaks signature verification
- **Scan refresh:** x402-list re-scans every ~5h — expect chip to flip on next pass
- **Lesson:** Any 402 builder must include `extra` on every accepts entry, and discovery must exist at the canonical `/.well-known/x402` path, not just the Bazaar variant. Check both when building a new gateway.

---

## Issue #2 — GitHub account flagged: repos 404 on web despite public
- **Date:** 2026-08-02 (discovered during SPC application link verification)
- **Symptom:** `github.com/ProtoJay4789/<repo>` returns 404 on the web, but API says repo is public and git push works. GitHub Pages (`ProtoJay4789.github.io`) also 404s.
- **Root cause:** The personal account (ProtoJay4789) has a flag that hides web visibility of repos — known issue on this account. The **Gentech-Labs org** (created 2026-04-13, 21+ repos) serves fine.
- **Fix:** Mirror/move public-facing repos to `Gentech-Labs` org. E.g. `programmable-money-x402` → `github.com/Gentech-Labs/programmable-money-x402` (verified 200). Use org URLs everywhere public links matter (applications, READMEs, hackathon submissions).
- **Verification:** `curl -o /dev/null -w "%{http_code}" https://github.com/Gentech-Labs/<repo>` → 200
- **Lesson:** For anything user-facing (applications, submissions, portfolio), ALWAYS verify the URL returns 200 — don't trust that "public" means visible. Prefer org URLs.

---

## Issue #1 — Nous Portal "grant spent" confusion
- **Date:** 2026-08-01
- **Symptom:** Repeatedly mislabeled Nous Portal balance as "the grant" and reported it spent.
- **Root cause:** The balance reads from `member_spend_usd` in the access-token JWT (`/root/.hermes/shared/nous_auth.json`) — it's the research portal subscription spend (~$1.09, tier 2, paid), NOT a grant.
- **Fix:** None needed — corrected labeling. Read balance from JWT claims, not the portal UI.
- **Lesson:** Nous balance = `member_spend_usd` in JWT. Hourly access-token expiry is normal OAuth refresh, not a balance problem. Don't add funds based on a misread.
