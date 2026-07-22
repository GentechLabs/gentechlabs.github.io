# GenTech x402 Gateway — Architecture & Operations Guide

## Overview

The x402 gateway is a Cloudflare Worker that serves as the payment layer for all GenTech Labs APIs. It implements the **HTTP 402 Payment Required** pattern: agents pay per-call in USDC via x402 protocol, and on verification the request is proxied to the VPS backend service.

## Architecture

```
Agent → api.gentechlabs.net → Cloudflare Worker (gentechlabs-api)
  ├── /health, /pricing, /openapi.json → handled directly
  ├── /.well-known/agent.json → handled directly
  └── /v1/* (paid endpoints)
       ├── No payment → HTTP 402 + payment instructions
       └── X-Payment-Proof header → On-chain verification → VPS proxy
```

## Payment Verification Flow (v7.0.0+)

1. Agent sends tx hash, sender address, timestamp, amount, nonce as base64 JSON in `X-Payment-Proof` header
2. Worker validates proof format + timestamp window (5 min)
3. Worker fetches transaction from Base RPC (`eth_getTransactionByHash`)
4. **ChainID check**: verifies `tx.chainId === 0x2105` (Base mainnet)
5. **Contract check**: verifies `tx.to === USDC contract` on Base
6. **Sender recovery**: uses `tx.from` (node-recovered from ECDSA signature)
7. Worker fetches receipt (`eth_getTransactionReceipt`)
8. **Status check**: verifies `status === 0x1` (success) + blockHash present
9. **Log parsing**: extracts `Transfer` event from receipt logs (NOT tx.input — logs are emitted by the canonical contract and cannot be forged)
10. **Recipient check**: verifies log `to` matches GenTech payment address
11. **Amount check**: verifies USDC amount >= required price
12. On success: stores tx hash in KV for idempotency, proxies to VPS backend
13. On failure: returns 402 with error details

## File Locations (VPS)

| File | Purpose |
|------|---------|
| `src/worker.ts` | Cloudflare Worker source (TypeScript) |
| `src/x402-verification.ts` | Verification logic (reference, kept for testing) |
| `src/test-x402.ts` | Unit tests for verification |
| `wrangler.toml` | Wrangler deployment config |
| `~/.hermes/profiles/gentech/secrets/cloudflare-token` | Cloudflare API token |

## Deployment

```bash
cd /root/vaults/gentech
export CLOUDFLARE_API_TOKEN=$(cat ~/.hermes/profiles/gentech/secrets/cloudflare-token)
npx wrangler deploy
```

## VPS Backend Services

| Port | Service | Subdomain | Status |
|------|---------|-----------|--------|
| 8080 | Deal Tracker | deals.gentechlabs.net | Running |
| 8082 | Price API | prices.gentechlabs.net | Running |
| 8084 | Gas Price | gas.gentechlabs.net | Running |
| 8086 | Security | security.gentechlabs.net | Running |
| 8088 | Rugcheck | rugcheck.gentechlabs.net | Running |
| 8090 | DeFi Intelligence | defi.gentechlabs.net | ✅ Healthy |
| 8091 | Agent Search | search.gentechlabs.net | Running |

## Testing

```bash
# Health check
curl https://api.gentechlabs.net/health

# Pricing
curl https://api.gentechlabs.net/pricing

# Paid endpoint (no payment → 402)
curl https://api.gentechlabs.net/v1/wallet/analyze

# Paid endpoint (with payment — returns data or 402 if invalid)
curl -H "X-Payment-Proof: $(echo '{"signature":"0x...","sender":"0x...","timestamp":123,"amount":"0.025","nonce":"abc123"}' | base64)" https://api.gentechlabs.net/v1/wallet/analyze
```

## Pricing Tiers

| Tier | Price | Endpoints |
|------|-------|-----------|
| Micro | $0.001 | news, details, trailers |
| Standard | $0.005 | search, cheapest, NFT, shipping |
| Premium | $0.01 | airdrops, AI token risk |
| Pro | $0.025 | AI wallet analytics |
| Ultra | $0.10 | AI agent scan |

## History

- **v6.0.0** (Forge): Cloudflare worker, metadata only, paid endpoints returned 404
- **v7.0.0** (Gentech): Full 402 payment gateway with on-chain verification, log-based transfer parsing, chainID checks, idempotency
