---
name: hackathon-bounty-scanner
description: Scan for upcoming hackathons and active smart contract bug bounty programs across Immunefi, Code4rena, Sherlock, Devpost, ETHGlobal, and DoraHacks. Handles bot detection, rate limits, and platform quirks.
tags: [hackathon, bug-bounty, smart-contract, solidity, security, web3, defi]
---

# Hackathon & Bug Bounty Scanner

Scan for upcoming hackathons and active smart contract bug bounty programs across multiple platforms.

## Purpose
Recurring scan to surface opportunities relevant to a Solidity/EVM + AI agent stack. Designed for scheduled cron jobs — handles bot detection, rate limits, and platform quirks.

## Platform Access Strategy (ordered by reliability)

### Tier 1: Browser + JS Extraction (most reliable)
These work via `browser_navigate` + `browser_snapshot` or JS console extraction:

| Platform | URL | Notes |
|----------|-----|-------|
| Immunefi | `https://immunefi.com/bug-bounty/` | Table renders client-side. Use JS to extract rows |
| Code4rena | `https://code4rena.com/audits` | Accessible, no bot detection. Shows active/judging/completed audits |
| Sherlock | `https://audits.sherlock.xyz/contests` | Clean rendering. Active contests shown prominently |
| Devpost | `https://devpost.com/hackathons?search=blockchain%20AI` | Search with keywords. Filter by Open/Upcoming |

### Tier 2: web_extract (may hit rate limits)
Try these as `web_extract` first, fall back to browser if rate-limited:
- HackerOne (crypto programs)
- Luma event pages

### Tier 3: Cloudflare-blocked (skip or manual check)
These aggressively block automated access:
- **ETHGlobal** (`ethglobal.com/events`) — Cloudflare challenge
- **DoraHacks** (`dorahacks.io/hackathon`) — Human verification

**Workaround:** Note in report that these require manual check. Don't burn retries.

## Immunefi Extraction Pattern
```javascript
const rows = document.querySelectorAll('table tbody tr');
const bounties = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 4) {
    const nameLink = cells[0]?.querySelector('a');
    bounties.push({
      name: cells[0]?.textContent?.trim().replace(/Triaged by Immunefi/g, '').trim(),
      vaultTVL: cells[1]?.textContent?.trim(),
      maxBounty: cells[2]?.textContent?.trim(),
      totalPaid: cells[3]?.textContent?.trim(),
      link: nameLink?.href
    });
  }
});
```

## Relevance Filtering Keywords
Prioritize bounties/hackathons matching:
- Solidity, EVM, Base, Arbitrum, Optimism
- DeFi, lending, DEX, perpetuals
- AI agents, agentic commerce, autonomous agents
- Solana (if Rust expertise exists)

## Output Format
Structure as:
1. **🏆 HACKATHONS** — Name | Platform | Deadline | Prize | Relevance | Link
2. **🛡️ BUG BOUNTIES** — Active contests + standing bounties
3. **📌 RECOMMENDATIONS** — Top 2-3 with reasoning
4. **⏰ DEADLINES** — Anything within 7 days flagged

## Rate Limit Handling
- `web_extract` has ~10 requests/5min rate limit
- If rate-limited, switch to `browser_navigate` instead of retrying
- Batch independent extractions when possible
- Prefer browser for sites that render client-side (React SPAs)
