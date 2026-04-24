---
type: queue
project: browser-harness
created: 2026-04-18
---

# browser-harness — Domain Skills Queue

Source: `/root/Documents/Obsidian Vault/02-Labs/browser-harness-domain-skills-proposal.md`

## How Domain Skills Work
- `.md` files in `/root/browser-harness/domain-skills/<site>/`
- Document: URL patterns, APIs (preferred over browser), stable selectors, gotchas
- Contribute upstream via PR when generalizable
- Reference: `domain-skills/github/scraping.md`

---

## Queue (Build Order)

| # | Skill | Owner | Status | Notes |
|---|-------|-------|--------|-------|
| 1 | Snowtrace | Dmob | ⬜ queued | Contract verification, ABI extraction, token holders. AAE Layer 2. |
| 2 | LFJ (TraderJoe) | Dmob | ⬜ queued | Pool discovery, LP position mgmt, swap routes. LP monitor upgrade. |
| 3 | Twitter/X | Desmond | ⬜ queued | Tweet extraction, profile monitoring, engagement metrics. |
| 4 | Polymarket | YoYo | ⬜ queued | Market discovery, odds extraction, volume tracking. |
| 5 | ETHGlobal | Gentech | ⬜ queued | Hackathon submission forms, file uploads, multi-platform. |

## Future Candidates

| Skill | Owner | Why |
|-------|-------|-----|
| CoinMarketCap UI | YoYo | Portfolio export, new listing alerts (supplement API) |
| TradingView | YoYo | Chart patterns, screener extraction |
| Snapshot / Tally | Dmob | Governance proposal extraction, vote tallying |
| Dune Analytics | YoYo | Dashboard data when API limited |
| YouTube channels | Desmond | Channel monitoring (supplement transcript tool) |
| Linear / Notion | Gentech | PM automation for agent team |
| Vercel / Netlify | Gentech | Deploy monitoring for hackathon projects |

## Rules
- **API first, browser last** — `http_get()` beats browser every time
- Browser for: JS-rendered pages, complex forms, file uploads, UI-only features
- Self-healing: if selector breaks, edit `helpers.py` mid-task
- Headless Chrome gets 403 from some sites — user-agent spoofing as workaround
