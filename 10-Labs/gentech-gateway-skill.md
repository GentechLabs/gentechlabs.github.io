---
name: gentech-x402-gateway
version: 1.0.0
description: >
  Pay-per-call intelligence APIs for agents over x402 (USDC). Use when the task
  needs token security, market price, wallet analysis, DeFi LP analytics, NFT
  search, agent discovery, lineage checks, deal tracking, or AI research.
  GenTech Labs' x402 gateway — 11 services, 5+ chains, HTTP 402 pay-per-call.
---

# GenTech x402 Gateway — machine money for agents

GenTech's gateway is **pay-per-call crypto/DeFi intelligence** over HTTP x402
(USDC). **11 services, 7 chains, $0.001–$0.10/call.** Every paid call quotes on
HTTP 402. No account, no API key, no monthly commitment — an agent that calls
twice pays $0.02; an agent that calls 1,000 times pays $10. Self-funding.

Agent one-liner: `set up https://api.gentechlabs.net/skill.md`

## Once connected, try these
- Get token security / rugcheck for an address
- Real-time market price for a symbol
- DeFi LP pool analysis + efficiency score
- Wallet portfolio (balances + USD value)
- NFT collection search
- Search the ERC-8004 agent registry
- On-demand AI research / analysis / summary

Every paid call returns HTTP 402 with pricing. Discovery is free.

## Setup (agent-native, no keys)
GenTech's gateway is a standard x402 v2 endpoint. A wallet-capable agent pays
in USDC. For a Solana or Base wallet:

```bash
# Add the gateway as an MCP (if using MCP):
claude mcp add gentx \
  -e GENTX_API_BASE_URL=https://api.gentechlabs.net \
  -e GENTX_PAYER_KEYPAIR=your-funded-usdc-wallet \
  -- npx -y @gentech/mcp-server@latest
```

Or just call the HTTP endpoints directly — the gateway serves a proper 402
challenge; your agent's wallet signs and retries with `Payment-Signature`.

Fund ≥ $1 USDC (Solana) or USDC on Base. Paid tools return 402 without it.

## Service catalog (11 services, all x402 v2)

| Service | Endpoint | What it does |
|---------|----------|--------------|
| token_security | `/v1/security/score/{address}` | Token risk + rugcheck |
| market_intelligence | `/v1/market/price/{symbol}` | Real-time price |
| agent_discovery | `/v1/agents/search` | ERC-8004 agent registry |
| defi_lp_analytics | `/v1/defi/lp/{address}` | LP efficiency via DexScreener |
| wallet_analysis | `/v1/wallet/portfolio/{address}` | Token balances + USD |
| nft_search | `/v1/nft/search` | NFT collection search (Solana) |
| treasury_defender | `/v1/defender/classify/{chainId}/{token}` | Airdrop/dust defense |
| lineage_guard | `/v1/lineage/guard?urn={urn}` | Data blast-radius guard |
| sie_inference | `/v1/sie/embeddings` | Self-hosted embeddings |
| deal_tracker | `/v1/deals/deals` | Game deals, price-watch, radar |
| agent_research | `/v1/agent/research?task={t}&topic={t}` | AI research/analysis/doc |

Prices range **$0.001–$0.10/call** depending on service. The 402 challenge
states the exact price for the service and network.

## Payment rails
- **Networks**: base, ethereum, avalanche, solana, bnb, arbitrum, algorand, xlayer
- **Protocol**: x402 v2 (PAYMENT-SIGNATURE / X-Payment headers)
- **Currency**: USDC
- **Facilitators**: PayAI / Dexter / GoPlausible (multi-facilitator failover)

## Discovery
- Full OpenAPI: `https://api.gentechlabs.net/openapi.json`
- x402 well-known: `https://api.gentechlabs.net/.well-known/x402`
- Bazaar manifest: `https://api.gentechlabs.net/.well-known/x402-bazaar`
- Docs: `https://api.gentechlabs.net/docs`

## How to drive GenTech gateway
1. Pick a service from the catalog above (or let the user's intent pick it).
2. Call the HTTP endpoint with no payment → get HTTP 402 + price.
3. Sign the payment with your wallet, retry with `Payment-Signature`.
4. Get your answer.

That's it — no API keys, no signup, no monthly commitment. Self-funding,
pay-per-call crypto + DeFi + AI intelligence.
