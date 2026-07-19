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
- [x] **Course outline drafted**: `09-Green Room/designs/gentech-academy-course-design.md` (6 modules, 3 pricing tiers, distribution plan)

## x402 Gateway — Paid API Platform as a Product 💰

- [ ] **Concept**: "Stripe for AI agents" — any dev can deploy their API behind an x402 paywall in 10 minutes
- [ ] **What it replaces**: Custom Cloudflare Worker, custom verification logic, VPS setup, pricing config
- [ ] **MVP**: A single `npx create-x402-api my-api` command that scaffolds everything
- [ ] **Revenue**: % of each transaction OR flat $49/mo
- [ ] **Competition**: Nobody has this yet. Coinbase has the protocol, but no "deploy your API" tooling.

---

## Completed

- [x] Bitrefill awesome-agentic-payments PR (live at #26)
- [x] KeeperHub Hackathon — added to build queue (July 27)
- [x] Build queue v2 — canonical JSON, tick script, auto handoff
- [x] x402 Gateway v7.0.0 — deployed, verified, audited (GLM-5.2)

## Inference Farming — GPU Compute as a Yield Strategy 🧠

- [ ] **Concept**: Rent GPU compute → supply to decentralized inference networks → earn yields (next meta after perp farming)
- [ ] **Why now**: Open models (Kimi K3) hit frontier quality at fraction of cost → inference volume shifts to decentralized networks → farmers needed to supply compute
- [ ] **Projects to explore**: Dolphin AI, SN53 Engy (Bittensor subnet), AntSeed AI
- [ ] **Our angle**: Agent economy stack (ERC-8004, x402) maps directly to inference network needs — identity, settlement, payments
- [ ] **First step**: Research in Labs — pick one network, test the farming mechanics, evaluate ROI vs DeFi LP
