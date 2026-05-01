---
name: crypto-hackathon-bounty-scout
description: "Scan for crypto/AI hackathons, bug bounties, and audit competitions across Devpost, Immunefi, Code4rena, and Sherlock. Compile structured opportunity reports with actionable deadlines and prize ranges."
tags: [crypto, hackathon, bug-bounty, immunefi, code4rena, devpost, security, web3, ai-agents, google-startups]
triggers:
  - Scanning for upcoming crypto or AI hackathons
  - Finding bug bounty programs in crypto/DeFi
  - Checking for new audit competitions on Code4rena or Sherlock
  - Compiling a crypto opportunity report
  - Running a periodic hackathon/bounty scout cron job
  - Searching for Web3 security research opportunities
  - Researching AI agent hackathons or challenges
  - Looking up Google for Startups, Meta, or other big-tech AI competitions
  - Finding in-person builder events on Luma
---

# Crypto Hackathon & Bug Bounty Scout

Periodic scan for hackathons, bug bounties, and audit competitions in crypto/AI/Web3.

## Platforms to Scan

### 1. Devpost (Hackathons)
- **URL:** `https://devpost.com/hackathons`
- **Search:** Filter by "crypto", "web3", "blockchain", "artificial intelligence", "AI agents"
- **Status filters:** Upcoming + Open
- **Data extracted:** Event name, host, prizes, dates, format (online/in-person), tags
- **Workaround:** Direct navigation works; no Cloudflare issues
- **Note:** Some Devpost invite links go through `devpost.team` which has Cloudflare — use `curl -sL -o /dev/null -w "%{url_effective}" URL` to resolve redirects first

### 2a. CryptoNewsZ (Hackathon Aggregator)
- **URL:** `https://www.cryptonewsz.com/events/hackathons`
- **Data:** Structured table with DATE, HACKATHONS, LOCATION, PRIZES columns
- **Coverage:** Blockchain, Web3, DeFi, NFT, AI/ML hackathons — updated monthly
- **Workaround:** Loads fully in browser; no Cloudflare issues
- **Note:** Best single-page overview of upcoming crypto hackathons with prize data

### 2b. Web3Voyager (Monthly Hackathon Roundups)
- **URL:** `https://web3voyager.com/web3-hackathons-april-2026` (change month/year)
- **Data:** Curated list sorted by submission deadline; includes format, ecosystem, detailed descriptions
- **Coverage:** Ethereum, Solana, Algorand, XRP, Farcaster, and more
- **Workaround:** Loads fully; sidebar has featured events with dates
- **Note:** Published monthly; search Yahoo for "Web3 hackathons [MONTH] [YEAR]" to find latest

### 2c. CompeteHub (AI Competition Directory)
- **URL:** `https://competehub.dev/en/competitions`
- **Data:** Hackathons, AI Agent Challenges; filterable by region, status, tags
- **Coverage:** AI agents, Web3, data visualization, finance — many with prize pools in tokens
- **Workaround:** Loads fully; search box works for keyword filtering
- **Note:** Good for finding AI-specific hackathons; shows time remaining

### 2d. lablab.ai (AI Hackathons)
- **URL:** `https://lablab.ai/ai-hackathons`
- **Data:** AI-focused hackathons; often tied to tech conferences (e.g., Milan AI Week)
- **Coverage:** Autonomous agents, LLMs, computer vision, NLP
- **Workaround:** Loads fully in browser
- **Note:** Many are co-hosted with major AI events; good for in-person opportunities

### 2. Immunefi (Bug Bounties)
- **URL:** `https://immunefi.com` → "Explore Bounties"
- **Data extracted:** Protocol name, vault TVL, max bounty, total paid, resolution time, last updated
- **JavaScript extraction:** Query table rows from `table tbody tr` → `td` cells
- **Workaround:** May need to navigate to homepage first, then click "Explore Bounties"

### 3. Code4rena (Audit Competitions)
- **URL:** `https://code4rena.com/audits`
- **Data extracted:** Project name, chain/language, prize pool, deadline, audit status
- **Workaround:** Direct navigation works; no Cloudflare issues
- **Note:** Shows active, awarding, and completed audits

### 4. Sherlock (Audit Contests & Bug Bounties)
- **URL:** `https://sherlock.xyz` → "Active Contests & Bounties"
- **Workaround:** Often returns 404 on deep links; navigate from homepage
- **Status:** Site may be unstable; monitor separately if issues persist

### 5. DoraHacks (Hackathon Platform)
- **URL:** `https://dorahacks.io/hackathon/`
- **Data:** Hackathons with prize pools, tracks, timelines
- **Coverage:** Web3, AI, DeFi — many major hackathons hosted here (Mantle, HashKey, etc.)
- **Workaround:** Has human verification CAPTCHA; may need to use search snippet data instead
- **Note:** If blocked, extract details from Yahoo search snippets or news articles about the hackathon

### 6. Luma (In-Person Hackathons)
- **URL:** `https://luma.com` → search or explore events
- **Data extracted:** Event name, host, dates, location, attendees, tags (AI, Crypto, etc.)
- **Workaround:** Direct navigation works; pages load fully
- **Note:** Many AI agent hackathons are in-person only (Jakarta, Singapore, etc.)

### 7. Google for Startups (AI Challenges)
- **URL:** `https://startup.google.com/programs/` or search "Google for Startups AI Agent Challenge"
- **Data extracted:** Challenge name, prize pool, credits, deadline, tech stack requirements
- **Note:** Often announced via YouTube videos with registration links (goo.gle shortlinks → Devpost)
- **Workaround:** Resolve shortlinks with `curl -sL -o /dev/null -w "%{url_effective}" URL`

## Search Engine Fallbacks

When Google/DuckDuckGo/Bing block with CAPTCHAs (common for headless browsers):
1. **Yahoo Search** — Works reliably without CAPTCHA; use as primary or fallback
   - Pattern: `https://search.yahoo.com/search?p=QUERY`
   - Site-specific: `site:devpost.com "hackathon name"`
   - **Multi-query strategy:** Run 4-6 varied queries for comprehensive coverage:
     - `"crypto hackathon 2026 upcoming"`
     - `"web3 hackathon prize money 2026"`
     - `"AI agent hackathon 2026"`
     - `"DeFi hackathon 2026 prize pool"`
     - `"Solana hackathon 2026 prize"` (or other chain-specific)
     - `"hackathon April May 2026 blockchain prize"` (month-specific)
2. **Direct URL resolution** — Use curl to resolve shortened URLs before browser navigation
   - `curl -sL -o /dev/null -w "%{url_effective}" "https://goo.gle/SHORTCODE"`
3. **YouTube descriptions** — Many challenges link via YouTube video descriptions; check for registration URLs
4. **Aggregator sites** — After initial search, visit CryptoNewsZ, Web3Voyager, CompeteHub for structured data

## Cloudflare & Bot Detection Workarounds

Most crypto platforms use Cloudflare protection. Strategies:

1. **Direct browser navigation** — Works for Devpost, Code4rena, Immunefi homepage
2. **Avoid search engines** — Google, DuckDuckGo, Bing all block headless browsers with CAPTCHAs
3. **Navigate from homepage** — Don't deep-link to specific pages; click through navigation
4. **JavaScript console extraction** — When page loads but content is in tables, use `browser_console` with `document.querySelectorAll` to extract structured data
5. **API fallbacks** — Immunefi has an internal API; Code4rena may have one; check for GraphQL endpoints

## Data Extraction Patterns

### Immunefi Table Extraction
```javascript
const rows = document.querySelectorAll('table tbody tr');
const bounties = [];
rows.forEach((row, i) => {
  if (i >= LIMIT) return;
  const cells = row.querySelectorAll('td');
  if (cells.length > 0) {
    bounties.push({
      name: cells[0]?.textContent?.trim(),
      vault: cells[1]?.textContent?.trim(),
      maxBounty: cells[2]?.textContent?.trim(),
      totalPaid: cells[3]?.textContent?.trim(),
      resolution: cells[4]?.textContent?.trim(),
      lastUpdated: cells[5]?.textContent?.trim()
    });
  }
});
JSON.stringify(bounties, null, 2);
```

### Devpost Filter URL Pattern
```
https://devpost.com/hackathons?search=KEYWORD&status[]=upcoming&status[]=open
```

### Luma Event Extraction
Luma pages load fully in browser; extract from snapshot:
- Event name, host, date/time, location
- Attendee count ("98 Going")
- Tags (AI, Crypto, etc.)
- Registration status (Approval Required vs open)
- Pattern: Navigate to `luma.com/EVENT_ID` → snapshot → parse heading + paragraphs

## Report Structure

```markdown
# 🔍 Hackathon & Bounty Scout — [Date]

## 🏆 UPCOMING HACKATHONS
| Event | Host | Prizes | Dates | Format |
|-------|------|--------|-------|--------|

## 🛡️ ACTIVE BUG BOUNTIES (Immunefi)
| Protocol | Max Bounty | Vault TVL | Total Paid | Status |
|----------|-----------|-----------|------------|--------|

## 📋 AUDIT COMPETITIONS (Code4rena)
| Project | Chain | Prize Pool | Deadline | Focus |
|---------|-------|------------|----------|-------|

## 🎯 ACTIONABLE RECOMMENDATIONS
1. Immediate (this week):
2. Short-term (this month):
3. Bug bounty hunting:
```

## Known Pitfalls

- **Google/DuckDuckGo/Bing CAPTCHAs** — All major search engines block headless browsers; use Yahoo Search instead
- **Cloudflare blocks** — Most crypto sites use aggressive bot detection; avoid direct API calls via curl
- **devpost.team Cloudflare** — Devpost invite links go through devpost.team which has Cloudflare; resolve redirects first
- **Sherlock 404s** — Site restructured; deep links break; always navigate from homepage
- **Devpost filter UX** — URL params may not apply correctly; may need to click checkboxes manually
- **Immunefi rate limits** — Don't refresh excessively; extract data in one pass
- **Prize data may be private** — Immunefi shows "Private" for many total_paid fields
- **Code4rena completion states** — "Awarding" means submissions closed but winners not yet announced
- **In-person only events** — Luma events (Real World AI Agents, etc.) may be location-restricted; check before recommending
- **Student-only restrictions** — Some hackathons (Mega Agent-A-Thon) restrict to students; check eligibility upfront
- **DoraHacks CAPTCHA** — Has human verification; if blocked, extract data from news articles or search snippets
- **ETHGlobal Cloudflare** — ethglobal.com uses Cloudflare; extract data from CryptoNewsZ or search results instead
- **SoftServe domain issues** — AgentX hackathon domain may not resolve; check for alternative registration links
- **Multiple queries needed** — Single Yahoo query misses many hackathons; run 4-6 varied queries for full coverage
- **Aggregator sites are gold** — CryptoNewsZ and Web3Voyager have structured tables; visit them early in the scan

## Related Skills

- `defi-dashboard-digest` — DeFi market data pattern (similar "scan multiple sources" approach)
- `blogwatcher` — RSS monitoring (different domain, similar periodic scan pattern)
