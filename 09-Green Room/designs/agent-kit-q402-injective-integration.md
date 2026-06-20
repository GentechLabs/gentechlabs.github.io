# Agent Kit × Q402 × Injective — Integration Spec

**Date:** 2026-06-20
**Status:** 🟡 In Progress — MCP servers added, SDK integration pending

## Problem

Agent Kit needs a payment rail and trading capability. Today agents can't:
- Move money gaslessly across chains
- Trade on an order book (only AMM via LFJ)
- Earn passive income from trading fees
- Prove payments cryptographically

## Three Pillars

| Layer | Provider | Role | Status |
|-------|----------|------|--------|
| Payment Rail | Q402 | How agents move money | MCP added |
| Identity Standard | ERC-8004 (Injective) | Who agents are | MCP added |
| Policy + Orchestration | Agent Kit | What agents can do | Core exists |

## Architecture

```
┌─────────────────────────────────────────────┐
│                Agent Kit                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Identity  │  │ Policy   │  │ Audit    │  │
│  │ (AAE)    │  │ Hooks    │  │ Trail    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  │
│  │ ERC-8004 │  │ Q402     │  │ Trust    │  │
│  │ Registry │  │ Policy   │  │ Receipts │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
         │              │              │
    ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐
    │Injective │  │ Q402     │  │ Q402     │
    │Identity  │  │ Payment  │  │ Receipt  │
    │Registry  │  │ Rail     │  │ Service  │
    └──────────┘  └──────────┘  └──────────┘
```

## Q402 Integration

### What It Provides
- Gasless stablecoin payments across 11 EVM chains
- EIP-712 signing + EIP-7702 execution
- Trust Receipts (verifiable settlement proof)
- MCP server with 27 tools
- Recurring payments, batch payouts, yield routing

### Integration Points
1. **Payment Module** — `@q402/core` SDK for signing + settlement
2. **Receipt Verification** — Trust Receipts feed into audit trail
3. **Enforcement Hooks** — AAE policy runs before Q402 settlement
4. **MCP Server** — `@quackai/q402-mcp` added to Hermes config

### Supported Chains
BNB, Ethereum, Avalanche, Arbitrum, Base, Monad, Mantle, Scroll, Injective, X Layer, Stable

### Tokens
USDC, USDT, RLUSD

### Pricing
- Free: 2K TXs/30 days (BNB only)
- Starter: $29/500 TXs
- Pro: $149/10K TXs ← sweet spot
- Scale: $449/50K TXs

## Injective Integration

### What It Provides
- ERC-8004 on-chain identity (NFT per agent)
- 168 trading markets (crypto perps, spot, stocks, gold, FX)
- 40% fee routing on every trade
- Sub-cent gas (~$0.00008/tx)
- 25K tx/s throughput, instant finality
- MCP server with 30+ tools

### Integration Points
1. **Identity Module** — Register agent on ERC-8004 Identity Registry
2. **Trading Module** — Grid trader + DCA bot via Trader SDK
3. **Fee Recipient** — Agent wallet earns 40% of trading fees
4. **Identity Bridge** — AAE identity ↔ ERC-8004 identity tuple
5. **MCP Server** — Injective MCP added to Hermes config

### Available Markets
- **Crypto Perps:** BTC, ETH, SOL, ATOM, DOGE, LINK, MATIC, UNI (100x leverage)
- **Spot:** INJ, SOL, ATOM, FET, TIA, KAVA, wETH
- **Stocks:** PLTR (Palantir), tokenized pre-IPO
- **Commodities:** Gold (XAU), Silver (XAG)
- **Forex:** Currency pairs

### Wallet Requirements
- Standard EVM private key (hex)
- One key → two addresses (0x... EVM + inj1... Cosmos)
- Supported: MetaMask, Keplr, Ledger, Trezor
- Minimum: just enough INJ for gas (~$0.00008/tx)

## Implementation Phases

### Phase 1: MCP Servers (Done ✅)
- [x] Q402 MCP added to Hermes config
- [x] Injective MCP cloned, built, added to config
- [x] Smart routing updated with build queue auto-detection
- [x] Build queue cron job created (daily 10 AM ET)

### Phase 2: SDK Integration (Next)
- [ ] Install @q402/core + @q402/middleware-express
- [ ] Install @injective/agent-sdk
- [ ] Build Agent Kit payment module
- [ ] Build Agent Kit trading module
- [ ] Wire Trust Receipts to audit trail

### Phase 3: Identity Bridge (Week 2)
- [ ] Register Agent Kit on Injective Identity Registry
- [ ] Connect AAE identity ↔ ERC-8004 identity tuple
- [ ] Test cross-chain identity verification

### Phase 4: Passive Income (Week 3)
- [ ] Configure fee recipient on Injective
- [ ] Deploy grid trader strategy
- [ ] Set up DCA bot for watch list tokens
- [ ] Monitor fee earnings

## Success Criteria
- Agent can pay gaslessly via Q402 (any EVM chain)
- Agent has ERC-8004 identity on Injective
- Agent can trade on Injective order book
- Agent earns trading fees automatically
- All actions logged in audit trail
- Trust Receipts verify every settlement
