# x402 on Solana — Ecosystem Research

**Date:** April 20, 2026
**Source:** https://solana.com/x402
**Status:** Active research

---

## What is x402?
Internet-native payment standard for AI agents. Named after HTTP 402 "Payment Required" status code. Enables machine-to-machine microtransactions — agents pay APIs per-use automatically.

## Key Stats (as of Apr 2026)
- **37M+** transactions on Solana
- **20K+** buyers and sellers
- **70%** monthly volume on Solana (dominant chain)

## Ecosystem Players

| Project | What They Do | Link |
|---------|-------------|------|
| x402.org | Foundation — docs, GitHub, resources | https://x402.org |
| Corbits | Pay-per-use API endpoints via x402 | https://corbits.dev |
| PayAI | Solana facilitator — microtransactions + agent marketplace | https://payai.network |
| x402scan | Explorer — tracks servers, transactions, usage | https://x402scan.com |
| T54 | Trust layer — identity, verification, risk mgmt | https://t54.ai |
| CDP Wallet | Coinbase embedded wallet solution | https://docs.cdp.coinbase.com |
| Dexter AI | SDK v3.0 — first x402 search engine ($DEXTER token) | https://dexteraisol |
| Birdeye Data | Pay-per-request API ($0.003/req) — full REST API, no subscription | https://bds.birdeye.so |

## Toolkit / Dev Resources
- **x402 Docs:** https://x402.gitbook.io/x402
- **Faremeter:** OSS framework for agentic payments (https://docs.corbits.dev/quickstart)
- **PayAI:** Sell services with x402 (https://docs.payai.network/x402/servers/introduction)
- **x402Secure (T54):** Security SDK layer (https://t54.ai/x402-secure)
- **Privy:** Wallet integration (https://x402.gitbook.io/x402/guides/mcp-server-with-x402)
- **MCP + x402:** Payment-gate MCP servers per-call
- **Solana Templates:** https://solana.com/developers/templates

## Dexter AI — x402 SDK v3.0
- **Announced:** Apr 15, 2026
- **What's new:** First genuine x402 search engine — cross-marketplace resource discovery
- **Install:** `npm i @dexterai/x402`
- **Token:** $DEXTER on Solana (`EfPoo4wWgxKVToit7yX5VtXXBrhao4G8L7vrbKy6pump`)
- **Dev:** @BranchM

## Why It Matters for Gentech
- Our multi-agent setup (Gentech, YoYo, DMOB, Desmond) could transact autonomously via x402
- MCP + x402 = monetize any tool server per-call
- x402 search engine = agents discover services to pay for
- Solana-native = aligns with our blockchain focus (Base + Solana)

## Birdeye Data Services — x402 Integration (Apr 16, 2026)
**Source:** https://bds.birdeye.so/blog/detail/introducing-x402-on-birdeye-data-pay-per-request-api-access

### Pricing & Specs
- **$0.003 per request** — full REST API, no subscription
- Payment: USDC via x402
- Settlement: Instant (~2s) via Coinbase CDP (Base) or PayAI (Solana)
- Networks: Base, Solana
- Limitation: No WebSocket streaming under x402

### What You Can Access
- Real-time token data (prices, market cap, volume, liquidity) — Solana, Sui, EVM chains
- Trading data (live trades, OHLCV, buy/sell ratios, top traders)
- Wallet analytics (portfolio tracking, tx history, PnL)
- Market discovery (trending tokens, new listings, gainers/losers)
- Token security (safety signals, metadata, holder distribution)
- New listings with creation timestamps — ideal for meme/early-entry agents

### Target Users
1. **AI agents** — autonomous data queries, pay from own wallet, no human in loop
2. **Developers prototyping** — test with real data before committing to subscription
3. **Variable usage apps** — no need to guess subscription tier

### x402 Payment Flow
1. Client sends API request
2. Server responds `402 Payment Required` + payment instructions
3. Client signs USDC payment
4. Server verifies via on-chain facilitator → returns data

### Why This Matters
Birdeye powers Phantom, Backpack, Raydium, and Bybit. Full API at $0.003/request via x402 = premium on-chain data for our agents without subscriptions. ### Birdeye Build in Public Competition ($7,000 total)
- **4-week sprints** (Apr 18 – May 16, 2026) — new winners each week
- $2,000 cash + $5,000 enterprise API credits
- Sprint 1: 500 USDC for 1st + Premium Plus plan
- Judging: Community Support, Product Utility, Technical Depth, Presentation
- Minimum 50 API calls, submit via Superteam Earn
- Source: https://superteam.fun/earn/listing/birdeye-data-4-week-bip-competition-sprint-1

## Potential Hackathon Opportunities
- ElevenLabs ElevenHacks (11 weekly hackathons, $74k+ total prizes)
- Solana-specific x402 hackathons (check x402.org)
- Birdeye Build in Public competition ($7,000 rewards)

## Next Steps
- [ ] **URGENT:** Birdeye BIP Sprint 1 — submit by Apr 25 (4 days left!)
- [ ] Get Birdeye API key at bds.birdeye.so
- [ ] Scope a quick build: token radar, meme discovery, or trending alert bot
- [ ] Test Birdeye x402 API with a simple agent script
- [ ] Deep dive MCP + x402 integration docs
- [ ] Check if any of our protocols touch LayerZero (security audit)
- [ ] Evaluate Dexter SDK for agent-to-agent payments
- [ ] Map x402 to our AgentEscrow architecture
