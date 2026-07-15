# Circle Agent Marketplace — Submission Package

## For Form at: https://forms.gle/7YFzvdmMcn1JH5tF6

---

### Seller Info
- **Company:** GenTech Labs
- **Website:** https://gentechlabs.net
- **Gateway URL:** https://gentech-x402-gateway.jordanjones0902.workers.dev
- **x402 Protocol:** ✅ Native support — returns 402 with Base/Solana/Avalanche/BNB/OKX USDC
- **Settlement Wallet (Base):** 0x7ebff188... (full address in vault/credentials)

---

### 5 Endpoints for Listing

**1. Token Risk Assessment**
| Field | Value |
|-------|-------|
| Name | Token Risk |
| Endpoint | `GET /api/token/risk?address=&chain=` |
| Price | $0.01 / call |
| Description | AI-powered token contract risk analysis. Evaluates liquidity locks, holder concentration, trading patterns, and known threat vectors across Base, Solana, Avalanche, BNB, and OKX. Returns risk score (0-100), severity level, and detailed findings. |
| Use case | Agents check token safety before trading, investing, or interacting with unknown contracts. |

**2. Market Intelligence — Price & Deals**
| Field | Value |
|-------|-------|
| Name | Market Intel |
| Endpoint | `GET /api/intel/search?q=` |
| Price | $0.005 / call |
| Description | Unified price comparison engine across games, entertainment, and digital goods. Finds the cheapest option for any product across multiple storefronts. Supports natural language queries. |
| Use case | Agents research pricing, find best deals, compare costs across vendors. |

**3. Wallet Analytics — Smart Money Tracking**
| Field | Value |
|-------|-------|
| Name | Wallet Analyzer |
| Endpoint | `GET /api/wallet/analyze?address=` |
| Price | $0.025 / call |
| Description | AI-powered wallet analysis with smart money tracking. Analyzes transaction history, P&L, portfolio composition, top trader identification, and behavioral pattern recognition. Supports multi-chain. |
| Use case | Agents analyze wallet performance, track smart money movements, evaluate trading strategies. |

**4. Game Intelligence**
| Field | Value |
|-------|-------|
| Name | Game Intel |
| Endpoint | `GET /api/games/search?q=` |
| Price | $0.005 / call |
| Description | Multi-platform game search engine with price comparison, release schedules, and patch note aggregation. Covers Steam, Epic, GOG, PlayStation, Xbox, and Nintendo stores. |
| Use case | Agents search games, compare prices, find deals, get release dates across gaming platforms. |

**5. NFT Search**
| Field | Value |
|-------|-------|
| Name | NFT Search |
| Endpoint | `GET /api/nft/search?q=` |
| Price | $0.005 / call |
| Description | Multi-chain NFT collection and asset search across Ethereum, Solana, Polygon, and other major ecosystems. Returns collection metadata, floor prices, volume data, and asset details. |
| Use case | Agents research NFT collections, check floor prices, find asset data across chains. |

---

### Notes
- All endpoints accept GET requests with query parameters
- Gateway returns standard x402 402 Payment Required with `X-Payment-Price` header
- Supports: Base, Solana, Avalanche, BNB Chain, OKX X Layer
- Multi-chain USDC settlement
- Gateway version 6.1.0 — Bazaar-indexed, x402 v2 compliant
- 99.9% uptime (Cloudflare Workers)
