# Virtuals ACP — GenTech Offerings Setup

## Prerequisites
- Node.js >= 18 installed
- Builder code: `acp-61d240f77b21c86fe8c9`

## Steps to Publish

### 1. Install CLI
```bash
npm install -g @virtuals-protocol/acp-cli
```

### 2. Sign in (browser OAuth)
```bash
acp configure
```
This opens a browser — sign in with your Virtuals account.

### 3. Register Offerings

Run each of these to publish our services:

**Token Risk Assessment ($0.01)**
```bash
acp offering create \
  --name "Token Risk Assessment" \
  --price-type fixed --price-value 0.01 \
  --sla-minutes 5 \
  --requirements '{"type":"object","properties":{"address":{"type":"string"},"chain":{"type":"string","enum":["base","solana","avalanche","bnb","okx"]}}}' \
  --deliverable "Risk score, severity level, findings with categories" \
  --json
```

**Market Intel — Price Comparison ($0.005)**
```bash
acp offering create \
  --name "Market Intel — Price Comparison" \
  --price-type fixed --price-value 0.005 \
  --sla-minutes 3 \
  --requirements '{"type":"object","properties":{"query":{"type":"string"}}}' \
  --deliverable "Price results across stores with cheapest option" \
  --json
```

**Wallet Analyzer — AI Smart Money Tracking ($0.025)**
```bash
acp offering create \
  --name "Wallet Analyzer" \
  --price-type fixed --price-value 0.025 \
  --sla-minutes 10 \
  --requirements '{"type":"object","properties":{"address":{"type":"string"}}}' \
  --deliverable "Wallet analysis, P&L, portfolio, smart money patterns" \
  --json
```

**Game Intel ($0.005)**
```bash
acp offering create \
  --name "Game Intel — Multi-Store Search" \
  --price-type fixed --price-value 0.005 \
  --sla-minutes 3 \
  --requirements '{"type":"object","properties":{"query":{"type":"string"}}}' \
  --deliverable "Game prices, cheapest deals, release info" \
  --json
```

**NFT Search ($0.005)**
```bash
acp offering create \
  --name "NFT Search — Multi-Chain Collections" \
  --price-type fixed --price-value 0.005 \
  --sla-minutes 3 \
  --requirements '{"type":"object","properties":{"query":{"type":"string"}}}' \
  --deliverable "Collection metadata, floor prices, volume data" \
  --json
```

### 4. Verify Offerings
```bash
acp offering list --json
```

### 5. Start Event Listener (to receive job requests)
```bash
acp events listen --output events.jsonl --json
```

---

## Notes
- All endpoints are at https://gentech-x402-gateway.jordanjones0902.workers.dev
- Builder code is auto-applied to all transactions
- USDC escrow on Base mainnet (chain: 8453)
