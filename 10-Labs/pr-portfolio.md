# PR Portfolio — GenTech Labs Ecosystem Listings

Generated: 2026-07-18
Run type: Scheduled cron job (Ecosystem Lister)

---

## Existing PRs — Already Submitted

### 1. awesome-x402 (xpaysh/awesome-x402)
| PR | Status | Title | Notes |
|----|--------|-------|-------|
| [#701](https://github.com/xpaysh/awesome-x402/pull/701) | ✅ **MERGED** Jul 17 | Add GenTech Labs to Ecosystem Projects | GenTech Labs listed in Ecosystem Projects, Infrastructure section |
| [#881](https://github.com/xpaysh/awesome-x402/pull/881) | 🔄 OPEN | Add GenTech Labs x402 Gateway | Adds to Production Implementations > High-Volume Production Deployments |
| [#810](https://github.com/xpaysh/awesome-x402/pull/810) | 🔄 OPEN | Update GenTech Labs listing, add Agent Kit | Overlapping with #881 |
| [#761](https://github.com/xpaysh/awesome-x402/pull/761) | 🔄 OPEN | Add GenTech Labs — x402 Gateway + Agent Kit + ecosystem | Overlapping with #881, #810 |

### 2. awesome-mcp-servers (punkpeye/awesome-mcp-servers)
| PR | Status | Title | Notes |
|----|--------|-------|-------|
| [#10224](https://github.com/punkpeye/awesome-mcp-servers/pull/10224) | 🔄 OPEN | Add ProtoJay4789/genTech-shop to Gaming section 🤖🤖🤖 | Uses automated fast-track |
| [#10099](https://github.com/punkpeye/awesome-mcp-servers/pull/10099) | 🔄 OPEN | Add GenTech Agent Kit (BlockRun MCP) to Finance & Fintech 🤖🤖🤖 | Uses automated fast-track |

### 3. awesome-solana-ai (solana-foundation/awesome-solana-ai)
| PR | Status | Title | Notes |
|----|--------|-------|-------|
| [#197](https://github.com/solana-foundation/awesome-solana-ai/pull/197) | 🔄 OPEN | Add GenTech Agent Kit and x402 Gateway | Added to Infrastructure section |

### 4. public-apis (public-apis/public-apis)
| PR | Status | Title | Notes |
|----|--------|-------|-------|
| [#6539](https://github.com/public-apis/public-apis/pull/6539) | 🔄 OPEN | Add GenTech Agent Kit to Cryptocurrency | |

### 5. awesome-agentic-payments (bitrefill/awesome-agentic-payments)
| PR | Status | Title | Notes |
|----|--------|-------|-------|
| [#26](https://github.com/bitrefill/awesome-agentic-payments/pull/26) | 🔄 OPEN | Add GenTech Labs — multichain x402 gateway + Agent Kit | |

---

## Repos Checked — Skipped / Not Suitable

### ❌ Not Submitted (Issues)

| Repo | Reason |
|------|--------|
| awesome-mpp (mbeato/awesome-mpp) | MPP protocol, not x402. No overlap with GenTech services. |
| awesome-ai-agents-2026 (caramaschiHG) | No clear category for Agent Kit or x402 gateway. Protocols section is for protocol specs, not implementations. |
| awesome-crypto-mcp-servers (hive-intel) | High curation bar — "selective maintenance phase." Would need nomination issue first. Our Agent Kit duplicates CoinGecko/BlockRun MCP entries. Noted for Jordan review. |
| Merit-Systems/awesome-agentic-commerce | Repo exists but README is 404/empty. |
| awesome-openclaw-skills (VoltAgent) | Requires skills to be published on ClawHub first. Our Agent Kit is MCP-based, not an OpenClaw skill. |
| ratatui/awesome-ratatui | TUI apps, not relevant. |
| scrapy/awesome-game-deals | No suitable repo found for game deal APIs. |

### ⚠️ Service Health Issues (Cannot List Until Fixed)

| Service | Status | Issue |
|---------|--------|-------|
| **Rugcheck v2 API** (rugcheck.gentechlabs.net) | 🔴 DOWN — HTTP 522 | Cloudflare connection timeout. All endpoints unavailable. Fix before listing anywhere. |
| **x402 Gateway** (api.gentechlabs.net) | ✅ LIVE v7.0.0 | 15+ endpoints, x402 discovery at /.well-known/x402, OpenAPI spec, across 6 chains |
| **GenTech Shop** (gentechlabs.net/shop) | ✅ LIVE | Game deals, wishlist sync |
| **Subscription Hub** (gentechlabs.net/subscription-hub.html) | ✅ LIVE | 3-tier Q402 subscriptions |
| **GenTech Agent Kit** (github) | ✅ LIVE | MCP server, 15+ tools, market data + x402 payments |

---

## 👤 Jordan Review Items

1. **Existing open PRs need attention** — 5 repos have open PRs that haven't merged yet. Consider following up on Discord/DM with maintainers.
2. **awesome-crypto-mcp-servers** — If we want to push for listing here, file a nomination issue first (higher barrier than PR). The GenTech Agent Kit has market data + DeFi + x402 tools which are unique.
3. **Rugcheck v2 API is down (522)** — Must fix before submitting to any listing. Once fixed, strong candidate for awesome-x402 (Security section), awesome-mcp-servers, and public-apis.
4. **Game deal specific awesome lists** — There doesn't appear to be a dedicated awesome list for game deal APIs/aggregators. The GenTech Shop endpoints would fit perfectly in one if it existed.

---

## Services Matched to Listing Opportunities

| Service | Best Fit Repos | Status |
|---------|---------------|--------|
| x402 Gateway (api.gentechlabs.net) | awesome-x402, awesome-solana-ai, awesome-agentic-payments, public-apis, **gold-402** ✅ NEW | 📋 PRs in place |
| GenTech Agent Kit | awesome-mcp-servers, awesome-solana-ai, public-apis | 📋 PRs submitted |
| GenTech Shop | awesome-mcp-servers (Gaming section) | 📋 PR submitted |
| Rugcheck v2 API | awesome-x402 (security), awesome-mcp-servers, public-apis | ⏸️ Waiting on service fix |
| Subscription Hub | awesome-x402 (Use Cases) | 🔄 Not yet submitted — Q402 vs x402 distinction needs Jordan's guidance |
| DeFi LP Monitor | awesome-mcp-servers (Finance section) | 🔄 Not yet submitted — needs Jordan's guidance |
| Agent Credit Score | awesome-x402, awesome-solana-ai | 🔄 Not yet submitted — needs Jordan's guidance |

---

## Gold-402 — NEW Submission

| Detail | Value |
|--------|-------|
| Repo | Haustorium12/gold-402 — curated x402 resource directory |
| PR # | [#39](https://github.com/Haustorium12/gold-402/pull/39) |
| Status | 🔄 OPEN (submitted this run) |
| Section Added To | directory/apis.md > Crypto & DeFi Data |
| Entry | GenTech x402 Gateway — 15 endpoints, 5 chains, $0.001-$0.10 USDC |
| Why It Fits | CURATED list (not exhaustive) — production live x402 with multi-chain support |
