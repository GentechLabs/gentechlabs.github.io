# Robinhood Chain x402 Plugin — Scope

> **Status:** Research complete, pending build
> **Date:** 2026-07-10
> **Trigger:** Atelier x402 live on Robinhood Chain via Naven Network
> **Tags:** #notebooklm

---

## What We Know

**Robinhood Chain**
- Chain ID: 4663 (mainnet), 46630 (testnet)
- EVM-compatible (OP Stack) — Solidity/Hardhat/Foundry work as-is
- RPC: `https://rpc.mainnet.chain.robinhood.com`
- Explorer: `https://robinhoodchain.blockscout.com`
- Native gas: ETH
- USDG (Paxos) — canonical contract: `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`

**Naven Network (Facilitator)**
- Endpoint: `https://facilitator.naven.network`
- Standard x402 endpoints: `/verify` and `/settle`
- Supported tokens: USDG (Robinhood), USDC (X Layer), USDC (KiteAI Testnet)
- Robinhood demo: `https://api.naven.network/x402-test/ping` ($0.0001 USDG)
- First live tx: https://robinhoodchain.blockscout.com/tx/0xf7180c33598a6f5887262a59c5f1fad1877d3e6317c1dd44259463e54a8be8a6

**Atelier Integration**
- Already registered (Agent ID + API key in .env)
- Atelier agents now hireable from Robinhood Chain
- x402 payments settle in USDG via Naven

---

## Plugin Architecture

New plugin in Agent Kit: `plugins/robinhood_x402/`

### Tools

| Tool | Description | Pricing |
|------|-------------|---------|
| `rh_info()` | Robinhood Chain + Naven facilitator status | Free |
| `rh_verify_payment(proof)` | Verify x402 payment via Naven | x402 fee |
| `rh_get_quote(symbol)` | Crypto price quote via x402 | $0.001 USDG |
| `rh_get_stock(symbol)` | Tokenized stock price (AAPL, NVDA, TSLA, etc.) | $0.005 USDG |
| `rh_list_stocks()` | Available tokenized stocks on Robinhood Chain | Free |

### Payment Flow

1. Seller declares price: `$0.001 USDG`, network `eip155:4663`, asset `0x5fc...`
2. Buyer hits endpoint → gets `402 Payment Required` with challenge
3. Buyer signs payment payload → submits to `facilitator.naven.network/verify`
4. Facilitator settles on-chain → returns receipt
5. Seller verifies receipt → serves the resource

### Files

```
plugins/robinhood_x402/
├── __init__.py     # Plugin registration, all tools
├── plugin.json     # Manifest
├── schemas.py      # Pydantic models for RH Chain data
└── README.md       # Usage docs
```

### Dependencies (already in Agent Kit)
- `httpx` — for Naven facilitator API calls
- `pydantic` — for output schemas (Output Enforcer compatible)
- `mcp` — for tool registration

---

## Build Effort

| Task | Time |
|------|------|
| Scaffold plugin + manifest | 20 min |
| Naven integration (verify/settle) | 1 hour |
| USDG pricing + Robinhood Chain config | 30 min |
| Crypto quote via CMC (reuse existing) | 10 min |
| Stock price tool (RH Chain tokens) | 1 hour |
| Test with smoke endpoint | 30 min |
| **Total** | **~3.5 hours** |

---

## Why This Matters

1. **Distribution** — Robinhood has millions of users. Our agents on Robinhood Chain via Atelier = exposure we don't have elsewhere
2. **USDG** — Paxos-issued regulated stablecoin. Enterprise-friendly
3. **Naven** — They're doing "guarded brokerage actions" — policy guardrails, spend limits, audit trails. That's the HITL layer we want to build. We can learn from their implementation
4. **Tokenized stocks** — Robinhood Chain has AAPL, NVDA, TSLA, MSFT, META, etc. as native tokens. Price data for these is valuable for agent trading strategies
5. **GenTech Academy** — Robinhood Chain x402 = a module on "Multi-Chain x402"

---

## Next Steps

- [ ] Decide: build the Robinhood Chain x402 plugin
- [ ] Update Atelier listing to include Robinhood Chain support
- [ ] Test Naven verification with the demo endpoint
- [ ] Add Output Enforcer schemas for RH tools
