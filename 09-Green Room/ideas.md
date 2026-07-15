# 🧠 Green Room — Ideas to Build

> Checkbox list of things to explore. Build first, talk later.

---

## 🎓 GenTech Academy — Module 1: "Ship a Compliant x402 API"

- [x] **Syllabus drafted**: `09-Green Room/academy-module-1-shipping-x402.md` — 5 parts, 4 pricing tiers
- [x] **Test harness deployed**: `test.api.gentechlabs.net` — free reference endpoint for students
- [ ] **Compliance Checker packaged**: Turn 42-check script into `pip install x402-compliance-checker`
- [ ] **Checklist web UI**: Public page where devs paste their endpoint URL → instant scan results
- [ ] **Academy landing page**: One-pager at academy.gentechlabs.net
- [ ] **Discord server**: Community for alumni + support
- [ ] **First paying student**: Validate $49 Standard tier pricing

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
