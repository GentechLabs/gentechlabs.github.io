# Agent Payment Infrastructure Research — April 28, 2026

## Context
Jordan requested research on agent payment platforms for AAE (Agent-as-a-Service) positioning. Two key platforms reviewed: **Kite Passport** (Avalanche) and **Ampersend** (multi-chain).

---

## Kite Passport (Avalanche)
- **Three-layer identity model:** User (root wallet) → Agent (delegated HDK-derived address) → Session (ephemeral, scoped keys)
- **X402 integration:** Native HTTP 402 payment protocol for stateless agent payments
- **Agent Payment Protocol (APP):** State channels for micropayments (sub-100ms latency, ~$0.000001 cost)
- **SPACE framework:** Stablecoin-native, Programmable, Agent-first, Compliance-ready, Economically viable
- **Privacy:** Selective disclosure via cryptographic proofs (agent proves human backing without revealing identity)
- **Key insight:** Avalanche has zero competition in AI agent payments — blue ocean positioning

## Ampersend
- **Core feature:** Create wallet + budget for every agent; agents can get paid and spend
- **Live product:** 75K views, 247 likes, 81 reposts on announcement tweet
- **Integration:** Available as OpenClaw skill (`ampersend.ai/skill.md`); also has Hermes MCP integration (`edgeandnode/ampersend-hermes` on GitHub)
- **Setup:** `pnpm setup --name my-hermes-agent` patches Hermes config, starts MCP proxy
- **Features:** MCP payment proxy, agent wallet management, spend limits (e.g., `--daily-limit 10000000` for 10 USDC)
- **Network:** Defaults to Base chain
- **GitHub:** `edgeandnode/ampersend-hermes`

## Comparison

| Feature | Kite Passport | Ampersend |
|---------|--------------|-----------|
| Identity | 3-layer (User→Agent→Session) | Wallet per agent |
| Payments | X402 + state channels | X402 + MCP proxy |
| Focus | L1-native identity + settlement | Wallet/budget management |
| Chain | Avalanche only | Multi-chain (Base default) |
| Status | Infrastructure layer | Live product |

## Strategic Positioning
- **Kite = Trust substrate** (identity, delegation, privacy)
- **Ampersend = Payment execution** (wallets, budgets, spend controls)
- **Together:** Complete agent payment stack — Kite provides identity layer, Ampersend provides wallet management
- **AAE positioning:** Marketplace and reputation layer built ON TOP of these tools
- **Not competitive with either** — complementary. Potential partnership opportunity with @ampersend_ai

## Open Questions
- DMOB to evaluate Kite Passport SDK technically (handoff created in Green Room)
- Ampersend-Hermes integration not yet installed/tested
- No outreach to Ampersend yet — Jordan to look into it tomorrow
