# GenTech Labs API Worker

## x402 Pay-Per-Call Backend

### Deployment

```bash
# Install dependencies
npm install

# Local development
npm run dev

# Deploy to production
npm run deploy
```

### Endpoints

All endpoints require x402 payment proof in headers:

```
X-Payment-Proof: <base64-encoded-payment-signature>
```

Or Q402 token:

```
X-Payment-Token: <q402-token>
```

### Pricing

| Endpoint | Price (USDC) |
|----------|--------------|
| /v1/games/search | $0.005 |
| /v1/games/cheapest | $0.005 |
| /v1/games/{id}/news | $0.001 |
| /v1/games/{id}/release | $0.001 |
| /v1/movies/search | $0.005 |
| /v1/movies/cheapest | $0.005 |
| /v1/movies/{id}/details | $0.001 |
| /v1/movies/{id}/trailers | $0.001 |
| /v1/intel/search | $0.005 |
| /v1/intel/cheapest | $0.005 |
| /v1/airdrops/check | $0.01 |
| /v1/wallet/analyze | $0.025 |
| /v1/nft/search | $0.005 |
| /v1/score/{mint} | $0.01 |

### Example Usage

```bash
curl https://gentechlabs.net/v1/games/search?q=cyberpunk \
  -H "X-Payment-Proof: <your-payment-proof>"
```

### Development

The Worker is built with TypeScript and Cloudflare Workers runtime.