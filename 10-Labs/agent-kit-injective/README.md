# Agent Kit × Injective — Trading + Identity Module

**Status:** Phase 2 — MCP Tools Mapped
**Date:** June 20, 2026

## What This Is

A trading and identity module for Agent Kit that wraps Injective's MCP tools with:
- ERC-8004 identity registration (on-chain agent identity)
- Order book trading (perpetual futures, spot)
- Fee earning (40% of trading fees routed to agent wallet)
- Portfolio management (positions, balances, P&L)

## Architecture

```
Agent Kit Identity Layer
        │
        ▼
┌───────────────────┐
│  ERC-8004 Registry │ ← on-chain NFT identity per agent
│  (Injective)       │
└────────┬──────────┘
         │ registered
         ▼
┌───────────────────┐
│  Trading Engine    │ ← order book execution
│  (Injective MCP)   │
└────────┬──────────┘
         │ executed
         ▼
┌───────────────────┐
│  Fee Recipient     │ ← 40% of fees earned
│  (passive income)  │
└───────────────────┘
```

## Available Markets

| Type | Assets | Leverage |
|------|--------|----------|
| **Crypto Perps** | BTC, ETH, SOL, ATOM, DOGE, LINK, MATIC, UNI | Up to 100x |
| **Spot** | INJ, SOL, ATOM, FET, TIA, KAVA, wETH | 1x |
| **Stocks** | PLTR (Palantir), tokenized pre-IPO | 1x |
| **Commodities** | Gold (XAU), Silver (XAG) | 1x |
| **Forex** | Currency pairs | 1x |

## MCP Tools (30+)

### Identity
- `wallet_generate` — Create new Injective wallet
- `wallet_import` — Import from private key
- `address_normalize` — Convert between inj1... and 0x...

### Trading
- `trade_open` — Open position (market order, Cosmos signing)
- `trade_close` — Close position
- `trade_open_eip712` — Open position (EIP-712, MetaMask-compatible)
- `trade_close_eip712` — Close position (EIP-712)
- `trade_limit_open` — Open limit order
- `trade_limit_orders` — List open limit orders
- `trade_limit_close` — Cancel limit order

### Markets
- `market_list` — List all active perp markets
- `market_price` — Get oracle price for a symbol

### Accounts
- `account_balances` — Bank + subaccount balances
- `account_positions` — Open positions with unrealized P&L

### Transfers
- `transfer_send` — Send tokens to another address
- `subaccount_deposit` — Deposit to trading subaccount
- `subaccount_withdraw` — Withdraw from subaccount

### Bridging
- `bridge_withdraw_to_eth` — Bridge to Ethereum via Peggy
- `bridge_debridge_quote` — Get deBridge DLN quote
- `bridge_debridge_send` — Bridge via deBridge

### EVM
- Raw EVM transaction support

## Integration Points

1. **Identity Module** — Register Agent Kit on Injective Identity Registry (ERC-8004)
2. **Trading Module** — Grid trader + DCA bot via Trader SDK
3. **Fee Recipient** — Agent wallet earns 40% of trading fees
4. **Identity Bridge** — AAE identity ↔ ERC-8004 identity tuple
5. **MCP Server** — Injective MCP added to Hermes config

## Files

- `trading_module.py` — Core trading logic with risk management
- `identity_module.py` — ERC-8004 identity registration
- `config.yaml` — Trading configuration
- `test_trading.py` — Unit tests
