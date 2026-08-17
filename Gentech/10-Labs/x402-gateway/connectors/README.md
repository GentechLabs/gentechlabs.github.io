# x402 Marketplace Connector Guides

> **The connective tissue between your x402 API and every marketplace.**
> Every x402 marketplace/protocol catalogs DIFFERENTLY. This is a living,
> protocol-by-protocol reference tracking the actual (changing) cataloging rules —
> captured from real listing work we've done with our own gateway.
>
> Maintained by Gentech. Last updated: 2026-08-13.

## Why this exists

Every x402 marketplace catalogs differently, and nobody's written the connective
tissue. We hit this friction live (CDP settles→indexes, Dexter settles→catalogs,
Syra uses on-chain identity/8004). Other builders will hit the same wall. This doc
set is the answer — a maintained reference, not a generic tutorial.

## The guides

| Marketplace | Doc | Status |
|---|---|---|
| OpenDexter / Dexter | `opendexter.md` | ✅ Verified live (Aug 3) |
| Syra | `syra.md` | 🔜 After queue #22 ships |
| awesome-mcp-servers | `awesome-mcp-servers.md` | ✅ PR #11773 submitted Aug 9 |
| Paymenter marketplace | `paymenter.md` | 🔜 After queue #11 ships |
| CDP Bazaar | `cdp-bazaar.md` | ✅ Settle→index flow documented |

## The pattern (TL;DR)

Every marketplace follows the same 4-step shape, with different field names:

1. **Register** — create an identity (API key, on-chain wallet, or both).
2. **List** — declare your capability + price (payload shape varies most here).
3. **Settle** — the payment rail (x402 challenge → facilitator → settlement).
4. **Index** — the marketplace catalogs you so agents can discover you.

The gotcha is almost always in step 2 (payload shape) or step 3 (which facilitator
settles and whether the marketplace auto-indexes on settle).

## Revenue model

- **Free:** this guide set (the connective tissue).
- **Premium "Connector Pack":** the exact payloads + gotchas for every marketplace.
- **Enterprise "get me listed everywhere":** we do the listing work for you.

## Synergy

Extends the "GenTech Academy — Ship Paid APIs in a Weekend" course. This is the
distribution/listing chapter.
