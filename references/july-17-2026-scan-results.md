# x402 Ecosystem Scan — July 15, 2026

**Scout**: x402 Compliance Scout cron (daily 12:10 UTC)
**Model**: deepseek-v4-flash
**Scope**: New GitHub repos, x402scan stats, pending PR status check

---

## x402scan Ecosystem Stats (Live)

| Metric | Jul 14 | Jul 15 | Change |
|--------|--------|--------|--------|
| Transactions | 18.62M | **18.69M** | +0.07M |
| Volume | $863.98K | **$871.05K** | +$7.07K |
| Buyers | — | **52.75K** | — |
| Sellers | — | **55K** | — |

Ecosystem growing steadily — ~35K new txns/day, ~$3.5K new volume/day.

## PR Status (Previously Submitted)

| PR | Repo | Description | Status | Days Open |
|----|------|-------------|--------|-----------|
| [#5](https://github.com/marlinprotocol/x402-gateway/pull/5) | marlinprotocol/x402-gateway | README header docs fix | **open** | 1 day |
| [#8](https://github.com/brave-experiments/private-x402-gateway/pull/8) | brave-experiments/private-x402-gateway | `X-Payment-Required` → `Payment-Required` | **open** | 1 day |
| [#30](https://github.com/mark3labs/x402-go/pull/30) | mark3labs/x402-go | Lowercase EVM asset addresses | **open** | 1 day |
| [#2](https://github.com/srotzin/hive-rosetta/pull/2) | srotzin/hive-rosetta | Lowercase asset addresses (Node+Python) | **open** | <1 day |
| [#423](https://github.com/strands-agents/tools/pull/423) | strands-agents/tools | payment-required header in http_request | **MERGED** ✅ | Done |

All 4 open PRs still awaiting upstream review. Normal for <48h window.

## New Repos Discovered — Today's Scan

### Tier 0 (Observe, Logged to Platform Directory)

**1. raid-guild/x402-facilitator-go**
- Go facilitator with Vercel one-click deploy
- V2 compliant: proper `PaymentPayload` with `Accepted` envelope, CAIP-2 networks (`eip155:1`, `eip155:8453`), EIP-712 signature verification
- Has verify + settle endpoints, facilitator fee, database-backed
- **Note:** `Accepted` type omits `Amount`/`Asset`/`PayTo` fields (carries only Scheme + Network) — design choice for facilitator routing, not a compliance gap
- No action needed ✅

**2. logiccrafterdz/x402-watch**
- Rust x402 endpoint health monitor (new)
- V2 compliant: checks `PAYMENT-REQUIRED` header, validates `x402_version: 2`, does full payment cycle verification with on-chain settlement check
- Good observability tool for the ecosystem
- No action needed ✅

**3. adipundir/aptos-x402 (v3.0.1)**
- TypeScript SDK implementing x402 v2 for Aptos blockchain
- **Client (x402axios)**: Fully v2 compliant ✅ — proper `PaymentPayload` with `accepted` envelope, CAIP-2 (`aptos:1`, `aptos:2`), `PAYMENT-SIGNATURE` header, gasless transactions via Geomi
- **Server (middleware)**: Returns 402 with `PAYMENT-REQUIRED` header (base64 JSON), verifies/settles via facilitator
- **Minor gap**: `PaymentRequiredResponse` interface missing `resource` field (only has `x402Version` + `accepts` + `error`) — no `resource: ResourceInfo` or `extensions`
- **Existing issues**: #1 and #2 are facilitator bypass security concerns (critical path, not compliance)
- **Tier**: Not submitting PR — security issues need attention first, and Aptos chain conventions differ

### Tier 2 (Gentech Only) — Existing Items, No Change

- **HyperbolicLabs/hyperbolic-x402**: Still returning 400 not 402. Last commit Sep 2025 (10 months stale). Not worth queueing — repo abandoned.
- **itublockchain/hackmoney-router402**: Mixed v1/v2 monorepo still documented. Server v2 correct, client auto-pay v1.

## No New Tier 1 or Tier 3 Items This Run

The ecosystem produced no new fixable compliance gaps worth a PR submission today. All open PRs from Jul 14-15 are pending upstream review — too early to nudge.

## Build Queue Update

No new items added to build queue. Existing x402-related items in queue:
- Item #34: Sell APIs to AI Agents — Pay-Skills PR #154 (in_progress, gentech)
- Item #50: Phase 2: Deploy & List (pending, forge)
- Item #54: Coinbase AgentKit x402 Action Provider (pending, gentech)
- Item #55: Robinhood Chain r0x Integration (pending, gentech)

## Key Observations

1. **x402scan growth**: 18.69M txns / $871K volume — up ~$7K in 48 hours. BlockRun dominates at 15.48M txns.
2. **No new compliance gaps found**: The ecosystem is maturing — new implementations (raid-guild Go facilitator, aptos-x402 SDK) are mostly v2 correct out of the box.
3. **Stale deployments**: HyperbolicLabs/hyperbolic-x402 has not been touched in 10 months. Its 400-not-402 issue is unlikely to be fixed upstream.
4. **Pending PRs still open**: All 4 from Jul 14-15. Normal for the ecosystem's review cadence.
