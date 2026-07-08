# Green Room — Ideas

## 🟢 APPROVED — Building

- [x] **CMC x402 Gateway** — CoinMarketCap data behind an x402 paywall. Agents pay $0.001/query in USDC on BSC (B402) or Base (x402). 5 endpoints: quotes, listings, search, trending, DEX pairs. Free endpoints: health + pricing. ✅ SHIPPED Jul 8, 2026 — deployed to `cmc-x402-gateway.wood-professor.workers.dev`. Needs permanent CF token for prod domain.

- [x] **Wishlist Tracker / Deal Agent** — Cross-store price comparison bot. Pulls Steam wishlist, compares prices across Gamesplanet, Instant Gaming, GMG, Fanatical, Humble, GOG, Epic, CDKeys, AllYouPlay. Telegram alerts when prices drop. Revenue: freemium SaaS or paid bot access. Pitch: "Not another comparison site — a personal deal agent." (Jun 2026) → **APPROVED — Building as `gaming/deal-tracker`** ✅ MVP SHIPPED — 12/12 tests, 35 stores via CheapShark API

- [x] **Agent Arena** — DeFi automation platform. Three roles (Boss/Executive/Partner), four factions, Tekken-inspired lore. Revenue: protocol fees + licensing. (Jan 2027 launch target) → ✅ MVP SHIPPED — 16/16 tests, role system + faction standings + match lifecycle

## 🟡 NEW IDEAS — Service Opportunities

- [ ] **Agent Registration API** — ERC-8004 agent identity on-chain across 22 chains. Wrap registration script as a paid API. "Register your agent, get verified, list on Bazaar." Revenue: x402 micropayment per registration (~$0.01). Effort: 1 week. Stack: Python + web3.py + ERC-8004 contract.

- [ ] **Atelier Marketplace Listing** — Register GenTech as agent provider on Atelier (Solana + Base, USDC, x402). List CMC Gateway, DeFi Intelligence, Agent Registration APIs as services. Live revenue channel, existing distribution. **Greenlit — Forge builds.**

- [ ] **SCN Partnership + Contribution** — Outreach to Avi Gaba (EventHorizon Labs). Contribute x402 economic layer to Singularity Cloud Network compute markets. **Greenlit — Forge builds.**

- [ ] **Agents as RWAs Thesis** — Position GenTech as decentralized AI infrastructure. Agents = tokenized compute assets (weights + allocation + access rights). Geopolitical model fragmentation makes this urgent. Document in `10-Labs/rwa-agent-compute-thesis.md`.

- [ ] **Agent Fleet Monitor** — SaaS dashboard for multi-agent operators. Detect crashes, stuck processes, missed cron jobs, systemic failures. "Is your agent fleet healthy?" Revenue: $5-20/mo subscription. Effort: 2 weeks. Stack: Hermes health checks + Telegram alerts + simple dashboard.

['DeFi Intelligence API** — Protocol TVL, yield pools, token prices, DEX data. Wrap BlockRun tools as a paid API. Revenue: $0.001-0.005 per call on x402. Effort: 1 week. Stack: BlockRun MCP tools + x402 payment endpoint.\n- [ ] **L1Beat API Integration** — Avalanche C-Chain + P-Chain data: blocks, transactions, fees, validators, staking. Open REST API, no key required. URL: https://l1beat.io/api - Potential enhancement for DeFi yield monitoring and cross-chain analysis. Shared via X on 2026-07-01\n- [ ] **ElevenLabs Pipecat Integration** — Speech Engine now supports Pipecat AI for voice agents. Enables voice loop, STT/TTS, turn-taking while Pipecat handles LLM text generation. Documentation: https://elevenlabs.io/docs/eleven-api/guides/how-to/speech-engine/pipecat-integration - Shared via X @ElevenLabsDevs on 2026-07-01']

- [ ] **Agent Starter Kit** — White-label template for building AI agents. "Launch your own AI agent in 24 hours." Includes: Hermes setup, identity (ERC-8004), payment rails (x402), basic skills. Revenue: $49 one-time purchase or $9/mo license. Effort: 2 weeks. Stack: Hermes config + templates + docs.

['Agent Search API** — Structured web intelligence for AI agents. Bundle Exa + Grok Search + Surf as a unified search API.', 'Search the web, get structured data.', 'Revenue: x402 micropayments per query ($0.01-0.025). Effort: 1 week. Stack: BlockRun search tools + x402 endpoint.\n- [ ] **L1Beat API Integration** — Avalanche C-Chain + P-Chain data: blocks, transactions, fees, validators, staking. Open REST API, no key required. URL: https://l1beat.io/api - Potential enhancement for DeFi yield monitoring and cross-chain analysis. Shared via X on 2026-07-01']

- [ ] **Gepard 1.0 TTS** — Open-source real-time TTS from nineninesix.ai. Apache 2.0, 555M params, vLLM-native. Voice cloning from short clips, 25× real-time on RTX 5090. Replace ElevenLabs for production TTS. Forge runs on desktop GPU as local API, VPS calls it for voice generation. Use for Agent Companion game character voices and all voice pipeline. URL: https://huggingface.co/nineninesix/gepard-1.0
- [ ] **Human Feedback API** — Agent-to-human microtask layer via WURK.FUN integration. "Get 10 human responses for $0.25." Resell human feedback at margin. Revenue: markup on WURK.FUN pricing. Effort: 1 week. Stack: WURK.FUN API + x402 payments.

## 🔴 BIG PLAYS — From Revenue Model

- [ ] **Agent Finance Intermediary** — Klarna/PayMeButton for AI agents. Agents as payment processors: split payments, extend credit, handle loans. Revenue: transaction fees (3-5%), interest (12-24% APR), lending fees (5-10%). Stack: x402 payments + ERC-8004 credit scoring + DeFi Intelligence risk engine + Sana bot card integration. See `/root/vaults/gentech/11-Mess Hall/2026-07-05-agent-finance-intermediary.md`. Added: Jul 5, 2026.
- [ ] **Virtuals ACP Integration** — $481M AGDP market. Risk scoring, compliance, data access for Virtuals agents. Revenue: 0.001-0.01% of AGDP. Effort: Month 2-3. Stack: Virtuals ACP SDK + Agent Kit.
- [ ] **Compound vs. Extract** — DeFi yield optimization engine. Automated LP management, yield farming, rebalancing. Revenue: protocol fees + yield share. Effort: Month 4-6. Stack: DeFi tools + automation + smart contracts.
- [ ] **Multi-Asset Rotation Agent** (AAE Special Edition) — Agent rotates user portfolio across tokenized stocks (Robinhood Chain), crypto LP, metal pools, and stablecoin lending based on macro regime + on-chain yields. Revenue: yield share + subscription. Effort: Month 3-6. Stack: AAE + Q402 + DeFi Intelligence API. See `aae-product-vision.md` for full special edition thesis.

## 🔵 GAMING AGENT ECOSYSTEM — NEW STRATEGY (Jul 6, 2026)

### **Core Product: Agent Companion**
Vision-based AI Player 2 for emulated games (Xenia, RPCS3, Dolphin). Agent plays split-screen co-op with human player. Uses Ollama Cloud for cost-efficient inference. **Status: Added to build queue.**

### **Vision: Agent Marketplace + Training Platform**
"Imagine a marketplace full of gaming agents where users could train data based on their gamer tag and gameplay hours. Agents wait in 'Rec Mode' to get picked up by humans to play games — like 2K's Park but with AI companions."

**Three layers:**
1. **Agent Companion (Core)** — AI Player 2 technology
2. **Training Platform** — Users train agents on their gameplay data
3. **Marketplace + Discovery** — "Rec Mode" lobby where agents get picked up

### **Revenue Model**
| Stream | Pricing | Potential |
|--------|---------|-----------|
| **Pay-per-session** | $2-8/2hrs (Ollama) or $15-30/2hrs (cloud) | Casual players |
| **SaaS subscription** | $20/mo (unlimited local) | Power users |
| **Agent marketplace** | 10-15% commission on agent sales | Content creators |
| **Training data monetization** | User gets % when their data trains agents sold | Game influencers |
| **Highlight generation** | $0.50/clip or $10/mo unlimited | Streamers |

### **Use Cases**
- **Solo gamers** — Play co-op games without finding friends
- **Streamers** — Agent Army (multiple agents with different personalities)
- **Content creators** — Train and sell their playstyle as an agent
- **Competitive players** — Practice against AI versions of themselves
- **Casual players** — "Rec Mode" pickup games with personality agents

## 🟠 REVENUE POTENTIAL (Year 1 Estimates)

| Service | Conservative | Realistic | Aggressive |
|---------|-------------|-----------|------------|
| Deal Tracker (SaaS) | $1,200/yr | $6,000/yr | $18,000/yr |
| Agent Registration API | $1,800/yr | $9,000/yr | $36,000/yr |
| Agent Fleet Monitor | $4,200/yr | $12,000/yr | $36,000/yr |
| DeFi Intelligence API | $1,800/yr | $18,000/yr | $135,000/yr |
| Agent Starter Kit | $2,400/yr | $8,400/yr | $24,000/yr |
| Agent Search API | $1,200/yr | $6,000/yr | $18,000/yr |
| Human Feedback API | $600/yr | $3,000/yr | $9,000/yr |
| Agent Finance Intermediary | $12,000/yr | $60,000/yr | $360,000/yr |
| **Total (excl. big plays)** | **$25,200/yr** | **$122,400/yr** | **$636,000/yr** |

## 💡 PRIORITY EXECUTION ORDER

1. **Deal Tracker** — Already building, API key verified
2. **DeFi Intelligence API** — We have the tools, just wrap them
3. **Agent Registration API** — Script already exists, just needs API layer
4. **Agent Search API** — BlockRun tools already integrated
5. **Agent Fleet Monitor** — Build for ourselves first, then sell
6. **Agent Starter Kit** — Bundle everything above into a template
7. **Human Feedback API** — WURK.FUN integration ready
8. **Runtime/Tooling/Portal infra** — See `build-queue.md` items 8-12; enabling work that cuts integration time for 1-7
9. **Virtuals ACP** — Month 2-3
10. **Compound vs. Extract** — Month 4-6

## 🏷️ COMMON PITCH

> "GenTech builds the infrastructure layer for AI agents. We provide agent identity (ERC-8004), payment rails (x402 + Q402), data intelligence (DeFi, stocks, metals, search, game deals), and multi-asset yield automation. Think of us as the Stripe for AI agents — infrastructure that other agents pay to use."

## 📊 MARKET CONTEXT (July 2026)

- x402 ecosystem: $24.24M/mo volume, 75M transactions, 22K sellers
- Virtuals ACP: $481M AGDP, $4M/mo revenue, 2.28M jobs
- Robinhood Chain + Q402 — stock tokens entering DeFi composability
- Total TAM: $340M annualized (crypto-only) | Expanding to regulated equities + metals
- We don't need to be big — we need to be essential

## 🕶️ META RAY-BAN TRAVEL HUD (July 2026)

**Overview:** Heads-up display for Meta Ray-Ban glasses - travel assistance, navigation, currency conversion, POI management, AI briefings about current location.

**Tech Stack:**
- Node.js (Express server, no build step)
- JSON file storage (multi-user profiles)
- Cloudflare tunnel for HTTPS access
- Optional: Anthropic API for AI briefings, Google Maps API for geocoding

**Features:**
- NEARBY: Saved POIs with bearing arrows, AR mode
- OBJECTIVES: Trip checklist
- NOTES: Reference info (addresses, phrases)
- CONVERT: Currency converter with live rates
- BRIEF: AI briefings (block/neighborhood/city scale)

**Deployment:**
- Running on VPS: `https://salty-ravens-flash.loca.lt` (auto-restarts)
- Admin UI: `/admin` (for data entry)
- HUD: `/` (600×600 webview optimized)
- Git repo: `/root/reference-hud/` (clone of meta-rayban-display-travel-hud)
- Tunnel Service: localtunnel with watchdog (HTTPS, auto-restart)
- Status: ✅ Live with auto-restart watchdog
- Watchdog: `/root/localtunnel-watchdog.sh` (maintains tunnel availability)
- Tunnel: URLs auto-regenerate when they timeout (~10 min intervals)

**For Japan Trip:**
- Pre-seeded Tokyo POIs (ramen shops, temples, crossings, markets)
- JPY/USD conversion ready
- Emergency phrases pre-loaded
- Solo travel optimized (small booths, 24h shops noted)

## 🔵 MIXAR — 3D CONTENT PIPELINE (Jul 8, 2026)

**Decision:** Option C — Both paths

- [ ] **Mixar → Agent Companion Training Pipeline** — Use Mixar's Mixie agent (Blender 5.0 fork) to generate 3D scene renders, character sprites, environment maps for vision model training
- [ ] **Standalone x402 3D Generation API** — Wrap Mixar CLI behind x402 paywall ($0.01-0.05/gen), list on Atelier + x402.org

**Reference:** Mixar-AI/mixar-app, v2.0.0 (Jul 7), 61 stars, GPL-3.0
