# Module 3: Pricing Strategies

**Course:** Ship Paid APIs in a Weekend  
**Duration:** 4 lessons + 1 hands-on exercise  
**Target:** Web3 / dev-focused developers  
**Style:** Practical, concise, real examples

---

## Lesson 3.1: Per-Call vs Per-Decision Pricing

### The Two Models

There are fundamentally two ways to price an API for AI agents:

| Model | How It Works | Best For | Example |
|-------|-------------|----------|---------|
| **Per-call** | Fixed price per request | Simple data lookups | $0.001 per price check |
| **Per-decision** | Price scales with output value | Analysis, risk scoring | $0.01 per rugcheck, $0.05 per credit score |

### Per-Call Pricing

The simplest model. Every API call costs the same amount, regardless of what the agent does with the data.

**When to use it:**
- Your API returns a fixed piece of data (price, balance, block info)
- The computation cost is roughly the same per request
- You want maximum agent adoption (lowest friction)

**Real example from GenTech Labs:**

```json
{
  "endpoint": "/api/v1/price",
  "model": "per-call",
  "price": "0.001 USDC",
  "chain": "base",
  "reasoning": "Price lookups are stateless, cacheable, and cheap to serve"
}
```

### Per-Decision Pricing

The agent pays more when the answer is more valuable. This aligns your revenue with the value you deliver.

**When to use it:**
- Your API performs analysis, not just lookups
- The output has variable value (a "risky" verdict is worth more than a "safe" one)
- You're competing on quality, not price

**Real example from GenTech Labs:**

```json
{
  "endpoint": "/api/v1/rugcheck",
  "model": "per-decision",
  "price": "0.01 USDC",
  "chain": "base",
  "reasoning": "A rugcheck verdict saves an agent from losing its entire treasury. Worth 10x a price lookup."
}
```

### The Hybrid Approach

Many successful x402 APIs use both models:

```
Free tier:    5 calls/day (no payment needed)
Per-call:     $0.001/call (basic data)
Per-decision: $0.01/call (analysis, scoring)
Enterprise:   Custom pricing (dedicated throughput)
```

---

## Lesson 3.2: Finding the Right Price Point

### The Rule of Thumb

**Your API should cost less than the value it provides, but more than the cost to serve it.**

```
Cost to serve < Your price < Value to the agent
```

### Price Anchors

Here's what agents are used to paying:

| Service | Price | Category |
|---------|-------|----------|
| Simple data lookup | $0.001–$0.005 | Per-call |
| Token analysis | $0.005–$0.02 | Per-decision |
| Security audit | $0.01–$0.10 | Per-decision |
| Credit score | $0.05–$0.25 | Per-decision |
| Human feedback | $0.025–$0.10 | Per-task |

### The $0.001 Floor

x402 makes micropayments practical. The minimum viable price is **$0.001** (1/1000th of a USDC). Below that, the transaction overhead (signing, verification, chain fees) dominates the economics.

**Rule:** Never price below $0.001 per call. If your data is that cheap, bundle it — 100 lookups for $0.01 instead of 1 lookup for $0.0001.

### Finding Your Price: The 3-Step Method

**Step 1: Calculate your cost**

```python
# Example: VPS-hosted FastAPI
monthly_vps = 10.00  # $10/month
monthly_requests = 100000  # 100k requests
cost_per_request = monthly_vps / monthly_requests
print(f"Cost per request: ${cost_per_request:.6f}")
# Cost per request: $0.000100
```

**Step 2: Apply margin**

```python
cost = 0.0001
margin = 10  # 10x margin
price = cost * margin
print(f"Price per call: ${price:.4f}")
# Price per call: $0.0010
```

**Step 3: Compare to value**

```python
# If your API saves an agent $0.05 per call in gas fees:
value_to_agent = 0.05
your_price = 0.001
print(f"Agent saves: ${value_to_agent - your_price:.4f} per call")
# Agent saves: $0.0490 per call
```

### Pricing Psychology for Agents

Agents don't have emotions about pricing — they optimize for utility. But the humans who deploy them do:

- **Round numbers** are easier to reason about ($0.01 > $0.0097)
- **Tiered pricing** signals professionalism
- **Free tier** builds trust before payment
- **Transparent pricing** in the 402 response is non-negotiable

---

## Lesson 3.3: Tiered Offerings

### The Three-Tier Pattern

Every successful x402 API follows this pattern:

| Tier | Price | What They Get | Who It's For |
|------|-------|---------------|-------------|
| **Free** | $0 | Limited calls, basic data | Discovery, testing |
| **Pro** | $0.001–$0.01/call | Full data, higher rate limit | Production agents |
| **Enterprise** | Custom | Dedicated throughput, SLA | High-volume clients |

### Implementing Tiers in Your 402 Response

```typescript
// src/index.ts — tiered pricing
const TIERS = {
  free: {
    price: "0",
    rateLimit: 5,  // requests per hour
    features: ["basic_price"],
  },
  pro: {
    price: "0.001",
    rateLimit: 1000,
    features: ["basic_price", "historical", "analysis"],
  },
  enterprise: {
    price: "contact_us",
    rateLimit: 100000,
    features: ["all"],
  },
};

function getTierFromRequest(request: Request): string {
  // Check for a tier header or API key
  const tier = request.headers.get("X-Tier") || "free";
  return TIERS[tier] ? tier : "free";
}

async function handleRequest(request: Request, env: Env): Promise<Response> {
  const tier = getTierFromRequest(request);
  const config = TIERS[tier];

  if (config.price === "0") {
    // Free tier — serve directly (with rate limiting)
    return handleFreeTier(request, env, config);
  }

  if (config.price === "contact_us") {
    // Enterprise — issue 402 with custom instructions
    return new Response(JSON.stringify({
      version: "x402-v1",
      payment: {
        type: "enterprise",
        instructions: "Contact us at enterprise@gentechlabs.net for dedicated pricing",
      },
    }), { status: 402 });
  }

  // Pro tier — standard x402 flow
  return handle402Challenge(request, env, config);
}
```

### The Free Tier Trap

**Don't make the free tier too good.** If agents can get everything they need for free, they'll never pay. Your free tier should:

- ✅ Demonstrate the API works
- ✅ Let agents test integration
- ❌ Not provide enough value for production use
- ❌ Not include your most valuable features

**Good free tier:** 5 calls/hour, basic data only, no historical data  
**Bad free tier:** 1000 calls/day, full data, no rate limiting

### Enterprise Pricing

Enterprise clients (large protocols, hedge funds, other agent networks) need custom pricing. The 402 response should gracefully redirect them:

```json
{
  "version": "x402-v1",
  "payment": {
    "type": "enterprise",
    "instructions": "Contact us at enterprise@gentechlabs.net for dedicated pricing",
    "alternatives": [
      { "tier": "pro", "price": "0.001", "rate_limit": "1000 req/h" }
    ]
  }
}
```

---

## Lesson 3.4: Caching Strategies

### Why Caching Matters for x402

Every paid API call costs the agent money. If two agents ask the same question in the same block, they shouldn't both pay. Caching reduces:

- **Agent costs** — agents don't pay for duplicate data
- **Your server costs** — fewer compute cycles
- **Latency** — cached responses are instant

### Time-Based Caching

The simplest strategy. Cache responses for a fixed TTL.

```typescript
// src/cache.ts
interface CacheEntry {
  data: any;
  expiresAt: number;
}

const cache = new Map<string, CacheEntry>();

export function getCached(key: string): any | null {
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) {
    cache.delete(key);
    return null;
  }
  return entry.data;
}

export function setCache(key: string, data: any, ttlMs: number): void {
  cache.set(key, { data, expiresAt: Date.now() + ttlMs });
}
```

**TTL guidelines by data type:**

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Token price | 10–30s | Changes every block |
| Wallet balance | 60s | Changes on tx |
| Rugcheck verdict | 300s (5 min) | Sticky — doesn't flip fast |
| Credit score | 3600s (1 hour) | Slow-moving |
| Historical data | 86400s (1 day) | Doesn't change |

### Content-Based Caching

Cache based on the request parameters, not the URL.

```typescript
function cacheKey(request: Request): string {
  const url = new URL(request.url);
  const params = new URLSearchParams(url.search);
  // Sort params for consistent keys
  const sorted = [...params.entries()].sort();
  return `${url.pathname}:${JSON.stringify(sorted)}`;
}
```

### The "Cache Receipt" Pattern

When an agent pays for data that's already cached, issue a **cache receipt** instead of charging again:

```typescript
async function handleRequest(request: Request, env: Env): Promise<Response> {
  const key = cacheKey(request);
  const cached = getCached(key);

  if (cached) {
    // Return cached data with a "cache hit" header
    return new Response(JSON.stringify(cached.data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'X-Cache': 'HIT',
        'X-Cache-Expires': String(cached.expiresAt),
      },
    });
  }

  // Not cached — proceed with 402 challenge
  return handle402Challenge(request, env);
}
```

Agents can check the `X-Cache` header. If it's `HIT`, they know they didn't pay. This encourages agents to try the cache first before paying.

### Cache Busting for Stale Data

Some data needs to be fresh. Let agents request a cache bypass:

```typescript
// Agent sends: X-Cache-Bypass: true
// Server skips cache and charges full price
if (request.headers.get('X-Cache-Bypass') === 'true') {
  return handle402Challenge(request, env);  // Always charges
}
```

### Pricing Cached vs Fresh Data

A common pattern: **cached data is free or discounted, fresh data costs full price.**

| Data Freshness | Price | Use Case |
|---------------|-------|----------|
| Cached (< 30s) | Free | Quick checks, monitoring |
| Fresh (real-time) | $0.001 | Trading decisions, critical ops |

```typescript
function getPrice(request: Request, key: string): string {
  const cached = getCached(key);
  if (cached) return "0";  // Free if cached
  return "0.001";  // Full price for fresh data
}
```

---

## Hands-on Exercise: Set Up 3 Pricing Tiers for a Data API

### Goal

Take a basic price API and add three tiers: Free (5 calls/hour), Pro ($0.001/call), and Enterprise (custom).

### Step 1: Start with the Module 2 Template

```bash
cp -r hello-x402 tiered-x402
cd tiered-x402
```

### Step 2: Add the Tier Configuration

Create `src/tiers.ts`:

```typescript
export interface TierConfig {
  price: string;
  rateLimit: number;
  features: string[];
}

export const TIERS: Record<string, TierConfig> = {
  free: {
    price: "0",
    rateLimit: 5,
    features: ["price"],
  },
  pro: {
    price: "0.001",
    rateLimit: 1000,
    features: ["price", "historical", "analysis"],
  },
  enterprise: {
    price: "contact_us",
    rateLimit: 100000,
    features: ["all"],
  },
};

export function getTier(request: Request): TierConfig {
  const tier = request.headers.get("X-Tier") || "free";
  return TIERS[tier] || TIERS.free;
}
```

### Step 3: Add Rate Limiting

Create `src/ratelimit.ts`:

```typescript
interface RateLimitEntry {
  count: number;
  resetAt: number;
}

const rateLimits = new Map<string, RateLimitEntry>();

export function checkRateLimit(key: string, limit: number): boolean {
  const now = Date.now();
  const entry = rateLimits.get(key);

  if (!entry || now > entry.resetAt) {
    rateLimits.set(key, { count: 1, resetAt: now + 3600000 }); // 1 hour
    return true;
  }

  if (entry.count >= limit) return false;

  entry.count++;
  return true;
}
```

### Step 4: Wire It Into the Handler

Update `src/index.ts`:

```typescript
import { TIERS, getTier } from './tiers';
import { checkRateLimit } from './ratelimit';

async function handlePriceRequest(request: Request, env: Env): Promise<Response> {
  const tier = getTier(request);
  const clientIp = request.headers.get('CF-Connecting-IP') || 'unknown';

  // Rate limit check
  if (!checkRateLimit(clientIp, tier.rateLimit)) {
    return new Response(JSON.stringify({
      error: 'Rate limit exceeded',
      tier: tier,
      upgrade: 'Send X-Tier: pro for higher limits',
    }), {
      status: 429,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Free tier — serve directly
  if (tier.price === "0") {
    const price = await fetchPrice('ETH');
    return new Response(JSON.stringify({
      symbol: 'ETH',
      price: price,
      tier: 'free',
      remaining: 'See X-RateLimit-Remaining header',
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Enterprise — redirect
  if (tier.price === "contact_us") {
    return new Response(JSON.stringify({
      version: 'x402-v1',
      payment: {
        type: 'enterprise',
        instructions: 'Contact us at enterprise@gentechlabs.net',
      },
    }), { status: 402 });
  }

  // Pro tier — standard 402 challenge
  return handle402Challenge(request, env, tier);
}
```

### Step 5: Deploy and Test

```bash
wrangler deploy

# Test free tier
curl -i -H "X-Tier: free" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH

# Test pro tier (should get 402)
curl -i -H "X-Tier: pro" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH

# Test enterprise tier
curl -i -H "X-Tier: enterprise" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH

# Test rate limiting (hit free tier 6 times)
for i in $(seq 1 6); do
  curl -s -H "X-Tier: free" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH | head -c 100
  echo ""
done
```

### Step 6: Verify the Output

```bash
# Free tier should return data
curl -s -H "X-Tier: free" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'✅ Free tier: {data[\"symbol\"]} = {data[\"price\"]}')
"

# Pro tier should return 402
curl -s -o /dev/null -w '%{http_code}' -H "X-Tier: pro" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH
# Should print: 402

# Enterprise should return 402 with contact info
curl -s -H "X-Tier: enterprise" https://tiered-x402.your-name.workers.dev/api/price?symbol=ETH | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'✅ Enterprise: {data[\"payment\"][\"instructions\"]}')
"
```

### What You Built

```
✅ Three-tier pricing (Free / Pro / Enterprise)
✅ Rate limiting per tier
✅ Cache-ready architecture
✅ Enterprise redirect flow
✅ curl-verifiable test suite
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Free tier returns 402 | Check that `tier.price === "0"` comparison uses string, not number |
| Rate limit not working | Ensure `CF-Connecting-IP` header is available (Cloudflare only) |
| Enterprise tier shows wrong message | Check the `contact_us` string match in your handler |
| Cache not returning hits | Verify `X-Cache` header is set on cached responses |

---

## Module Summary

| Lesson | Key Takeaway |
|--------|-------------|
| 3.1 Per-call vs Per-decision | Simple data = per-call. Analysis = per-decision. Both can coexist. |
| 3.2 Finding the Right Price | Cost × 10x margin, compare to agent value, never below $0.001 |
| 3.3 Tiered Offerings | Free → Pro → Enterprise. Free tier demonstrates, Pro tier monetizes, Enterprise tier scales. |
| 3.4 Caching Strategies | Cache reduces agent costs and your server load. Cache receipts let agents skip payment for duplicate data. |
| Hands-on | You deployed a 3-tier x402 API with rate limiting and caching |

**Next Module: Building Production-Grade x402 Services — CORS, rate limiting, security, and VPS proxying.**

---

*GenTech Academy — Ship Paid APIs in a Weekend*  
*Based on real-world experience building GenTech Labs' x402 gateway*
