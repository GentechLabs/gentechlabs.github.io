# Context Snapshot — July 9, 2026

**Run by:** Context Snapshot Cron (fcca23360df2)
**Time:** ~16:15 ET / 20:15 UTC

---

## Recent Activity (July 8–9)

### 1. Hub Platform Vision (July 9)
**Files created:**
- `09-Green Room/hub-product-vision.md` — Product vision doc
- `11-Mess Hall/hub-platform-discussion.md` — Discussion thread for Forge

**Key insight:** The two personal hubs (Jordan's DeFi + Atlas hub, Vanito's music + Fighter + Travel hub) are the first two profiles on a platform. One engine, infinite layouts. Jordan sees the marketplace potential: "Maybe the hub could be like a marketplace where you share templates."

**5 phases defined:**
1. ✅ Profiles (live) — Jordan + Vanito hubs deployed
2. 💰 Template Marketplace — sell layouts via x402 ($0.01–0.25)
3. 🚀 Social Profiles — "look at my hub" as marketing
4. 🧠 Widget SDK — third-party widgets with x402 rev share
5. 🔄 Earn App / Work Fund — field agent bounties → Atlas data

**Pending:** Forge input on template schema feasibility.

### 2. Composio Integration (July 8)
Jordan's architecture vision:
- **Google Sheets** = source of truth (bills, calendar, goals)
- **Composio** = integration layer (read sheets, classify data)
- **Routing layer** = the brain (this sheet row is a bill due Friday → fire action)
- **Hub** = visual dashboard (bills due this week, schedule)

Composio is open source (29.1k GitHub stars), 1,000+ connectors. Jordan plans to sign up with his Google account. Need to wire this up when Jordan is available.

### 3. PixelRAG Demo Script (July 8)
Created for Forge to run on desktop:
- `/root/vaults/gentech/10-Labs/pixelrag-tool/pixelrag-demo.py`
- Screenshots Vanito's Hub, Jordan's Hub, GenTech Atlas
- Builds FAISS visual index, runs test queries
- Requires RTX 3070 (Forge's desktop)
- Added to build queue as item #28

### 4. BNB Agent Studio + CMC Data (July 8)
Jordan shared: [Build AI Agents on BNB Agent Studio that can pay for CMC data via B402](https://www.bnbchain.org/en/blog/build-ai-agents-on-bnb-agent-studio-that-can-access-and-pay-for-coinmarketcap-data-via-binance-pays-b402)
- BNB Agent Studio allows agents to pay for CoinMarketCap data
- Uses B402 (BNB's x402 equivalent)
- Research status: link shared, exploration initiated

### 5. Japan Travel HUD
- **HTTP:** `http://2.24.195.196:3001/?at=35.6595,139.7004&hd=90`
- **HTTPS:** `https://2.24.195.196:3443/` (self-signed)
- 10 Tokyo POIs, works on Meta Ray-Ban glasses
- **Bug:** UI buttons don't respond to mouse clicks (DPAD-only, needs click handlers)
- Localtunnel was stuck in infinite restart loop → replaced with direct HTTPS proxy

### 6. Hub Nightly Sync Fix (July 9, 20:06)
`defi-data.json` had 105 merge conflict markers from a failed stash pop. Restored from clean commit `789c3a7d`. Fixed and deployed.

### 7. AI Companion Status
- Phase 0 complete
- Xenia #2353 submitted (awaiting maintainer feedback)
- RPCS3 #18999 submitted (awaiting maintainer feedback)
- Gepard 1.0 TTS: test plan written, handed to Forge
- Game target: Gears of War 2

---

## Cron Job Health (as of July 9)

### Fixed this session
- Context Snapshot job `fcca23360df2` → model updated to `deepseek-v4-flash` / `opencode-go`
- 4 GenTech Shop cron jobs redirected to Entertainment group
- 15 jobs paused for vacation on July 6 remain paused

### Jobs running OK (30 total configured)
- Hub Nightly Sync ✅ (ran at 20:06, fixed defi-data.json)
- Revenue Monitor ✅ (ran at 20:01)
- Cron Health Monitor ✅
- Daily Session Reset ❌ (still error)
- Build Queue + Labs Standup ❌ (still error)
- Context Snapshot ❌ (last run error — this is this run, hopefully fixed)

---

## Memory Status
- **Last consolidation:** July 8 (98% → 84%)
- 4 stale entries replaced/shortened
- Using GLM-4.7 for heavy work, deepseek-v4-flash for cron jobs, Ollama Qwen for simple tasks

---

## Links to Related Notes
- [[hub-platform-discussion|Hub Platform Discussion]]
- [[hub-product-vision|Hub Product Vision]]
- [[lobby-ui-product-vision|Lobby UI Product Vision]]
- [[lobby-ui-order-book|Lobby UI Order Book]]
- [[ideas|Mess Hall Ideas]]
