# 🤖 Zerion Agent

**Autonomous DeFi agent powered by Zerion CLI** — auto-discovers opportunities and delegates on-chain tasks.

> "An agent that auto-discovers and delegates tasks via CLI"

## What It Does

Zerion Agent wraps the [Zerion CLI](https://developers.zerion.io) with intelligent discovery and execution layers:

1. **🔍 Discover** — Scans your wallet for idle assets and finds yield opportunities across protocols
2. **📊 Analyze** — Portfolio breakdown, DeFi positions, PnL tracking, transaction history
3. **⚡ Execute** — Swap, bridge, send tokens via Zerion CLI with safety policies
4. **👁️ Monitor** — Real-time watching for price changes, position shifts, new opportunities
5. **🛡️ Policy Engine** — Set transfer limits, chain restrictions, token allowlists

## Quick Start

```bash
# Install
npm install -g zerion-agent

# Or run directly
npx zerion-agent discover vitalik.eth
```

### Without API Key (x402 pay-per-call)

```bash
# Analysis commands work with x402 — $0.01 USDC per request
ZERION_X402=true zerion-agent discover 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

### With API Key (full functionality)

```bash
# Get free key at dashboard.zerion.io
export ZERION_API_KEY=zk_...

# Full analysis
zerion-agent analyze vitalik.eth

# Execute swaps
zerion-agent execute swap usdc eth 100 --chain ethereum

# Auto-execute top opportunities
zerion-agent execute auto vitalik.eth --max-ops 3 --dry-run
```

## Commands

| Command | Description | Auth Required |
|---------|-------------|---------------|
| `discover <wallet>` | Scan wallet + find DeFi opportunities | x402 or API key |
| `analyze <wallet>` | Full wallet analysis | x402 or API key |
| `execute swap/bridge/send` | Execute trades | API key + agent token |
| `execute auto <wallet>` | Auto-execute top recommendations | API key + agent token |
| `monitor <wallet>` | Real-time wallet monitoring | x402 or API key |
| `wallet list/create/sync` | Manage wallets | Manual |
| `wallet policy set` | Set trading policies | Manual |

## Architecture

```
┌─────────────────────────────────────────────┐
│              Zerion Agent CLI                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  Discover    │    │  Opportunity     │   │
│  │  Command     │───▶│  Scanner         │   │
│  └─────────────┘    └──────────────────┘   │
│                          │                  │
│                          ▼                  │
│                   ┌──────────────────┐      │
│                   │  Task Delegator  │      │
│                   │  + Policy Engine │      │
│                   └──────────────────┘      │
│                          │                  │
│                          ▼                  │
│                   ┌──────────────────┐      │
│                   │  Zerion Client   │      │
│                   │  (CLI wrapper)   │      │
│                   └──────────────────┘      │
│                          │                  │
└──────────────────────────┼──────────────────┘
                           │
                           ▼
                   zerion-cli (npm)
                           │
                           ▼
                    Zerion API / x402
```

## Safety Model

- **Agent tokens** — Scoped trading credentials bound to specific wallets
- **Policies** — Transfer limits, chain restrictions, token allowlists
- **Dry run** — Preview all actions before execution
- **No-idle protocol** — Agent keeps working, queues next task on stopping points

## Development

```bash
# Install deps
npm install

# Build
npm run build

# Run in dev mode
npm run dev -- discover vitalik.eth

# Run tests
npm test
```

## Roadmap

- [ ] Yield oracle integration (DeFiLlama, Ranger)
- [ ] Multi-wallet portfolio aggregation
- [ ] Automated rebalancing based on policy
- [ ] Webhook notifications for opportunity alerts
- [ ] Integration with Hermes Agent for natural language commands

## License

MIT — Gentech Labs
