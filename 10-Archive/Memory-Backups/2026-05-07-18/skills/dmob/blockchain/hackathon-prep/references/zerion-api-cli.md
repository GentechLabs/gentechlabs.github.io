# Zerion API & CLI — Reference for Solana Frontier Sidetrack

## Bounty: "Build an Autonomous Onchain Agent using Zerion CLI" — $5,000

## Zerion CLI (open-source: github.com/zeriontech/zerion-ai)

### Installation
```bash
npx -y zerion-cli init -y --browser   # Full setup (CLI + API key + agent skills)
npm install -g zerion-cli              # CLI only (requires Node.js 20+)
```

### Authentication (3 modes)
1. **API key** (recommended) — `export ZERION_API_KEY="zk_..."` from dashboard.zerion.io
2. **x402 pay-per-call** — $0.01 USDC/request via `export ZERION_X402=true` (no API key needed, analysis only)
3. **MPP pay-per-call** — $0.01 USDC on Tempo (EVM only)

### Commands
| Command | Purpose | Auth |
|---------|---------|------|
| `zerion analyze <addr>` | Full analysis (portfolio + positions + history + PnL) | x402 or API key |
| `zerion portfolio <addr>` | Portfolio value + top positions | x402 or API key |
| `zerion positions <addr>` | Token + DeFi positions (`--positions all\|simple\|defi`) | x402 or API key |
| `zerion history <addr>` | Transaction history (`--limit`, `--chain`) | x402 or API key |
| `zerion pnl <addr>` | Profit & loss | x402 or API key |
| `zerion search <query>` | Search tokens | x402 or API key |
| `zerion chains` | List supported chains | x402 or API key |
| `zerion swap <from> <to> <amt>` | Swap tokens | API key + agent token |
| `zerion bridge <token> <chain> <amt>` | Bridge cross-chain | API key + agent token |
| `zerion send <token> <amt> --to <addr>` | Send tokens | API key + agent token |
| `zerion wallet list/create/sync` | Wallet management | Manual |
| `zerion agent create-token` | Mint scoped trading credential | Manual |
| `zerion agent create-policy` | Attach rules to agent token | Manual |
| `zerion watch <addr>` | Real-time monitoring | x402 or API key |

### Agent Skills (for AI coding agents)
6 skills ship with CLI: `zerion`, `zerion-analyze`, `zerion-trading`, `zerion-sign`, `zerion-wallet`, `zerion-agent-management`
Install via: `zerion setup skills` or per-agent: `zerion setup skills --agent claude-code`

## REST API (developers.zerion.io)

### Key Endpoints
| Endpoint | Purpose |
|----------|---------|
| `GET /v1/wallets/{addr}/charts/day` | Balance chart |
| `GET /v1/wallets/{addr}/pnl` | PnL data |
| `GET /v1/wallets/{addr}/portfolio` | Portfolio overview |
| `GET /v1/wallets/{addr}/positions` | DeFi positions |
| `GET /v1/wallets/{addr}/transactions` | Transaction history |
| `GET /v1/wallets/{addr}/nft-positions` | NFT positions |
| `GET /v1/fungibles/{chain}/{address}` | Token info |
| `GET /v1/chains` | Supported chains |
| `GET /v1/swap/quote` | Swap quotes |

Auth: `Authorization: Basic <base64-encoded-api-key>`

### AI & Agents Integration
- Full docs: `https://developers.zerion.io/llms.txt`
- MCP server available
- x402 + MPP pay-per-call for analytics
- Supported chains: all EVM + Solana

## Submission Requirements (Zerion Sidetrack)
- Must use Zerion CLI/API in a meaningful way
- Agent that auto-discovers and delegates tasks via CLI
- Clean UX — should feel like a real product
- Demo video showing the agent in action
- Source code + README + submission writeup

## Architecture Pattern for Agent Build
```
Off-chain Agent (TS/Python)
    │
    ├── uses ──▶ Zerion CLI (data + quotes + trades)
    │
    ├── decisions ──▶ LLM / rule-based engine
    │
    └── executes ──▶ Zerion CLI (swap, bridge, send)
                          │
                          ▼
                     On-chain (Solana/EVM)
```

Key insight: Zerion CLI already handles wallet management, trade routing, and chain abstraction. The agent adds intelligence (discovery, policy, automation) on top.
