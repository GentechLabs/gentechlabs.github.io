---
title: GTA Product Thesis — Open Execution + Authorized Proxy
date: 2026-08-03
status: thesis (drives build)
owner: Jordan + Gentech
related: [gta-execution-engine-build-plan, agentic-arbitrage, gentech-subscription-tiers]
---

# GTA — GenTech Trading Agent: Open Execution + Authorized Proxy

> **One-line thesis:** GTA is the **open execution + authorized-proxy layer** — your
> agent does everything for you across every venue you're legally entitled to use,
> without you needing to be in the room or tied to a single platform.

**Why this is the bigger, brighter version (Jordan, Aug 3):** The market wants you to
pick ONE platform and trade on it. GTA makes that the wrong move by being
**chain-agnostic across every agent-native rail**. We sit *between* the onramps
(Coinbase, Robinhood, Polymarket, Ondo) arbitraging the basis — and CLARITY only
makes that gap richer by deepening US-regulated venues.

---

## The three-layer model

### Layer 1: Open Aggregation & Execution (the core, buildable now)
GTA taps into every venue that exposes **agent-native rails** — no per-user account
setup needed because *we* hold the accounts/wallets and let agents trade through us.

| Venue | Leg | Status |
|-------|-----|--------|
| **Coinbase** (CDP) | Spot | ✅ LIVE — verified key + cbBTC leg working |
| **Robinhood** (MCP) | Perps / RWA | ⏳ Jordan completing KYC/OAuth |
| **Polymarket** | Prediction / UP-DOWN | ⏳ US-legal, ready to wire |
| **Ondo Perps** | RWA perps | 🔭 when API releases |
| **Hyperliquid** | Perp price signal | 🧭 detection-only (execution = US gray zone) |

**Design principle:** venue-agnostic. Swap the venue in config, keep the agent logic.
Same GTA reasoning layer, different execution rail.

### Layer 2: Authorized Proxy (the concierge-agent, the differentiator)
The "agent as VPN" insight, reframed cleanly:

- **Agents don't have a home address** — they operate from an IP, but nothing binds
  that IP to a person. So an agent can legitimately act on your behalf from wherever
  it runs, on accounts you're authorized to use.
- **It's a remote operator you granted permission to — NOT a mask hiding you.**
- **Account-linked sessions** (Composio's open-sourced skill stack / OAuth / saved
  login) let the agent *sign into and operate* your accounts: pay bills, file forms,
  move money, access what you're entitled to — so you never have to.

**Same power as a VPN concierge, zero ToS-evasion.** The pitch:
> "Your agent does everything for you, anywhere you're legally entitled to operate."

### Layer 3: Agent Intelligence (the data layer — built with agents IN mind, Jordan, Aug 3)
> *"I made the layers with people in mind, but I didn't think about — with all this
> data, all these ways of identifying agents, we can see how they trade and give that
> data back to users, or whoever wants to know."*

Layers 1 & 2 were designed around **people** as users and **venues** as rails. Layer 3
recognizes that **agents are also participants** — and their behavior is measurable,
first-class data:

- **We already collect every trade GTA and connected agents execute** — that's an
  agent-flow dataset, not just a P&L ledger.
- **We can identify agents** (the a2a / ERC-8004 / trust-layer identity work) — so
  agent trades are attributable, not anonymous noise.
- **Agent sentiment / flow index** (see `agent-arena-vision.md`) — net positioning,
  confidence, and agent-vs-human divergence become a **proprietary data product**
  we sell or expose, feeding GTA's own reasoning AND external users.

**The reframe:** the layers aren't just "how GTA trades for a person." They're also
**"how GTA reads the market — including what other agents are doing."** The data
collected in Layers 1 & 2 becomes the input to Layer 3's signal. This is what makes
The Agency of Traders a platform, not a trader.

---

## Granular permissions (the trust substrate — non-negotiable)

The thing that keeps this a product and not a liability:

| Level | What the agent can do |
|-------|----------------------|
| **Read** | View balances, prices, statements |
| **Trade** | Place/cancel orders, swaps |
| **Move** | Transfer between venues, bridge funds |
| **Withdraw / pay** | Outbound transfers, bill-pay — HIGHEST bar, explicit per-action |
| **Cold storage** | Never — funds stay under Jordan's custody |

- User authorizes once per account (OAuth / saved session), stays in control of links
- **Trade-only keys** where supported (can place/cancel, cannot withdraw)
- Withdrawals always require explicit confirmation — the agent never moves funds out
  without a human yes

---

## Strategic positioning

- **CLARITY Act** → deepens US venues (Coinbase/Robinhood/Ondo/Polymarket), moving the
  arb opportunity ONTO rails we can trade cleanly. Offshore access becomes optional,
  not required.
- **Offshore edge** (HL/Bybit/dYdX) → keep as a *capability we're ready for*, NOT the
  pitch. Don't build a business on helping users bypass ToS.
- **Competition framing** → everyone picks one platform; we arbitrage *between* them.

---

## Build order (this thesis drives the build)

1. ✅ Coinbase spot leg (live)
2. ⏳ Robinhood perp leg (needs Jordan KYC/OAuth)
3. 🔭 Composio / account-session research (authorized-proxy plumbing)
4. 🔭 Polymarket + Ondo rails
5. 🔭 Granular-permission wallet layer
6. 🔭 **Layer 3 seed — agent-flow dataset**: log every GTA/connected-agent trade with agent attribution (from day one, even before it's a product) so the data exists when we want to build the sentiment index. Cheap to start, expensive to retrofit.
7. 🔭 **Agent sentiment / flow index** — the Layer 3 data product (see `agent-arena-vision.md`)

## Strategic signal — BlackRock BRSRV (Aug 6, 2026): the enterprise "home"
BlackRock launched **BRSRV** (Daily Reinvestment Stablecoin Reserve Vehicle) — an
institutional fund backing stablecoins, invested in cash + short-term Treasuries +
overnight repos, built to qualify as a reserve asset under the GENIUS Act. Ownership
is recorded on **Solana, Ethereum, and Tempo**.

**Jordan's read (confirmed):** "Enterprise is gonna want their own home." Institutional
money wants a *controlled box* — their own custody, compliance, reporting — not a
public free-for-all. The chains are just the settlement rails underneath.

**Why this strengthens our thesis, not weakens it:**
- The enterprise "home" still needs a payment rail to move in/out. Someone has to be
  the tollbooth between the institutional vault and the public chains — per-tx,
  auditable, gasless. **That's the x402 middleware layer we're building.**
- **The home is the product, the rail is the moat.** Enterprises build their own
  custody/compliance boxes; they won't build settlement rails (too expensive, too
  risky). The middleware connecting box → chain is where the recurring fee lives.
- **Tempo's inclusion is the tell.** BlackRock picked a non-EVM rail alongside Solana
  and Ethereum → **multi-rail is a first-class requirement, not a nice-to-have.**
  GTA must be rail-agnostic by design — settle wherever the counterparty lives.

**Play:** don't compete with the enterprise home — be the door they walk through.

## Status
🟢 Thesis confirmed by Jordan (Aug 3). Drives the execution-engine + demo build.
**Next:** Composio research (open-sourced account-sign-in stack) to unlock Layer 2.
