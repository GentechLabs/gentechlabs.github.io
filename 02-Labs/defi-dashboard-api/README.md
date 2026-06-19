# GenTech DeFi Dashboard API

DeFi intelligence for AI agents — pay per query via x402.

## Endpoints

| Endpoint | Description | Pricing |
|----------|-------------|---------|
| `GET /` | API info | Free |
| `GET /api/v1/position/status` | Current LP position status | $0.001-0.01 |
| `GET /api/v1/position/fees` | Fee analytics | $0.002-0.02 |
| `GET /api/v1/position/range` | Range optimization | $0.005-0.05 |
| `GET /api/v1/portfolio/sync` | Portfolio sync status | $0.01-0.10 |
| `GET /api/v1/market/macro` | Macro events | $0.001-0.01 |
| `GET /api/v1/agent/health` | Agent health | Free |

## Pricing Tiers

| Agent Type | Rate |
|------------|------|
| Verified (AAE-compliant) | $0.001-0.01/request |
| Unverified | $0.01-0.10/request |

## Payment

- **Method:** x402 (HTTP 402)
- **Currency:** USDC on Base
- **Facilitator:** Coinbase (zero fees)
- **No API keys required** — just pay per request

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Deployment

1. Deploy to CloudFront
2. Enable WAF Bot Control
3. Create Protection Packs for each endpoint
4. Enable x402 monetization

## Agent Usage

```python
import requests

# Verified agent (AAE-compliant)
response = requests.get(
    "https://api.gentech.dev/api/v1/position/status",
    headers={"X-Agent-Verification": "verified"}
)

# Unverified agent
response = requests.get(
    "https://api.gentech.dev/api/v1/position/status"
)
```

## Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

*GenTech DeFi Dashboard API — 2026-06-18*
