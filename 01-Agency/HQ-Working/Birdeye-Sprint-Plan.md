# Birdeye Sprint Plan — 7 Days

**Status:** ACTIVE — Time-sensitive (7 days from Apr 18)
**Goal:** Quick money via Birdeye builder opportunity
**Owner:** Jordan + Agents

---

## What Birdeye Offers (For Building)

- **MCP Server** — AI agents can query Birdeye data natively via `https://mcp.birdeye.so/mcp`
- **x402 Pay-Per-Request** — USDC on Solana, no API key or subscription needed
- **Real-time WebSocket** — Price, trades, new listings, meme stats
- **APIs:** Price, OHLCV, token overview, trades, wallet PnL, smart money, security data
- **Bug Bounty** — security findings = paid prizes
- **Supported Chains:** Solana, BSC, Base, MegaETH, 10+ networks

## Why This Fits Us

- We already run AI agents (Hermes) — Birdeye MCP = native integration
- x402 means we can demo without upfront API costs
- Solana-native payment aligns with our AVAX/DeFi positioning
- "Works while you work" + AI agents + market data = compelling pitch

---

## 7-Day Sprint Breakdown

### Day 1 (Apr 18-19): Research & Setup
- [ ] Register at `bds.birdeye.so` — get API key
- [ ] Test MCP server locally: `npx -y mcp-remote@0.1.38 https://mcp.birdeye.so/mcp --header "x-api-key:<KEY>"`
- [ ] Read x402 pay-per-request docs thoroughly
- [ ] Review bug bounty program rules and prize tiers
- [ ] Identify the specific submission requirements

### Day 2 (Apr 19-20): Architecture & Prototyping
- [ ] Decide: Agent tool? Dashboard? API integration?
- [ ] Prototype Birdeye MCP → Hermes agent integration
- [ ] Test x402 flow — pay per request with USDC on Solana
- [ ] Document API capabilities for our watchlist tokens

### Day 3-4 (Apr 20-22): Build Core Feature
- [ ] Build the submission — likely:
  - **Option A:** Birdeye-powered DeFi agent (analyze any token on demand)
  - **Option B:** Smart money tracker with WebSocket real-time alerts
  - **Option C:** x402-enabled agent that pays per query (no subscription needed)
- [ ] Get working demo with real data
- [ ] Write clean README with screenshots

### Day 5-6 (Apr 22-24): Polish & Demo
- [ ] Record demo video (Loom or screen capture)
- [ ] Write compelling pitch narrative
- [ ] Test edge cases, error handling
- [ ] Prepare submission materials

### Day 7 (Apr 25): Submit
- [ ] Final review
- [ ] Submit before deadline
- [ ] Share on X/Twitter for visibility

---

## Competitive Advantages We Have

1. **Real agent infrastructure** — not a demo, it's our production system
2. **Multi-agent coordination** — YoYo (strategy), Desmond (content), Turing (code) working together
3. **x402 integration** — cutting-edge pay-per-request pattern
4. **Existing DeFi positioning** — LP management, watchlist, market data
5. **"Works while you work"** — narrative for working-class crypto builders

## Risk Assessment

- **Time:** 7 days is tight but doable for a demo
- **API key needed:** Free tier available at bds.birdeye.so
- **x402 cost:** Minimal (USDC per request, fractions of a cent)
- **Competition:** Unknown — first mover advantage if we move fast

---

## Decision Needed

- [ ] Confirm: What is the specific Birdeye sprint/hackathon?
- [ ] Confirm: Bug bounty vs builder challenge vs both?
- [ ] Confirm: Do we have a Birdeye API key?
- [ ] Confirm: Submission format (GitHub repo? Demo video? Live app?)

---

*Drafted by Desmond — Apr 18, 2026*
