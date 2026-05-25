# GMGN.AI — Meme Token Trading Terminal + Agent API

**Date:** 2026-05-25
**Status:** 📁 Filed for later
**Source:** https://gmgn.ai / https://docs.gmgn.ai
**Relevance:** AAE market data layer, token security, trade execution

## What It Is

Multi-chain meme token trading terminal with an Agent API built for AI agents. Real-time on-chain data, security checks, smart money tracking, and swap execution.

## Key Features

- **Token data** — real-time prices, contract security, liquidity pool status, top holders/traders
- **Market data** — candlestick data (1m to 1d), trending tokens
- **Portfolio** — wallet holdings, PnL tracking, transaction history
- **Trading** — swap execution via GMGN hosted wallet (no local private key for queries)
- **Security** — insider/sniper detection, bundled wallet ID, honeypot checks

## Chains

Solana, BSC, Base (ETH in progress)

## Agent Integration

- **MCP tools** — `npx skills add GMGNAI/gmgn-skills`
- **CLI** — `npx gmgn-cli`
- **Skills** — `/gmgn-token`, `/gmgn-market`, `/gmgn-swap`
- **API Key** — get at gmgn.ai/ai, upload public key

## API Key Setup

1. Generate key pair (asymmetric)
2. Go to https://gmgn.ai/ai
3. Upload public key, get API key
4. Add to .env: `GMGN_API_KEY=...` and `GMGN_PRIVATE_KEY=...`

## Integration Options for AAE

1. Real-time market data for trading game
2. Token security checks (overlap with Rugcheck v2)
3. Smart money tracking for "rep-as-currency"
4. Trade execution rails

## Next Steps

- [ ] Get API key when ready to build
- [ ] Install MCP tools and test
- [ ] Map to AAE integration stack
