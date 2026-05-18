# Sidetrack Adapter Specs — Option B (Locked)
**Created:** May 5, 2026
**Status:** 🟢 Ready for DMOB

---

## Adapter 1: Zerion CLI ($5K)

### What We're Building
Agent that auto-discovers DeFi opportunities and delegates tasks via CLI. Wraps Zerion's API to give an AI agent real-time portfolio intelligence.

### API Surface (from developers.zerion.io)

**Auth:** HTTP Basic Auth — API key as username, empty password
- Get key from: dashboard.zerion.io
- Alternative: x402 (pay USDC per request, no rate limits) or MPP (pay on Tempo)
- For hackathon: use free tier API key

**Key Endpoints:**
| Endpoint | Purpose | Agent Use |
|----------|---------|-----------|
| `GET /wallets/{address}/portfolio` | Total portfolio value + token breakdown | Discover agent's current holdings |
| `GET /wallets/{address}/defi-positions` | DeFi positions across protocols | Find yield opportunities, LP positions |
| `GET /wallets/{address}/transactions` | Transaction history | Learn from past agent actions |
| `GET /wallets/{address}/pnl` | Profit/loss tracking | Performance metrics for reputation |
| `GET /tokens/{chain}/{address}` | Token analytics | Evaluate new tokens |
| Webhooks | Real-time position alerts | Trigger agent actions on events |

**Rate Limits:**
- Free tier: limited requests/sec and daily cap
- Headers: `RateLimit-Org-Second-Limit`, `RateLimit-Org-Day-Limit`
- x402/MPP: no rate limits (pay per request)

**SDK:** TypeScript (`@zerion/api`) — or direct REST calls

**Solana Support:** ✅ Zerion supports Solana natively

### Adapter Architecture
```
adapters/zerion_cli/
├── index.ts          # Main entry — CLI commands
├── discovery.ts      # Auto-discover DeFi opportunities
├── delegation.ts     # Delegate tasks to agent network
├── portfolio.ts      # Portfolio analysis via Zerion API
├── config.ts         # API key, wallet address, chain config
└── README.md         # Submission docs
```

### CLI Commands
```bash
# Discover opportunities
agent discover --wallet <address> --chain solana

# Analyze portfolio
agent portfolio --wallet <address> --format json

# Delegate task
agent delegate --task "optimize-yield" --target-agent <agent_id>

# Run full scan
agent scan --all --output report.md
```

### Submission Narrative
"An AI agent that uses Zerion's API to autonomously discover, evaluate, and delegate DeFi tasks. The agent reads portfolio data, identifies yield opportunities, and coordinates with other agents in the Agent Economy to execute optimal strategies."

---

## Adapter 2: GoldRush/Covalent ($3K)

### What We're Building
Agent risk dashboard that pulls real-time on-chain position data via GoldRush API. Feeds into AgentEscrow reputation system.

### API Surface (from goldrush.mintlify.app)

**Auth:** API key
- Get from: goldrush.covalenthq.com
- Also supports: x402 per-request payments

**Key Endpoints:**
| Endpoint | Purpose | Agent Use |
|----------|---------|-----------|
| `GET /v2/{chain}/address/{address}/balances_v2/` | Token balances with USD pricing | Agent portfolio snapshot |
| `GET /v2/{chain}/address/{address}/transactions_v2/` | Transaction history | Verify agent task completion |
| `GET /v2/{chain}/address/{address}/token-transfers/` | Token transfers | Track agent payments |
| `GET /v2/{chain}/tokens/{token_address}/` | Token metadata | Evaluate token quality |
| `GET /v2/{chain}/address/{address}/nfts/` | NFT holdings | Reputation NFT tracking |
| `GET /v2/{chain}/transaction/{tx_hash}/` | Decoded transaction | Verify escrow releases |

**Supported Chains:** 200+ chains including Solana, Ethereum, Base, Avalanche

**SDK:** TypeScript (`@covalenthq/client-sdk`)
```bash
npm install @covalenthq/client-sdk
```

**Also Available:**
- GoldRush CLI — for quick queries
- GoldRush MCP Server — for AI agent integration
- GoldRush Agent Skills — pre-built agent capabilities

**Pricing:** Starts at $10/mo (hackathon: free tier likely sufficient)

### Adapter Architecture
```
adapters/goldrush/
├── index.ts          # Main entry — dashboard queries
├── risk-scoring.ts   # Agent risk score computation
├── position-health.ts # DeFi position health monitoring
├── reputation-feed.ts # Feed data into AgentEscrow reputation
├── config.ts         # API key, chain config
└── README.md         # Submission docs
```

### Dashboard Features
```bash
# Risk score for an agent
goldrush risk-score --agent <agent_id>

# Position health check
goldrush health --wallet <address> --chain solana

# Reputation feed
goldrush reputation --agent <agent_id> --output report.json

# Full risk dashboard
goldrush dashboard --all-agents --format html
```

### Integration with AgentEscrow
The GoldRush adapter feeds directly into our existing `reputation` Solana program:
1. Fetch on-chain balances + transaction history via GoldRush
2. Compute risk scores (balance stability, tx frequency, DeFi engagement)
3. Feed into `reputation` program as on-chain reputation data
4. Judges see: real-time agent risk dashboard + reputation scores

### Submission Narrative
"A risk intelligence dashboard powered by GoldRush/Covalent that gives agents real-time on-chain data feeds. Tracks agent portfolio health, computes risk scores, and feeds verified on-chain reputation into the AgentEscrow trust infrastructure."

---

## Shared Infrastructure

### Common Dependencies
- `@zerion/api` — Zerion API client
- `@covalenthq/client-sdk` — GoldRush API client
- `anchor` — Solana program interaction (existing)
- `@solana/web3.js` — Solana SDK (existing)

### API Keys Needed
| Service | Key Source | Cost |
|---------|-----------|------|
| Zerion | dashboard.zerion.io | Free tier (or x402) |
| GoldRush | goldrush.covalenthq.com | $10/mo or free tier |

### What DMOB Needs to Do
1. **Day 2 (May 6):** Register for both API keys, scaffold both adapter projects
2. **Day 3 (May 7):** Zerion adapter — portfolio discovery + CLI commands
3. **Day 3 (May 7):** GoldRush adapter — risk scoring + position health
4. **Day 4 (May 8):** Polish both, add error handling, test end-to-end
5. **Day 5 (May 9):** Final testing, write submission docs

### Submission Strategy
- **Main submission** (AgentEscrow) goes to Colosseum Frontier grand prizes
- **Zerion adapter** goes to Zerion "Autonomous Onchain Agent" sidetrack ($5K)
- **GoldRush adapter** goes to "Build with GoldRush" sidetrack ($3K)
- Both adapters reference the same core AgentEscrow architecture

---

*Last updated: 2026-05-05 by YoYo*
