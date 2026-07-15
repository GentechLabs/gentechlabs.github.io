# 🧠 Green Room — Ideas to Build

> Checkbox list of things to explore. Build first, talk later.

---

## GenTech Academy — "Ship Paid APIs in a Weekend" Course 🎓

- [ ] **Concept**: Turn our 1.5-month x402 gateway journey into a reusable course/guide
- [ ] **What it teaches**: How to set up paid APIs with x402, Cloudflare Workers, on-chain payment verification, VPS proxying
- [ ] **Why it's a business**: This took us 6 weeks of painful trial and error. Most devs won't do it. There's a market for "one-click paid API" setup.
- [ ] **Possible product**: 
  - Free GenTech Academy guide (content marketing)
  - Premium: "x402 Starter Kit" — pre-built worker + config + deploy script ($49)
  - Enterprise: "Deploy your APIs as x402 services" — we do it for them ($499+)
- [ ] **Assets needed**: Tutorial video, worker template, wrangler config template, deployment guide
- [ ] **Vault reference**: `09-Green Room/x402-gateway-architecture.md`

## x402 Gateway — Paid API Platform as a Product 💰

- [ ] **Concept**: "Stripe for AI agents" — any dev can deploy their API behind an x402 paywall in 10 minutes
- [ ] **What it replaces**: Custom Cloudflare Worker, custom verification logic, VPS setup, pricing config
- [ ] **MVP**: A single `npx create-x402-api my-api` command that scaffolds everything
| **Revenue**: % of each transaction OR flat $49/mo
| **Competition**: Nobody has this yet. Coinbase has the protocol, but no "deploy your API" tooling.

## x402 Compliance Checker & Onboarding Service ✅

- **x402 Compliance Checker** — **SHIPPED** ✅ CLI tool at `10-Labs/x402-compliance-checker.py`
  - Scans any endpoint for x402 v2 spec compliance
  - Checks Payment-Required header, 402 body, /.well-known/x402
  - Generates fix templates
  - 42+ checks per endpoint
  - Used by x402 Compliance Scout cron
- [ ] **Why**: We discovered our own 15 endpoints all had format issues (missing accepts[], Payment-Required header). Every seller on x402scan (46K of them) likely has the same gaps.
- [ ] **What it does**:
  - Probe an API endpoint → validate x402 v2 response format
  - Generate missing `/.well-known/x402` file
  - One-click registration on x402scan, Syra marketplace, etc.
  - End-to-end test: 402 → sign → retry → success
- [ ] **Revenue**: Free scan → paid fix ($19 one-time or $9/mo monitoring)
- [ ] **Academy tie-in**: Module 1 of GenTech Academy — "Ship a Compliant x402 API"

## Game Port Restoration Service — "Fix My Game" 🎮

- **Status**: 🔴 New — Needs scoping
- **Why**: Sonic Heroes won't load on modern PCs. The retro gaming community is massive, underserved, and scattered across forums. Nobody has branded "we fix your game" as a service.
- **Tier**: $2-5 (single game fix pack), $10-20 (concierge), $25 (bundle)
- **Connection**: GenTech Shop retro gaming vertical, x402 payments, gets eyes on our stack
- **First target**: Sonic Heroes PC port fix (d3d8 wrapper, widescreen patch, controller config)
- **Next step**: Scope what Sonic Heroes specifically needs to run on Windows 10/11
- [ ] **Status**: 🔴 PRIORITY — directly feeds our first paying customer pipeline

---

## Completed

- [x] Bitrefill awesome-agentic-payments PR (live at #26)
- [x] KeeperHub Hackathon — added to build queue (July 27)
- [x] Build queue v2 — canonical JSON, tick script, auto handoff
- [x] x402 Gateway v7.0.0 — deployed, verified, audited (GLM-5.2)
