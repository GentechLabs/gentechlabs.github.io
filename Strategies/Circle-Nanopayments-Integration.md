# Circle Nanopayments Integration — Build Brief

**Date:** 2026-05-20
**Status:** Approved by Jordan
**Category:** Finance / x402

## What

Add Circle Gateway nanopayments as the **seller-side** x402 payment layer for our Express APIs.

## Why

- We have buyer-side covered: Ampersend (Base) + pay.sh (Solana)
- Missing: seller-side — putting payment walls on our own endpoints
- Circle's `@circle-fin/x402-batching` gives us Express middleware with batched USDC settlement
- Gas-free, sub-cent minimums, crosschain withdrawal

## Stack Complete Picture

| Side | Tool | Chain | Role |
|------|------|-------|------|
| Buyer | Ampersend | Base | Our agents paying for APIs |
| Buyer | pay.sh | Solana | Our agents paying for APIs |
| **Seller** | **Circle Gateway** | **Multi-chain** | **Our endpoints charging for access** |

## Packages

- `@circle-fin/x402-batching` — Circle Gateway SDK (recommended)
- `@x402/express` — Open-source Express middleware (alternative)
- `@x402/core`, `@x402/evm` — Core protocol + EVM schemes
- `viem` — EVM utilities

## Key Endpoints

- Testnet facilitator: `https://gateway-api-testnet.circle.com`
- Production facilitator: `https://gateway-api.circle.com`
- Open facilitator: `https://facilitator.x402.org`

## Next Steps

1. Scaffold Express server with `createGatewayMiddleware`
2. Protect a test route at `$0.01`
3. Test with buyer client from Circle quickstart
4. Deploy to our infra
5. Register endpoints in x402 catalog

## Docs

- Circle nanopayments: https://developers.circle.com/gateway/nanopayments
- Seller quickstart: https://developers.circle.com/gateway/nanopayments/quickstarts/seller
- npm: `@x402/express` v2.12.0
- Skill: `circle-nanopayments` (created)
