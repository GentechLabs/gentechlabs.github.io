# x402 Gateway Skill

> Integrate x402 pay-per-call payment into any Hermes agent.
> Every endpoint that costs money to run should cost money to call.

## What

x402 is an HTTP 402 Payment Required protocol for AI agents. Endpoints return 402 unless the caller includes a valid payment — then they get the actual API response.

## How to use

### Protecting an endpoint

Wrap any handler with x402 middleware:

```typescript
import { withX402 } from '@x402/hono'
import { Hono } from 'hono'

const app = new Hono()

app.get('/api/analyze', withX402(), async (c) => {
  const result = await analyzeSomething()
  return c.json(result)
})
```

### Making a paid call

```bash
curl -X POST https://your-agent.workers.dev/api/analyze \
  -H "Content-Type: application/json" \
  -H "x402-authorization: USDC base 0x..." \
  -d '{"query": "analyze this"}'
```

### Supported chains

- Base (recommended — lowest fees)
- Polygon
- Arbitrum

## Configuration

In your `config.yaml`:

```yaml
custom_providers:
  x402:
    api_key: ${X402_API_KEY}
    base_url: ${X402_GATEWAY_URL}
```

In `.env`:

```
X402_GATEWAY_URL=https://gentech-x402-gateway.jordanjones0902.workers.dev
X402_API_KEY=your_key
```

## GenTech x402 Gateway

Your starter agent already points to the GenTech-managed x402 gateway:

- **URL:** https://gentech-x402-gateway.jordanjones0902.workers.dev
- **Status:** Live — 16 endpoints, 3 chains
- **CLARITY Act:** Compliant — DeFi Exclusion (Sec. 309/409)

## Pricing

- **Pay-per-call:** $0.01–$0.50 per request depending on compute
- **Revenue share:** 70% to you, 30% to gateway operator
- **Settlement:** USDC on Base (instant), Polygon/Arbitrum (within blocks)

## Deployment

Deploy your own gateway:

```bash
npm install -g @x402/cli
x402 init my-gateway
cd my-gateway
x402 deploy
```

Or use GenTech's managed gateway (recommended for new agents):
https://gentechlabs.net/pricing
