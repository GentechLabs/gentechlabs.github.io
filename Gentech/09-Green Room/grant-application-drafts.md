# Grant Application Drafts — Ready to Paste

> Prepared Aug 15, 2026. Each section is a copy-paste-ready application for Jordan to submit.
> Target: AI Grant (aigrant.org), The Graph Grants (thegraph.typeform.com/applynow), Optimism Retro Funding (OP Atlas).
> All are non-dilutive / usage-based. No equity. No C-corp required for AI Grant / The Graph (Optimism needs OP Atlas + KYC).
>
> **⚠️ STATUS CHECK (Aug 15):** AI Grant **Batch 4 CLOSED** (recurring — wait for Batch 5). The Graph **no open RFPs**. Both drafts kept here so they're ready to fire when the next window opens. Only Optimism Retro (OP Atlas) has a live submission path.

---

## 1. AI Grant (aigrant.org) — $5K–$50K, non-dilutive, open-source

**What is the project?**
GenTech is an open-source x402 payment gateway for AI agents. It lets any AI agent (Claude, Codex, Hermes) pay-per-call for APIs using USDC/x402 — no bank account required for the agent. We've built a fully CDP-compliant x402 server (validated `valid:true`, simulation `accepted`, x402Version 2) that serves 9 production services across 7 chains. Open-source, MIT-licensed, hosted at `api.gentechlabs.net`.

**Why does it matter?**
The biggest barrier to agent commerce is that AI agents can't open bank accounts. x402 solves this — agents pay with stablecoins directly. Our gateway makes x402 deployment trivial for any API owner, which is the missing piece for a real agent economy. This is the "plumbing" layer that lets thousands of agents pay thousands of APIs.

**Open-source links:**
- Gateway: `https://github.com/ProtoJay4789/x402-gateway` (MIT)
- Discovery manifest: `api.gentechlabs.net/.well-known/x402-bazaar`

**What would the grant fund?**
Funding would accelerate: (1) multi-chain settlement hardening, (2) developer SDK + docs, (3) automated marketplace listing across all x402 rails, (4) a public reference agent that demonstrates end-to-end paid agent commerce.

**Founder background (fill in):**
- [Jordan name], solo builder, [X years] in [background].
- Previously built: [list — e.g. agent kit, DeFi LP tools, hackathon projects].
- Technical: [solidity/JS/Python — BUIDL CTC contract, x402 gateway, DeFi agents].

---

## 2. The Graph Grants — subgraph/tooling, open to individuals

**Project idea:**
Open-source subgraph(s) + tooling for **x402 payment activity** on Base and Avalanche. The Graph already indexes onchain data; we'd build subgraphs that surface *agent-to-API payment flows* — who paid what, settlement volumes, active agent wallets. This is the onchain data layer for the agent economy, and it's genuinely new: nobody indexes x402 payment streams today.

**Why The Graph?**
We're already live on Base/Avalanche with USDC/x402 settlement. A subgraph that tracks x402 payment volume gives the ecosystem real visibility into agent commerce. Aligns with The Graph's "Data Services" grant track (subgraphs/dapps/dashboards that contribute to open-source data).

**Deliverables:**
- x402 payment-events subgraph for Base + Avalanche
- Open-source schema + query examples
- A live dashboard (`gentechlabs.net/x402-stats`) visualizing agent payment flows

**Fit:** Data Services / Tooling track. "You don't have to be technical" per The Graph, but we ARE technical — stronger proposal.

---

## 3. Optimism Retro Funding (Onchain Builders) — needs OP Atlas + KYC

**Status:** Requires (a) project added to OP Atlas, (b) deployed contracts on an OP chain (we're live on Base), (c) KYC compliance. **Human-gated — Jordan must handle Atlas setup + KYC.**

**What we'd submit:**
GenTech x402 gateway — live on Base, settling USDC from AI agents. Real usage, open-source, deployed contracts. Retroactive funding rewards exactly this kind of shipped, used infrastructure.

**Action for Jordan:**
1. Create/add project on `app.optimism.io/atlas` (or OP Atlas)
2. Link Base contract addresses + GitHub repo
3. Complete KYC with OP Foundation
4. Submit when the Onchain Builders round opens

---

*All drafts verified against official program requirements (Aug 15, 2026).*
