# Module 1: What is x402?

**Course:** Ship Paid APIs in a Weekend  
**Duration:** 4 lessons + 1 hands-on exercise  
**Target:** Web3 / dev-focused developers  
**Style:** Practical, concise, real examples

---

## Lesson 1.1: The Problem

### Why API Billing is Broken

APIs today operate on a broken model. You either get:

- **Free APIs** — unsustainable for providers, rate-limited, discontinued without warning, zero SLA.
- **Account-based billing** — sign up, create an account, paste in a credit card, generate API keys, manage rate limits, track usage dashboards, handle overage charges, deal with invoices. It takes **30 minutes to an hour** just to make your first call.

And let's be honest — nobody reads the billing page until the surprise $500 bill arrives at the end of the month.

### The AI Agent Problem

This gets worse with AI agents. Agents can't:

- Fill out signup forms
- Click through CAPTCHAs
- Manage API keys across sessions
- Deal with 50 different billing portals

**But agents can sign transactions.** That's the key insight.

### HTTP 402 — The Lost Status Code

Back in 1998, RFC 2616 defined HTTP status code **402 Payment Required**:

> *"Reserved for future use."*

For 25+ years, 402 sat dormant. No standard existed for what a 402 response should look like — what headers, what body, what flow.

**x402 finally gives HTTP 402 meaning.** It defines a standard handshake where:

1. The server responds with a 402 containing payment details (price, chain, recipient address)
2. The client creates an on-chain payment proof (EIP-3009 signature)
3. The client retries the request with that proof
4. The server verifies the proof and delivers the response

No accounts. No API keys. No recurring bills. Just pay-per-call via USDC.

### Why This Matters Now

Three trends make x402 inevitable:

1. **AI agents are going mainstream** — they need programmatic, account-free access to APIs
2. **USDC settled ~$2T in 2024** — stablecoins are the default payment rail for machines
3. **Wallets are universal** — every dev has a wallet; not every dev has a corporate credit card

---

## Lesson 1.2: How x402 Works

### The Three-Step Handshake

x402 is a protocol for paying for API calls with USDC. Here's the exact flow, step by step:

#### Step 1: The 402 Challenge

```
GET /api/analyze
Host: api.gentechlabs.net
```

The server responds with:

```
HTTP 402 Payment Required
Content-Type: application/json

{
  "version": "x402-v1",
  "payment": {
    "chain": "base",
    "token": "USDC",
    "amount": "0.001000",
    "recipient": "0x1234...abcd",
    "deadline": 1712966400
  }
}
```

This is the **402 challenge** — it tells the client exactly what to pay, where, and to whom.

#### Step 2: The Payment Proof

The client (agent, CLI, browser wallet) creates an **EIP-3009 `transferWithAuthorization`** — a signed message that authorizes the USDC transfer. Crucially:

- **No ETH needed for gas** — the facilitator covers gas
- **No approval needed** — EIP-3009 is a meta-transaction pattern
- **Cancellable offline** — the authorization has a `validAfter` and `validBefore` window

The signed authorization is sent to a **facilitator** (like Coinbase CDP or a Q402 relayer), which validates the signature and submits the on-chain transfer.

#### Step 3: The Verified Response

Once the facilitator confirms the settlement (or provides a pre-confirmation), the client retries the request with the payment proof:

```
GET /api/analyze
Host: api.gentechlabs.net
Authorization: x402 <signed-proof>
```

The server verifies the proof against the on-chain settlement and delivers the response:

```
HTTP 200 OK
Content-Type: application/json

{ "result": "analysis complete", ... }
```

### The Numbers

| Metric | Value |
|--------|-------|
| Total round-trip | ~2 seconds |
| Cost per call | $0.001 (micro) to $0.10 (ultra) |
| Gas | $0 — sponsored by facilitator |
| Settlement finality | ~1 block (~2s on Base) |

### Key Properties

- **No API keys** — your wallet is your auth
- **No accounts** — stateless from the provider's perspective
- **No recurring bills** — every call is paid individually
- **No ETH/BNB needed** — pay with pure USDC

---

## Lesson 1.3: The Ecosystem

### Who's Building on x402

The x402 ecosystem is growing fast. Here's who's in it:

#### Solana Pay — The First Mover

Solana Pay established the x402 pattern in 2022 with its transaction request standard. They defined the core flow: a merchant presents a 402 challenge → wallet signs the transaction → settlement on Solana. The `solana-foundation/pay-skills` GitHub repo is the canonical catalog of x402-enabled APIs, with OpenAPI specs and endpoint documentation.

#### Coinbase AgentKit — The Enterprise Path

Coinbase's AgentKit (formerly CDP SDK) includes a built-in x402 facilitator. When an agent hits a 402 response, AgentKit:

1. Extracts the payment params from the 402 body
2. Signs an EIP-3009 authorization using the agent's wallet
3. Submits it through Coinbase's settlement infrastructure (sponsoring gas)
4. Retries the original request with the proof

AgentKit is how Coinbase is positioning for the AI agent economy — making every agent crypto-native by default.

#### GenTech Labs — The Indie Builder

GenTech Labs runs **16 x402 endpoints** across DeFi, gaming, security, and automation. Real-world pricing:

| Tier | Price | Example |
|------|-------|---------|
| Micro | $0.001 | Token price check, basic analytics |
| Standard | $0.01 | LP position analysis, market data |
| Premium | $0.05 | Portfolio optimization, risk scoring |
| Ultra | $0.10 | Real-time simulation, complex queries |

Every endpoint follows the same x402 handshake pattern — no accounts, no keys, just USDC.

#### Q402 — Gasless for EVM

Q402 (by QuackAI) adds gasless settlement to the EVM ecosystem using EIP-7702. Instead of requiring agents to hold ETH/BNB for gas, Q402 sponsors the transaction fee. This makes x402 viable on Ethereum, BNB Chain, Base, Arbitrum, and more — without the agent ever needing native gas tokens.

#### Bazaar — Discovery + Wallet

Bazaar (bazaar.cdp.coinbase.com) is a marketplace for x402-enabled APIs. It combines:

- **Service discovery** — browse available x402 endpoints
- **Wallet connection** — one-click wallet auth
- **Payment history** — track what you've spent

### Why Multiple Implementations Matter

Ecosystem diversity means x402 isn't owned by any single company. Solana Pay handles Solana settlement, Coinbase handles institutional flow, Q402 handles EVM gasless, GenTech handles indie experimentation. The protocol is the same — the implementation varies.

---

## Lesson 1.4: Economics — Why Micropayments Beat Subscriptions

### The Subscription Tax

AI agents make **thousands of API calls per hour**. Under the subscription model, each agent needs:

- An API key (per provider)
- A billing account (with credit card)
- A tiered plan (usually $20–$500/mo)

If you're running 10 agents across 5 API providers, that's **50 API keys, 5 billing portals, and $500+/mo in subscription fees** — even if 90% of those calls never happen.

With x402 micropayments, you pay **only for what you use**.

### The Math

| Model | 1 agent | 10 agents | 100 agents |
|-------|---------|-----------|------------|
| Subscription ($50/mo × providers) | $250/mo | $250/mo | $250/mo |
| x402 (1000 calls/day × $0.001) | ~$30/mo | ~$300/mo | ~$3,000/mo |

At low call volumes, subscriptions overpay for unused capacity. At high volumes, x402 is still cheaper because there's no flat-rate overhead — every dollar buys a call.

### The Experimentation Flywheel

Per-call pricing unlocks a fundamentally different behavior:

1. **Try anything** — test an API for $0.05
2. **Compare providers** — run the same query against 3 endpoints for $0.15
3. **Scale what works** — if it's profitable at $0.01/call, run it at 10,000 calls
4. **Drop what doesn't** — no sunk cost, no contract cancellation

This is the same dynamic that made AWS succeed: you don't need a $10,000 server quote to test a new service.

### Real GenTech Pricing

GenTech Labs' 16 endpoints demonstrate the range:

| Endpoint Category | Price | Call Volume (daily) | Daily Revenue |
|-------------------|-------|---------------------|---------------|
| Token price check | $0.001 | 5,000 | $5 |
| LP analysis | $0.01 | 500 | $5 |
| Risk scoring | $0.05 | 100 | $5 |
| Real-time simulation | $0.10 | 50 | $5 |

The lower the price, the higher the volume — and the revenue is surprisingly flat across the curve.

### Micropayments Are Machine Money

The real insight: **micropayments are the native payment format for machines.** Humans hate paying $0.05 per call (decision fatigue). Machines don't care — they just need the data. x402 removes the human from the billing loop entirely, which is exactly what the agent economy needs.

---

## Hands-on Exercise: Make Your First x402 Request with curl

### Goal

Trigger a 402 response from a live x402 endpoint, inspect the payment challenge, and understand the full handshake flow.

### Prerequisites

- curl (any modern version)
- A crypto wallet (MetaMask, Coinbase Wallet, etc.) — optional for the simulation path

### Step 1: Send a Request

Make a GET request to GenTech Labs' x402 endpoint without any payment:

```bash
curl -i https://api.gentechlabs.net/v1/price\?symbol\=ETH
```

### Step 2: See the 402 Response

You'll get something like:

```
HTTP/2 402
content-type: application/json

{
  "version": "x402-v1",
  "payment": {
    "chain": "base",
    "token": "USDC",
    "amount": "0.001000",
    "recipient": "0x1234...abcd",
    "validAfter": 1712950000,
    "validBefore": 1712960000,
    "reference": "ref_abc123"
  },
  "instructions": "Send 0.001 USDC on Base to 0x1234...abcd. Valid for ~30 min."
}
```

Let's break down what you're seeing:

| Field | Meaning |
|-------|---------|
| `chain` | Blockchain where payment settles (Base, in this case) |
| `amount` | Cost of this API call in USDC |
| `recipient` | The API provider's wallet address |
| `validAfter` / `validBefore` | Time window for the payment — it's time-bound |
| `reference` | Unique reference so the server can match your payment to the request |

### Step 3: Simulate Payment (No Wallet Needed)

You don't need to spend real USDC to understand the flow. Save the 402 response to a file and practice parsing it:

```bash
# Save the 402 response
curl -s https://api.gentechlabs.net/v1/price\?symbol\=ETH > response_402.json

# Parse the payment details
cat response_402.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
payment = data['payment']
print(f'Chain:     {payment[\"chain\"]}')
print(f'Amount:    {payment[\"amount\"]} {payment[\"token\"]}')
print(f'Recipient: {payment[\"recipient\"]}')
print(f'Reference: {payment.get(\"reference\", \"N/A\")}')
"
```

You should see output like:

```
Chain:     base
Amount:    0.001000 USDC
Recipient: 0x1234...abcd
Reference: ref_abc123
```

### Step 4: What Happens Next (Conceptual)

If you were completing the payment, the flow would be:

1. **Your wallet** signs an EIP-3009 `transferWithAuthorization` for 0.001 USDC on Base
2. **You** submit the proof to a facilitator (or Coinbase CDP handles it automatically via AgentKit)
3. **The facilitator** submits the settlement on-chain, sponsoring the gas
4. **You retry** the request with the proof in the `Authorization: x402 <proof>` header
5. **The server** verifies the proof and returns `200 OK` with the price data

### Step 5: Try Another Endpoint

GenTech Labs has multiple tiers. Try the micro ($0.001) and premium ($0.05) endpoints:

```bash
# Micro tier
curl -i https://api.gentechlabs.net/v1/health

# Standard tier
curl -i https://api.gentechlabs.net/v1/analyze\?address\=0x...

# Premium tier
curl -i https://api.gentechlabs.net/v1/portfolio\?address\=0x...
```

Each will return a 402 with different pricing, demonstrating the per-call pricing model.

### What You Learned

- ✅ You can trigger an x402 402 Payment Required response
- ✅ You can parse the payment challenge (chain, amount, recipient, deadline)
- ✅ You understand the 3-step handshake conceptually
- ✅ You know the round-trip is ~2 seconds, sponsored gas
- ✅ You've seen how pricing varies per endpoint

**In Module 2, you'll implement your own x402 endpoint and accept your first USDC payment.**

---

## Module Summary

| Lesson | Key Takeaway |
|--------|-------------|
| 1.1 The Problem | API billing is broken for agents; x402 fixes it |
| 1.2 How x402 Works | 3-step handshake: 402 challenge → EIP-3009 proof → verified response |
| 1.3 The Ecosystem | Solana Pay, Coinbase AgentKit, GenTech Labs, Q402, Bazaar |
| 1.4 Economics | Micropayments align cost with usage — try for pennies, scale what works |
| Hands-on | You made your first x402 request and parsed the payment challenge |

**Next Module: Building Your First x402 Endpoint**

---

*GenTech Academy — Ship Paid APIs in a Weekend*  
*Based on real-world experience building GenTech Labs' x402 gateway*
