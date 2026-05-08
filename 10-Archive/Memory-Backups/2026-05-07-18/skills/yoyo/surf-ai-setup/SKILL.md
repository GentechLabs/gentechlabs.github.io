---
name: surf-ai-setup
description: >-
  Install and configure Surf AI CLI for crypto intelligence queries across 14 data domains
  (prices, wallets, social, on-chain SQL, prediction markets, news, etc.). 95+ commands.
metadata:
  version: "1.0.0"
tools:
  - bash
---

# Surf AI — Crypto Intelligence CLI

Surf gives agents direct access to 95+ crypto data endpoints via natural language commands.

## Installation

Two parts: the CLI binary and the skill package.

### CLI Binary

Official install script at https://agent.asksurf.ai/cli/releases/install.sh — installs to `~/.local/bin/surf`.

If the pipe-to-shell install times out, download the script first then execute it separately.

### Skill Package

```bash
npx skills add asksurf-ai/surf-skills -y
```

## Session Startup

Always run these two commands at the start of any session:

```bash
export PATH="$HOME/.local/bin:$PATH"
surf sync                       # Refresh API spec cache
```

## Quick Test

```bash
surf market-price --symbol BTC --json
```

## Common Gotchas

- **Flags are kebab-case** (`--sort-by`), NOT snake_case (`--sort_by`)
- **Chains need long names**: `eth` → `ethereum`, `sol` → `solana`, `avax` → `avalanche`
- **Enum values are lowercase**: `--indicator rsi`, NOT `RSI`
- **Search uses `--q` (double dash)**, never `-q` (that's a global flag)
- **On-chain SQL requires `agent.` prefix**: `agent.ethereum_dex_trades`
- **Always filter on `block_date`** in SQL queries (partition key)

## Domain Routing

| Need | Grep for |
|------|----------|
| Prices, market cap, rankings | `market` |
| Wallet portfolio, balances | `wallet` |
| Twitter/X profiles, sentiment | `social` |
| Token holders, DEX trades | `token` |
| DeFi TVL, protocol metrics | `project` |
| Prediction markets | `polymarket`, `kalshi` |
| On-chain SQL, gas | `onchain` |
| News, cross-domain search | `news`, `search` |

## Discovery Commands

```bash
surf list-operations                      # All commands
surf list-operations | grep <domain>      # Filter by domain
surf <command> --help                     # Full params and schema
```

## Auth

Free tier: 30 credits/day without key. New accounts: 1,000 free credits.

```bash
surf auth --api-key <your-key>
```

Key from: https://agents.asksurf.ai
