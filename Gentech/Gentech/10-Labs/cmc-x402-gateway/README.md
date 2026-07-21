# CMC x402 Gateway

**CoinMarketCap data behind an x402 paywall.** Any agent with a wallet pays per query in USDC — no API keys, no subscriptions.

Built by **GenTech Labs**.

---

## Quick Start

```bash
# Install
npm install

# Set CMC API key
npx wrangler secret put CMC_API_KEY

# Deploy
npm run deploy
```

## Usage

All endpoints require an **x402 payment** of **$0.001** per call. Make a GET request, and if no payment proof is attached, the gateway returns HTTP 402 with a payment manifest.

### cURL (no payment → see paywall)

```bash
curl -i "https://cmc-x402-gateway.jordanjones0902.workers.dev/v1/cmc/quotes?symbol=BTC,ETH"
```

Response: `HTTP 402` with a JSON payment manifest telling your wallet to pay 1000 microUSDC.

### cURL (with payment proof)

```bash
curl -s "https://cmc-x402-gateway.jordanjones0902.workers.dev/v1/cmc/quotes?symbol=BTC,ETH" \
  -H "X-PAYMENT: <your-x402-proof>"
```

### Python (with x402 SDK)

```python
import requests

gateway = "https://cmc-x402-gateway.jordanjones0902.workers.dev"

# Payment is handled automatically by the x402 SDK
response = requests.get(f"{gateway}/v1/cmc/quotes", params={"symbol": "BTC,ETH"})
data = response.json()
btc_price = data["data"]["BTC"]["quote"]["USD"]["price"]
```

### Hermes Agent

```yaml
# cron job or agent prompt
fetch cmc data:
  url: https://cmc-x402-gateway.jordanjones0902.workers.dev/v1/cmc/quotes
  params:
    symbol: BTC,ETH
  payment: auto  # Hermes signs x402 payment automatically
```

---

## Endpoints

| Endpoint | Description | Required Params | Price |
|----------|-------------|----------------|-------|
| `GET /v1/cmc/quotes` | Latest quotes by symbol | `symbol` (comma-separated) | $0.001 |
| `GET /v1/cmc/listings` | Top coins by market cap | (none, optional `limit`, `sort`) | $0.001 |
| `GET /v1/cmc/dex/pairs` | DEX pair quotes | `address` (token contract) | $0.001 |
| `GET /v1/cmc/trending` | Trending/movers | (none) | $0.001 |
| `GET /v1/cmc/search` | Coin info | `symbol` or `address` | $0.001 |

### Health / Info (free, no payment)

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service status + available endpoints |
| `GET /pricing` | Full pricing info + accepted networks |

---

## Payment Details

- **Protocol:** x402 v2 (B402 compatible on BSC)
- **Price:** 1000 microUSDC = $0.001 per call
- **Networks:**
  - **BNB Smart Chain** — B402 native (`USDC: 0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d`)
  - **Base** — x402 native (`USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Wallet:** `0x7ebff188f2Eba16518C02864589b1403a5d1296a`

### How Payment Works

1. Agent calls endpoint without payment → receives HTTP 402 with payment manifest
2. Agent's wallet pays the exact amount to the wallet address on the chosen network
3. Agent re-calls the endpoint with `X-PAYMENT: <proof>` header
4. Gateway proxies to CoinMarketCap → returns data

> **Note:** For MVP, payment proofs are accepted as-is. On-chain verification will be added in Phase 2.

---

## Architecture

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Agent       │────▶│  CMC x402 Gateway   │────▶│  CoinMarketCap   │
│  (Hermes,    │     │  (Cloudflare Worker)│     │  (Pro API)       │
│   Python,    │◀────│  x402 paywall +     │◀────│  $79/mo sub      │
│   cURL)      │     │  CMC proxy          │     │                  │
└──────────────┘     └─────────────────────┘     └──────────────────┘
                          │
                          │ pays $0.001
                          ▼
                     ┌──────────┐
                     │ USDC on  │
                     │ BSC/Base │
                     └──────────┘
```

**Key insight:** The agent pays per query in USDC. We hold the CMC API key and take the spread between our CMC subscription cost and per-query pricing. No API key management for consumers — payment IS authentication.

---

## Deployment

```bash
# Prerequisites
export CF_API_TOKEN="your-token"

# Deploy
npx wrangler deploy

# Monitor
npx wrangler tail

# Check health
curl https://cmc-x402-gateway.jordanjones0902.workers.dev/health
```

---

## Rate Limits

- **CMC free plan:** 10k calls/month (333/day)
- **Our pricing:** $0.001/call means ~$10/month at 10k calls
- **Upgrade path:** Upgrade CMC plan for higher limits → scales automatically

---

## License

MIT — GenTech Labs
