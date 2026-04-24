# x402 Protocol Research — AAE Integration

**Date:** 2026-04-20
**Source:** solana.com/x402, x402.gitbook.io, github.com/x402-foundation/x402

---

## What is x402?

Open payment protocol built on **HTTP 402 "Payment Required"** status code. Developed by **Coinbase Development Platform**. Licensed under **Apache-2.0**.

Enables any API or web service to require payment *before* serving content. No accounts, sessions, or credential management needed.

## Why Solana?

- **400ms finality**
- **$0.00025 transaction costs**
- **35M+ transactions** processed via x402
- **$10M+ volume** and growing
- **70% monthly volume** on Solana vs other chains
- **20K+ buyers/sellers** in ecosystem

## Protocol Flow

1. Buyer requests resource from server
2. Server responds with `402 Payment Required` + payment instructions
3. Buyer prepares and submits payment payload
4. Server verifies/settles via x402 facilitator (`/verify` and `/settle` endpoints)
5. If valid, server provides the resource

## GitHub Repository

- **Repo:** `x402-foundation/x402` (forked by Coinbase at `coinbase/x402`)
- **Stars:** 6,000+
- **Forks:** 1,500+
- **Languages:** TypeScript (primary), Python, Go, Java

### TypeScript Packages

| Package | Purpose |
|---------|---------|
| `core` | Core protocol logic |
| `http` | HTTP middleware/facilitator client |
| `mcp` | MCP (Model Context Protocol) integration |
| `extensions` | Framework adapters (Express, Fastify, Hono, etc.) |
| `mechanisms` | Payment mechanisms (Solana, EVM, etc.) |
| `legacy` | Backward compatibility |

## Ecosystem

| Project | Description | Link |
|---------|-------------|------|
| **x402.org** | Foundation & docs | x402.org |
| **Corbits** | Pay-per-use API platform | corbits.dev |
| **Faremeter** | OSS framework for agentic payments | docs.corbits.dev |
| **PayAI** | Solana facilitator + agent marketplace | payai.network |
| **x402scan** | Transaction explorer | x402scan.com |
| **T54** | Trust layer (identity, verification, risk) | t54.ai |
| **CDP Wallet** | Coinbase embedded wallets | docs.cdp.coinbase.com |
| **Privy** | Wallet integration | privy.io |
| **Dexter AI** | x402 search engine SDK v3.0 | npm @dexterai/x402 |

## Key Supporters

- **Cloudflare** — supports x402
- **Google** — supports x402
- **Vercel** — supports x402

## Use Cases (AAE-Relevant)

- AI agents autonomously paying for API access, data feeds, compute
- Developer APIs monetized per-request (no subscriptions)
- Micropayments for content, model inference
- Agent marketplaces where autonomous buyers/sellers transact 24/7
- MCP servers payment-gated with x402

## Dexter AI x402 SDK v3.0

- **Package:** `@dexterai/x402` (npm)
- **Key feature:** First genuine x402 search engine
- **Solves:** Discovery layer — not locked to one bazaar, no walled gardens
- **Token:** `$DEXTER` on Solana (`EfPoo4wWgxKVToit7yX5VtXXBrhao4G8L7vrbKy6pump`)

## AAE Integration Map

| x402 Layer | AAE Layer | Status |
|------------|-----------|--------|
| Payment protocol | Autonomous commerce | Research |
| Solana settlement | $TECH token / Solana infra | Existing |
| MCP integration | MCP servers | Need to build |
| Service discovery | Agent capability registry | Dexter SDK or custom |
| Trust/identity | Agent authentication | T54 or custom |

## Production Integration: Birdeye Data Services

**Launched:** 2026-04-16
**Pricing:** $0.003/request (USDC via x402)
**Settlement:** ~2s on-chain (Base via CDP, Solana via PayAI)
**Access:** Full REST API — all endpoints, no subscription

### Available Data
- Real-time token prices, market cap, volume, liquidity (Solana, Sui, EVM)
- Live trades, OHLCV candles, buy/sell ratios, top traders
- Wallet analytics — portfolio, tx history, PnL
- Market discovery — trending, new listings, gainers/losers
- Token security — safety signals, metadata, holder distribution
- New token listings with creation timestamps

### Key Quotes
> "AI agents. This is the primary use case. Autonomous agents need data to make decisions... an AI agent can query Birdeye's APIs and pay for each request autonomously using its own wallet. No human in the loop."

### AAE Impact
- YoYo (Strategies agent) can query Birdeye autonomously instead of relying on CMC cron jobs
- $0.003/call = 1,000 calls for $3. Very viable for agent economics.
- Reference implementation for how to integrate x402 as an API provider
- No WebSocket under x402 — need to use REST polling or subscribe separately

### Links
- Blog: https://bds.birdeye.so/blog/detail/introducing-x402-on-birdeye-data-pay-per-request-api-access
- x402 docs: https://docs.cdp.coinbase.com/x402/docs/welcome

## Agentic Market (Coinbase) — Live x402 Marketplace

**URL:** agentic.market
**Volume:** $49M+ lifetime, $424K/day
**Transactions:** 1.88M in 30 days
**Buyers/Sellers:** 80K / 13K
**Services:** 68+ (all pay-per-request, zero API keys)

### Key Services for AAE
| Need | Service | Cost/tx |
|------|---------|---------|
| LLM inference | Anthropic, OpenAI, DeepSeek, Groq | $0.001 |
| Crypto data | CoinGecko, CoinMarketCap, Nansen, Messari | $0.01-0.22 |
| Web search | Perplexity, Firecrawl, Exa | $0.004-0.022 |
| Browser | Browserbase, Hyperbrowser | $0.002-0.003 |
| Image gen | FAL (fal.ai) | $0.012 |
| TTS/STT | Deepgram | $0.170 |
| Social | X API | $0.007 |
| Trading | Mycelia Signal | $0.005 |

### Install
`npx skills add coinbase/agentic-wallet-skills`

### AAE Impact
- Replaces CMC cron jobs with direct agent queries
- Eliminates API key management
- YoYo can query CoinGecko/Nansen/Messari directly
- DMOB can use Anthropic/OpenAI inference per-request
- Desmond can use Deepgram for TTS/STT
- All via agent wallets, no human in loop

## Apolo × GenLayer — Trustless Escrow

**Live on BNB mainnet.** Built during GenLayer Builders Hackathon.
Flow: x402 → Apolo escrow → GenLayer adjudicates → BNB settles
"Funds lock automatically. AI verifies the condition. Settlement executes without human approval."

## GenLayer Skills (Claude Code Plugin)

**Repo:** genlayerlabs/skills
**Plugins:** genlayer-dev (contract writing, linting, testing), genlayernode (validator setup/management)
**Install:** `/plugin marketplace add genlayerlabs/skills`

## BuildersClaw — Agent Hackathon Platform

**By:** GenLayer. Agents join real hackathons, ship code, win prizes. Verified onchain via Optimistic Democracy.

## GenLayer Passive Income Analysis

**Date:** 2026-04-21
**Source:** docs.genlayer.com (staking, economic model, validators, slashing pages)
**Network:** Bradbury Testnet | RPC: https://rpc-bradbury.genlayer.com | Chain ID: 4221

### Overview

GenLayer uses **Optimistic Democracy** — a Delegated Proof of Stake consensus where validators run LLMs to reach consensus on subjective decisions. Passive income comes from staking as a validator or delegator.

### Two Passive Income Plays

#### 1. DELEGATOR (Low barrier, truly passive)

| Parameter | Value |
|-----------|-------|
| Min stake | 42 GEN |
| Infrastructure | None required |
| Rewards | ~90% of pro-rata (validator takes 10% ops fee) |
| Unbonding | 7 epochs (~7 days, epochs = 1 day) |
| Risk | Slashing shared with validator |

**How it works:**
- Delegate GEN tokens to a validator via smart contract
- Validator runs infrastructure + LLM, you earn passively
- Rewards auto-compound via shares system (stake_per_share ratio increases)
- No manual claiming needed — compounding is automatic

**Reward sources:**
- Transaction fees (variable, depends on network usage)
- Inflation rewards (starts at **15% APR**, decays to **4% APR** over time)

**Selection weight formula:**
```
Weight = (0.6 × Self_Stake + 0.4 × Delegated_Stake)^0.5
```
Square-root damping = smaller validators get better $/GEN efficiency. Spread delegation across smaller validators for optimal returns.

#### 2. VALIDATOR (Higher barrier, active)

| Parameter | Value |
|-----------|-------|
| Min stake | 42,000 GEN |
| Infrastructure | Node + LLM API (ongoing cost) |
| Ops fee | 10% of all delegator rewards |
| Max active | 1,000 validators |
| Critical | Must call `validatorPrime()` every epoch |

**Revenue split per epoch:**
- 75% → Stake pool (validators + delegators, proportional)
- 10% → Validator owner (ops fee)
- 10% → Developers
- 5% → DeepThought AI-DAO reserve

**Validator costs to consider:**
- LLM API calls for consensus (variable, depends on tx volume)
- Server/node infrastructure
- GEN capital lockup (opportunity cost)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Still testnet — no real token value | Confirmed | High | Get positioned now, evaluate at mainnet |
| Inflation-funded yields (low real yield) | 60% | Medium | Monitor tx volume growth as signal |
| Slashing from validator misbehavior | 20% | Medium | Pick validators with track record |
| LLM costs eat validator profits | 40% | Medium | Wait for mainnet economics |
| 7-day unbonding = illiquidity | Certain | Low | Only stake what you can lock |

### Scenario Analysis (Delegator APR)

| Scenario | APR | Assumptions |
|----------|-----|-------------|
| Bull | 12-15% | High tx volume from prediction markets + dispute resolution |
| Base | 5-8% | Moderate adoption, inflation + some fees |
| Bear | 2-4% | Low volume, mostly inflation-funded dilution |

### Dual Play: Product + Positioning

GenLayer serves us two ways:

1. **Product integration** — GenLayer as AI arbiter for AgentEscrow (x402 → escrow → GenLayer → settle). Already in build: `GenLayerOracle.sol`, `IResolver.sol`, 51/51 tests passing.

2. **Passive income** — Delegator staking + Builder Points positioning. Since we're deploying contracts on Bradbury testnet for Colosseum anyway, we're simultaneously:
   - Earning Builder Points (potential airdrop)
   - Building on-chain activity history
   - Positioning as early validators/delegators when mainnet drops

### Immediate Action Plan

- [x] Get testnet GEN from faucet
- [x] Deploy contracts on Bradbury (GenLayerOracle.sol)
- [ ] Register on dev portal → earn Builder Points → leaderboard
- [ ] Join GenLayer Discord + builder channels
- [ ] Stake as delegator with testnet GEN (epoch 0 = no minimum)
- [ ] Monitor GEN token economics announcement
- [ ] Evaluate validator economics when mainnet economics published

## Next Steps

- [ ] Clone x402-foundation/x402 and explore MCP package
- [ ] Test x402 facilitator locally (Solana devnet)
- [ ] Evaluate Dexter SDK for service discovery
- [ ] **Prototype YoYo → Birdeye x402 integration** (HIGH PRIORITY)
- [ ] Design AAE x402 integration layer
- [ ] Map to existing AAE 8-layer architecture
- [ ] Study Birdeye's x402 integration as reference implementation
