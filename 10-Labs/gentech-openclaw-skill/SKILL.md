---
name: gentech-x402-gateway
description: >
  Enable x402 pay-per-call payments from OpenClaw — wrap any tool with
  GenTech's x402 gateway and earn USDC per request, with a self-improvement
  loop that tracks usage and suggests optimizations.
version: 0.1.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
      env:
        - X402_GATEWAY_URL
    primaryEnv: X402_GATEWAY_URL
    envVars:
      - name: X402_GATEWAY_URL
        required: true
        description: >
          GenTech x402 gateway URL.
          Default: https://gentech-x402-gateway.jordanjones0902.workers.dev
      - name: X402_API_KEY
        required: false
        description: >
          Optional API key for authenticated gateway access.
      - name: GENTECH_RECEIPTS_DIR
        required: false
        description: >
          Directory to store usage receipts for the self-improvement loop.
          Default: ~/.gentech/receipts/
    emoji: "💳"
    homepage: https://gentechlabs.net/pricing
    install:
      - kind: node
        package: "@x402/hono"
        bins: []
    always: false
    user-invocable: true
---

# GenTech x402 Gateway — Pay-per-call for OpenClaw agents

Every tool call can earn USDC. This skill wraps OpenClaw tools with x402
payment middleware and includes a **self-improvement loop** that tracks usage
patterns, identifies bottlenecks, and suggests skill improvements.

## Quick start

```bash
# 1. Set your gateway URL
export X402_GATEWAY_URL=https://gentech-x402-gateway.jordanjones0902.workers.dev

# 2. Verify connectivity
openclaw skills verify @gentechlabs/gentech-x402-gateway

# 3. Make your first paid call
curl -X POST $X402_GATEWAY_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "hello"}'
```

## How it works

When you ask this skill to make a paid call, the agent:

1. **Checks credentials** — verifies `X402_GATEWAY_URL` is set
2. **Constructs the request** — builds the x402-compatible HTTP call
3. **Handles the 402 response** — if the gateway returns 402 (payment required),
   it prompts you to send USDC to the payment address
4. **Verifies the receipt** — checks the payment was confirmed on-chain
5. **Logs the transaction** — saves a receipt for the self-improvement loop
6. **Returns the result** — passes the API response back to you

## Available endpoints

| Endpoint | Description | Price |
|----------|-------------|-------|
| `/api/analyze` | Analyze data | $0.70 |
| `/api/scan` | Security scan | $0.70 |
| `/api/credit-score` | Agent credit score | $0.50 |
| `/api/compliance-check` | CLARITY Act compliance | $0.70 |
| `/api/treasury/balance` | Treasury balance | $0.50 |
| `/api/predict` | Prediction | $1.00 |
| `/api/trade/signal` | Trading signal | $1.04 |

## Making paid calls

### Protected endpoint

```bash
# A paid call — the gateway returns 402 unless payment is attached
curl -X POST $X402_GATEWAY_URL/api/scan \
  -H "Content-Type: application/json" \
  -H "x402-authorization: USDC base <your-signed-receipt>" \
  -d '{"target": "0x..."}'
```

### Check endpoint metadata

```bash
# Returns x402 pricing info as HTTP headers
curl -I $X402_GATEWAY_URL/api/scan
```

### Supported chains

- **Base** (recommended — lowest fees, fastest settlement)
- **Polygon**
- **Arbitrum**

All payments settle in **USDC**.

## Self-improvement loop

This skill learns from its own usage. Each call logs a receipt. Over time,
the agent analyses the log to improve the skill itself.

### What gets tracked

Each receipt captures:
- `timestamp` — when the call happened
- `endpoint` — which endpoint was called
- `amount_usdc` — how much was paid
- `chain` — which chain was used
- `latency_ms` — how long the call took
- `status` — success or failure
- `error` — any error message

### Improvement signals

The agent watches for:

| Signal | Action |
|--------|--------|
| **High latency** on an endpoint | Suggest caching or batch processing |
| **Frequent 402 responses** | User may need to fund their wallet |
| **Low usage** of a paid endpoint | Consider reducing its price |
| **Single-chain bias** | Suggest multi-chain routing |
| **Recurring error patterns** | Flag for debugging |

### Triggering a review

```bash
# Tell the agent to review its receipts
"review my x402 usage this week"

# The agent will:
# 1. Read receipts from GENTECH_RECEIPTS_DIR
# 2. Compute metrics (avg latency, error rate, popular endpoints)
# 3. Write improvement suggestions to SKILL.md
```

### Sample improvement note

The agent might update this skill's instructions based on usage:

```markdown
<!--
  Self-improvement note (2026-07-24):
  - /api/scan has 40% error rate — suggest timeout increase
  - 80% of calls use Base chain — make Base the first recommendation
  - /api/credit-score has < 5 calls/week — consider price reduction
-->
```

## Receipt storage

Receipts are stored as JSON files in `~/.gentech/receipts/` (or
`$GENTECH_RECEIPTS_DIR`). Each receipt is named
`<endpoint>-<timestamp>.json`.

```json
{
  "id": "receipt_001",
  "endpoint": "/api/scan",
  "amount_usdc": 0.70,
  "chain": "base",
  "caller": "0x...",
  "timestamp": "2026-07-24T12:00:00Z",
  "latency_ms": 340,
  "status": "success",
  "tx_hash": "0x..."
}
```

## Verbose mode

When configuration or tool output has `verbose` mode, each receipt includes a
diagnostic block:

```text
[gentech-x402] POST /api/scan — 200 OK (340ms, $0.70)
[gentech-x402] Receipt: 0xabc...123 (Base, 2 confirmations)
[gentech-x402] Balance: $123.45 remaining
```

## Pricing

- **Pay-per-call:** $0.50 to $1.04 depending on endpoint compute
- **Revenue share:** 70% to the agent operator, 30% to gateway operator
- **Settlement:** USDC on Base (instant), Polygon/Arbitrum (within blocks)

Get a gateway URL at: https://gentechlabs.net/pricing

## CLARITY Act compliance

Every call through this skill is CLARITY Act compliant by default:

- ✅ **Agent identity** — caller is identified
- ✅ **Payment integrity** — x402 protocol ensures fair settlement
- ✅ **DeFi Exclusion** — Sec. 309/409 exempt from SEC/CFTC registration
- ✅ **Audit trail** — every receipt is verifiable on-chain

## Related

- `@genechlabs/gentech-q402` — Subscription billing on top of x402
- `@genechlabs/gentech-compliance` — CLARITY Act security scanning
- [GenTech Labs](https://gentechlabs.net) — Gateway dashboard and pricing
- [x402 Protocol](https://x402.org) — HTTP 402 Payment Required standard
