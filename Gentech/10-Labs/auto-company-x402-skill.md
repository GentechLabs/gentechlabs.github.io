---
name: x402-monetization
description: Register API endpoints on the GenTech x402 gateway and start charging per-call via HTTP 402 micropayments. No API keys, no subscriptions — just USDC on 5 chains.
---

# x402 Monetization Skill

Let your agents monetize the products they build. Register any API endpoint on the GenTech x402 gateway and start charging per-call in USDC.

## Prerequisites

- A wallet with USDC on any supported chain (Base, Solana, Avalanche, BNB, OKX X Layer)
- An API endpoint that returns JSON

## Tools

### `x402-register`

Register a new paid endpoint on the gateway.

```
POST https://api.gentechlabs.net/api/register
{
  "endpoint": "/api/my-service",
  "method": "POST",
  "description": "What this endpoint does",
  "tier": "standard",
  "target_url": "https://your-service.com/actual-endpoint"
}
```

Pricing tiers:
| Tier | Price | Best for |
|------|-------|----------|
| micro | $0.001 | News, lookups, simple queries |
| standard | $0.005 | Search, analysis, moderate compute |
| premium | $0.01 | AI inference, risk assessment |
| pro | $0.025 | Deep analysis, multi-source |
| ultra | $0.10 | Full agent scans, heavy compute |

### `x402-pricing`

View or update pricing for your registered endpoints.

```
GET https://api.gentechlabs.net/api/pricing
```

### `x402-revenue`

Check your earnings from paid calls.

```
GET https://api.gentechlabs.net/api/revenue?wallet=<your-wallet>
```

### `x402-status`

Verify gateway health and supported chains.

```
GET https://api.gentechlabs.net/health
```

## How It Works

1. Your agent builds a product → registers it on the gateway
2. A buyer agent calls your endpoint → gets HTTP 402 with payment requirements
3. Buyer pays USDC → gateway proxies the request to your real endpoint
4. You receive the payment minus 5% gateway fee
5. Settlement happens on-chain in seconds

## Supported Chains

| Network | Chain ID | USDC Address |
|---------|----------|--------------|
| Base | 8453 | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Solana | 5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| Avalanche | 43114 | `0x9702230A8Ea53601f5cD2dc00fDBcE2c3Ed7B5E9` |
| BNB Chain | 56 | `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` |
| OKX X Layer | 196 | `0x8b1c7B3aD3a26C5EB0dD8b4D0CDbB56c8B33c5B8` |

## Example Flow

```
Agent builds: /api/price-alert
Agent registers: x402-register endpoint=/api/price-alert tier=standard
Buyer calls: GET /api/price-alert?symbol=BTC
Response: 402 Payment Required — pay $0.005 USDC on Base
Buyer pays: signature sent, request replayed
Buyer gets: { "price": 68420, "alert": "below support" }
Seller earns: $0.00475 (after 5% fee)
```
