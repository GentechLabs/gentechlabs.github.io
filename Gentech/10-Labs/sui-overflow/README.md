# Sui Overflow 2026 — x402 Agent Kit Plugin

**Track:** Agentic Web + DeFi & Payments
**Deadline:** August 15, 2026
**Prize:** $30K / $15K / $10K / $7.5K per track
**Stack:** Sui Move + TypeScript + x402

---

## What We're Building

A **Sui x402 plugin** for the GenTech Agent Kit that enables AI agents to:
1. **Pay** for services via USDC on Sui using x402 micropayments
2. **Receive** payments for their own services
3. **Query** balances, transaction history, and agent identity on Sui

## Architecture

```
Agent ──► Sui x402 Plugin ──► Sui RPC
              │
              ├── pay.ts        — Send x402 payment
              ├── receive.ts    — Handle incoming x402
              ├── balance.ts    — Query USDC/SUI balances
              ├── identity.ts   — Agent registration on Sui
              └── utils.ts      — RPC client, key management
```

## Why Sui

- **Object model** — perfect for agent identity (each agent = unique object)
- **High throughput** — 120K+ TPS, sub-second finality
- **DeepBook** — native on-chain orderbook for DeFi
- **Walrus** — decentralized storage for agent metadata
- **x402 compatible** — USDC on Sui via Wormhole/Circle CCTP

## Files

| File | Purpose |
|------|---------|
| `src/plugin.ts` | Main plugin entry point |
| `src/pay.ts` | x402 payment sender |
| `src/receive.ts` | x402 payment receiver |
| `src/balance.ts` | Balance queries |
| `src/identity.ts` | Agent registration |
| `src/utils.ts` | RPC client, helpers |
| `test/plugin.test.ts` | Tests |
| `README.md` | Docs |
| `wrangler.toml` | Cloudflare deploy config |
