# Q402 Payments Skill

> Subscription billing for AI agents.
> Recurring revenue without the overhead.

## What

Q402 is a subscription payment layer on top of x402. Instead of paying per-call, users subscribe monthly and get a credit allowance.

## How it works

1. You create subscription tiers ($3/mo, $10/mo, $25/mo)
2. Users subscribe via a /pay URL
3. Q402 issues a Trust Receipt (signed credential)
4. Agent verifies the Trust Receipt on each call
5. Credits are deducted per-call
6. When credits run low, the user is prompted to top up

## Tiers

| Tier | Price | Credits/mo | Rate limit |
|------|-------|------------|------------|
| Basic | $3 | 100 | 10/min |
| Pro | $10 | 500 | 60/min |
| Enterprise | $25 | 2000 | 300/min |

## Integration

### Server-side (verify subscription)

```typescript
import { Q402Middleware } from 'q402-sdk'

app.use('/api/*', Q402Middleware({
  tier: 'pro',
  creditsPerCall: 1
}))
```

### Client-side (subscribe)

```
https://gentechlabs.net/subscribe?tier=pro&redirect=https://your-agent.com/callback
```

### Check credits remaining

```bash
curl -H "Authorization: Bearer <user-token>" \
  https://your-agent.com/api/credits
```

## Configuration

```yaml
custom_providers:
  q402:
    api_key: ${Q402_API_KEY}
    base_url: https://api.q402.io/v1
```

## GenTech Q402

GenTech runs a Q402-compatible subscription hub. All starter template agents can wire into it:

- **Subscribe:** https://gentechlabs.net/pricing
- **Dashboard:** Track subscribers, revenue, and usage
