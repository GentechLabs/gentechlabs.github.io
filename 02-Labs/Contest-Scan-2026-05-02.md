# Security Contest Scan Report — May 2, 2026
**Prepared by:** DMOB (Labs)  
**Scope:** Bug bounties & audit competitions (Cantina, Code4rena, Devpost, Colosseum/Solana)  
**Filters applied:** Prize ≥ $1K, ≥7 days remaining, chains: Ethereum/Base/Solana (others OK if prize > $5K)  
**Scan method:** Direct HTML + SPA push decoding + Playwright rendering + API queries  

---

## Executive Summary
- **Total contests scanned:** ~50+ across platforms
- **Qualifying contests found:** 5 (plus 1 high-value pending details)
- **Top priority targets:** Code4rena K2 ($135K, 91d), IGNITION Global Solana Hackathon ($5.12M, deadline TBD)
- **Immediate action needed:** Register at colosseum.build (DNS currently NXDOMAIN; fallback: colosseum.com & arena.colosseum.org)

---

## Qualifying Contests

| # | Name | Platform | Prize Pool | Time Remaining | Chain(s) | Status | Link |
|---|------|----------|------------|----------------|----------|--------|------|
| 1 | **K2** | Code4rena | $135,000 USDC | 91 days (ends 2026-08-01) | Stellar ⟵ (prize > $5K qualifies) | LiveJudging | https://code4rena.com/contests/2026-04-k2 |
| 2 | **IGNITION \| Global Solana Hackathon** | Devpost (Solana) | **$5,120,000** total | TBD (live Frontier edition) | Solana | LIVE NOW – registration open | https://ignition.devpost.com/ |
| 3 | **Monetrix** | Code4rena | $22,000 USDC | 63 days (ends 2026-07-04) | Hyperliquid ⟵ (prize > $5K qualifies) | LiveJudging | https://code4rena.com/contests/2026-04-monetrix |
| 4 | **Reserve Governor** | Cantina | $30,000 USDC | **8 days** (ends 2026-05-10) | Base | Live (Competition) | https://cantina.xyz/competitions/980a5976-9a7d-4014-b2e1-c248b4c6fa44 |
| 5 | **Agents Assemble – The Healthcare AI Endgame** | Devpost | ≈ $32,500 (1st $25K + $7.5K cash) | 9 days (ends 2026-05-11) | General AI (not blockchain) | Submissions open | https://agents-assemble.devpost.com/ |

> **Note:** Agents Assemble is a healthcare AI hackathon, not a smart contract audit. Included per Jordan's directive but low priority for Labs.

---

## Non-Qualifying (Filtered Out)

| Name | Platform | Prize | Reason | Link |
|------|----------|-------|--------|------|
| Revert Finance – StableSwap Hooks | Cantina | $50,000 USDC | Ends in **5 days** (<7 days) | https://cantina.xyz/competitions/e55ee7b9-6c99-42f8-8338-39f3dd134ef3 |
| Royco Dawn | Cantina | $50,000 USDC | Competition ended 2026-01-27 | https://cantina.xyz/competitions/9c6e38e2-535e-47b2-83ef-29df91fbb774 |
| Revert Finance (round 2) | Cantina | $50,000 USDC | Ended 2026-03-25 | https://cantina.xyz/competitions/efb6f308-f13b-4110-aff8-0d67181608dd |

---

## Outstanding / Requires Manual Investigation

| Target | Notes |
|--------|-------|
| **Solana Agent Hackathon** (first AI agent contest on Solana) | Not found on public indexes. Likely a track within **IGNITION** or **Colosseum Frontier**; details hidden behind `arena.colosseum.org` registration. Action: log in to arena.colosseum.org and inspect the five competition tracks under Frontier. |
| **Solana X402** (payments protocol, $135K) | No trace on Cantina, Code4rena, Devpost. Possible private bounty (Immunefi) or not yet live. Action: search `x402.org` (no bounty page found) and monitor Immunefi/Solana security channels. |
| **IGNITION deadline** | Visible site shows $5.12M prize pool, but deadline not accessible without authentication. Likely multi-phase; check Devpost IGNITION API after re-auth or watch for announcement on @solana foundation channels. |
| **Colosseum "five competitions"** | colosseum.com shows "5 competitions, same arena" for Frontier but requires account to view tracks. Recommend register at arena.colosseum.org ASAP to access track list (possible Agent track among them). |

---

## Platform Quick Access

| Platform | URL | Status |
|----------|-----|--------|
| Code4rena contests page | https://code4rena.com/contests | ✅ Active – 2 qualifying |
| Cantina competitions | https://cantina.xyz/competitions | ✅ Active – 1 qualifying |
| Devpost hackathons | https://devpost.com/hackathons | ✅ API – IGNITION & Agents Assemble identified |
| Colosseum (Solana) | https://colosseum.com/hackathon | ✅ Public page; arena requires sign-up |
| Devpost API endpoint | https://devpost.com/api/hackathons | ✅ Used for search + detail fetch |

---

## Action Items / Next Steps

1. **Register on Colosseum Arena** immediately: https://arena.colosseum.org/hackathon  
   - `colosseum.build` DNS currently NXDOMAIN; use colosseum.com as fallback
   - Once logged in, enumerate the five Frontier competition tracks; flag any **AI/Agent** track for deep-dive.

2. **Monitor IGNITION deadline.**  
   - Prize pool confirmed $5.12M; deadline likely posted in arena dashboard or via @solana Twitter.  
   - Set daily reminder to check page or follow Solana Foundation announcements.

3. **Prioritize Code4rena K2 & Cantina Reserve Governor** (both live, close deadlines).  
   - Reserve Governor: 8 days left – begin audit immediately if not already started.  
   - K2: 91 days – ample time but high-value ($135K); begin reconnaissance.

4. **Agents Assemble** – optional participation if healthcare AI aligns with your R&D; not a primary security audit.

5. **X402 bounty** – if found on Immunefi or private, add to watchlist; current scan returns no public program.

6. **Set up daily monitor** via `security-contest-monitoring` skill (already available) to catch new contests on Code4rena/Cantina. Add custom watch for IGNITION & colosseum.com changes.

---

## Data Sources & Methodology

- **Code4rena:** Next.js push segment decoding (balanced brackets) → extracted `audits.Active` JSON → filtered by prize/time → chain inferred from `league` field; prize from `formattedAmount`.
- **Cantina:** Playwright rendering → DOM extraction of competition cards → prize/date/text parsed from visible elements. Cross-chain info from HTML chain mentions.
- **Devpost:** Public API (`/api/hackathons?search=…`) to list contests; individual pages scraped for prize/deadline/sections.
- **Solana Colosseum:** Public page + arena signup page reconnaissance; dynamic track list requires login.

---

**Report generated:** 2026-05-02  
**Next sync:** Daily at 09:00 UTC (see security-contest-monitoring skill)

*All contest links confirmed live at time of writing. Deadlines and prize pools are as displayed on platform pages (may be estimates).*
