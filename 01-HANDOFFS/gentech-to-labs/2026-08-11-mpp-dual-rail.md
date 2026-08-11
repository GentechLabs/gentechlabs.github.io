# Gentech → Labs — 2026-08-11

## ✅ Shipped this session

### #47 — Dual-Protocol Payments: MPP rail alongside x402 (labs)
**Status:** SHIPPED (gentech, 2026-08-11) — verified live.

The x402 gateway now serves **both** payment rails on every paid endpoint:

- **402 challenge is dual-rail:** unauthenticated requests now return HTTP 402 with **both** `PAYMENT-REQUIRED` (x402) **and** `WWW-Authenticate: Payment` (MPP, IETF draft-httpauth-payment-00) headers. MPP clients can settle the same endpoint as x402 clients.
- **MPP credential verification:** `Authorization: Payment <base64-json>` credentials are extracted (`extract_mpp_credential`) and verified (`verify_mpp_simulation`) via the same HMAC simulation path as x402. EVM method accepted (settles via our USDC rails); other methods rejected with a clear reason.
- **Settle-on-success routing:** a valid MPP credential routes to the backend through the shared `_route_to_backend` helper (extracted from the x402 proof path — no code duplication).

**Verification (all real):**
- 37/37 tests pass (26 existing + 11 new MPP tests in `test_mpp_dual_rail.py`).
- Live server: `GET /v1/security/score/0xabc` → **402** with both `PAYMENT-REQUIRED` + `WWW-Authenticate: Payment` headers.
- Live MPP-settled request: `Authorization: Payment <valid cred>` → **HTTP 200** with real token-security data (score 39, CRITICAL) — proof the MPP path bypasses the 402 gate and reaches the backend.

**Files:**
- `10-Labs/x402-gateway/server.py` — MPP challenge + extraction + verification + route integration
- `10-Labs/x402-gateway/test_mpp_dual_rail.py` — 11 new tests

**Note:** MPP settlement is currently the HMAC **simulation** path (dev/ARC flow). Production MPP settlement would go through a facilitator (PayAI etc.) — flagged as a follow-up, not a blocker.

## Group returns consumed
- Labs returns (29, 52, 19, 2, 30, 1, 6, 48, 49) — already applied in 2026-08-10 status corrections; no new action needed.
- Forge returns (61, 59, 60, 66, 62, 65) — not in current queue (processed in prior session).
