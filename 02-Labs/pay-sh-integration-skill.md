---
name: pay-sh-integration
description: "pay.sh integration for Hermes agents — x402/MPP payment CLI, MCP server, paid API access"
version: 1.0.0
author: Gentech Labs
license: MIT
tags: [x402, mpp, pay-sh, solana, payments, api-access, mcp]
---

# pay.sh Integration for Hermes Agents

pay.sh is a CLI wrapper that intercepts HTTP calls, detects x402/MPP payment challenges (HTTP 402), prompts a local wallet to sign, and retries with payment proof. It supports both MPP (Solana Foundation) and x402 (Coinbase) protocols.

## When to Use

- Agent needs to call paid APIs without managing API keys
- User wants local approval (Touch ID, Windows Hello) before payments
- Need to discover paid API providers via catalog
- Want to expose GenTech endpoints as paid services

## Prerequisites

- `pay` CLI v0.16+: `npm install -g @solana/pay`
- Node.js 20+ for MCP server
- Solana wallet with stablecoins (USDC, USDT, CASH)

## Agent Setup

### Install pay CLI

```bash
npm install -g @solana/pay
pay --version
```

### Wallet Setup

```bash
pay setup    # Touch ID on macOS, Windows Hello on Windows, GNOME Keyring on Linux
pay topup    # Import funds from Venmo, PayPal, or mobile wallet
```

### Sandbox Mode (Testing)

```bash
# Use sandbox for testing — no real funds needed
pay --sandbox curl https://debugger.pay.sh/mpp/quote/AAPL
```

## MCP Server Integration

pay.sh ships with a built-in MCP server. To integrate with Hermes:

### Option 1: Direct MCP Registration

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  pay:
    command: "pay"
    args: ["mcp"]
    timeout: 120
    connect_timeout: 60
```

After config changes, run `/reload-mcp` in Hermes chat.

### Option 2: Subprocess Calls

Use `terminal` tool to call pay CLI directly:

```bash
# Search for API providers
pay skills search "maps"

# Get endpoint details
pay skills endpoints <provider>

# Make a paid API call (sandbox mode)
pay --sandbox curl https://debugger.pay.sh/mpp/quote/AAPL

# Make a real paid API call (requires wallet setup)
pay curl <provider-endpoint>
```

## Core Workflow

1. **Discovery**: Use `pay skills search` to find API providers
2. **Inspection**: Use `pay skills endpoints` to see pricing and endpoints
3. **Payment**: Use `pay curl` with provider URL — handles 402 challenges automatically
4. **Approval**: Local wallet prompts for approval before signing

## MCP Tools (when MCP server is running)

- `search_catalog({query, category?, max_results?})` — rank providers for a task
- `get_catalog_entry({fqn})` — get endpoint URLs and usage notes
- `curl({url, method, headers, body})` — make HTTP requests with 402 handling
- `get_balance()` — check stablecoin balances
- `list_catalog()` — browse all available API providers

## Security Model

- Keys stay in local secure storage (macOS Keychain, GNOME Keyring, Windows Hello)
- Every payment requires local user approval (Touch ID, biometrics)
- Providers are curated in open-source catalog
- External responses treated as untrusted data

## Pitfalls

- **Sandbox vs mainnet**: Use `--sandbox` for testing, real payments require funded wallet
- **Linux polkit setup**: Required for GNOME Keyring auth:
  ```bash
  sudo cp rust/config/polkit/sh.pay.unlock-keypair.policy /usr/share/polkit-1/actions/
  ```
- **MCP server restart**: After config changes, run `/reload-mcp` — don't restart gateway
- **USDC-only**: No multi-token support yet
- **Centralized catalog**: AgentLayer controls discovery

## Related

- **pay.sh docs**: https://pay.sh/docs
- **pay-skills repo**: https://github.com/solana-foundation/pay-skills
- **x402 protocol**: https://x402.org
- **MPP protocol**: https://paymentauth.org/draft-solana-charge-00.html
