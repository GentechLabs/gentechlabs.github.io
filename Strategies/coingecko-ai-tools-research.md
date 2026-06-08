# CoinGecko AI-Native Tools Research
**Date:** 2026-04-18
**Status:** Installed & Configured
**Relevance:** Arc Hackathon (Apr 20)

## What CoinGecko Released

CoinGecko launched an **AI Agent Hub** with 4 tools under `/docs/ai-agent-hub/`:

### 1. MCP Server ✅ INSTALLED
- **Package:** `@coingecko/coingecko-mcp` (v3.1.0, March 2026)
- **Repo:** `coingecko-typescript` monorepo, `packages/mcp-server`
- **Mode:** "Code Mode" — agent writes TypeScript against the SDK, executed in sandbox
- **Config:** Added to `~/.hermes/config.yaml` under `mcp_servers.coingecko`
- **Tools exposed as:** `mcp_coingecko_*`
- **Env vars:** `COINGECKO_DEMO_API_KEY` or `COINGECKO_PRO_API_KEY`
- **Docs:** https://docs.coingecko.com/docs/ai-agent-hub/mcp-server

### 2. CoinGecko CLI
- **Docs:** https://docs.coingecko.com/docs/ai-agent-hub/cli
- **Community package:** `coingecko-cli` (v1.6.1, outdated 2022)
- **Official CLI:** Referenced in AI Agent Hub docs but unclear if it's a separate package or part of the TypeScript SDK
- **Action needed:** Verify if there's an official CLI binary

### 3. x402 Endpoints 🔥 ARC HACKATHON GOLD
- **Docs:** https://docs.coingecko.com/docs/ai-agent-hub/x402
- **Protocol:** Coinbase x402 — pay-per-use over HTTP with USDC
- **Key insight:** NO API KEY REQUIRED — payment is the auth
- **How it works:**
  1. Make request to x402 endpoint
  2. Server returns 402 + payment requirements
  3. Wallet signs USDC authorization
  4. Send signed payment header → receive data
- **URL pattern:** Insert `/x402/` after `/v3/` in the API path
- **Payment:** USDC on Base (Coinbase L2)
- **Status:** Experimental — "subject to change"
- **Quickstart:** https://docs.cdp.coinbase.com/x402/quickstart-for-buyers

### 4. AI Prompts / Skills
- **Docs:** https://docs.coingecko.com/docs/ai-agent-hub/ai-prompts
- **Pre-built prompts** for TypeScript and Python
- **Tags:** CoinGecko Demo API, CoinGecko Pro API, Onchain, Pools, Tokens

## Arc Hackathon Angle

**Thesis:** CoinGecko x402 data endpoints + Arc settlement = killer demo

- CoinGecko already uses x402 (Coinbase's nanopayment protocol)
- We can build an **Arc-native bridge** that:
  - Accepts Arc payments (not just Base/USDC)
  - Routes to CoinGecko x402 endpoints
  - Provides premium crypto data without API keys
- Differentiator: Cross-chain nanopayments for data access
- CoinGecko's involvement = instant credibility

## Next Steps
1. Get CoinGecko Demo API key (free) → https://www.coingecko.com/en/api/pricing
2. Test MCP server in new agent session
3. Prototype x402 → Arc bridge for hackathon
4. Build demo UI showing pay-per-call data flow
