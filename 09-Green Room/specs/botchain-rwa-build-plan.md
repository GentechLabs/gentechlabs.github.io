# BOT Chain Builder Challenge #2 — AI × RWA Build Plan

**Source:** [Luma event](https://luma.com/238et7cw) · [Challenge Handbook (Notion)](https://app.notion.com/p/BOT-Chain-Builder-Challenge-2-3b246f6c38d5803495bac38b8c078690)
**Date:** 2026-08-06
**Timeline:** Build Aug 10–20 · Submission Aug 20 23:59 UTC+8 · Demo Day Aug 22 · Winners Aug 27
**Prize:** Up to 5,000 USDT (quality-first — awards may be withheld if bar not met)
**Status:** 🟢 Jordan GO (Aug 6) — scoping. Register on Luma.

---

## Why we win

- **Squarely our lane:** x402 middleware, agent economy (ERC-8004), GTA treasury agent. BOT Chain is an AI-native L1 built *for* autonomous agents — the ecosystem wants exactly what we build.
- **RWA is the highest-priority track**, and AI must be a *core* on-chain decision-maker (not chat/API call). An **AI-driven RWA asset-management agent** hits both at once and is a natural GTA evolution.
- **We're not starting from zero:** GTA exec engine, x402 gateway, agent-economy stack all exist. This is a port + integration, not a greenfield build.
- **Learning value (Jordan's point):** BOT Chain's **AI Agent Launchpad V1** — agent wallets earn 80% of trading-fee revenue once their token lists on MemeX — is a deep-end agent-as-a-service model we haven't explored. Worth studying regardless of prize.

## The one hard requirement

**BOT Chain Mainnet deployment is mandatory** — testnet-only projects are excluded from final review. Must also have: public demo site, wallet integration, GitHub repo, complete user/business loop. Review weights: Product 30% / Mainnet Integration 25% / Innovation 20% / UX 15% / Technical 10%.

## Network config (verified)

- **Chain ID:** 677 (BOT Chain Mainnet)
- **RPC:** `https://rpc.botchain.ai` · WSS `wss://ws-rpc.botchain.ai`
- **100% EVM-compatible** — MetaMask, Truffle, Remix, Hardhat, Foundry work out of the box
- **Fees:** ~$0.06/tx · **Blocks:** ~0.75s · **Finality:** ~0.9s
- **Testnet:** tBOT faucet available (dev-docs.botchain.ai/docs/Developers/claim-test-tbot-tokens)
- **Gas support:** 1 BOT per eligible project from BOT Chain
- **Explorer:** scan.botchain.ai · **Dev docs:** dev-docs.botchain.ai · **GitHub:** github.com/BOTChain-bot

## Chosen approach

**Product:** **RWA Yield Guard Agent** — an AI-driven asset-management agent that monitors a user's RWA/stablecoin positions on BOT Chain and auto-rebalances based on health factors, yield, and risk thresholds. AI is the *core* decision-maker (risk scoring + rebalance decisions), executing on-chain via BOT Chain's fast/cheap rails.

This is a **GTA evolution** — the same treasury-agent logic, ported to BOT Chain's RWA track. It satisfies:
- **RWA track** (highest priority): asset management, restaking, product aggregation
- **AI Native track**: AI as core on-chain decision entity, not auxiliary
- **Real user value**: automated yield/risk management for RWA holders

## Scope (tight, no creep)

1. **Register on Luma** (Jordan, today) — luma.com/238et7cw
2. **Join Builder Hub** (t.me/BotChain_official/61) for announcements + mainnet gas support
3. **Scaffold contracts** — RWA position registry + rebalance executor (Solidity, Hardhat/Foundry)
4. **Wire AI decision layer** — risk scoring + rebalance triggers (reuse GTA logic)
5. **Deploy to BOT Chain Mainnet** (testnet first, then mainnet)
6. **Build demo site** — wallet connect + position dashboard + agent actions
7. **Record demo video** + assemble submission (GitHub repo + demo + video)

## Judging criteria mapping

| Criterion | How we satisfy |
|---|---|
| Product Completion (30%) | Working RWA asset-management agent with full user loop |
| Mainnet Integration (25%) | Real BOT Chain Mainnet deploy, verified on explorer |
| Innovation (20%) | AI-driven risk/rebalance decisions on-chain (GTA evolution) |
| User Experience (15%) | Clean wallet-connected dashboard |
| Technical Quality (10%) | Solid Solidity + documented AI decision layer |

## Competitive intel — Meridian (mrdn.finance)

- BOT Chain ecosystem partner. **Decentralized inference router powered by x402** — 400+ models, 19 settlement chains, pay-as-you-go, no KYC.
- **Direct adjacent player to our x402 gateway.** We'd be measured against it.
- **But:** Meridian is inference routing; our play is *asset management*. Different lane, same rail. Validates x402 as the standard on BOT Chain.

## Risks

- **Mainnet deploy is non-negotiable** — must lock a working mainnet path early, not day 8.
- **10-day window** (Aug 10–20) is tight — keep scope to ONE focused agent, no creep.
- **Quality-first judging** — awards may be withheld if bar not met. Polish the demo + docs.
- **Gas on mainnet** — BOT Chain offers 1 BOT/project; fees are ~$0.06 so cheap to operate.

## Action items
- [ ] **Jordan:** register at luma.com/238et7cw (same Luma as other hackathons)
- [ ] **Jordan:** join Builder Hub t.me/BotChain_official/61
- [ ] **Gentech:** scaffold RWA Yield Guard contracts + AI decision layer
- [ ] **Gentech:** deploy to BOT Chain Mainnet + build demo site
- [ ] **Gentech:** record demo video + assemble submission
