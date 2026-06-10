# AAE LP Dashboard Boilerplate

**Source:** LFJ/Trader Joe yield farm tracker (AVAX/USDC, Mar 31, 2026)  
**Purpose:** Core visual interface for AgentFi Agent (AAE) — learning + farming layers

---

## What's Included

| File | Status | Description |
|------|--------|-------------|
| `index.html` | ✅ Created | Mobile-responsive dashboard template |
| `config.example.json` | ✅ Created | Chain/pool/strategy config (multi-chain ready) |
| `data-layer.md` | ✅ Created | API integration spec (Chainlink, DexScreener, LFJ) |

---

## Key Features (Retained from Original)

- Dark theme (low battery, night use)
- Mobile-first responsive grid
- Fee tracking + rewards APR + DCA progress
- Color-coded stat boxes (green/blue/gold/purple/teal)
- Strategy badges (CURVE, RANGE, etc.)
- Pool info cards with address copy

---

## What Changed

### 1. Config-Driven Design
- `config.example.json` separates UI from data
- Add new chains/pools without touching HTML
- Example config includes Ethereum (Uniswap), Base (Aerodrome), Solana (Raydium)

### 2. Multi-Chain Ready
- Chain adapter pattern (like Trade Off platform)
- `CHAIN_ID` config field → auto-select oracle, router, token addresses

### 3. Action Triggers
- `actions` section in JSON → auto-generate claim/compound/swap buttons
- Agent signal overlay: `"trigger": "Claimed > $1.00 available"`

---

## Recommended Next Steps

| Priority | Task | Owner |
|----------|------|-------|
| 🟢 High | Connect to real data (Chainlink, DexScreener) | DMOB |
| 🟡 Medium | Add DeFi milestone progress bars | AAE Team |
| 🟡 Medium | Add "Ghost Position" toggle (simulated vs live) | AAE Team |
| 🟢 High | Agent action triggers (auto-claim/rebalance flags) | DMOB |

---

## Tags  
`#aae #dashboard #lp-tracking #defi #yield-farming #frontend #template #boilerplate`
