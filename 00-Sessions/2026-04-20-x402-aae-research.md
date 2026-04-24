# Session Note: 2026-04-20 — x402 / AAE Research Sprint

## Context
Jordan shared links to explore the x402 ecosystem. What started as "check this out" became a full AAE architecture research session.

## What We Found

### x402 Protocol (Coinbase)
- Open payment standard (HTTP 402), Apache-2.0 license
- AI agent payments — no API keys, wallet-only
- Solana + Base settlement, 35M+ txns, $50M+ volume
- GitHub: x402-foundation/x402 (6k stars)

### Production Integrations
- **Birdeye Data** — $0.003/req, full REST API, launched Apr 16
- **Agentic Market** (Coinbase) — 68+ services, $49M+ volume, live transactions
  - Anthropic, OpenAI, DeepSeek, CoinGecko, Nansen, Perplexity, Firecrawl, Browserbase, Deepgram, FAL, X API
- **Apolo** — trustless escrow on BNB mainnet (x402 → escrow → GenLayer → settle)

### GenLayer
- Optimistic Democracy consensus for AI verification
- Bridge to 130+ chains (LayerZero as first transport, but supports Hyperlane/Axelar/IBC)
- Shipyard: one-click contract deployment (17+ templates)
- Skills: Claude Code plugins for dev + validator ops
- BuildersClaw: agent hackathon platform

### Competitions Found
- **Birdeye BIP** — Sprint 1 closes Apr 25, $500 USDC + API credits
- **ElevenLabs ElevenHacks** — 11-week series, $109K+ pool
- **Agentic Economy on Arc** (lablab.ai) — Circle's chain + x402 hackathon
  - Arc Testnet settle method broken, fix Apr 22
- **BuildersClaw** — agent-native hackathons, onchain verification

### LayerZero Risk
- 47% of 2,665 integrations run 1/1 DVN (KelpDAO hack)
- GenLayer uses LayerZero as FIRST transport but isn't locked to it
- Risk is manageable — modular architecture allows swap

## Key Files
- Full research: `/root/vaults/gentech/01-Projects/AAE/x402-research.md`
- LayerZero warning: `/root/vaults/gentech/04-Intelligence/layerzero-dvn-warning-2026-04-20.md`

## AAE Stack Mapped
x402 (payment) → Agentic Market (services) → Birdeye (data) → Apolo (escrow) → GenLayer (trust) → Solana (settlement)

## Next Steps
- Deploy Escrow with AI Arbiter or Token Price Tracker on Bradbury testnet
- Enter Birdeye BIP Sprint 1 (4 days left)
- Check lablab.ai Arc hackathon
- Prototype YoYo → Birdeye x402 integration
