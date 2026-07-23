# Forge Handoff — July 22-23 Night Session

## Date: 2026-07-23
## From: Gentech (running on OpenCode Go — Ollama Cloud capped)
## To: Forge

---

## Model Routing — TAS v2

**Stack changed today:**
- 🥇 **Ollama Cloud** (primary, $0, 100/wk) — burned through in 3 days, resets ~Jul 26
- 🥈 **OpenCode Go** (fallback, $10/mo, 1,000/mo) — currently active, 63% used, 17 days left
- ❌ **Nous axed** — saved $20/mo. Total stack: $10/mo
- **V2 logic**: Pre-emptive switching at 85-90% cap, not on failure
- **Auto-return** to Ollama Cloud when it resets

Jordan needs to run `hermes fallback add` on his machine to re-add OpenCode Go as the sole fallback (I cleared Nous from the VPS side).

---

## ✅ Completed Tonight

### Victus Global — Robinhood Ecosystem Fund ($10M)
- Jordan DMed them after their fund announcement, they moved to Telegram
- $TREASURY passes their minimum requirement (token must be trading on Robinhood Chain)
- **Active conversation** — they asked for the trading link
- Prep doc saved: `10-Labs/victus-global-call-prep.md`
- **Key ask**: Liquidity support for $TREASURY pool ($50-100K)

### Circle Grant Application (2026 Cohort 2)
- Full 7-section draft completed for Circle's grant program
- Investor deck created: `gentechlabs.net/investor-deck.html` (10-slide reveal.js)
- Key integrations: USDC (live), CCTP (planned), Arc (planned), Programmable Wallets (planned)

### Website — Hub Page Updated
- Added **"7 Chains"** badge and **"Multi-Chain Agent Treasury"** section
- ⚠️ **Cloudflare Worker issue** — The `gentechlabs-api` Worker intercepts root traffic. Jordan needs to remove the root domain route.

### OKX A2A Agent — Fixed for 24/7 Uptime
- "Gen Tech Strategies" rejected because it wasn't online 24/7
- **Fixed on VPS:**
  - Node.js upgraded to v22.14.0
  - `@okxweb3/a2a-node` installed
  - A2A daemon running (pid 2777058)
  - Systemd service for auto-start on boot
  - Onchain OS skills installed
- **Needs Jordan**: Restart Hermes (`/restart`), register agent with Onchain OS, resubmit

### Composio — Discovered as Distribution Multiplier
- 500+ app integrations through one MCP server
- **Build queue #68**: Composio x402 Payment Connector
- Vision: Every Composio user can accept USDC micropayments through our gateway

---

## Build Queue Status
- **36 items total** — 0 shipped, 1 in progress, 25 pending, 10 blocked
- **4 duplicates identified** (#33/#45 CMC, #50/#55 Swarms, #51/#54 Atelier, #52/#56 OKX AI)
- **Needs your help**: Review items Forge completed so we can mark them shipped

---

## ⏳ Priority — Needs Jordan

| Priority | What |
|----------|------|
| 🔴 | **Victus Global Telegram** — Active convo, send trading link |
| 🔴 | **Cloudflare Worker root route** — Remove at dash.cloudflare.com |
| 🔴 | **DNS records** — A records for vanito + portfolio subdomains |
| 🔴 | **Composio OAuth** — Run `hermes mcp login composio` on your machine |
| 🔴 | **OKX A2A resubmit** — Restart Hermes, register agent, resubmit |
| 🟡 | **Circle grant submission** | Review + submit |
| 🟡 | **Fallback re-add** | Run `hermes fallback add` → pick opencode-go |
| 🟡 | **Superteam KYC** | Unlock 100 USDG |
| 🟡 | **Claim Bankr fees** | 0.00322 WETH + 39.21M TREA |

---

## 🔧 Forge's Tasks
- **#58** — Animate $TREASURY token image (Seedance 2.0, desktop GPU)
- **#65** — GenTech OpenClaw Skill (384k-star distribution)
- **#66** — Unity CLI Integration
- **#68** — Composio x402 Payment Connector (start after Jordan auths OAuth)
- **Kagekō 3D** — Visual Kei rhythm game in Unreal 5.8

---

## 📝 Notes
- Three-pillar model: Humans ($3/$10/$25 subs), AI Agents (x402 pay-per-call), Ecosystem (free Treasury)
- Agent economy is crypto's Trojan horse — game devs adopt x402 without caring about blockchain
- Composio + x402 = 500+ apps becoming revenue streams
- Chinese AI ban risk — model-agnostic routing already in place
