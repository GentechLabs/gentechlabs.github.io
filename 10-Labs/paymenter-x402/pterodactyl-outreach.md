# Pterodactyl Community Post — x402 Crypto Gateway for Game Server Hosts

---

**🎮 Crypto payments for your game servers — now in Paymenter**

Hey Pterodactyl community! 

We built something that makes crypto payments dead simple for game server hosts: **x402 Crypto Gateway for Paymenter.**

If you're using Pterodactyl + Paymenter to sell game servers, your customers probably already hold crypto. Now they can pay with it — directly at checkout, no Stripe/PayPal middleman.

**Why this matters for game server hosts:**

- **Your customers have crypto** — gamers hold USDC, SOL, ETH. Let them spend it.
- **Gasless** — customers pay $0 in network fees. No "it costs $5 to send $10" problem.
- **Instant settlement** — seconds, not days like traditional gateways.
- **Multi-chain** — Solana, Base, Ethereum, Polygon. Whatever your customers use.
- **Agent-ready** — AI agents can auto-pay monthly server invoices. Yes, really.

**Simple setup:**
```
cd /var/www/paymenter
git clone https://github.com/ProtoJay4789/paymenter-x402 extensions/Gateways/X402
```
Enable in admin panel → configure wallet → start accepting crypto.

**MIT license, open-source, self-hostable.** No per-transaction fees beyond network gas (which is gasless for your customers).

Repo: https://github.com/ProtoJay4789/paymenter-x402
Docs: https://gentechlabs.net

First crypto gateway in the Paymenter ecosystem. Would love to hear what game server hosts think — what chains would you want supported?

#pterodactyl #paymenter #gameservers #crypto #x402 #selfhosted
