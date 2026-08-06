# MetaMask Agent Wallet — Treasury Watch (Aug 6, 2026)

**Jordan directive:** "follow this development and how it benefits our Agentic Treasury."

## What's set up
A daily watcher (`metamask_agent_watch.py`) polls the MetaMask agent-wallet dev repos
for new commits and emits a treasury-relevant digest (or stays silent on no-change).

**Repos watched (MetaMask org):**
- `MetaMask/agent-skills` — agent skill definitions (pushed daily)
- `MetaMask/agent-runner` — agent execution runtime
- `MetaMask/client-mcp-core` — MCP client core (agent tool access)
- `MetaMask/metamask-sdk` — SDK (integration surface)

**Treasury-relevant keywords flagged (🔑):** x402, payment, bridge, swap, yield, vault,
perpetual/perps, prediction/polymarket, hyperliquid, aave, erc-8004/8004, avalanche,
base, wallet, permission, limit, spend, security, tee, signer, agent, mcp, rail.

**Cron:** `efd0d66adca0` "MetaMask Agent Wallet — Treasury Watch", daily 09:00 UTC,
delivers to Treasury group. Silent when nothing new.

## How it benefits the Agentic Treasury (the lens)
MetaMask Agent Wallet = the wallet **home** (custody + security). GenTech = the
**treasury intelligence + x402 middleware tollbooth**. We watch for features we can:
1. **Integrate** — MetaMask Agent Wallet as a custody/execution venue (it supports
   x402 + ERC-8004 + Avalanche + Base). Our treasury logic could target it.
2. **Validate** — x402 payments, ERC-8004 identity, granular permissions, yield
   vaults, perps, prediction markets = the exact Agentic Treasury product shape.
3. **Differentiate** — they provide the wallet; we provide the decision layer + rail.

## Status
- Watcher baselined (4 repos), silent on no-change, verified working.
- Cron live, first meaningful delivery 2026-08-07 09:00 UTC.
- Full signal note: `09-Green Room/specs/metamask-agent-wallet-signal-2026-08-06.md`
