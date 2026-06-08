# Beam SDK Research — Avalanche Subnet Integration

**Date:** 2026-04-21
**Status:** Initial Research
**Requested by:** Jordan

---

## What is Beam?

**Beam** is an Avalanche L1 (formerly subnet) focused on gaming and AI agent infrastructure. It's a full EVM-compatible chain with custom tooling for player management, automation agents, and marketplace operations.

### Chain Details

| Property | Value |
|----------|-------|
| Mainnet RPC | `https://build.onbeam.com/rpc` |
| Chain ID | 4337 (mainnet), 13337 (testnet) |
| Testnet RPC | `https://build.onbeam.com/rpc/testnet` |
| TPS | Up to 4,500 |
| Finality | 1 second |
| Tx Fees | Sub $0.1 |
| Bridge | LayerZero (app.onbeam.com/bridge) |
| DEX | BeamSwap (swap.onbeam.com) |
| Faucet | faucet.avax.network/?subnet=beam |
| Explorer | subnets.avax.network/beam/ |
| L1 ID | `eYwmVU67LmSfZb1RwqCMhBYkFyG8ftxn6jAwqzFmxC9STBWLC` |

### Ecosystem Links
- **Docs:** https://docs.onbeam.com
- **SDK Docs:** https://docs.onbeam.com/sdk
- **Grants:** https://grants.onbeam.com
- **Governance:** https://gov.onbeam.com
- **Node Dashboard:** https://delegation.onbeam.com
- **Telegram:** https://t.me/buildonbeam_news
- **Discord:** http://discord.gg/beamcommunity

---

## Beam SDK — Two Services

### 1. Player Service (C# SDK + REST API)
Manages end-user interactions:
- **Users** — connecting wallets, managing profiles
- **Operations** — creating/processing blockchain operations
- **Sessions** — stateful user sessions, signing with sessions
- **Transactions** — sponsored txs, profile-paid txs, custom token charges, custom txs
- **Assets** — reading/managing player assets (NFTs, tokens)
- **Marketplace** — currencies, listing assets, buying, offers
- **Exchange** — converting tokens
- **Webhooks** — event-driven notifications

### 2. Automation Service (AI Agent Focus ⭐)
This is the killer feature for GenTech:
- **Profiles** — creating/matching/minting/treasury profiles for agents
- **Policies** — defining what agents can/cannot do (permissions, spending limits)
- **Trading** — automated trade execution
- **Webhooks** — event-driven agent triggers

### SDK Repos
| Repo | Description |
|------|-------------|
| `BuildOnBeam/beam-api-clients` | Official SDKs (C# primary, OpenAPI-generated) |
| `BuildOnBeam/beam-docs` | Documentation (MDX, updated Apr 2026) |
| `BuildOnBeam/beam-subnet` | Subnet connection details, ABIs |
| `BuildOnBeam/beam-nodes-staking-contracts` | PoS staking via Avalanche ICM |
| `BuildOnBeam/beam-token` | Token contract (TypeScript) |
| `BuildOnBeam/layerzero-contracts` | LayerZero V1 omnichain contracts |
| `BuildOnBeam/merit-nft` | Merit NFT contracts |

---

## Integration Opportunities with GenTech Stack

### 1. Payment Router → Beam Chain
Our `TechPaymentRouter.sol` (Foundry/Solidity) is EVM-compatible → deploy directly to Beam.
- Benefit: 1s finality, sub-$0.1 fees vs. Base L2 costs
- Beam's native token + BeamSwap DEX for liquidity

### 2. LP Monitor → Beam Automation Service
Replace custom Python cron with Beam's Automation Service:
- Agent profiles with spending policies
- Native webhook triggers for position alerts
- Automated rebalancing via on-chain policies

### 3. x402 + Beam = Cross-Chain Agent Payments
- x402 HTTP 402 agent payments on Solana (current)
- Beam's LayerZero bridge enables cross-chain agent payments
- "Swap the chain, keep the agent" — modular architecture fits perfectly

### 4. AAE Protocol → Beam Automation
- 8-layer agent protocol can leverage Beam's policy system
- Agent profiles map to AAE's agent identity layer
- Automation policies enforce spending/permission guardrails

### 5. Birdeye Token Radar → Beam Trading
- Token safety radar can trigger automated trades on BeamSwap
- Policy-based execution (e.g., "only buy tokens with safety score > 80")

---

## Next Steps

- [ ] Get testnet BEAM from faucet
- [ ] Deploy TechPaymentRouter to Beam testnet
- [ ] Test Beam SDK Automation Service locally
- [ ] Evaluate BeamSwap liquidity for AVAX/USDC equivalent
- [ ] Check Beam Foundation grants for AI agent projects
- [ ] Compare Beam automation vs. current cron-based approach

---

## Resources
- GitHub Org: https://github.com/BuildOnBeam
- Beam Subnet (connection details): https://github.com/BuildOnBeam/beam-subnet
- Beam SDK: https://github.com/BuildOnBeam/beam-api-clients
- Staking Contracts: https://github.com/BuildOnBeam/beam-nodes-staking-contracts
