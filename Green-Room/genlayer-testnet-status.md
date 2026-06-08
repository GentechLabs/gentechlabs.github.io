# GenLayer Testnet Status — April 24, 2026

## TL;DR
Both testnets are **LIVE NOW**. Bradbury is the one to target for real contract deployment and AI/LLM experimentation.

## Networks

### Testnet Bradbury (Target This One)
- **Focus:** LLM config, adversarial testing, multi-round appeals, validator specialization
- **GenLayer RPC:** `https://rpc-bradbury.genlayer.com`
- **Chain RPC:** `https://rpc.testnet-chain.genlayer.com`
- **Chain ID:** 4221
- **Explorer:** https://explorer-bradbury.genlayer.com
- **Chain Explorer:** https://explorer.testnet-chain.genlayer.com
- **Faucet:** https://testnet-faucet.genlayer.foundation
- **Status:** LIVE — builders can deploy real contracts for benchmarking
- **Caveat:** History resets periodically; not for production apps

### Testnet Asimov
- **Focus:** Core infrastructure, node stability, validator onboarding
- **GenLayer RPC:** `https://rpc-asimov.genlayer.com`
- **Same Chain ID / Chain RPC / Faucet as Bradbury**
- **Status:** LIVE

### Studionet (Local Simulator)
- **RPC:** `https://studio.genlayer.com/api`
- **Chain ID:** 61999
- For local development only

## Architecture Note
GenLayer is a **two-layer system:**
- **GenLayer RPC** → handles intelligent contract ops (`gen_*` methods)
- **GenLayer Chain** → underlying L2 (zkSync Elastic Chain) for standard Ethereum ops (`eth_*`, `zks_*`)
- The GenLayer RPC passthroughs all `eth_*` calls, so wallets can use either endpoint

## Incentives
- **Points system:** https://points.genlayer.foundation/
- XP earned for quests, validator uptime, testing contributions, bug reports, educational content
- Top validators → potential mainnet rewards, exclusive NFTs, early access
- **Inference subsidized** during testnet (free credits from io.net, Heurist/LibertAI, Comput3)

## Intelligent Oracle Context
- Intelligent Oracle is a **product built ON GenLayer**, not GenLayer itself
- IO's GitHub shows appeals as "TODO" and production bridge as unimplemented — this refers to their specific product layer
- **GenLayer Bradbury core protocol DOES have multi-round appeals active now**
- IO can deploy to Bradbury for real benchmarking

## Strategic Relevance for GenTech
1. **Cross-chain via LayerZero** — can bridge to Base, Solana, etc.
2. **x402 pattern alignment** — Apolo escrow demo shows AI adjudicated trustless payments
3. **Agent economy validation** — GenLayer's skills system mirrors our multi-agent architecture
4. **Hackathon opportunity** — BuildersClaw runs competitions on GenLayer
5. **Testnet staking** — 42 GEN min delegator, ~90% of rewards, 15% APR starting (inflation-funded)

## Open Questions
- Mainnet timeline? (Roadmap says "after Bradbury" but no hard date)
- GEN token economics for mainnet not yet published
- Team is small (~4 core on GitHub)

## Action Items
- [ ] Get testnet GEN from faucet
- [ ] Deploy a simple Intelligent Contract to Bradbury
- [ ] Evaluate Intelligent Oracle deployment feasibility
- [ ] Consider validator/delegator position for testnet points
