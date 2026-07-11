# Vault Audit — July 10, 2026

## ✅ What's Clean

- **Core vault structure** — `Gentech/` directory hierarchy is solid (00-HQ, 10-Labs, 09-Green Room, 11-Mess Hall, 12-TRAVEL, etc.)
- **Handoffs** — All handoffs documented and pushed to git
- **Ideas log** — Well-organized with status tracking
- **Cron jobs** — All 30 green, model fallback fixed

## 🗑️ Cleanup Opportunities

### 55M _legacy directory
- 16 subdirectories of old project iterations
- Already versioned in git — leaving it is fine since it's not in the working tree
- **Recommendation:** Archive only if disk is tight, otherwise leave

### 30+ untracked microservice directories in `10-Labs/`
All the `*-api` directories (deal-tracker-api, gas-price-api, crypto-price-api, content-scraping-api, etc.) were scaffolded but never deployed. Most are experiments that got superseded by the consolidated x402 gateway.
- **Recommendation:** Delete the never-shipped ones, keep the ones with real work (agent-arena, agent-starter-kit, cmc-x402-gateway, model-router)

### Root-level duplicate directories
`HQ/`, `Labs/`, `Strategies/`, `Games/`, `Travel/`, `Gaming/`, `Entertainment/` at root mirror what's in `Gentech/`. These are remnants from before the v4 structure.
- **Recommendation:** Delete root-level dupes, only keep `Gentech/` and a few workspace dirs

### Stale context snapshots
`Gentech/11-Mess Hall/context-snapshot-2026-07-07.md` and `2026-07-08.md` are still there.
- **Recommendation:** Clean up snapshots older than 3 days

---

## 💡 Ideas We Haven't Acted On

### Low Effort — Quick Wins

| Idea | Effort | Why Still Waiting |
|------|--------|-------------------|
| **Donut AI Application** | ✉️ Send | Tonight's #1 task — cover letter + resume → hiring@donutbrowser.ai |
| **Cloudflare Monetization Gateway** | 1h | Signed up for waitlist Jul 1, never followed up. New x402 channel |
| **Atelier Marketplace Listing** | 2h | Greenlit Jul 4, never submitted. Free distribution |
| **Xenia Issue #2239 Bug Fix** | 3-4h | Offered to fix. Maintainer wants it. Builds reputation |

### Medium Effort — Wrap What Exists

| Idea | Effort | Stack |
|------|--------|-------|
| **Agent Registration API** | 1 week | Python + web3.py + ERC-8004. Script already exists |
| **DeFi Intelligence API** | 1 week | Wrap BlockRun tools as x402 endpoint |
| **Agent Fleet Monitor** | 2 weeks | Hermes health checks + Telegram + dashboard |
| **Human Feedback API** | 1 week | WURK.FUN resell at margin |
| **Agent Starter Kit** | 2 weeks | Bundle existing templates into $49 product |

### Strategic Plays (Needs Planning)

| Idea | Priority | Status |
|------|----------|--------|
| **SCN Partnership** | Medium | Greenlit — outreach to Avi Gaba |
| **Travala MCP Travel Agent** | Medium | Accelerates travel API by weeks |
| **Condor Evaluation** | Medium | Could accelerate Agent Arena execution layer |
| **Agents as RWAs Thesis** | Medium | Geo-politics window is closing |
| **Agent Finance Intermediary** | High | $12K-360K/yr potential — biggest play |
| **Virtuals ACP Integration** | Medium | $481M market waiting |
| **Gepard TTS** | Low | Self-hosted voice replacement |

### Quick Hits in the Vault

| File | What It Is | Do With It |
|------|-----------|------------|
| `09-IDEAS/` (root) | Duplicate of `Gentech/09-Green Room/` | Delete |
| `deals/`, `games/`, `analytics/` (root) | Old separate project dirs | Archive or delete |
| `website/`, `src/`, `scripts/` (root) | Old website build artifacts | Clean up if unused |

---

## Recommendation

**Short session tonight:** Send Donut app + Atelier listing + fix Cloudflare waitlist → 2-3 easy wins before dinner.

**If you want to dive:** Start wrapping the DeFi Intelligence API — we already have all the BlockRun tools, just need an endpoint and a PAY.md.
