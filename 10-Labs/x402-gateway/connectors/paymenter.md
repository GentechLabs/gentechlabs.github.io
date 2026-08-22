# Connector: Paymenter Marketplace — Game Server Hosting

> **Source:** https://paymenter.org/marketplace
> **Status:** ✅ Fleshed out 2026-08-20 — listing fields captured. Submission itself Jordan-gated (needs live Paymenter account + Discord bot token).

## What it catalogs

**Paymenter** is the billing platform for game server hosts (Pterodactyl ecosystem).
The **Paymenter marketplace** lists extensions/plugins. Our `paymenter-x402`
extension is the **first crypto gateway for game server hosts** — their customers
already hold crypto.

## The listing model

- **Extension listing** on paymenter.org/marketplace.
- **Repo:** github.com/ProtoJay4789/paymenter-x402 (live, main @ bb1857d, verified 2026-08-20).
- **Discord community** (1.9k members) for outreach.

## Exact listing fields (drafted, ready to paste)

**Title:** x402 Crypto Gateway — Accept Gasless Crypto Payments
**Category:** Gateway
**Short description (≤200 chars):** Accept crypto payments via x402 — gasless, instant settlement. Multi-chain (Solana, Base, Ethereum, Polygon). Q402 Trust Receipts. Powered by GenTech Labs.

**Config fields:**
| Field | Description |
|-------|-------------|
| x402 Gateway URL | Your x402 endpoint (default: https://api.gentechlabs.net/x402) |
| Merchant Wallet | Your wallet address for settlement |
| Blockchain Network | Solana, Base, Ethereum, or Polygon |
| Accepted Token | USDC, USDT, SOL, or ETH |

**Support links:** GitHub github.com/ProtoJay4789/paymenter-x402 · Docs gentechlabs.net/docs/x402 · Discord discord.gg/gentechlabs

## The flow

1. **Submit** the paymenter-x402 extension to the marketplace.
2. **Post** in the Paymenter Discord community.
3. **Pterodactyl outreach** (queue #5, shipped) — the biggest Paymenter use case.

## Gotchas we hit

1. **Game server hosts are the biggest Paymenter use case** — their customers
   already hold crypto, so x402 is a natural fit.
2. **Marketplace listing + Discord post** are both drafted in the vault — ready to
   submit once greenlit.
3. **2026-08-20:** the canonical `Paymenter/Extensions` GitHub repo is **archived
   (read-only)** — no PR path to add the extension there. The marketplace submission
   must go through the live paymenter.org/marketplace UI, which requires a Paymenter
   account (Jordan-gated). Discord post needs a bot token (Jordan-gated).

## Our status

- Queue #4 (submit to marketplace + Discord) — **pending, Jordan-gated** (needs live
  Paymenter account + Discord bot token). Repo live, listing + post drafted.
- **Next:** Jordan submits via paymenter.org/marketplace UI + posts in Discord.
