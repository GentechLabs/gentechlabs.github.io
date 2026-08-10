# Paymenter Marketplace Listing

## Title
x402 Crypto Gateway — Accept Gasless Crypto Payments

## Category
Gateway

## Short Description (max 200 chars)
Accept crypto payments via x402 — gasless, instant settlement. Multi-chain (Solana, Base, Ethereum, Polygon). Q402 Trust Receipts. Powered by GenTech Labs.

## Full Description

**The first crypto payment gateway for Paymenter.**

x402 lets your customers pay invoices with USDC, USDT, SOL, or ETH — gasless, instant, no blockchain fees. Every payment generates a Q402 Trust Receipt (rct_ ID) for verifiable settlement proof.

### Why x402?

- **Gasless** — customers pay $0 in network fees
- **Instant** — settlement in seconds, not minutes
- **Multi-chain** — Solana, Base, Ethereum, Polygon
- **Agent-ready** — AI agents can auto-pay invoices without a human
- **Trust Receipts** — every payment gets a cryptographically verified receipt

### Perfect for

- **Game server hosts** (Pterodactyl) — your tech-savvy customers already hold crypto
- **Web hosting** — offer an alternative to Stripe/PayPal
- **VPS providers** — recurring subscriptions paid in stablecoins

### How it works

1. Customer checks out and selects "Pay with Crypto (x402)"
2. A QR code + payment URL is generated
3. Customer pays with their wallet
4. x402 gateway confirms the transaction
5. Paymenter marks the invoice as paid

### Configuration

| Field | Description |
|-------|-------------|
| x402 Gateway URL | Your x402 endpoint (default: https://api.gentechlabs.net/x402) |
| Merchant Wallet | Your wallet address for settlement |
| Blockchain Network | Solana, Base, Ethereum, or Polygon |
| Accepted Token | USDC, USDT, SOL, or ETH |

### Self-hosted option

Run your own x402 gateway: `git clone https://github.com/ProtoJay4789/x402-gateway`

### Support

- GitHub: https://github.com/ProtoJay4789/paymenter-x402
- Docs: https://gentechlabs.net/docs/x402
- Discord: https://discord.gg/gentechlabs

---

*MIT License — open-source contribution from GenTech Labs*
*Repo verified live: Aug 10, 2026 — 7 files, public, branch: main*
