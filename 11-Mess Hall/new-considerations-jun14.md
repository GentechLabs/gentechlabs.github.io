## [ ] Travala Travel MCP — Agentic Travel Integration
- **Added:** 2026-06-14
- **Source:** u.today, The Block, Crypto Briefing — launched Jun 4, 2026
- **Link:** https://travala.com/developers
- **What:** World's first agentic AI travel protocol. AI agents search, book, and pay for 2.2M hotels (Marriott, Hilton, IHG) autonomously. Built on Base with x402 + gasless USDC. ~$0.01 per booking.
- **Why us:** 
  - They use **ERC-8004** for trust/reputation — we already built Agent Credit Score on this
  - They use **x402** — we already support this (Ampersend, Circle Gateway)
  - They use **MCP** — Hermes supports this natively
  - Connects to **GenTech Travels** dashboard — upgrade from static JSON to live booking
  - 10% cbBTC rebate for developers building on their protocol
- **Architecture:** ERC-7715 session keys + ERC-8004 (reputation) + x402 (payments)
- **Market:** $8B in 2026 → $3.5T by 2031
- **Status:** WATCH. Integrate MCP into GenTech Travels dashboard.
- **Next:** Test their MCP server, plan integration.

## [ ] WURK.FUN — Agent-to-Human Microtask Marketplace
- **Added:** 2026-06-11
- **Link:** https://wurk.fun/developer
- **API:** https://wurkapi.fun
- **What:** Microtask marketplace where AI agents hire humans. Payment IS authentication — no API key, no signup. x402 on Solana & Base, MPP on Tempo & Solana, USDC pay-per-request.
- **Why us:** Missing piece for Agent Economy. Our agents can hire humans for feedback, content moderation, product testing, social proof. We already support x402 (Ampersend), Solana (AgentBridge), Base (AgentBridge), MCP (Hermes).
- **Pricing:** $0.025/response for feedback, $0.025/unit for X likes/reposts, from $0.03/unit for followers.
- **Status:** HIGH PRIORITY. Direct integration opportunity. They have MCP skill available.
- **Blocker:** Needs Solana wallet with USDC ($1 total). Address: HasFooCfsJnia9Qo6Jjvk2aKVBTYKNRhiQjfR6tYMxGt
- **Next:** Fund wallet, test with $0.25 job (10 human responses on Cookbook dashboard).

## [ ] EarnFi — Microtask Marketplace (Secondary)
- **Added:** 2026-06-14
- **Link:** https://earnfi.fun
- **What:** Solana-based microtask platform. Community-driven version of WURK.FUN. Web3 jobs, contests, rewards.
- **Status:** TRACK. Second marketplace to plug into after WURK.FUN is validated.
