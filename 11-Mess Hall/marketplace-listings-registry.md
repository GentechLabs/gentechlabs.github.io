# GenTech Marketplace / Listing Registry

**Purpose:** Every marketplace, directory, website, or protocol where GenTech Labs is listed. One place to check when anything changes (new service, price change, rebrand, new chain, new endpoint) so we can update everywhere — no forgotten listings.

**The rule (Jordan, Aug 2 2026):** When we change ANYTHING about our services/brand/listing, update EVERY row here that's affected. The agent should prompt Jordan: "we changed X — want to go back and update Y?" if a row needs human action.

**How to use:**
- New listing → append a row with today's date
- Change to our services → scan this file, update each affected row
- Before a big change → this is the checklist

---

## 🟢 LIVE LISTINGS (verified)

| # | Platform | URL / Location | What's tracked | Status | Last verified |
|---|----------|---------------|----------------|--------|---------------|
| 1 | x402-list.com | https://x402-list.com/services/gentech-labs-x402-gateway | 6 endpoints, uptime, compliance, signability, price, traction | 🟢 ONLINE (was "route not signable" → fixed EIP-712 + standard header 2026-08-02) | 2026-08-02 |
| 2 | 8004scan.io (ERC-8004 registry) | https://8004scan.io/agents?chain=43114 · agent #1770 | GenTech Labs identity, 16 x402 endpoints, feedback | 🟢 LIVE (Avalanche, owner 0x7ebff188f2Eba16518C02864589b1403a5d1296a) | 2026-08-02 |
| 3 | api.gentechlabs.net (gateway) | https://api.gentechlabs.net | 6 paid x402 services, /.well-known/x402, bazaar manifest v8.0.0 | 🟢 ALL 6 SERVICES PAYING E2E | 2026-08-02 |
| 4 | gentechlabs.net | https://gentechlabs.net | Landing page, links to gateway + kit | 🟢 | 2026-08-02 |
| 4b | Games API (deal-tracker) | api.gentechlabs.net/v1/games/* (port 8080) | deal search, price-watch, release-radar, preorder-advisor | 🟢 LIVE + real data (was stub `[]`, fixed Aug 3) | 2026-08-03 |
| 4c | Crypto Price API | api.gentechlabs.net/v1/price (port 8082) | real-time crypto prices | 🟢 LIVE (was placeholder, fixed Aug 3) | 2026-08-03 |
| 4d | Gas Price API | api.gentechlabs.net/v1/gas (port 8084) | live gas prices (eth/base/polygon) | 🟢 LIVE (was all-zero placeholder, fixed Aug 3) | 2026-08-03 |
| 4e | Token Security API | api.gentechlabs.net/v1/score (port 8086) | Solana token risk scoring → Rugcheck engine | 🟢 LIVE (was placeholder, now proxies Rugcheck, fixed Aug 3) | 2026-08-03 |
| 5 | GitHub — Gentech-Labs org | https://github.com/Gentech-Labs | programmable-money-x402, genTech-agent-kit, agent-credit-score (21 repos) | 🟢 PUBLIC + VISIBLE | 2026-08-02 |
| 6 | GitHub — ProtoJay4789 (personal) | https://github.com/ProtoJay4789 | All repos (kit, portfolio, etc.) | ⚠️ FLAGGED — web 404s despite public; use ORG URLs | 2026-08-02 |
| 7 | Agentic.Market (Bazaar) | https://agentic.market | Auto-indexed when CDP facilitator settles a payment | ⏳ NOT INDEXED YET — needs first on-chain settlement | 2026-08-02 |

## 🟡 PENDING / WATCHLIST

| # | Platform | Notes | Action needed |
|---|----------|-------|---------------|
| 8 | x402.org / x402scan | Standard x402 scanner — check if we appear | Verify listing after fix settles |
| 9 | signal402 / other x402 directories | Was submitted earlier — verify status | Check + update |
| 10 | MCP directories (mcp-directory, etc.) | Our mcp-directory service reports ok — confirm which directories list us | Audit + collect URLs |

## ⚪ KNOWN BUT NOT PURSUED / OTHER

- Solana Foundation `pay` CLI (MPP/SIWX protocol) — separate protocol from x402, not applicable
- Pay skills catalog — MPP/SIWX based, not x402

---

## CHANGE PROTOCOL (run this on ANY service change)

1. Edit gateway/manifest → bump manifest version (currently 8.0.0)
2. Update this registry: mark affected rows, set "last verified" = today
3. Check x402-list.com (re-scans ~5h) — verify compliance chips still green
4. Check 8004scan — agent identity/metadata current?
5. If new service added → update manifest + x402-list endpoint list + this registry
6. If price changed → x402-list price chip + manifest prices
7. If brand/URL changed → EVERY row above + GitHub org description + landing page
8. If a real on-chain settlement lands → Agentic.Market auto-indexes (row 7 flips to LIVE)

**Prompt rule:** after any change, agent asks Jordan: "we changed X — want to go back and update [affected platforms]?" Do NOT silently skip rows.


| **Bankr (bankr.bot)** | Robinhood Chain + Base | LAUNCHED ✅ (Jul 22) | **$TREASURY token launched via Bankr** on Robinhood Chain: contract 0x56D03C0f4167cC2c26B781dE47E608d660F13ba3, 100B supply (85% LP / 15% creator vesting), claimable TREA ~39M (Revenue Monitor). PLUS gentech-x402-services SKILL.md published Aug 2 (Gentech-Labs/genTech-agent-kit/master/skills/bankr, 200) so Bankr agents can pay our 6 API services. Next: verify skill install + first paid API call; monitor TREA claims. | Verify skill discovery + first API settlement | 2026-08-02 (corrected — was already launched Jul 22) |

| **Treasury Defender (new service #7)** | Multi-chain | LIVE ✅ (Aug 2) | New paid x402 service (port 8096): classifies any token KNOWN/SUSPICIOUS (homoglyph detection + liquidity check), quarantines flagged tokens, returns safe burn calldata. 3 scam tokens from Jordan's Avalanche wallet already quarantined (ÚSDС, USḌC, UЅDС). Manifest v9.0.0. | Add to Bankr skill + x402-list rescan | 2026-08-02 |
---

*Last updated: 2026-08-02 (created by Jordan directive — keep this file current)*
