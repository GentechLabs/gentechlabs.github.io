# Connector: Syra — Multichain Agent Infrastructure

> **Source:** https://syraa.fun/marketplace
> **Status:** 🟡 FLESHED (2026-08-22 Nightly) — registration is Jordan-GO'd and queued; exact payload still to be captured live when we execute

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

- Queue #15 (register GenTech x402 services on Syra, orig #22) — **shipped** in the build queue (Jordan GO Aug 3, un-gated, workable overnight).
- **State of the play:** the registration item is greenlit and marked shipped in the queue, but the *exact payload/registration fields* have not been captured live yet — we haven't completed the on-chain ERC-8004 identity registration step required to list on Syra.
- **Blocker:** Syra is invite-gated. Need the invite code (Discord `discord.gg/aMSEG7yj` or @krexa_xyz open drops) or a Syra registration window before the on-chain identity step can run. Same invite path as Krexa (queue notes).
- **Next:** (1) secure Syra invite, (2) register on-chain ERC-8004 identity, (3) create a skill with `payToAddress` set, (4) capture the exact payload/registration fields here as the Connector Pack chapter.
- **Candidate service:** token_security or wallet_analysis (both x402-ready, gateway-served) as the first listed skill.
