# Context Snapshot — June 19, 2026

**Generated:** 12:09 AM UTC (8:09 PM ET, Jun 18)

---

## Session 1: WURK.FUN MCP Integration Standup (Jun 18, 12:10 PM – ongoing)

**Topic:** WURK.FUN MCP server integration, Agent Rug 2.0 research, dashboard features, Compound vs. Extract Protocol testnet.

**Key Decisions:**
- **WURK.FUN MCP Integration — verified and documented:**
  - MCP server confirmed live at `https://wurkapi.fun/mcp` — 6 tools, 3 resources, 2 prompts
  - x402 v2 payment flow verified (402 challenge → PayAI facilitator → Solana USDC)
  - Two existing WURK skills already in gentech profile
  - Integration doc: `09-Green Room/build-logs/wurk-mcp-integration-2026-06-18.md`
  - **Blocker:** MCP server returns 500 on some tool calls — needs WURK team fix before full integration

- **Dashboard Features Built:**
  - **🪞 Reflect** — personalized reflection entries on dashboard (not generic, written per-entry)
  - **💬 Ask Gentech** — advice feature grounded in actual context
  - Both shipped and live

- **Compound vs. Extract Protocol — Testnet Scaffold Complete:**
  - Executor module created with 3 swap adapters: LFJAdapter (Avalanche), ZeroXSwapRouter (EVM), JupiterSwapRouter (Solana)
  - Testnet scaffold on Avalanche Fuji: `02-Labs/compound-extract/testnet/`
  - 11 tests passing (5 extract + 6 compound)
  - Build log: `09-Green Room/build-logs/compound-extract-testnet-2026-06-18.md`

- **Agent Kit Installer Spec Written:**
  - 14-section spec with full install.sh bash script (~150 lines)
  - Covers: Hermes install, skills+crons, wallet wizard, DeFi dashboard, GitHub backup, skill marketplace, health dashboard
  - File: `09-Green Room/build-logs/agent-kit-installer-spec-2026-06-18.md`

- **DeFi Regime Wiring:**
  - Regime detection + strategy comparison data wired to `defi-data.json`
  - Dashboard now shows: regime classification (bear_trend), strategy alternatives (LP Curve 493% APR vs AVAX Staking 7% vs Hold vs Stablecoin LP)
  - Build log: `09-Green Room/build-logs/defi-regime-wiring-2026-06-18.md`

---

## Session 2: Vals AI Fellowship Details (Jun 18, 8:33 AM – ongoing)

**Topic:** Vals AI Fellowship research, resume updates, funding applications.

**Key Decisions:**
- **Vals AI Fellowship** — $1,000–$2,500/week stipend, 3-6 months, remote or SF
  - Focus: frontier AI evaluation benchmarks
  - Deadline: June 30
  - Application: https://www.notion.so/vals-ai/Vals-Fellowship-3668a877dd8d80d6b10ac4bf96c4f6be
  - Fits "tough love for the agent economy" angle

- **Resume Updated:**
  - Email added: jordanjones0902@gmail.com
  - Location removed from top
  - File: `02-Labs/Resumes/Jordan_Master_Resume.pdf`

- **AWS WAF AI Traffic Monetization** — Jordan shared article about AWS WAF adding AI bot traffic monetization. Potential angle for content protection products.

---

## Session 3: Live Data Support for Rebalancing (Jun 18, 8:35 AM – ongoing)

**Topic:** DeFi LP position rebalancing, cron schedule optimization, live data pipeline.

**Key Decisions:**
- **AAE DeFi cron shifted to active hours** — now `11-23,0-2 UTC` (7am-11pm ET)
- **Jordan rebalanced LP position** — switched to Curve shape, range **6.19–6.40**
  - Efficiency: 96.9% (massive improvement from 48.4%)
  - IL: +0.16% (slightly positive)
  - 24h fees: $0.825
- **defi-data.json synced** — updated vault copy + deployed to 5 target locations
- **Regime detection** wired to dashboard — currently classified as `bear_trend`

---

## Updated Open Threads

1. **🔴 Encode Vibe Coding Hackathon** — **TODAY (Jun 19)**. ⚠️ DEADLINE TODAY. 3-day sprint.
2. **🔴 Sui Overflow** — **2 days left (Jun 21)**. Token Risk Oracle (Move). Jordan to verify registration.
3. **🔴 BNB Hackathon** — **5 days left (Jun 24)**. CMC Strategy Engine 21/21 tests, ready to submit.
4. **🔴 Compound vs. Extract** — Testnet scaffold done (11 tests). Next: LFJ RPC integration, then extract execution.
5. **🟡 WURK.FUN MCP** — Verified live, but server returns 500 on some calls. Waiting on WURK team fix.
6. **🟡 AAE Product Vision** — North star: yield farming clarity for choppy markets. "What am I actually earning?"
7. **🟡 Dashboard Features** — Reflect + Ask Gentech shipped. Monitor adoption.
8. **🟡 Vals AI Fellowship** — $1K-$2.5K/week, deadline Jun 30. Worth applying.
9. **🟡 Agent Kit Installer** — Spec complete. Ready to prototype.
10. **⏳ Encode Solana Bootcamp** — Starts Jun 22 (3 days). Registered.
11. **⏳ Encode Arc Bootcamp** — Starts Jun 22 (3 days). Registered.
12. **⏳ Lepton Agents** — Due Jun 29 (10 days). Cookbook Nanopay.
13. **⏳ Casper Buildathon** — Due Jun 30 (11 days). $150K. Existing RWA agent code ready.
14. **⏳ Colosseum Fall Hackathon** — Sep 28–Nov 2. Primary Solana target.
15. **🟢 Ray-Ban Bridge** — Built, deferred to Vanito for live testing.
16. **🟢 POE2 Build** — Tempest Bell switch complete. Farming for tier 2 support gems in Act 2.

---

## Key Context Carried Forward

- **Encode Vibe Coding deadline is TODAY.** This is the most urgent item. Must submit or pass today.
- **BNB Hackathon due Jun 24** — CMC Strategy Engine 21/21 tests, ready to submit. 5 days left.
- **Sui Overflow due Jun 21** — Token Risk Oracle. Jordan needs to verify registration. 2 days left.
- **Jordan's directive:** Hackathons are enjoyable but space them out. Focus on building AAE platform into an app. Orchestrator identity, not coder.
- **AAE Product Mission:** Yield farming clarity for choppy markets. "What am I ACTUALLY earning?" not flashy APRs.
- **DeFi Dashboard is live.** Cron runs every 10 min. Regime detection + strategy comparison wired.
- **Position is Curve.** Jordan rebalanced. Range 6.19–6.40. Efficiency 96.9%.
- **Compound vs. Extract Protocol** — Testnet scaffold complete (11 tests). 2 weeks to MVP, 6 weeks full product.
- **WURK.FUN MCP** — Server live but flaky (500s on some calls). x402 payment flow works.
- **Vals AI Fellowship** — Interesting opportunity. $1K-$2.5K/week, deadline Jun 30. Remote.
- **Resume updated** — Email added, location removed. Ready for applications.
- **web_extract backend broken** — DuckDuckGo is search-only. Use TinyFish Fetch or browser for URL extraction.

---

*Last updated: 2026-06-19 00:09 UTC (8:09 PM ET)*
