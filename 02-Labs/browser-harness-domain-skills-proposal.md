# browser-harness — Domain Skill Proposals

Date: 2026-04-18
Source: Jordan — "Collaborate with everyone on what skills to add"

## How Domain Skills Work

- Detailed `.md` files in `/root/browser-harness/domain-skills/<site>/`
- Document: URL patterns, APIs (preferred over browser), stable selectors, gotchas
- Contributed back upstream via PR when generalizable
- Format: see `domain-skills/github/scraping.md` as reference

---

## 🔧 Dmob (Smart Contract / DeFi)

### Priority 1: Snowtrace / Etherscan
- Contract source verification reading
- ABI extraction from verified contracts
- Transaction history parsing
- Token holder analysis
- **Why:** rug-pull monitoring, contract risk assessment, verification helpers

### Priority 2: LFJ (TraderJoe)
- Pool discovery and TVL
- Liquidity position management UI
- Swap route analysis
- Farm/staking page automation
- **Why:** LP management layer, cross-protocol rebalancing

### Priority 3: Snapshot / Tally
- Governance proposal extraction
- Vote tallying
- DAO activity monitoring
- **Why:** governance intel, DAO participation automation

### Priority 4: Hackathon Platforms
- ETHGlobal submission forms
- Arc (x402, escrow) project pages
- Devpost registration/submission
- **Why:** automate the painful multi-form submission process

---

## 📊 YoYo (Market Intelligence)

### Priority 1: CoinMarketCap / CoinGecko
- Already have API — browser skill for UI-only features (portfolio, watchlist export)
- Price chart data extraction
- New listing alerts
- **Why:** supplement API data with UI-scraped signals

### Priority 2: TradingView
- Chart pattern reading
- Indicator snapshots
- Screener page extraction
- **Why:** visual TA automation, chart-to-alert pipeline

### Priority 3: Polymarket
- Market discovery and odds extraction
- New market alerts
- Volume/liquidity tracking
- **Why:** prediction market intel, event-driven trading signals

### Priority 4: Dune Analytics
- Dashboard data extraction
- Query result scraping (when API is limited)
- **Why:** on-chain data visualization capture

---

## ✍️ Desmond (Content / Social)

### Priority 1: Twitter/X
- Tweet extraction and thread reading
- Profile monitoring
- Engagement metrics capture
- **Why:** social signal monitoring, rug-pull community alerts

### Priority 2: YouTube
- Already have transcript tool — skill for channel monitoring
- Video metadata extraction
- Comment sentiment
- **Why:** content pipeline, creator monitoring

### Priority 3: Medium / Mirror / Paragraph
- Blog post extraction
- Author monitoring
- **Why:** thought leadership tracking, content curation

---

## 🏗️ Gentech (Project Management / Infra)

### Priority 1: Linear / Notion
- Issue status tracking
- Project board extraction
- **Why:** PM automation for agent team

### Priority 2: Vercel / Netlify
- Deployment status checks
- Build log extraction
- **Why:** deploy monitoring for hackathon projects

---

## 🌐 Cross-Team (Jordan's Priorities)

### 1. Contract Verification Monitor (AAE Layer 2)
Given address → navigate Snowtrace → read source → flag risks
(Mintable? Proxy? Owner pause? Timelock?)

### 2. Rug Pull Scanner
New token alerts → auto-verify → score risk → alert
(Combine Snowtrace + social signals from Twitter)

### 3. Hackathon Auto-Submit
Navigate platform → fill forms → upload files → submit
(ETHGlobal, Devpost, Arc — all different UIs, self-healing handles differences)

### 4. Cross-Protocol LP Manager
LFJ → check pool → close position → open on different protocol
(DEX UIs change constantly — self-healing is critical)

---

## Recommended Build Order

1. **Snowtrace** (Dmob) — immediate utility for AAE
2. **LFJ** (Dmob) — LP monitoring upgrade
3. **Twitter/X** (Desmond) — rug-pull community signal
4. **Polymarket** (YoYo) — event-driven trading
5. **ETHGlobal** (Gentech) — hackathon submission automation

## Notes
- Browser should be last resort — always check for APIs first
- `http_get()` + API beats browser every time (faster, cheaper, no headless detection)
- Browser is for: JS-rendered pages, complex forms, file uploads, UI-only features
- Self-healing: if a selector breaks mid-task, edit helpers.py and retry
- Contribute skills upstream via PR when generalizable
