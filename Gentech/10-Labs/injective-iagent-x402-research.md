# Injective iAgent × x402 Integration — Research

**Date:** 2026-07-23
**Queue Item:** #57 — Injective Labs — iAgent x402 Payment Integration
**Priority:** High
**Difficulty:** Medium

## Key Findings

### Injective + x402 Status
- **Injective joined the x402 Foundation** on July 16, 2026 as a Member under Linux Foundation governance
- x402 is **live on Injective mainnet** — 650ms block time, ~$0.0001/tx
- Injective is one of 40+ Foundation members alongside AWS, Google, Visa, Mastercard, Stripe, Coinbase, Circle
- This is a **Premier-level ecosystem partner** — contributing here builds credibility with the x402 Foundation directly

### iAgent Repo (50⭐, 38 forks)
- **Python-based** AI agent fine-tuned on Injective trading framework
- Uses `injective-py` SDK + OpenAI GPT-4o
- Architecture: Quart (async Flask) server with chat endpoints, function execution via `injective_functions`
- 16 commits, last updated March 2025 — somewhat stale but maintained
- 3 contributors (Injective Labs team)

### Integration Opportunity
The iAgent already has a server architecture (`agent_server.py`) with:
- OpenAI chat completions
- Injective on-chain function execution (account, exchange, staking, bank, etc.)
- Session management

**What we can contribute:**
1. **x402 payment middleware** — Add x402 payment verification to iAgent's API endpoints so agents can pay per-call for Injective trading functions
2. **x402 facilitator integration** — Wire iAgent as an x402 facilitator for Injective-specific operations
3. **Compliance plugin** — Same pattern as our GOAT AgentKit compliance plugin, adapted for Injective's SDK

### Recommended Approach
1. Fork `InjectiveLabs/iAgent`
2. Add x402 payment verification middleware to `agent_server.py`
3. Add `x402-required` decorator for paid endpoints
4. Submit PR with AI disclosure

### Files
- `agent_server.py` — Main server, add x402 middleware here
- `injective_functions/` — Function execution layer, add payment gating
- `agents_config.yaml` — Configuration, add x402 settings

### Blockers
- None — fully actionable by Gentech
- No Jordan dependency
- No special hardware needed
