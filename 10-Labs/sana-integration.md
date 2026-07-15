# GenTech x402 Gateway — Sana Bot Integration

## Architecture

Two systems that complement each other:

| Layer | Sana Bot | GenTech x402 Gateway |
|-------|----------|---------------------|
| **What** | Banking + card for agents on Solana | Multi-chain x402 API services |
| **Auth** | API key (bearer token) | x402 micropayment (402 → sign → settle) |
| **Protocol** | MCP (tools/list, tools/call) | REST (GET /api/*) |
| **Chain** | Solana only | Base, Solana, Avalanche, BNB, OKX |
| **Payment** | Card balance, wallet swap | USDC per-call via x402 |

## Setup

Sana API key is stored in:
```
/root/vaults/gentech/credentials/sana-api-key.txt
sana_live_Pc597qQesCmYS9wVKZ1gNZss7MztC3lselyWyOk5AH5NTZoi_4931c7
```

## Sana MCP Gateway

Endpoint: `https://mcp.sana.bot/mcp`
Auth: `Authorization: Bearer <key>`
Protocol: JSON-RPC 2.0 over HTTP POST

### Available Sana Tools (12 total)

| Tool | Description | Input |
|------|-------------|-------|
| `get_account` | User's wallet, email, chain | {} |
| `get_card` | Card metadata (type, status, last4, expiry) | {} |
| `get_card_balance` | Credit limit, pending charges, available | {} |
| `get_card_sensitive` | Full PAN + CVV | {} |
| `card_deposit` | Deposit USDC from wallet to card | { amount: string, idempotency_key?: uuid } |
| `get_holdings` | Non-zero token holdings | { refresh?: boolean } |
| `get_net_worth` | Total net worth + breakdown | { refresh?: boolean } |
| `get_notifications` | Recent notification feed | {} |
| `get_price` | USD price + 24h change | { symbol?: string } |
| `get_supported_tokens` | Full token catalog | {} |
| `get_transaction_history` | Paginated tx history | { limit?: int, cursor?: string } |
| `wallet_swap` | Token swap via Jupiter | { from: string, to: string, amount: string, slippageBps?: int } |

## Integration Pattern — Workflow

When an agent needs data our gateway serves better:

1. **Agent discovers Sana tools** — via `tools/list` on `mcp.sana.bot/mcp`
2. **Agent uses Sana for banking** — card balance, deposits, swaps
3. **Agent uses GenTech for intelligence** — token risk, yields, wallet analysis via our REST endpoints
4. **Payment flows both ways** — Sana settles in Solana USDC, GenTech settles via x402 on any chain

## Sample Queries

### "Is this token safe before I buy it?"
```
→ Sana: get_price(symbol: "TOKEN")
→ GenTech: GET /api/token/risk?address=0x...&chain=solana
```

### "What's my wallet worth and how can I optimize yield?"
```
→ Sana: get_net_worth(refresh: true) / get_holdings()
→ GenTech: GET /api/intel/search?q=best lending APY solana
```

### "Analyze this wallet before I send funds"
```
→ GenTech: GET /api/wallet/analyze?address=<wallet>
→ Sana: card_deposit(amount: "result") if safe
```
