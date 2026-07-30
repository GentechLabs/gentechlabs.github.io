# GenTech Labs — Marketplace Audit

**Date:** 2026-07-29
**Purpose:** Track every marketplace we're listed on, what's live, what needs updating.

---

## 1. OKX AI Marketplace ✅ — Registered

**Type:** A2MCP (Agent-to-MCP) — pay-per-call API
**Status:** Registered, needs review — agent rejected (offline)
**URL:** https://www.okx.ai/

### Requirements
- **A2A node** (24/7 daemon) — OKX pings your agent for uptime verification. Without it, listings are rejected.
- **Node 22.14.0+** — `@okxweb3/a2a-node` enforces this at install.
- **Sampling calls** — OKX may send test requests from their wallets for quality verification (Section 7.7). No payment for these.
- **Review process** — every listing goes through manual/automated review. Rejection is fixable: update → re-activate.

### Fix Path (current rejection)
```
npm i -g @okxweb3/a2a-node
okx-a2a doctor --fix
# Daemon stays running 24/7
```
Then resubmit via chat.

### Current Listing
- ASP "Gen Tech Strategies" — A2MCP mode
- Rejected: agent offline (no A2A node)

### Needs Update
- [x] A2A node installed (daemon running)
- [ ] Add x402 Compliance Scanner endpoint
- [ ] Add Agent Credit Score API
- [ ] Update description with 16-endpoint gateway

### Action
- [x] Install A2A node
- [ ] Confirm daemon stays live after reboot
- [ ] Resubmit for review
- [ ] Update service endpoints

---

## 2. Swarms Marketplace ✅ — Listed

**Type:** Agent listing
**Status:** Live, needs update
**URL:** https://swarms.world/agent/72be9677-82f7-404b-b52f-86ab36dcf6c4
**Agent Name:** defi-lp-monitor

### Requirements
- **Manual edit** — no automated API for updates. Jordan logs in and edits.
- **x402 toggle** — available but not enabled. Must turn on for pay-per-call.
- **No strict uptime SLA** — listing-based, less stringent than OKX.

### What Needs Updating
- Name: `defi-lp-monitor`
- Price: $9.99 one-time
- No x402 toggle enabled
- Old description

### What Needs Updating
| Field | Current | Should Be |
|-------|---------|-----------|
| Name | defi-lp-monitor | GenTech Labs x402 Gateway |
| Description | Old LP monitor | 16-endpoint x402 gateway |
| Pricing | $9.99 one-time | x402 pay-per-call |
| Tags | — | x402, mcp, gateway |
| x402 toggle | Off | On |
| Integration URLs | — | Add `.well-known/x402-bazaar` |

### Action
- [ ] Jordan logs into Swarms → Edit Agent → update fields
- [ ] Enable x402 toggle
- [ ] Add discovery URLs

---

## 3. x402 Bazaar ✅ — Indexed

**Type:** x402 service discovery
**Status:** Live, auto-indexed
**URL:** https://api.gentechlabs.net/.well-known/x402-bazaar

### Requirements
- **Stateless HTTP** — no daemon, no uptime check. Just serve the manifest.
- **Auto-indexed** — no listing/review process. Manifest is crawled.
- **Zero maintenance** — update manifest → new services appear automatically.

### Current
- 16 endpoints listed
- 5 pricing tiers
- 5 supported chains
- Bazaar manifest auto-serves

### Status
No action needed.

---

## 4. Atelier ✅ — Registered (useatelier.ai)

**Type:** AI Agent Marketplace (Solana)
**Status:** Registered, credentials saved
**URL:** https://useatelier.ai/
**Agent ID:** `ext_1783295225717_09ms3exvh`
**API Key:** Saved at `Gentech/00-HQ/atelier-credentials.md`

### Requirements
- **API key-based** — registered with credentials, deployed on VPS
- **Solana-focused** — Solana native ecosystem
- **No uptime SLA** — profile-based listing

### Current
- Registered as an agent
- Credentials stored for VPS deployment

### Needs Update
| New Capability | Should We Add? |
|----------------|----------------|
| x402 Gateway (16 endpoints) | ✅ Yes — list as services |
| Compliance Scanner | ✅ Yes |
| Agent Credit Score | ✅ Yes |
| Gaming APIs | ✅ Yes |

### Action
- [ ] Log into useatelier.ai and review current agent profile
- [ ] Add new services to listing
- [ ] Update description with current capabilities

---

## 5. Awesome Lists — Multiple PRs (Mixed Status)

**Type:** Ecosystem directory listings via PR

### Live (Merged)
| Repo | PR | What | Status |
|------|----|------|--------|
| bitrefill/awesome-agentic-payments | #26 | GenTech Labs listed | ✅ Merged |
| xpaysh/awesome-x402 | #701 | GenTech Labs in Ecosystem | ✅ Merged |
| gold-402 | #39 | Add GenTech x402 Gateway | ✅ Merged |

### Submitted (Open)
| Repo | PR | What | Status |
|------|----|------|--------|
| heilcheng/awesome-agent-skills | #361 | GenTech Agent Kit | 🟢 Open |
| 0xNyk/awesome-agent-cortex | #43 | Agent Kit in Identity & Wallets | 🟢 MERGEABLE |
| 0xNyk/awesome-agent-cortex | #44 | x402 Gateway in Payments | 🟢 MERGEABLE |
| xpaysh/awesome-x402 | #761 | Agent Kit + Gateway | 🟢 MERGEABLE |
| xpaysh/awesome-x402 | #881 | Gateway in Production Deployments | 🟢 MERGEABLE |
| e2b-dev/awesome-ai-agents | #1264 | Agent Kit in Agent list | 🟢 MERGEABLE |
| Scottcjn/awesome-agents | #40 | x402 Gateway | 🟢 Submitted |
| caramaschiHG/awesome-ai-agents-2026 | #455 | Agent Kit in Protocol Tooling | 🟢 Submitted |
| ARUNAGIRINATHAN-K/awesome-ai-agents-2026 | #171 | Agent Kit in Agent Tooling | 🟢 Submitted |

### Failed (Never Submitted — Forks Deleted)
| Repo | Intended PR | Why |
|------|-------------|-----|
| VaitaR/awesome-web3-services | #1 | Fork deleted, rate limited |
| 0xNyk/awesome-agent-cortex | #44 (second) | Fork deleted |
| Scottcjn/awesome-agents | #36 (replaced by #40) | Fork deleted |
| caramaschiHG/awesome-ai-agents-2026 | #443 (replaced by #455) | Fork deleted |

### Action
- [ ] Monitor open PRs for merge
- [ ] Re-submit failed PRs if needed

---

## 6. Agentic Market (Coinbase-backed) ⏸️ — Not Listed Yet

**Type:** x402 marketplace (Coinbase Bazaar)
**URL:** https://agentic.market
**Status:** Not listed — but we should be

### Requirements
- **x402 payment only** — no API keys, no accounts. Service needs x402 endpoint.
- **Validate Endpoint** — use their validator tool before listing
- **Base network** — all current services run on Base
- **No review process** — permissionless listing (validate endpoint → publish)
- **$52M+ TPV** — active marketplace, 14k+ monthly txns

### Action
- [ ] Validate our x402 gateway endpoint on Agentic Market
- [ ] List GenTech x402 Gateway
- [ ] List individual services (Compliance Scanner, Credit Score, etc.)

### Notes
- Coinbase Bazaar and Agentic Market are the same thing — Coinbase-backed
- Our x402-bazaar manifest is ready at `https://api.gentechlabs.net/.well-known/x402-bazaar`
- Agentic Market auto-indexes, so we may already be findable if they crawl our manifest

---

## 7. Agentic.Market — Not Listed

**Type:** x402 marketplace (Coinbase-backed)
**URL:** https://agentic.market
**Status:** Not listed yet

### Action
- [ ] Consider listing — new marketplace, early mover advantage

---

## Summary

| Marketplace | Status | Needs Update? | Priority |
|-------------|--------|---------------|----------|
| OKX AI | ✅ Registered | Maybe — review listing | Medium |
| Swarms | ✅ Listed | **Yes** — stale listing | High |
| x402 Bazaar | ✅ Indexed | No — auto-updates | None |
| Atelier | ✅ Registered | Maybe — review profile | Medium |
| Awesome Lists | ✅ 3 merged, 9 open | Monitor for merges | Low |
| Coinbase Bazaar | ❌ Not listed | Consider adding | Low |
| Agentic.Market | ❌ Not listed | Consider adding | Low |
