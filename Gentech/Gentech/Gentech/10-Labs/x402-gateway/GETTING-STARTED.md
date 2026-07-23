# GenTech x402 Gateway — Getting Started

**16 AI-powered API endpoints. Multichain: pay per call via x402 USDC on Base, Solana, Avalanche, BNB, or OKX.**

---

## 🌐 Base URL

```
https://api.gentechlabs.net
```

---

## 📋 Prerequisites

1. **A wallet with USDC** on any supported chain:
   - Base mainnet (recommended — cheapest gas)
   - Solana mainnet
   - Avalanche C-Chain
   - BNB Chain
   - OKX X Layer

2. **An x402-compatible agent** that can:
   - Sign x402 payment messages
   - Verify payment receipts
   - Retry failed payments

3. **Testnet USDC** (for testing):
   - Base Sepolia: [USDC faucet](https://faucet.quicknode.com/base)
   - Solana Devnet: [Solfaucet](https://solfaucet.com/)
   - Avalanche Fuji: [Avalanche faucet](https://faucet.avax.network/)

---

## 💰 Pricing

| Tier | Price | Endpoints |
|------|-------|-----------|
| **Micro** | $0.001 | News, details, trailers |
| **Standard** | $0.005 | Search, cheapest, NFT, shipping |
| **Premium** | $0.01 | Airdrops, AI token risk |
| **Pro** | $0.025 | AI wallet analytics |
| **Ultra** | $0.10 | AI agent scan |

**All endpoints:**
- `/api/games/search` — $0.005 — Game search across multiple platforms
- `/api/games/cheapest` — $0.005 — Cheapest game price finder
- `/api/games/news` — $0.001 — Game news and patch notes
- `/api/games/release` — $0.001 — Game release info and dates
- `/api/movies/search` — $0.005 — Movie search
- `/api/movies/cheapest` — $0.005 — Cheapest movie watch option
- `/api/movies/details` — $0.001 — Movie details (cast, studio, genres)
- `/api/movies/trailers` — $0.001 — Movie trailers (YouTube)
- `/api/intel/search` — $0.005 — Unified search across games + movies
- `/api/intel/cheapest` — $0.005 — Cheapest across all categories
- `/api/airdrops/check` — $0.01 — Airdrop eligibility checker
- `/api/wallet/analyze` — $0.025 — AI-powered wallet analytics
- `/api/nft/search` — $0.005 — NFT search and collection data
- `/api/token/risk` — $0.01 — AI-powered token risk assessment
- `/api/shipping/track` — $0.005 — Multi-carrier shipping tracker
- `/api/agentscan` — $0.10 — AI-powered agent reconnaissance

---

## 🔗 Supported Networks

| Network | Chain ID | USDC Address | Recommended For |
|---------|----------|--------------|-----------------|
| **Base** | 8453 | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | ✅ Best — lowest gas fees |
| **Solana** | 5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | Good — fast but higher fees |
| **Avalanche** | 43114 | `0x9702230A8Ea53601f5cD2dc00fDBcE2c3Ed7B5E9` | Alternative |
| **BNB Chain** | 56 | `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` | Alternative |
| **OKX X Layer** | 196 | `0x8b1c7B3aD3a26C5EB0dD8b4D0CDbB56c8B33c5B8` | Alternative |

**Receiving Wallet:**
- EVM chains: `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
- Solana: `71Y3H36eb2WRGseYM9GwinjNawfMfAUbcof5eeWGoGSA`

---

## 🚀 Quick Start

### Step 1: Check Gateway Health

```bash
curl https://api.gentechlabs.net/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "gentech-x402-gateway",
  "version": "6.0.0",
  "networks": ["base", "solana", "avalanche", "bnb", "okx"],
  "token": "USDC",
  "multichain": true,
  "ai_powered": true,
  "paid_endpoints": 16,
  "facilitator": "x402.org",
  "bazaar_indexed": true
}
```

---

### Step 2: Get Pricing

```bash
curl https://api.gentechlabs.net/pricing
```

---

### Step 3: Try a Paid Endpoint (Without Payment)

You'll get a `402 Payment Required` response:

```bash
curl https://api.gentechlabs.net/api/games/search?q=zelda
```

Expected response:
```json
{
  "error": "payment_required",
  "message": "Payment required to access this endpoint",
  "payment_options": {
    "x402": {
      "networks": ["base", "solana", "avalanche"],
      "token": "USDC",
      "amount": 5000,
      "resource": "https://api.gentechlabs.net/api/games/search"
    }
  }
}
```

---

### Step 4: Call With x402 Payment

Here's how to call the endpoint with x402 payment on Base:

```bash
# 1. Create x402 payment message (example using an x402 client)
# This step requires an x402 SDK or manual x402 signing

# 2. Call the endpoint with x402 payment in headers
curl -X GET "https://api.gentechlabs.net/api/games/search?q=zelda" \
  -H "x402-payment: <signed-payment-message>" \
  -H "Content-Type: application/json"
```

**For a full working example, see [EXAMPLES.md](./EXAMPLES.md).**

---

## 📚 Endpoints Reference

### AI-Powered Endpoints

#### `/api/token/risk` — Token Risk Assessment
**Price:** $0.01 | **Method:** GET

**Parameters:**
- `address` — Token contract address
- `chain` — Blockchain (default: `base`)

**Example:**
```bash
curl "https://api.gentechlabs.net/api/token/risk?address=0x4200000000000000000000000000000000000042&chain=base"
```

**Response:**
```json
{
  "success": true,
  "endpoint": "token/risk",
  "ai_powered": true,
  "address": "0x4200000000000000000000000000000000000042",
  "chain": "base",
  "analysis": {
    "risk_score": 35,
    "risk_level": "low",
    "factors": [
      "Verified contract on Base",
      "High liquidity",
      "Established protocol"
    ],
    "recommendation": "caution",
    "summary": "Lower risk profile due to verified status and high liquidity, but always DYOR."
  }
}
```

---

#### `/api/wallet/analyze` — Wallet Analytics
**Price:** $0.025 | **Method:** GET

**Parameters:**
- `address` — Wallet address
- `chain` — Blockchain (default: `base`)

**Example:**
```bash
curl "https://api.gentechlabs.net/api/wallet/analyze?address=0x7ebff188f2Eba16518C02864589b1403a5d1296a&chain=base"
```

---

#### `/api/agentscan` — Agent Reconnaissance
**Price:** $0.10 | **Method:** GET

**Parameters:**
- `target` — Agent/service URL or name (default: `self`)

**Example:**
```bash
curl "https://api.gentechlabs.net/api/agentscan?target=openai.com"
```

---

#### `/api/intel/search` — Unified Search
**Price:** $0.005 | **Method:** GET

**Parameters:**
- `q` — Search query

**Example:**
```bash
curl "https://api.gentechlabs.net/api/intel/search?q=blockchain%20games%202026"
```

---

#### `/api/airdrops/check` — Airdrop Eligibility
**Price:** $0.01 | **Method:** GET

**Parameters:**
- `address` — Wallet address

**Example:**
```bash
curl "https://api.gentechlabs.net/api/airdrops/check?address=0x7ebff188f2Eba16518C02864589b1403a5d1296a"
```

---

### Gaming Endpoints

#### `/api/games/search` — Game Search
**Price:** $0.005 | **Method:** GET

**Parameters:**
- `q` — Search query

**Example:**
```bash
curl "https://api.gentechlabs.net/api/games/search?q=elden%20ring"
```

---

#### `/api/games/cheapest` — Cheapest Game Prices
**Price:** $0.005 | **Method:** GET

**Parameters:**
- `q` — Game title

**Example:**
```bash
curl "https://api.gentechlabs.net/api/cheapest?q=zelda%20breath%20of%20the%20wild"
```

---

#### `/api/games/news` — Gaming News
**Price:** $0.001 | **Method:** GET

---

#### `/api/games/release` — Release Info
**Price:** $0.001 | **Method:** GET

---

### Movies Endpoints

#### `/api/movies/search` — Movie Search
**Price:** $0.005 | **Method:** GET

**Parameters:**
- `q` — Search query

**Example:**
```bash
curl "https://api.gentechlabs.net/api/movies/search?q=dune%202"
```

---

#### `/api/movies/cheapest` — Cheapest Watch Options
**Price:** $0.005 | **Method:** GET

---

#### `/api/movies/details` — Movie Details
**Price:** $0.001 | **Method:** GET

---

#### `/api/movies/trailers` — Movie Trailers
**Price:** $0.001 | **Method:** GET

---

### Other Endpoints

#### `/api/nft/search` — NFT Search
**Price:** $0.005 | **Method:** GET

---

#### `/api/shipping/track` — Shipping Tracker
**Price:** $0.005 | **Method:** GET

**Parameters:**
- `tn` — Tracking number

**Example:**
```bash
curl "https://api.gentechlabs.net/api/shipping/track?tn=1Z999AA10123456784"
```

---

## 🛠️ Free Endpoints

These endpoints are free (no payment required):

- `GET /health` — Gateway health check
- `GET /pricing` — Full pricing information
- `GET /openapi.json` — OpenAPI specification
- `GET /.well-known/agent.json` — Agent-to-Agent (A2A) agent card
- `GET /.well-known/x402` — x402 discovery
- `GET /.well-known/x402-bazaar` — x402 Bazaar manifest
- `GET /` — Root endpoint with links

---

## 🔐 Authentication

No API keys required. Authentication is handled via x402 payment verification.

**How it works:**
1. Client creates x402 payment message
2. Signs with wallet
3. Includes in `x402-payment` header
4. Gateway verifies via x402 facilitator
5. If payment valid → execute endpoint
6. Settle payment automatically

---

## 📊 OpenAPI Spec

Full OpenAPI specification available at:

```
https://api.gentechlabs.net/openapi.json
```

Import into Postman, Insomnia, or any API client for auto-generated documentation.

---

## 🔗 Discovery Endpoints

### Agent-to-Agent (A2A)

```bash
curl https://api.gentechlabs.net/.well-known/agent.json
```

### x402 Discovery

```bash
curl https://api.gentechlabs.net/.well-known/x402
```

### x402 Bazaar Manifest

```bash
curl https://api.gentechlabs.net/.well-known/x402-bazaar
```

---

## 🐛 Error Codes

| Status | Code | Meaning |
|--------|------|---------|
| 200 | `ok` | Success |
| 400 | `bad_request` | Invalid parameters |
| 402 | `payment_required` | No x402 payment provided |
| 404 | `not_found` | Endpoint not found |
| 429 | `rate_limited` | Too many requests (60/min) |
| 500 | `internal_error` | Server error |

---

## 🧪 Testing

### Testnet URLs

Coming soon — testnet versions of all endpoints.

Until then, use small amounts ($0.001 = 1,000 USDC) on mainnet for testing.

---

## 💬 Support

- **GitHub:** https://github.com/ProtoJay4789/gentech-vault
- **X/Twitter:** [@GenTechLabs](https://x.com/GenTechLabs)
- **Email:** hello@gentechlabs.net

---

## 📜 License

GenTech Labs x402 Gateway — 2026

All endpoints require valid x402 payment. Unauthorized use is monitored.

---

**Last Updated:** July 7, 2026
**Version:** 6.0.0