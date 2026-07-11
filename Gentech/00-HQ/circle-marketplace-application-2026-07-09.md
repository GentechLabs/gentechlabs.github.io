# Circle Agent Marketplace — Seller Application Prep
> **URL:** https://forms.gle/7YFzvdmMcn1JH5tF6
> **Requires:** Google sign-in
> **Prepared:** 2026-07-09

---

## What We're Listing

**Seller Name:** GenTech Labs
**Website:** https://gentechlabs.net
**Contact Email:** *(Jordan's email)*
**Wallet Address (Base):** *(your Base wallet where USDC settlements go)*

### Services

| # | Service Name | Endpoint | Price | Description |
|---|-------------|----------|-------|-------------|
| 1 | **Crypto Quote** | `GET /v1/quote/{symbol}` | $0.001 | Real-time BTC, ETH, SOL price quotes from CoinMarketCap |
| 2 | **Top Listings** | `GET /v1/listings` | $0.001 | Top 100 tokens by market cap |
| 3 | **Token Search** | `GET /v1/search/{symbol}` | $0.001 | Token metadata, description, tags, logo |
| 4 | **DEX Pairs** | `GET /v1/dex/{symbol}` | $0.001 | DEX pair data — price, volume, liquidity across exchanges |
| 5 | **Trending** | `GET /v1/trending/{kind}` | $0.001 | Gainers, losers, most visited, latest |

### Implementation

We use the `@circle-fin/x402-batching` SDK:

```js
import { createGatewayMiddleware } from "@circle-fin/x402-batching/server";
const gateway = createGatewayMiddleware({
  sellerAddress: "0xYOUR_WALLET",  // Base wallet
});

app.get("/v1/quote/:symbol", gateway.require("$0.001"), handler);
app.get("/v1/listings", gateway.require("$0.001"), handler);
app.get("/v1/search/:symbol", gateway.require("$0.001"), handler);
app.get("/v1/dex/:symbol", gateway.require("$0.001"), handler);
app.get("/v1/trending/:kind", gateway.require("$0.001"), handler);
```

### Why This Matters

Circle's marketplace has 41 services and 640 endpoints. We add 5 more. But more importantly — we're already shipping x402, we're already open source, and our Agent Kit is designed to be discovered by agents. Listing on Circle's marketplace is another distribution channel for the same tools.

---

## Quick Reference

| What | Link |
|------|------|
| Seller application | https://forms.gle/7YFzvdmMcn1JH5tF6 |
| Seller docs | https://developers.circle.com/gateway/nanopayments/quickstarts/seller |
| Marketplace | https://agents.circle.com/services |
| Our GitHub | https://github.com/ProtoJay4789/genTech-agent-kit |
| Our website | https://gentechlabs.net |