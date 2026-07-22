# GenTech Labs — Marketplace Audit

**Date:** 2026-07-22
**Purpose:** Track every marketplace we're listed on, what's live, what needs updating.

---

## 1. OKX AI Marketplace ✅ — Registered

**Type:** A2MCP (Agent-to-MCP) — pay-per-call API
**Status:** Registered, needs review
**URL:** https://www.okx.ai/

### Current Listing
- Registered as ASP (Agent Service Provider)
- A2MCP mode — standardized pay-per-call

### What's Changed Since Listing
| New Capability | Should We Add? |
|----------------|----------------|
| x402 Compliance Scanner | ✅ Yes — new endpoint |
| Agent Credit Score API | ✅ Yes — new service |
| 16 endpoints live (was fewer at listing) | ✅ Update listing |
| Robinhood Agentic Trading | ⏸️ Wait until account is set up |
| Remotion Content Pipeline | ❌ Not an API service |

### Action
- [ ] Review current OKX listing details
- [ ] Add new endpoints to service description
- [ ] Consider A2A listing for custom services (audits, research)

---

## 2. Swarms Marketplace ✅ — Listed

**Type:** Agent listing
**Status:** Live, needs update
**URL:** https://swarms.world/agent/72be9677-82f7-404b-b52f-86ab36dcf6c4
**Agent Name:** defi-lp-monitor

### Current Listing
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

### Current
- 16 endpoints listed
- 5 pricing tiers
- 5 supported chains
- Bazaar manifest auto-serves

### Status
No action needed — auto-indexed. New endpoints appear when we update the manifest.

---

## 4. Atelier ✅ — Registered (useatelier.ai)

**Type:** AI Agent Marketplace (Solana)
**Status:** Registered, credentials saved
**URL:** https://useatelier.ai/
**Agent ID:** `ext_1783295225717_09ms3exvh`
**API Key:** Saved at `Gentech/00-HQ/atelier-credentials.md`

### Current
- Registered as an agent on the marketplace
- Credentials stored for VPS deployment

### What's Changed Since Registration
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

## 6. Coinbase Bazaar — Not Listed

**Type:** x402 marketplace
**URL:** https://bazaar.cdp.coinbase.com
**Status:** Not listed yet

### Action
- [ ] Consider listing our gateway on Coinbase Bazaar
- [ ] Requires bazaar manifest (we have one)

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
