# x402 V2 Compliance Scout Report
**Date**: 2026-07-14  
**Reference**: Syra API (api.syraa.fun) — full V2 implementation  
**Spec**: Reverse-engineered from Syra + x402-foundation/x402 v2 spec + x402-rs crate (x402-axum)

---

## 🏆 First PR Target Recommendation

**marlinprotocol/x402-gateway** — This is the best first target. It uses the V2-compliant x402-rs middleware internally but is missing a `/.well-known/x402` endpoint and doesn't return the full spec body alongside the `Payment-Required` header. The fix is ~20 lines: add a route handler returning static discovery JSON and include a JSON body (not just headers) on 402 responses.

---

## Reference Implementation Status: ✅ Syra (api.syraa.fun)

Syra is the compliance gold standard. Both `/.well-known/x402` and 402 responses are fully V2-compliant.

| Field | Present? |
|---|---|
| `/.well-known/x402` with `version: 1` | ✅ |
| `resources[]` — full endpoint list | ✅ |
| `resourceDetails[]` — with url, name, description, price | ✅ |
| `baseGateway` — enabled, network, asset, payTo, gatewayUrl, discoveryUrl, openapiUrl | ✅ |
| `ownershipProofs[]` | ✅ |
| `instructions` block | ✅ |
| `Payment-Required` header (base64 JSON) | ✅ |
| `x402Version: 2` in header & body | ✅ |
| `accepts[]` with scheme, CAIP-2 network, amount, asset (lowercase), payTo, maxTimeoutSeconds | ✅ |
| `resource` block with url, description, mimeType, serviceName, tags | ✅ |
| No deprecated `X-PAYMENT` headers | ✅ |

---

## Scanned Implementations

### 1. twit.sh (x402.twit.sh) — ⚠️ Near-compliant

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Full discovery with resources |
| HTTP 402 | ✅ | |
| `Payment-Required` header (base64) | ✅ | |
| `x402Version: 2` in header payload | ✅ | |
| `accepts[]` with CAIP-2, amount, asset, payTo | ✅ | |
| `resource` block | ✅ | |
| `extensions` (bazaar) | ✅ | |
| Deprecated headers | ⚠️ | Still exposes `X-PAYMENT` alongside `PAYMENT-REQUIRED` |
| JSON body on 402 | ❌ | Body is empty — spec says body should include x402version, accepts[], etc. |
| `maxTimeoutSeconds` | ✅ | Set to 300 |

**Fix**: (a) Remove `X-PAYMENT` from `access-control-expose-headers` and stop setting the `x-payment` header. (b) Include the payment-required JSON in the response body (not just the header). **Effort: LOW**

---

### 2. JarvisClaw (api.jarvisclaw.ai) — ✅ Very close

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Returns full metadata |
| HTTP 402 | ✅ | |
| `Payment-Required` header | ✅ | V2-style, no deprecated headers |
| `x402Version: 2` | ✅ | In both header and body |
| `accepts[]` | ✅ | 2 entries (Base USDC + Solana USDC) |
| `resource` block | ✅ | |
| `extensions` (bazaar) | ✅ | |
| `facilitator` field | ✅ | Points to CDP facilitator |
| CAIP-2 networks | ✅ | `eip155:8453`, `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |

**Minor issues**: No `maxTimeoutSeconds` in body (present in header payload). No `instructions` block in the body. **Effort: VERY LOW**

---

### 3. BlockRun (blockrun.ai) — ⚠️ Body format differs

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Version 1 with resources, baseGateway |
| HTTP 402 | ✅ | |
| `Payment-Required` header | ✅ | Base64-encoded V2 JSON |
| `x402Version: 2` | ✅ | In header payload |
| `accepts[]` | ✅ | In header payload |
| Body JSON format | ❌ | Body uses `paymentInfo` object, not the spec format |
| Body `x402version` field | ❌ | Missing — body has `x402Version` inside `paymentInfo` |
| `instructions` block in body | ❌ | Body has `documentation` URL instead |
| Deprecated headers | ⚠️ | Also sets `X-PAYMENT-REQUIRED` alongside `PAYMENT-REQUIRED` |
| `www-authenticate` header | ⚠️ | Non-standard — uses `X402 requirements=...` format |

**Fix**: (a) Align body JSON with spec — include `x402version: "x402-v2"`, `accepts[]`, `network`, `asset`, `amount`, `payment_address` at top level. (b) Add `instructions` block. (c) Drop `X-PAYMENT-REQUIRED` header. **Effort: LOW-MEDIUM**

---

### 4. Marlin Protocol (github.com/marlinprotocol/x402-gateway) — ⚠️ Good middleware, no discovery

| Check | Status | Note |
|---|---|---|
| 402 V2-compliant middleware | ✅ | Uses `x402-rs` → `x402-axum` which generates compliant V2 responses |
| `Payment-Required` header | ✅ | Via middleware |
| `accepts[]` with CAIP-2 | ✅ | Internal types convert human names → proper CAIP-2 |
| `.well-known/x402` | ❌ | Not served by the gateway — needs manual addition |
| JSON body on 402 | ❌ | Middleware returns empty body with V2 |
| Config uses human names | ⚠️ | `"base-sepolia"`, `"solana-devnet"` — converted internally internally |
| `maxTimeoutSeconds` | ⚠️ | Not configurable in `config.json` |

**Fix**: (a) Add `/.well-known/x402` route serving discovery JSON. (b) Add route description/config fields so discovery can be auto-generated. **Effort: LOW**

---

### 5. 2s.io — ⚠️ Custom format

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Returns V2-style metadata |
| `x402Version: 2` | ✅ | In well-known |
| Resource catalog | ✅ | Has /api/directory with full endpoint list |
| `baseGateway` block | ❌ | Missing from well-known |
| `resourceDetails[]` | ❌ | Uses different structure (service, capabilities, authentication) |
| Standard accepts[] format | ⚠️ | Different structure than spec |

**Fix**: Align `.well-known/x402` with spec — add `baseGateway` and `resourceDetails[]`. **Effort: MEDIUM**

---

### 6. StableEnrich (stableenrich.dev) — ⚠️ Partial discovery

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Has version 1 with resources[] |
| `resourceDetails[]` | ❌ | Missing individual pricing |
| `baseGateway` block | ❌ | Missing |
| `instructions` block | ✅ | Present |
| HTTP 402 flow | ❌ | Returns 405 on test, may not be live |

**Fix**: Add `baseGateway`, `resourceDetails` with per-endpoint pricing. **Effort: MEDIUM**

---

### 7. agentutility.ai (x402.agentutility.ai) — ⚠️ Minimal well-known

| Check | Status | Note |
|---|---|---|
| `.well-known/x402` | ✅ | Present but minimal |
| `ownershipProofs` | ✅ | |
| `version` | ❌ | Missing |
| `resources[]` | ❌ | Missing |
| `baseGateway` | ❌ | Missing |

**Fix**: Build out the well-known endpoint with full resources, baseGateway, resourceDetails. **Effort: MEDIUM**

---

### 8. x402-rs (github.com/x402-rs/x402-rs) — ✅ SDK compliance

| Check | Status | Note |
|---|---|---|
| V2 `Payment-Required` header | ✅ | Base64-encoded JSON, proper header name |
| V2 `Payment-Signature` header | ✅ | |
| V2 `Payment-Response` header | ✅ | |
| CAIP-2 network identifiers | ✅ | |
| V1 backward compat | ✅ | V1 middleware includes JSON body on 402 |
| Facilitator integration | ✅ | Works with CDP and x402.org facilitators |

---

### 9. OneSource (api.onesource.io) — ❌ Not x402-gated

Returns HTTP 401 (API key required), not 402. Has `.well-known/x402` with description but the endpoint flow doesn't use x402. Documentation stub only.

---

### Not Scanned (SDK repos, not deployable gateways)

- **x402-foundation/x402** (6.3k ⭐): Canonical spec repo, multi-language SDK. Compliant by definition.
- **x402-rs/x402-rs** (279 ⭐): Rust SDK. See #8 above.
- **Merit-Systems/x402scan** (357 ⭐): Ecosystem explorer, not a gateway.

---

## Priority Action List

### 🔴 LOW Effort, HIGH Impact (easy PR wins)

1. **marlinprotocol/x402-gateway**: Add `/.well-known/x402` route (~20 lines of Rust). Add `description`, `serviceName`, `tags` to config so discovery can be auto-generated. Include JSON body on 402.

2. **twit.sh**: Delete `X-PAYMENT` from `access-control-expose-headers`. Include payment-required JSON in response body.

3. **BlockRun**: Drop `X-PAYMENT-REQUIRED` header. Restructure body to include spec fields at top level (`x402version`, `accepts`, `network`, `asset`, `amount`, `payment_address`, `instructions`). Remove non-standard `www-authenticate` format.

### 🟡 MEDIUM Effort

4. **StableEnrich**: Add `baseGateway` and `resourceDetails[]` to `.well-known/x402`. Implement x402 payment gating (returns 405 currently).

5. **agentutility.ai**: Add `version: 1`, `resources[]`, `resourceDetails[]`, `baseGateway` to `.well-known/x402`.

6. **2s.io**: Align `.well-known/x402` with spec — add `baseGateway` and `resourceDetails[]`.

### 🔵 HIGH Effort

7. **OneSource**: Implement actual x402 payment flow (currently API-key based). Full architectural change.

---

## 📊 Ecosystem Health Summary

| Metric | Value |
|---|---|
| Total endpoints tested | 10 |
| Fully V2-compliant | 1 (Syra) |
| Near-compliant (1-2 issues) | 3 (twit.sh, JarvisClaw, x402-rs SDK) |
| Partial (missing discovery) | 3 (Marlin, StableEnrich, agentutility) |
| Custom format | 1 (2s.io) |
| Not x402-implemented | 1 (OneSource) |
| Ecosystem transactions (30d) | 18.62M |
| Ecosystem volume (30d) | $863.98K |
