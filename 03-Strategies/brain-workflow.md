# Brain Dump Workflow

**Created:** 2026-04-20
**Owner:** YoYo (Strategies)

## Problem
Context window is limited. Important context gets lost between sessions. Need a reliable persistence system.

## Three-Layer System

### Layer 1: `memory` tool — Durable Facts (my brain)
- User preferences, environment quirks, stable conventions
- Things that prevent Jordan from having to repeat himself
- **Trigger:** After key corrections, new preferences, environment changes
- **Limit:** ~2,200 chars total — keep compact

### Layer 2: Obsidian Vault — Project Notes (shared brain)
- Research findings, token analyses, hackathon details, project decisions
- Lives at `/root/vaults/gentech/` — synced across sessions
- **Trigger:** After any substantial analysis or decision point
- **My folders:** `03-Strategies/`, `03-Projects/`

### Layer 3: Session Search — Recall Past Conversations (time machine)
- When Jordan says "remember when" or references something we did
- Search before asking Jordan to repeat himself
- **Trigger:** Start of any related task

## Simple Rule
Every time I produce something worth keeping (analysis, decision, preference learned):
1. Save to **memory** for durable facts
2. Save to **vault** for project context
3. Don't wait — save immediately

## Active Research Log

### 2026-04-20

**Birdeye Data Services — x402 Integration (Apr 16, 2026)**
- Birdeye now supports x402 pay-per-request API access
- Price: **$0.003 per request** via USDC (no subscription)
- Full REST API access — all endpoints, no account needed
- Settlement: instant (~2s) via Coinbase CDP (Base) or PayAI (Solana)
- Networks: Base + Solana
- Available data: real-time token data, trading data, wallet analytics, market discovery, token security, new listings
- Limitation: no WebSocket streaming under x402
- Primary use case: **AI agents** paying autonomously for data via their own wallets
- Same data powering Phantom, Backpack, Raydium, Bybit
- Also running 4-week BIP competition ($2,000 cash + $5,000 API credits) — 4 sprints Apr 18-May 16, Sprint 1 deadline Apr 25, 13 submissions so far, 500 USDC top prize + 2mo Premium Plus
- Doc links: docs.cdp.coinbase.com/x402, x402.org

**$DEXTER Token Analysis**
- 11 weekly hackathons, $131,849+ total prize pool
- Hack #5 (Kiro) live now, closes Apr 23 — $11,980 prizes, 0 submissions
- Upcoming: Zed, v0, Cursor, Stripe ($18,980), Blackbox, D-ID

**LayerZero DVN Risk**
- Dune analysis: 47% of 2,665 LayerZero OApps run 1/1 DVN (single point of failure)
- Follows KelpDAO hack
- 2/2 = 45%, 3/3+ = ~5%

**x402 on Solana**
- HTTP 402 payment protocol, built by Coinbase Dev Platform
- 37M+ transactions, 20K+ buyers/sellers, 70% monthly volume on Solana
- Ecosystem: Corbits, PayAI, x402scan, T54, CDP Wallet, Faremeter
- Solana: 400ms finality, $0.00025 tx costs

**$DEXTER Token (Dexter AI)**
- Contract: `EfPoo4wWgxKVToit7yX5VtXXBrhao4G8L7vrbKy6pump` (Solana)
- Price: ~$0.00093, Supply: 999.9B, Holders: 6,637
- RugCheck score: 41 (normalized), not rugged
- LP: 99.64% locked on Pump Fun AMM
- ⚠️ 20.69% single holder, 98 insider wallets detected
- Liquidity: ~$150K total across Meteora/Orca/Pump Fun
- Shipped x402 SDK v3.0 with first cross-bazaar search engine
