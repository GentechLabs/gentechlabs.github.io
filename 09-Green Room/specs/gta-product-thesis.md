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

## The two-layer model

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

## Status
🟢 Thesis confirmed by Jordan (Aug 3). Drives the execution-engine + demo build.
**Next:** Composio research (open-sourced account-sign-in stack) to unlock Layer 2.
