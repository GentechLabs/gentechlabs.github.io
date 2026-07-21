# DeFi Intelligence API

Real-time DeFi protocol data and analytics via BlockRun integration.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/tokens/{token_id}/price` | Get token price in USD |
| GET | `/api/v1/tokens/batch-prices` | Get multiple token prices |
| GET | `/api/v1/pools/top` | Get top yielding pools (filterable) |
| GET | `/api/v1/pools/{pool_address}/metrics` | Get specific pool metrics |
| GET | `/api/v1/protocols/{protocol_name}/analytics` | Get protocol analytics |
| GET | `/api/v1/flash-loans` | Get available flash loans |
| GET | `/api/v1/blockrun/status` | Check BlockRun connectivity |

## Deployment

```bash
bash deploy.sh
```

Server runs on port 8002.

## Usage Example

```bash
# Get top pools on Avalanche
curl "http://localhost:8002/api/v1/pools/top?chain=avalanche"

# Get token price
curl http://localhost:8002/api/v1/tokens/avalanche-2/price

# Get batch prices
curl "http://localhost:8002/api/v1/tokens/batch-prices?token_ids=bitcoin,ethereum,avalanche-2"
```

## Status

✅ Deployed and verified (PID: 2394616)