# Pay.sh + x402 Multi-Chain Implementation

**Date:** 2026-06-01
**Status:** Research Complete
**Source:** Jordan's discovery + research

---

## What is Pay.sh?

**Solana Foundation + Google Cloud** — Payment gateway for AI agents to discover, access, and pay for APIs using stablecoins on Solana. Built on x402 protocol.

**Key features:**
- 50+ API providers (Google Cloud: Gemini, BigQuery, BigTable, Cloud Run, Vertex AI)
- x402 protocol — agents pay per request, no accounts/subscriptions needed
- Stablecoins on Solana — USDC/USDT, no volatile gas
- Machine-native — designed for agent-to-API commerce

---

## x402 Protocol — Multi-Chain Support

**x402 is chain-agnostic.** The protocol works across multiple blockchains:

### Supported Chains (as of June 2026)

| Chain | Type | USDC | Gas | Settlement | Notes |
|-------|------|------|-----|------------|-------|
| **Base** | Ethereum L2 | ✅ Native | ~$0.001 | Instant | x402 "home chain" (Coinbase) |
| **Ethereum** | L1 | ✅ | Variable | ~15s | Higher gas, more secure |
| **Polygon** | Sidechain | ✅ | ~$0.001 | 2s | Low cost, high throughput |
| **Arbitrum** | Ethereum L2 | ✅ | ~$0.01 | Instant | Fast, low cost |
| **Optimism** | Ethereum L2 | ✅ | ~$0.01 | Instant | Fast, low cost |
| **Solana** | SVM | ✅ | ~$0.001 | 400ms | Pay.sh native chain |

### How x402 Works (Multi-Chain)

```
1. Agent sends HTTP request to API
2. API responds with 402 "Payment Required" + payment requirements
3. Agent constructs payment (USDC transfer on chosen chain)
4. Facilitator validates payment on-chain
5. API receives confirmation, serves the request
6. Settlement happens on the chosen chain
```

### Facilitator Network

**Facilitators** validate and settle x402 payments:

| Facilitator | Chains | Notes |
|-------------|--------|-------|
| **Coinbase CDP** | Base, Ethereum, Polygon, Arbitrum, Optimism | Official, most reliable |
| **Dexter** | Polygon, Arbitrum, Optimism, Avalanche | Community, EVM-focused |
| **x402-open** | EVM + SVM | Open-source, self-hostable |

---

## Implementation for Our Stack

### Current State (Solana-only via Pay.sh)

```yaml
Agent → Pay.sh (Solana) → x402 → Google Cloud APIs
```

### Multi-Chain Implementation

```yaml
Agent → Chain Router → x402 Facilitator → API Provider
         ↓
    Base (cheapest)
    Polygon (fastest)
    Arbitrum (balanced)
    Solana (Pay.sh native)
    Avalanche (AAE home chain)
```

### Recommended Chain Strategy

| Use Case | Best Chain | Why |
|----------|------------|-----|
| **Agent-to-API payments** | Base | Cheapest, Coinbase native, most x402 support |
| **Agent-to-agent payments** | Avalanche | AAE home chain, ERC-8004 native |
| **Human-to-agent payments** | Polygon | Low cost, fast, user-friendly |
| **High-value settlements** | Ethereum | Most secure, institutional trust |
| **Pay.sh integration** | Solana | Native support, 50+ APIs |

### Multi-Chain Router Architecture

```typescript
interface ChainRouter {
  route(payment: PaymentRequest): ChainConfig;
}

class SmartRouter implements ChainRouter {
  route(payment: PaymentRequest): ChainConfig {
    // Route based on: amount, speed, cost, availability
    if (payment.amount < 0.01) {
      return { chain: 'base', reason: 'cheapest gas' };
    }
    if (payment.speed === 'fast') {
      return { chain: 'solana', reason: '400ms finality' };
    }
    if (payment.chain === 'avalanche') {
      return { chain: 'avalanche', reason: 'AAE native' };
    }
    return { chain: 'base', reason: 'default' };
  }
}
```

---

## Integration Points for AAE

### 1. Agent Payments Layer

```typescript
// Agent pays for API access via x402
const payment = await agent.pay({
  api: 'google-gemini',
  chain: 'base',  // or 'solana', 'polygon', etc.
  amount: 0.001,
  currency: 'USDC'
});

// Agent receives API access
const result = await agent.callAPI('gemini', { query: '...' });
```

### 2. Lobby UI Order Book

```typescript
// Human places ask on any chain
const ask = await lobby.placeAsk({
  task: 'token research',
  price: 0.05,
  chain: 'base',  // human's preferred chain
  autoMatch: true
});

// Agent fills ask, payment settled on human's chain
await agent.fillAsk(ask.id);
```

### 3. Agent-to-Agent Commerce

```typescript
// Agent pays another agent for services
await agent.payAgent({
  recipient: '0x...',  // ERC-8004 address
  amount: 0.025,
  chain: 'avalanche',  // AAE native
  task: 'security audit'
});
```

---

## Pay.sh API Integration

### Current Pay.sh Endpoints (Solana)

```bash
# Discover APIs
GET https://pay.sh/api/v1/catalog

# Get API pricing
GET https://pay.sh/api/v1/catalog/{api_id}

# Make payment + access API
POST https://pay.sh/api/v1/pay
{
  "api": "google-gemini",
  "chain": "solana",
  "amount": 0.001,
  "currency": "USDC"
}
```

### Multi-Chain Extension

```bash
# Same API, different chain
POST https://pay.sh/api/v1/pay
{
  "api": "google-gemini",
  "chain": "base",  # or 'polygon', 'arbitrum', etc.
  "amount": 0.001,
  "currency": "USDC"
}
```

---

## Implementation Plan

### Phase 1: Solana (Current)
- [x] Pay.sh integration
- [x] x402 on Solana
- [ ] Google Cloud API access

### Phase 2: Base (Easiest EVM)
- [ ] Add Base chain support
- [ ] Use Coinbase CDP facilitator
- [ ] Test agent-to-API payments

### Phase 3: Multi-Chain Router
- [ ] Build chain router
- [ ] Add Polygon, Arbitrum, Optimism
- [ ] Smart routing (cost/speed/availability)

### Phase 4: AAE Integration
- [ ] Lobby UI order book (multi-chain)
- [ ] Agent-to-agent payments (any chain)
- [ ] Human-to-agent payments (user's choice)

---

## Revenue Model

| Layer | Revenue | Notes |
|-------|---------|-------|
| **Facilitator fee** | 0.1% per transaction | If we run our own facilitator |
| **Routing fee** | $0.001 per route | Smart chain selection |
| **Pay.sh integration** | Free (they take cut) | Use their infrastructure |
| **Premium routing** | Agent Pass ($15/mo) | Priority chain selection |

---

## Competitive Advantage

| Feature | Pay.sh | Stripe | Traditional |
|---------|--------|--------|-------------|
| **Multi-chain** | ✅ 6+ chains | ❌ Fiat only | ❌ Fiat only |
| **Agent-native** | ✅ Machine-to-machine | ❌ Human UX | ❌ Human UX |
| **No accounts** | ✅ Wallet-based | ❌ KYC required | ❌ KYC required |
| **Gas optimization** | ✅ Chain routing | N/A | N/A |
| **x402 standard** | ✅ Open protocol | ❌ Proprietary | ❌ Proprietary |

---

## Related

→ See [[Green-Room/lobby-ui-order-book.md]] (Order book design)
→ See [[Green-Room/lobby-ui-product-vision.md]] (Base Lobby UI)
→ See [[Projects/AAE/]] (Agent economy infrastructure)
