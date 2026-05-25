# Agent Launch (Fetch.ai / ASI Alliance) — Research

**Date:** 2026-05-25
**Status:** 🔍 Researching
**Source:** https://agent-launch.ai
**Relevance:** Agent Arena (AAE) integration layer for token issuance

## What It Is

Token launchpad for AI agents on BSC Mainnet. One API call to tokenize any agent. Bonding curve pricing with automatic DEX graduation at 30K FET.

## Key Stats

- **Chain:** BSC Mainnet (live since April 19, 2026)
- **Cost:** 120 FET deployment fee
- **Scale:** 2.7M+ agents, 150M+ users claimed
- **Tools:** TypeScript SDK, CLI, MCP (39 tools), REST API
- **Supports:** uAgents, LangChain, CrewAI, AutoGPT

## Bonding Curve Mechanics

```
Price formula: P(x) = (x / 375) / 10^18
where x = tokens already sold

Buy/sell fee: 2% → 100% protocol treasury (no creator fee)
Auto-graduation: 30K FET → PancakeSwap listing
Price range: ~10x from first buy to graduation
Tradeable supply: 800M tokens per launch
DEX reserve: 200M tokens (locked until graduation)
```

## Agent-to-Agent Scenarios

| Scenario | Description |
|----------|-------------|
| A: Self-tokenize | Agent tokenizes itself → human deploys |
| B: Tokenize others | Agent discovers high-value agent → tokenizes it |
| C: Trade signals | Agent monitors bonding curve → sends buy signals near graduation |
| D: Autonomous trade | Agent trades with private key — no human needed |

## Integration Options for AAE

1. **Token issuance layer** — AAE agents use Agent Launch to issue tokens (don't build our own)
2. **MCP tools (39)** — Wire into Hermes for direct agent tokenization
3. **Bonding curve math** — Study for AAE's "rep-as-currency" pricing model
4. **Handoff protocol** — Agent creates → human deploys via pre-filled link
5. **Agent-to-agent patterns** — Direct mapping to AAE's trading game mechanics

## API Quick Reference

```bash
# Tokenize an agent
curl -X POST https://agent-launch.ai/api/agents/tokenize \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agentAddress": "agent1q...", "name": "MyAgent", "symbol": "MYA"}'

# List tokens
GET /api/agents/tokens?sortBy=market_cap&sortOrder=DESC&limit=10

# Get token details
GET /api/agents/token/{address}

# Buy tokens (SDK)
buyTokens('0x...', '10', { chainId: 97, slippagePercent: 5 })

# Sell tokens (SDK)
sellTokens('0x...', '50000', { chainId: 97 })
```

## Platform Constants

```
Blockchain: BNB Smart Chain (BSC)
Chain IDs: 56 (mainnet), 97 (testnet)
FET Token (BSC): 0x031b41e504677879370e9DBcF937283A8691Fa7f
Deploy fee: 120 FET
Target liquidity: 30,000 FET → auto PancakeSwap listing
```

## Decision

**Integrate, don't compete.** They built the token launchpad. We build the experience layer (trading game, reputation, agent discovery). Plug their infrastructure into our AAE stack.

## Next Steps

- [ ] Evaluate MCP integration with Hermes
- [ ] Study bonding curve math for AAE rep pricing
- [ ] Test on BSC Testnet (chain 97)
- [ ] Map to AAE integration stack layers
