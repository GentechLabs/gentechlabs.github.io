# pay.sh Integration — Deployment Log

**Date:** 2026-05-22
**Status:** MCP registered, sandbox verified, ready for live testing

## What's Done

- **pay CLI v0.16.0** installed and verified on server (Node.js v22.11.0)
- **MCP server** registered in Gentech config.yaml under `mcp_servers.pay`
- **Sandbox mode** tested end-to-end:
  - `pay --sandbox curl https://debugger.pay.sh/mpp/quote/AAPL` → `{"symbol":"AAPL","price":"462.63"}`
  - `pay --sandbox curl https://debugger.pay.sh/mpp/quote/TSLA` → `{"symbol":"TSLA","price":"232.56"}`
  - `pay skills search "data"` → returns Alchemy, Apollo, Clado, Cloudflare, Exa providers
  - `pay skills search "market"` → returns StableCrypto, RentCast providers
- **Skill updated** — `pay-sh-integration` reflects actual deployment state

## What Works

| Feature | Status |
|---------|--------|
| CLI install | ✅ v0.16.0 |
| MCP server | ✅ Registered, starts clean |
| Sandbox payments | ✅ Auto-signs, returns data |
| Catalog search | ✅ Multiple providers discoverable |
| Dual protocol (x402 + MPP) | ✅ Server returns both in 402 headers |
| Dynamic pricing | ✅ price(ctx) per-request |
| Lifecycle hooks | ✅ onPaymentVerified, onPaymentSettled, onPaymentFail |

## 8 Testnet Chains Available

Base Sepolia, Avalanche Fuji, Polygon Amoy, Sei, X Layer, Rialo, SKALE, Solana devnet

## Next Steps

1. **Gateway restart** — `/reload-mcp` to pick up the new MCP server
2. **Live wallet setup** — `pay setup` for mainnet testing with real funds
3. **Agent integration test** — Have Hermes agent make a paid API call via MCP tools
4. **Catalog exploration** — `pay skills search` to find useful paid APIs for our stack

## Key Commands

```bash
# Sandbox testing (no real funds)
pay --sandbox curl <url>

# Catalog browsing
pay skills search "<query>"
pay skills endpoints <provider>

# Live payment (requires wallet)
pay curl <provider-endpoint>

# MCP server (auto-started by Hermes)
pay mcp
```

## Pits

- `pay balance` doesn't exist in v0.16.0 — use `pay account list` instead
- MCP server needs proper handshake (stdio) — can't test with raw `timeout pay mcp`
- Sandbox mode is great for development — no wallet setup needed
- Some catalog endpoints show "no published endpoints available" warnings — those services aren't live yet
