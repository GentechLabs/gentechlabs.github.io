# 🤖 GenTech AI DeFi Agent — "The Agency of Traders"

**One agent, one coherent stack, feeding four builds.**

An autonomous AI DeFi agent that analyzes markets, reads on-chain state, and
settles decisions — with every layer decentralized and agent-native.

## The unified stack

| Layer | Tech | Role |
|-------|------|------|
| **Settlement** | **Kite AI** | Agentic-payment L1 — Agent Passport identity, stablecoin rails, programmable policy. The machine-money loop. |
| **AI Compute** | **0G Compute** | Decentralized LLM inference (DeepSeek V3.1, Qwen, Gemma) for market analysis |
| **Storage** | **0G Storage** | Persistent agent memory + trade log (Merkle-verified) |
| **Chain** | **0G Chain** | EVM-compatible L1, agent identity (ERC-7857), settlement |
| **RPC** | **Goldsky** (via Circle for Agents) | Pay-per-call multi-chain JSON-RPC, $0.005/call, x402 v2 |
| **Payments** | **Circle USDC** | The rail — agent pays agent, no human checkout |

## The loop

```
0G Compute (analyze market)
        │
        ▼
Goldsky RPC (read on-chain state, multi-chain)
        │
        ▼
Kite AI (settle the agent's decision — stablecoin payment)
        │
        ▼
0G Storage (persist trade log, Merkle-verified)
```

## Feeds four builds

1. **0G Bridge Buildathon — Wave 3** ($15K) — "AI DeFi dashboards or trading bots" track. 30% of score = 0G stack integration (we use Compute + Storage + Chain).
2. **Midnight Buildathon** ($12.5K) — privacy-first angle: agent identity + selective disclosure on the settlement layer.
3. **Circle Agentic Economy prize** (in Build with Gemini XPRIZE) — the agent-pays-agent machine-money loop, live.
4. **Goldsky resell** — wrap Goldsky's pay-per-call RPC behind our own x402 endpoints, charge a markup. Pure middleware margin.

## Quick start

```bash
npm install
cp .env.example .env   # fill in PRIVATE_KEY, RPC_URL, PROVIDER_ADDRESS
npm run agent          # run the loop (dry-run settlement)
```

## Status

- [x] 0G SDK wired (`@0glabs/0g-serving-broker`, `@0glabs/0g-ts-sdk`) — verified loads
- [x] Goldsky x402 rail verified — returns proper x402 v2 challenge (USDC, $0.005/call)
- [x] Agent scaffold — 0G Compute analysis + Goldsky RPC read + Kite settlement (dry-run)
- [ ] Fund agent wallet (0G testnet + Circle USDC)
- [ ] Real 0G Compute inference call
- [ ] Real Goldsky paid call
- [ ] Kite AI Agent Passport registration
- [ ] Deploy + demo video for Wave 3 submission

## Files

- `src/agent.ts` — the unified agent loop
- `src/analyze.ts` — 0G Compute market analysis
- `src/deploy.ts` — 0G Chain contract deploy
- `contracts/` — Solidity (ERC-7857 agent identity)
- `.env.example` — config template (never commit real keys)
