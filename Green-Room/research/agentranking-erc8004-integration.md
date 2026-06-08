# AgentRanking + ERC-8004 Integration Research (May 24, 2026)

## Source
Jordan asked: "How customizable is AgentRanking? Can this be our credit score layer?"

## Findings

### The Stack (Three Layers)
1. **ERC-8004 Identity** — fully open standard, 130K+ agents registered. Any agent on any chain gets verifiable identity. Completely composable.
2. **AgentRanking MCP Server** — `search_agents`, `get_agent_profile` endpoints. Query trust scores, revenue badges, reputation data programmatically.
3. **AgentRank (0xIntuition)** — protocol layer uses trust graph with staking. Supports domain-specific reputation scores extendable per context.

### What's Customizable
- ERC-8004 identity layer — fully composable
- AgentRanking API — query and integrate signals
- Domain-specific reputation scores — extendable per context

### What's NOT Customizable
- AgentRanking's trust algorithm — their scoring model, we can't tweak weights
- "Verified Revenue" tracks on-chain execution wallets, not Arena-specific P&L
- Discovery/directory layer first, scoring service second

### The Play for Agent Arena
AgentRanking is an **input** to our credit score, not the credit score itself.

**Layer 1: ERC-8004** → Agent identity (who they are, wallet-linked, cross-chain)
**Layer 2: AgentRanking signals** → External trust baseline (revenue proof, endorsements, history across 30+ chains)
**Layer 3: Our credit score engine** → Game-specific scoring combining Arena performance data (win rate, risk-adjusted returns, portfolio health) WITH external AgentRanking signals

An agent verified on AgentRanking with real revenue history + Arena performance scores higher than a fresh anonymous agent.

## Key Insight
"Chainlink gives prices. We give trust scores." — but AgentRanking gives us the foundation layer to build that on, rather than starting from zero.

## Architecture Doc
`Green-Room/designs/aae-credit-layer-infra.md`

## Next Step (Queued for May 25)
Draft integration architecture showing how AgentRanking MCP feeds into our scoring engine.
