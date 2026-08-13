# Connector: CDP Bazaar / Agentic Market — Coinbase x402 Marketplace

> **Source:** https://agentic.market (Coinbase-backed, also "Coinbase Bazaar")
> **Status:** ✅ Settle→index flow documented; not yet listed (permissionless)

## What it catalogs

An **x402 marketplace** backed by Coinbase. Agents discover and pay for x402 APIs.
**$52M+ TPV, 14k+ monthly txns** — the most active x402 marketplace. Permissionless
listing: validate your endpoint → publish. No review process.

## The settle→index flow (the key gotcha)

- **Settle through the CDP facilitator** → the marketplace **indexes you**.
- The manifest needs `paymentPayload.resource` set correctly for the settle→index
  handoff to work.
- **Auto-indexing:** Agentic Market may already crawl our manifest at
  `https://api.gentechlabs.net/.well-known/x402-bazaar` — we may already be findable.

## Requirements

- **x402 payment only** — no API keys, no accounts. Service needs an x402 endpoint.
- **Validate endpoint** — use their validator tool before listing.
- **Base network** — all current services run on Base.

## The flow

1. **Validate** our x402 gateway endpoint on Agentic Market's validator.
2. **List** the GenTech x402 Gateway.
3. **List individual services** (Compliance Scanner, Credit Score, etc.).

## Gotchas we hit

1. **`paymentPayload.resource` is required** for the settle→index handoff — if it's
   missing, the marketplace won't catalog you after settlement.
2. **Base-only** — services on other chains won't list until the marketplace
   expands rails.

## Our status

- x402-bazaar manifest ready at `https://api.gentechlabs.net/.well-known/x402-bazaar`.
- **Next:** validate endpoint + list the gateway + individual services.
