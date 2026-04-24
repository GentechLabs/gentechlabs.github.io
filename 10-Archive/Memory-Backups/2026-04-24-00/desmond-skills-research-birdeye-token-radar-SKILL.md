---
name: birdeye-token-radar
description: Monitor new Solana token listings via Birdeye Data API with safety scoring and Telegram alerts
category: research
tags: [crypto, solana, birdeye, monitoring, safety, telegram]
---

# Birdeye Token Radar

Monitor new token listings on Solana via Birdeye Data Services API, score safety, and alert via Telegram.

## API Endpoints

Base URL: `https://public-api.birdeye.so`

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `GET /defi/v3/token/new_listing` | New tokens (params: `limit`, `meme_platform_enabled`, `time_from`) | `X-API-KEY` header + `x-chain: solana` |
| `GET /defi/token_security` | Safety signals (param: `address`) | Same |
| `GET /defi/v3/token/overview` | Price, mcap, liquidity (param: `address`) | Same |

**Auth headers:**
```
X-API-KEY: <your_key>
x-chain: solana
accept: application/json
```

**Note:** Docs at `docs.birdeye.so` may 404 or require login. Use BDS site (`bds.birdeye.so`) for API key setup. Endpoints were validated from community usage, not official docs.

## Safety Scoring (5 factors, 0-100)

| Factor | Points | Pass condition |
|--------|--------|----------------|
| Mint authority revoked | 25 | `mintAuthority` is null/None |
| Freeze authority revoked | 15 | `freezeAuthority` is null/None |
| LP locked or burned | 25 | `isLpTokenBurned` or `lpLocked` is true |
| Top 10 holder % < 50% | 20 | `top10HolderPercent` < 50 (< 70 gets 10) |
| Age > 1 hour | 15 | listing time > 1hr (> 15min gets 5) |

Grades: 🟢 80-100, 🟡 50-79, 🔴 0-49

## Rate Limiting

- Each token scan = ~3 API calls (1 new_listing + 1 security + 1 overview per token)
- Add `time.sleep(0.5)` between per-token calls
- 20 tokens × 3 calls = 60 calls per scan cycle

## Pitfalls

- **Web scraping fails:** Birdeye docs/auth pages block `web_extract` (AUTH_ERROR). Use browser tool if you need to read docs, but prefer known endpoint patterns from vault research.
- **402 responses:** x402 pay-per-request mode returns HTTP 402. In API key mode this shouldn't happen. If it does, the x402 payment flow needs client SDK integration.
- **`top10HolderPercent`** may be returned as string — cast to float before comparing.
- **`listingTime`** field name varies: check `liquidityAddedAt` and `createdAt`.

## BIP Competition Requirements

For Birdeye Build in Public competition:
- Minimum 50 API calls required
- Must build in public on X with `@birdeye_data` `#BirdeyeAPI`
- Judged on: Community Support, Product Utility, Technical Depth, Presentation (25% each)
- Sprint deadlines are weekly (Apr 18 – May 16, 2026)

## Project Location

Scaffold: `01-Projects/Birdeye-Token-Radar/`
