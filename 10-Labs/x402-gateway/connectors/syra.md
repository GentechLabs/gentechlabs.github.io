# Connector: Syra — Multichain Agent Infrastructure

> **Source:** https://syraa.fun/marketplace
> **Status:** 🔜 Pending — after queue #22 ships (register GenTech x402 services)

## What it catalogs

**"Machine Money for Agents"** — every AI agent operates on any chain, earns
revenue, interacts frictionlessly. Expanded to **Algorand** (Aug 6) beyond Solana +
Base — validates our multichain thesis.

## The listing model (the key gotcha)

- **On-chain identity + ERC-8004/SAP + payToAddress** — Syra uses on-chain identity,
  not a simple API-key registration.
- **Creator skills with payToAddress** — you register skills that carry a
  `payToAddress` for settlement.
- **MCP server + SDK** for agent access.

## The flow

1. **Register on-chain identity** (ERC-8004 agent identity).
2. **Create skills** with `payToAddress` set.
3. **List on the marketplace** — agents discover + pay via the skill.

## Gotchas we hit

1. **On-chain identity is mandatory** — this is not a flat API-key marketplace.
   You need ERC-8004/SAP set up first.
2. **Multichain** — Syra now spans Solana + Base + Algorand. Match your skill's
   chain to where your gateway settles.

## Our status

- Queue #22 (register GenTech x402 services on Syra) — pending.
- **Next:** after #22 ships, write the exact payload/registration fields here.
