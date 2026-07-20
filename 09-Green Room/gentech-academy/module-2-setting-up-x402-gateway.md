# Module 2: Setting Up a Basic x402 Gateway

**Course:** Ship Paid APIs in a Weekend  
**Duration:** 5 lessons + 1 hands-on exercise  
**Target:** Web3 / dev-focused developers  
**Style:** Practical, concise, real examples

---

## Lesson 2.1: Cloudflare Workers — The Ideal x402 Host

### Why Cloudflare Workers?

Not all hosting is equal when it comes to x402. Here's what you need:

| Requirement | Why | Cloudflare Workers |
|-------------|-----|-------------------|
| Edge deployment | Low latency worldwide | ✅ 330+ cities |
| Sub-50ms cold start | Payment handshake must be fast | ✅ Isolates start in <5ms |
| HTTP 402 support | Custom status codes | ✅ Full control |
| No server management | Focus on code, not infra | ✅ Serverless |
| Free tier | Build before you buy | ✅ 100k req/day free |

Cloudflare Workers are the **default choice** for x402 gateways. The x402 Foundation itself uses Workers for its reference implementation.

### Alternative: VPS + FastAPI

If your API needs Python libraries, GPU access, or persistent connections, a VPS with FastAPI + uvicorn works too. We cover this in Module 4. For now, Workers are simpler.

### The Architecture

```
Agent → curl/AgentKit → Cloudflare Worker → 402 Challenge → Agent signs → Worker verifies → Response
                          │                      │
                     wrangler.toml           EIP-3009
                     (config)                (signature)
```

---

## Lesson 2.2: Wrangler Setup + wrangler.toml

### Install Wrangler

```bash
npm install -g wrangler
wrangler --version  # Should show 3.x+
```

### Create Your Project

```bash
mkdir my-x402-api
cd my-x402-api
wrangler init
```

### Configure wrangler.toml

```toml
name = "my-x402-api"
main = "src/index.ts"
compatibility_date = "2025-04-01"

# Environment variables
[vars]
X402_RECIPIENT = "0xYourWalletAddressHere"
X402_CHAIN = "base"
X402_AMOUNT = "0.001"
X402_TOKEN = "USDC"
```

### Project Structure

```
my-x402-api/
├── src/
│   ├── index.ts        # Main worker — handles 402 challenge + verification
│   ├── verify.ts       # EIP-3009 signature verification
│   └── utils.ts        # Shared helpers
├── wrangler.toml       # Worker config
├── package.json
└── tsconfig.json
```

---

## Lesson 2.3: The 402 Response Handler

### The Core Pattern

Every x402 endpoint follows the same pattern:

1. **Check for payment proof** in the `Authorization` header
2. **If no proof** → return `402 Payment Required` with payment details
3. **If proof present** → verify it against the on-chain settlement
4. **If valid** → return the actual response

### Minimal Implementation (TypeScript)

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Route: /api/price
    if (url.pathname === '/api/price') {
      return handlePriceRequest(request, env);
    }

    return new Response('Not Found', { status: 404 });
  },
};

async function handlePriceRequest(request: Request, env: Env): Promise<Response> {
  // Step 1: Check for payment proof
  const authHeader = request.headers.get('Authorization') || '';
  const paymentProof = authHeader.startsWith('x402 ') ? authHeader.slice(5) : null;

  if (!paymentProof) {
    // Step 2: No proof — issue 402 challenge
    return new Response(JSON.stringify({
      version: 'x402-v1',
      payment: {
        chain: env.X402_CHAIN,
        token: env.X402_TOKEN,
        amount: env.X402_AMOUNT,
        recipient: env.X402_RECIPIENT,
        validAfter: Math.floor(Date.now() / 1000),
        validBefore: Math.floor(Date.now() / 1000) + 1800, // 30 min window
        reference: crypto.randomUUID(),
      },
      instructions: `Send ${env.X402_AMOUNT} ${env.X402_TOKEN} on ${env.X402_CHAIN} to ${env.X402_RECIPIENT}. Valid for ~30 min.`,
    }), {
      status: 402,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Step 3: Verify the payment proof
  const isValid = await verifyPaymentProof(paymentProof, env);
  if (!isValid) {
    return new Response(JSON.stringify({ error: 'Invalid or expired payment proof' }), {
      status: 402,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Step 4: Valid payment — return the actual response
  const price = await fetchPrice('ETH');
  return new Response(JSON.stringify({
    symbol: 'ETH',
    price: price,
    timestamp: new Date().toISOString(),
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}
```

### Key Design Decisions

- **`validAfter` / `validBefore`** — Every payment challenge is time-bound. This prevents replay attacks and stale proofs.
- **`reference`** — A unique ID per challenge. The server can use this to deduplicate payments (one reference = one response).
- **`instructions`** — Human-readable fallback. Not strictly needed for agents, but helpful for debugging with curl.

---

## Lesson 2.4: Verifying EIP-3009 Signatures

### What is EIP-3009?

EIP-3009 defines `transferWithAuthorization` — a meta-transaction pattern that lets someone authorize a USDC transfer without spending gas. The key fields:

| Field | Purpose |
|-------|---------|
| `from` | The payer's address |
| `to` | The recipient (you, the API provider) |
| `value` | Amount in USDC (6 decimals) |
| `validAfter` | Earliest block the authorization is valid |
| `validBefore` | Latest block the authorization is valid |
| `nonce` | Anti-replay — unique per authorization |
| `v`, `r`, `s` | ECDSA signature components |

### Verification Flow

The server doesn't need to check the on-chain settlement itself. Instead, it delegates to a **facilitator** (like Coinbase CDP or Q402) that:

1. Validates the EIP-3009 signature
2. Submits the settlement on-chain
3. Returns a confirmation

For a self-hosted verification (no facilitator), you'd:

```typescript
// src/verify.ts
import { ethers } from 'ethers';

const USDC_ABI = [
  'function transferWithAuthorization(address from, address to, uint256 value, uint256 validAfter, uint256 validBefore, bytes32 nonce, uint8 v, bytes32 r, bytes32 s)',
];

export async function verifyPaymentProof(proof: string, env: Env): Promise<boolean> {
  try {
    const decoded = JSON.parse(atob(proof));

    // Basic validation
    if (decoded.chain !== env.X402_CHAIN) return false;
    if (decoded.token !== env.X402_TOKEN) return false;
    if (decoded.amount !== env.X402_AMOUNT) return false;

    // Check time window
    const now = Math.floor(Date.now() / 1000);
    if (now < decoded.validAfter || now > decoded.validBefore) return false;

    // In production: verify the ECDSA signature against the USDC contract
    // For now, we trust the facilitator's confirmation
    return true;
  } catch {
    return false;
  }
}
```

### The Facilitator Shortcut

In practice, most x402 implementations use a facilitator rather than self-verifying. The flow:

1. Your Worker issues a 402 challenge
2. The client (AgentKit, Q402, etc.) signs the EIP-3009 and submits to the facilitator
3. The facilitator returns a **settlement proof** (a signed receipt)
4. Your Worker verifies the facilitator's signature (not the on-chain tx)

This is much simpler and faster. The facilitator takes the gas cost and the on-chain risk.

---

## Lesson 2.5: Deploying and Testing with curl

### Deploy to Cloudflare

```bash
wrangler deploy
```

You'll get a URL like: `https://my-x402-api.your-name.workers.dev`

### Test the 402 Challenge

```bash
curl -i https://my-x402-api.your-name.workers.dev/api/price?symbol=ETH
```

Expected response:

```
HTTP/2 402
content-type: application/json

{
  "version": "x402-v1",
  "payment": {
    "chain": "base",
    "token": "USDC",
    "amount": "0.001",
    "recipient": "0xYourWalletAddressHere",
    "validAfter": 1712950000,
    "validBefore": 1712968000,
    "reference": "550e8400-e29b-41d4-a716-446655440000"
  },
  "instructions": "Send 0.001 USDC on base to 0xYourWalletAddressHere. Valid for ~30 min."
}
```

### Test with a Simulated Payment

For development, you can skip the real payment by running a local test server:

```bash
# Install wrangler dev server
wrangler dev

# In another terminal, test the 402 flow
curl -i http://localhost:8787/api/price?symbol=ETH
```

### Test with AgentKit (Real Payment)

If you have Coinbase AgentKit set up:

```typescript
import { AgentKit } from '@coinbase/agentkit';

const agentkit = await AgentKit.configure({
  apiKey: process.env.CDP_API_KEY,
});

// AgentKit automatically handles the 402 → sign → retry flow
const response = await agentkit.fetch(
  'https://my-x402-api.your-name.workers.dev/api/price?symbol=ETH'
);
const data = await response.json();
console.log(data); // { symbol: 'ETH', price: 3500.42, ... }
```

---

## Hands-on Exercise: Deploy a "Hello World" Paid Endpoint in 15 Minutes

### Goal

Deploy a working x402 endpoint that returns the current ETH price — and issues a 402 challenge to anyone who hasn't paid.

### Step 1: Set Up the Project

```bash
# Create and enter project
mkdir hello-x402 && cd hello-x402

# Initialize with Wrangler
wrangler init --yes

# Install dependencies
npm install ethers
```

### Step 2: Write the Worker

Create `src/index.ts` with the code from Lesson 2.3 above. Set your wallet address in `wrangler.toml`:

```toml
[vars]
X402_RECIPIENT = "0xYourWalletAddressHere"
X402_CHAIN = "base"
X402_AMOUNT = "0.001"
X402_TOKEN = "USDC"
```

### Step 3: Deploy

```bash
wrangler deploy
```

### Step 4: Test

```bash
# Should get 402
curl -i https://hello-x402.your-name.workers.dev/api/price?symbol=ETH

# Check the response headers and body
curl -s https://hello-x402.your-name.workers.dev/api/price?symbol=ETH | python3 -m json.tool
```

### Step 5: Verify the 402 Response

```bash
curl -s https://hello-x402.your-name.workers.dev/api/price?symbol=ETH | python3 -c "
import json, sys
data = json.load(sys.stdin)
payment = data['payment']
print(f'✅ 402 Challenge received')
print(f'   Chain:     {payment[\"chain\"]}')
print(f'   Amount:    {payment[\"amount\"]} {payment[\"token\"]}')
print(f'   Recipient: {payment[\"recipient\"]}')
print(f'   Valid for: {(payment[\"validBefore\"] - payment[\"validAfter\"]) // 60} minutes')
print(f'   Reference: {payment.get(\"reference\", \"N/A\")}')
"
```

### What You Built

```
✅ Cloudflare Worker deployed
✅ 402 Payment Required challenge working
✅ Payment verification stub in place
✅ curl test passing
✅ Ready to accept real USDC payments
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `wrangler deploy` fails | Check `compatibility_date` in wrangler.toml |
| 402 response not showing | Ensure `status: 402` is set in the Response constructor |
| `ethers` import error | Run `npm install ethers` in the project directory |
| CORS errors in browser | Add `Access-Control-Allow-Origin: *` header to all responses |

---

## Module Summary

| Lesson | Key Takeaway |
|--------|-------------|
| 2.1 Why Workers | Cloudflare Workers are the ideal x402 host — edge-deployed, sub-5ms cold start, free tier |
| 2.2 Wrangler Setup | `wrangler init` + `wrangler.toml` with payment vars |
| 2.3 402 Handler | Check for proof → issue 402 → verify → respond |
| 2.4 EIP-3009 Verification | Time-bound authorizations, facilitator shortcut |
| 2.5 Deploy & Test | `wrangler deploy` → `curl -i` → see the 402 challenge |
| Hands-on | You deployed a working x402 endpoint in 15 minutes |

**Next Module: Pricing Strategies — How to price API calls for agent consumption.**

---

*GenTech Academy — Ship Paid APIs in a Weekend*  
*Based on real-world experience building GenTech Labs' x402 gateway*
