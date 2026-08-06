# 0x x402 Swap Rail — Scope & Strategy
**Jordan greenlit deep-dive (Aug 5, 2026).** Found via 0x docs MCP + 0x blog.

---

## 1. The discovery (why this matters)

0x (one of the largest DEX aggregators) made its **Swap API accessible via x402 and MPP** (June 2026) — the open payment standards GenTech is built on. This is **direct validation of GenTech's core thesis** (x402 rail/middleware, per-tx fees).

**Key facts (from 0x blog, June 23 2026):**
- Agents pay **$0.01/request in USDC from their own wallet — NO API key required.** Payment IS the credential.
- **x402** = Coinbase standard, pays USDC on **Base (EVM)** or Solana. Our home chain.
- Endpoint: `agent.api.0x.org/v1/x402/` — no key header needed.
- Every request **cryptographically attributable** by wallet address + on-chain tx hash.
- **MPP** (Stripe/Tempo) = USDC.e on Tempo Mainnet (chainId 4217), alternative.
- Swap execution chain is independent of payment network (any EVM chain via `chainId`).

---

## 2. Strategic value for GenTech (3 pillars)

### A. Compliance (Jordan's point)
We want people to **stay compliant**. 0x-x402 gives a **credential-free, attributable** swap path:
- No API key to leak/rotate → fewer credential-management attack surfaces.
- Every payment is on-chain + attributable → a **built-in audit trail** for compliance.
- Payment-as-credential means the agent's actions are provably its own.

### B. Multi-rail / multi-chain payments (Jordan's point)
Enables receiving payment from **other rails and other chains**:
- x402 (Base USDC / Solana USDC) + MPP (Tempo USDC.e) + keyed 0x + Coinbase CDP.
- The treasury can **receive and settle across rails**, then swap via 0x on any EVM chain.
- This is the "interchangeable sockets" model, proven: the swap rail is a config choice.

### C. Revenue model (GenTech as the rail)
If GenTech is the x402 middleware/rail, every 0x-x402 swap flowing through our infra is a **per-tx fee** (open-core pricing). We're positioned to be the rail *underneath* agent swaps, not just a user.

---

## 3. Build scope

### Phase 1 — Wire 0x-x402 as a treasury swap rail (build item #45)
- Add `zero_x402_leg.py` — venue-agnostic swap executor using the x402 flow:
  1. Send no-key request to `agent.api.0x.org/v1/x402/swap-allowance-holder-price/`
  2. On `402 Payment Required`, sign USDC payment (EIP-3009 via x402 client)
  3. Retry with payment header → get swap data
  4. Execute swap on-chain, verify receipt
- DRY_RUN-first, mirrors `gta_executor` pattern. REAL gated by `AAE_X402_REAL=1`.
- Uses Q402 trial key (live, 2000 credits, 10 days left) as the x402 rail.

### Phase 2 — Test flow (live, once rate-limit clears)
- **Test 1:** $0.01 USDC payment to 0x x402 endpoint from treasury wallet → prove no-key swap path.
- **Test 2:** Full swap USDC → WETH on Base via x402, verify on-chain.
- **Test 3:** Multi-rail — receive on one chain, swap on another (x402 pay on Base, execute on another EVM chain).

### Phase 3 — Compliance + multi-rail productization
- Document the attributable audit trail as a compliance feature.
- Expose "receive from any rail, swap anywhere" as a product capability.

---

## 4. Current status / blockers

- **0x API key** (`ZEROX_API_KEY` in .env) — **verified working** (needs `0x-version: v2` header + token addresses). See develop-and-verify skill.
- **0x x402 endpoint** — **rate-limited right now** (429 "Usage limit exceeded", team billing cap, retry ~1h). Live test blocked until it clears.
- **Q402 trial key** — live, 2000 credits, 10 days left (expires Aug 15). Ready as the x402 rail.
- **Treasury funded** — CDP server $31.50 USDC + gas. Ready for live tests.

---

## 5. Definition of Done
1. `zero_x402_leg.py` produces a verified x402 swap plan in DRY_RUN.
2. Live $0.01 x402 payment succeeds (no key), swap executes on-chain, receipt verified.
3. Multi-rail receive+swap demonstrated.
4. Compliance/attribution documented as a product feature.
