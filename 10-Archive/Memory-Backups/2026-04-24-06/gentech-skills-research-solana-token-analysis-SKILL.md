---
name: solana-token-analysis
category: research
description: Analyze Solana tokens using RugCheck API and alternative sources when browser-based trackers are blocked.
---

# Solana Token Analysis

## When to use
Whenever you need to analyze a Solana token — holder distribution, liquidity, risks, insider detection, LP locks.

## Problem
DexScreener, Birdeye, GMGN, Solscan, and RugCheck web all use aggressive Cloudflare bot detection. Browser-based scraping will almost always fail with "Performing security verification" or "Sorry, you have been blocked."

## Solution: RugCheck REST API
Use `curl` to hit the RugCheck API directly — no auth required:

```bash
curl -s "https://api.rugcheck.xyz/v1/tokens/<TOKEN_ADDRESS>/report"
```

This returns full JSON with:
- Token metadata (name, symbol, supply, decimals, authorities)
- Top holders with percentages
- RugCheck risk score (normalized 0-100, lower = riskier)
- Specific risk flags (single holder, correlation, concentration)
- Market/liquidity data (all pools, LP locks, DEX coverage)
- Insider network detection (clustered wallet graphs)
- Transfer fee config

## Parsing the response

Key fields to extract:
- `token.mintAuthority` / `freezeAuthority` — should be `null`
- `risks[]` — array of risk objects with `name`, `value`, `score`, `level`
- `score_normalised` — 0-100 normalized risk score
- `topHolders[].pct` — holder concentration
- `markets[]` — all DEX pools with liquidity amounts
- `rugged` — boolean, true = confirmed rug
- `transferFee.pct` — should be 0
- `insiderNetworks[]` — coordinated wallet clusters
- `graphInsidersDetected` — count of insider-connected wallets

## Report format
When presenting results, organize into:
1. **Token basics** — name, supply, price, holders, rugged status
2. **Security checks** — mint/freeze authority, transfer fees, metadata mutability
3. **RugCheck warnings** — scored risks with explanations
4. **Liquidity breakdown** — total liquidity, LP lock %, DEX distribution
5. **Insider detection** — cluster sizes and account counts
6. **Strategic assessment** — your analysis of the token

## Alternative data sources (if RugCheck API fails)
- Solana RPC: `curl` against public endpoints for account data
- Jupiter API: `https://api.jup.ag/price/v2?ids=<TOKEN_ADDRESS>` for price
- Birdeye API: requires key, but the API endpoint works when browser is blocked
- Birdeye x402 (NEW, Apr 2026): pay-per-request at $0.003/call via USDC, no account needed. Settlement via Coinbase CDP (Base) or PayAI (Solana). See bds.birdeye.so/blog for details.

## Limitations
- RugCheck API has rate limits (unknown exact threshold)
- Price data from RugCheck may lag real-time
- Insider detection is heuristic, not definitive
