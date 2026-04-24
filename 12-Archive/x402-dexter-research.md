# x402 Protocol & Dexter AI — Research

**Date:** 2026-04-21
**Source:** x402.org, ecosystem page, forwarded @dexteraisol announcement

## Protocol Overview
- **x402** = Open standard for HTTP-native micropayments using `402 Payment Required`
- Backed by **Coinbase Developer Platform**, co-founded with **Cloudflare**
- Production-ready, open-source, audited

## Ecosystem Stats (Last 30 Days — Apr 2026)
- 75.41M transactions
- $24.24M volume
- 94.06K buyers
- 22K sellers

## Key Adopters
Stripe, AWS, Cloudflare, Alchemy, Nansen, Messari, Vercel, World (Worldcoin)

## Dexter AI (x402 Facilitator)
- **Type:** Facilitator (not a bazaar/marketplace — sits between standard and marketplaces)
- **Networks:** Solana, Solana Devnet, Base, Base Sepolia
- **Payment Schemes:** `exact`, `bridge`
- **Assets:** SPL tokens, EIP-3009, Token-2022
- **Capabilities:** Verify Payments, Settle Payments, Endpoint List Resources
- **Base URL:** x402.dexter.cash
- **Website:** dexter.cash
- **SDK:** `npm i @dexterai/x402` (v3.0)
- **MCP integration:** Works with ChatGPT, Claude, Telegram, any MCP client
- **Cross-chain bridge** built into payment scheme

## x402 SDK v3.0 (Dexter) — Updated Apr 21
- First genuine x402 search engine
- Discovers resources across entire x402 ecosystem
- Breaks out of single-bazaar walled gardens
- Cross-platform resource discovery
- **8 chains**: Solana, Base, Polygon, Avalanche, Arbitrum, Optimism, BSC, SKALE
- **32.89M settlements / $5.76M USDC / 316 active sellers**
- **Free facilitator** — zero fees, settlement = distribution strategy
- **Session-based payments (MPP on Solana)** — open session, batch calls, single on-chain settlement
- **OpenDexter** — MCP runtime for agents (Claude, ChatGPT, Cursor, any MCP client)
- **x402gle** — real-time search across all facilitators/resources/chains
- **Instinct** (coming soon) — ad network in settlement receipts
- SDK: wraps `fetch` client-side, Express middleware server-side
- GitHub: Dexter-DAO/dexter-x402-sdk
- Token: $DEXTER on Solana (Jupiter: EfPoo4wWgxKVToit7yX5VtXXBrhao4G8L7vrbKy6pump)

## Relevance to GenTech
- **Solana + Base** dual-chain support matches our stack
- `bridge` payment scheme aligns with PaymentRouter contract patterns
- MCP integration enables agent-to-agent payments
- Token-2022 support for advanced Solana token features
- Agent payments: autonomous API access without API keys

## Useful Links
- Protocol: https://x402.org
- Docs: https://docs.x402.org
- GitHub: https://github.com/x402-foundation/x402
- Dexter: https://dexter.cash
- Ecosystem: https://x402.org/ecosystem
