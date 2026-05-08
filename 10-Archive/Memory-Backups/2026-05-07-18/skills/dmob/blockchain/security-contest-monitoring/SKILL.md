---
name: security-contest-monitoring
description: "Monitor active bug bounty contests and audit competitions across platforms (Cantina, Code4rena, Sherlock, Hack and Pro). Extract embedded SPA state, apply filter criteria, and generate consolidated reports."
version: 1.1.0
author: DMOB (Labs)
license: MIT
metadata:
  hermes:
    tags: [security, bug-bounty, audit, monitoring, web3, scraping, nextjs, spa]
    related_skills: [hackathon-prep, blockchain-operations]
---

# Security Contest Monitoring

Daily/periodic scanning workflow for active blockchain security contests (bug bounties, audit competitions) across major platforms. Handles SPA data extraction, filter application, and report delivery.

---

## When to Use

Trigger: Jordan asks to "scan for active contests", "check bug bounties", or scheduled daily cron at 09:00 UTC.

**Do NOT use** for one-off hackathon research (use `hackathon-prep` instead) or for smart contract audit work (use `requesting-code-review`).

---

## Platforms & Quorum

| Platform | URL | Status | Data Method |
|----------|-----|--------|-------------|
| Cantina | https://cantina.xyz/competitions | ✅ Active | TanStack dehydration / SPA HTML |
| Code4rena | https://code4rena.com/audits | ✅ Active | Browser DOM or Next.js push segments |
| Devpost | https://devpost.com/hackathons | ✅ Active | Public API + HTML scraping |
| Colosseum (Solana) | https://colosseum.com/hackathon / https://arena.colosseum.org | ✅ Active (arena requires login) | Public page + authenticated arena tracks |
| Sherlock | https://audits.sherlock.xyz/contests | ⚠️ Partial | Next.js push segments (subdomain) |
| Hack and Pro | https://hackand.pro | ❌ DNS failure | Domain does not resolve (NXDOMAIN) — site appears offline |
| HackenProof | https://hackenproof.com | 🚫 SKIPPED | Per Jordan: account doesn't qualify |

---

## Filter Criteria (Jordan's Rules)

Apply **all** criteria to each contest:

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Prize pool | ≥ $1,000 USD equivalent | Use DeFiLlama for crypto conversions |
| Time remaining | ≥ 7 days | Exclude contests closing <5 days |
| Chains | Ethereum, Base, Solana | Include others **only** if prize > $5,000 (Stellar qualifies) |
| Status | Must be "live" / "active" | Not "upcoming" or "closed" |
| Eligibility | No expert-level/portfolio gate | Skip if contest requires approval |

## Platform-Specific Notes

### Code4rena
- **URL redirect:** `/contests` redirects to `/audits`. Use `https://code4rena.com/audits` directly.
- **Browser-first approach:** `browser_navigate` renders the full page with all contest data visible in the DOM. Active audits, bounties, and submissions-closed sections are all accessible without push segment extraction. Use push segments only as fallback when browser is unavailable.
- **Bounties tab:** The page *may* have a "Bounties" button/tab (e.g., "Bounties 9") that reveals ongoing perpetual bounty programs. These are NOT time-boxed — they have no end date. Include them in a separate "Ongoing Bug Bounties" section in the report, not in the main contests table.
  - **⚠️ As of 2026-05-07, the Bounties button was NOT visible in the DOM** — the page only rendered audits (active, submissions closed, completed). If bounties are not visible, skip them and note in the report. Do not block on missing bounties data.
- **Push segment location (fallback):** Search entire HTML for `self.__next_f.push`; you'll find 32–48 segments. The contests data is in the **longest** segment (typically 30–80KB).
- **Data path:** After decoding, navigate `audits.Active[]` for live contests; `bounties` may be in a separate push or nested under `opportunities`.
- **Chain proxy:** The `league` field indicates chain (e.g., `"league":"ethereum"` → Ethereum mainnet; `"league":"stellar"` → Stellar). Use this for chain classification.
- **Prize parsing:** `formattedAmount` is like `"$135,000 USDC"`; convert to int. Beware of ranges like `"$10,000–$50,000"` — take the max or average as specified in filter rules.
- **Deadlines:** `endTime` is a Unix timestamp in milliseconds; convert to ISO. `startTime` exists but use `endTime` for time-remaining calculation.

### Cantina
- **Browser-first approach:** `browser_navigate` works directly — no 403 issues with the built-in browser. Page renders with competition cards visible. Use curl/Playwright only as fallback.
- **URL patterns:**
  - Competitions list: `https://cantina.xyz/competitions` (redirects to `/opportunities/competitions`)
  - Competition detail: `https://cantina.xyz/competitions/<uuid>` (e.g., `980a5976-9a7d-4014-b2e1-c248b4c6fa44`)
  - Bounties list: `https://cantina.xyz/opportunities/bounties`
- **Bounties vs Competitions:** Cantina separates "Competitions" (time-boxed audits with deadlines) from "Bounties" (perpetual ongoing programs with no end date). Bounties have massive pools (Uniswap $15.5M, Reserve $10M) but no deadline. Include bounties in a separate "Ongoing Bug Bounties" section.
- **Selector:** `.competition-card` reliably returns each contest card. Within each card, extract:
  - Title: `.title` or `h3`
  - Prize: Look for element containing `$` — try `[data-testid="prize"]` or `.reward-pot`
  - Time remaining: `[data-testid="time-remaining"]` or text matching `\d+ days? left`
  - Chain: Check `assetGroups[].chains[]` in hydrated state OR scan card text for "Base", "Ethereum", "Solana".
- **Dehydrated state:** If page source includes `window.__REACT_QUERY_STATE__`, `state.queries[].state.data.competitions` is the authoritative array.
- **Date ambiguity:** Cantina pages often show three dates: `submission_opens`, `competitions_opens`, `submission_deadline`. For the report, use the **latest** date as deadline.

### Devpost
- **API endpoint:** `https://devpost.com/api/hackathons?search=<term>` — returns basic list with IDs.
- **Detail fetch:** `https://devpost.com/api/hackathons/<ID>` returns full JSON including:
  - `prizes` array: `[{title, amount}]`
  - `submission_period_dates`: `{start, end}` (ISO-ish)
  - `themes` (tracks)
  - `organizer`, `organization`
- **Structured data on page:** Look for `<script type="application/ld+json">` — contains `"prize"` and `"deadline"` but may be incomplete; prefer API.
- **Prize summation:** Sum all `prizes[].amount` for total prize pool. Ignore in-kind prizes (software credits, cloud credits) unless USD equivalent is stated.
- **Chain inference:** Devpost is chain-agnostic; read the description for sponsor logos or explicit mentions (Solana Foundation, Base, Ethereum Foundation). If none, mark as "General / Multi-chain".

### Colosseum (Solana)
- **Domain status:** `colosseum.build` frequently NXDOMAIN; use `colosseum.com/hackathon` as the stable public page.
- **Arena access:** Track details require login at `arena.colosseum.org`. Register with GitHub/Twitter (OAuth).
- **Track extraction:** In the arena dashboard, each of the five Frontier tracks is a card linking to a Devpost microsite (e.g., `mega-agent-a-thon.devpost.com`). Visit each microsite and parse as Devpost (Technique C).
- **Prize display:** Track cards show "Up to $X in prizes" — record as `"Up to $X"` and flag as non-guaranteed maximum.
- **Agent track:** The "Mega Agent-A-Thon" or "Solana Agent Hackathon" is the AI agents track; prioritize this per Jordan's directive.

### Sherlock
- **CRITICAL**: Sherlock contests live on the `audits.sherlock.xyz` subdomain. The main `sherlock.xyz/contests` route returns 404. Always start at `https://audits.sherlock.xyz/contests`.
- **Browser-first approach:** `browser_navigate` renders the contests page with all data visible in the DOM — contest cards show title, prize, status, start/end dates directly. Use this as the primary method. Push segment extraction is fallback only.
- **Bug Bounties page:** Check `https://audits.sherlock.xyz/bug-bounties` separately. These are perpetual programs (not time-boxed) with large pools. Include in "Ongoing Bug Bounties" section.
  - **⚠️ Chain info missing:** The bug bounties list view does NOT display chain information. Mark chain as "Unknown" or omit the column for Sherlock bounties. Detail pages may have chain data but are not worth the extra navigation for bounties.
- **Data method (fallback):** Next.js SPA with push segments. The contests array is embedded in a TanStack Query dehydrated state inside `self.__next_f.push` payloads (19 segments total).
- **Extraction:**
  1. Fetch `https://audits.sherlock.xyz/contests` with browser headers.
  2. Locate the push segment containing `"pages":` and `"items":` (typically segment index 17).
  3. Decode with URL-unescape + unicode-escape decode.
  4. Navigate to `queries[].state.data.pages[].items[]` via bracket-counting extraction.
  5. Each item contains: `title`, `prizePool`, `rewards`, `startsAt` (Unix timestamp), `status`, `typeLabel`, `protocol.chain`, `id`.
- **Status codes:** `SHERLOCK_JUDGING`, `FINISHED`, `PUBLIC`, `SHERLOCK_SUBMISSION`, etc. Only include if `status` indicates active submission or judging window is open.
- **Chain detection:** The `protocol.chain` field may be null/unknown for some contests; cross-reference title keywords (e.g., "Ethereum", "Optimism", "Base") to infer, but mark as "Unknown" if ambiguous.
- **Fallback:** Detail pages at `https://audits.sherlock.xyz/contests/<ID>` may provide additional context but are not required for list extraction.

### Cross-Chain Flags Reference
When scanning pages or descriptions, flag if ANY of these appear:
- **LayerZero:** Any mention of "LayerZero", "OFIN", cross-chain messaging, or `layerzero.tech` in sponsors.
- **Kite AI:** Sponsor line includes "Kite AI", `kite.ai`, or "Kite Pavilion" (Colosseum track).
- **AgentEscrow Solana compatibility:** Mention of "AgentEscrow" or `agentescrow.xyz` + "Solana" in same context.

Add these flags to output under `cross_chain` keys (boolean).

---

## Data Extraction Techniques

### Technique A: Next.js Push Segment Extraction (Code4rena pattern)

Next.js apps often embed data in `self.__next_f.push()` segments in inline scripts.

**Steps:**
1. Fetch page HTML via `curl` (preferred) or Playwright (if JS rendering needed)
2. Locate script containing `self.__next_f.push`
3. Extract the segment content: `self.__next_f.push([1,"<DATA>"])`
4. URL-decode / unicode-escape decode the string
5. The DATA string is a serialized JavaScript array; parse with bracket-counting to extract JSON-like structures
6. Navigate to `audits.Active` or equivalent live contest array

**Reference script:** `scripts/extract_nextjs_push.py` (see references/)

**Pitfall:** The push segment is NOT valid JSON — it's a JS array with unquoted keys. Use bracket-balanced extraction to isolate sub-objects, then `json.loads()` on the extracted object string.

### Technique B: TanStack Query Dehydrated State (Cantina pattern)

Cantina uses TanStack Query (React Query) with Next.js; the dehydrated state lives in a script or inline `window` object.

**Steps:**
1. If Playwright available: load page, `page.content()` → get full HTML
2. Search for `window.__REACT_QUERY_STATE__` or data embedded in `self.__next_f.push` similar to Next.js
3. Extract the `state.queries[].state.data` chain
4. Within that, find the `items` or `competitions` array
5. Parse each item for `name`, `url`, `totalRewardPot`, `status`, `timeframe`, `assetGroups.chains`

**Common format:**
```json
{
  "dehydratedAt": 1777712677902,
  "state": {
    "data": { ... actual bounty/contest data ... }
  }
}
```

**Pitfall:** The data may be compressed/quoted; use `html.unescape()` and `encode().decode('unicode_escape')` before JSON parsing.

### Technique C: Devpost Public API (Hackathon Discovery)

Devpost exposes a public, unauthenticated API for listing hackathons.

**Endpoint pattern:**
```
https://devpost.com/api/hackathons?search=<keyword>&page=<n>
```

**Parameters:**
- `search` — keyword search (e.g., "agent", "solana", "ai")
- `page` — pagination (default 1)
- `filter[]` — optional filters (e.g., `filter[]=open`)

**Response:** JSON with `hackathons` array; each item includes:
- `id` — numeric ID for detail fetch
- `title`, `url` — Devpost subdomain URL
- `deadline` — ISO-like string (may need cleanup)
- `prize` — string like "$25,000" or "$$25,000 USD"
- `themes` — array of track/category names

**Detail fetch:** `https://devpost.com/api/hackathons/<ID>` returns full metadata including:
- `organizer.name`, `organization.name`
- `prize` breakdown array with `title` + `amount`
- `submission_period_dates` (start/end)
- `theme` list

**Pitfalls:**
- Prize fields may be strings with currency symbols/commas; strip and convert to int.
- Deadline format varies: "October 15, 2021 at 11:45pm PST" vs "2026-05-10T23:59:00Z" — parse with `dateutil.parser`.
- Some hackathons are multi-phase; API `deadline` may reflect final deadline or a past phase. Cross-check with page's "Timeline" section if uncertain.
- The `total_prize` field is often absent; sum individual `prize.amount` values from the `prizes` array.

### Technique D: Solana Colosseum Portal Access

Colosseum hosts Solana-focused hackathons via two interfaces:

1. **Public landing page** — `https://colosseum.com/hackathon` (no auth required)
   - Shows banner, overview, and a "ENTER FRONTIER" link leading to the arena.

2. **Arena (competition tracks)** — `https://arena.colosseum.org/hackathon` (requires sign-up/login)
   - Lists all active competition tracks (usually 5 per Frontier edition).
   - Each track has its own Devpost microsite (e.g., `mega-agent-a-thon.devpost.com`).
   - Tracks may be protocol-specific (X402, AI agents, DeFi, etc.).

**Extraction sequence:**
- Step 1: Visit public page → capture "ENTER FRONTIER" CTA URL (often points to arena sign-up).
- Step 2: Register at `arena.colosseum.org` (free; requires GitHub/Twitter OAuth).
- Step 3: In arena dashboard, enumerate the five active tracks; extract:
  - Track name (e.g., "Mega Agent-A-Thon")
  - Prize pool (displayed on track card or detail page)
  - Submission deadline (may be global hackathon deadline)
  - Specific protocol/target (e.g., "Build agents for X402 payments")
- Step 4: For deep details, follow track's Devpost link and parse JSON-LD or API data as in Technique C.

**Pitfalls:**
- `colosseum.build` may be NXDOMAIN or redirect; always try `colosseum.com` first, then follow CTA.
- Arena requires authentication; cannot scrape track list without login. Plan to use Playwright with persistent context or manual inspection for one-off research.
- Track prize pools are often "up to" amounts; record as listed (e.g., "$50,000 in prizes").
- Some tracks are "open-ended" or have rolling deadlines; mark as "ongoing" in report.

### Technique E: Fallback - Manual HTML Scraping

If all else fails, parse visible DOM elements:
- Prize pools often in `$XX,XXX` format → regex `\\$[\\d,]+`
- Countdown timers → either `data-end` attributes or text like "X days left"
- Status badges → look for `class="status-live"` or text "Live", "Active"

**Additional selectors per platform:**
- **Cantina:** `.competition-card` (each card), then within: `[data-testid="prize"]`, `[data-testid="time-remaining"]`
- **Code4rena:** Post-push decode, traverse to `audits.Active[].formattedAmount` and `endTime`.
- **Devpost:** `script[type="application/ld+json"]` contains `"prize"` and `"deadline"` in structured form.

---

## Canonical Output Format

### Report File
Save JSON to `/tmp/active_contests_report.json`:

```json
{
  "scan_date": "2026-05-02T09:14:00Z",
  "platforms_checked": ["cantina", "code4rena", "sherlock"],
  "contests": [
    {
      "name": "Reserve Governor Competition",
      "platform": "cantina",
      "prize_pool_usd": 30000,
      "currency": "USDC",
      "time_remaining_days": 8,
      "end_date": "2026-05-10T23:59:59Z",
      "chain": "Ethereum",
      "url": "https://cantina.xyz/competitions/980a5976-...",
      "notes": "Active competitions phase",
      "cross_chain": {
        "layerzero": false,
        "kite_ai": false,
        "agentescrow_solana": false
      }
    }
  ],
  "skipped": {
    "hackenproof": "Account does not qualify",
    "hackandpro": "Site inaccessible"
  }
}
```

### Telegram Delivery Format (Gentech Labs group)

Post as a **single message** with two sections:

1. **Summary table** (Markdown):
```markdown
| Contest Name | Platform | Prize Pool | Time Remaining | Chain |
|--------------|----------|------------|----------------|-------|
| Reserve Governor Competition | Cantina | $30,000 | 8 days | Ethereum |
| K2 Audit | Code4rena | $135,000 | 25 days | Stellar |
| Uniswap Bug Bounty | Cantina | $15,500,000 | Open-ended | Ethereum |
```

2. **Detailed breakdown** (Markdown, one subsection per platform):
```markdown
#### Cantina
- **[Reserve Governor Competition](URL)**
  - Prize: $30,000 USD | 8 days remaining
  - Chain: Ethereum
  - Notes: Active competitions phase

#### Code4rena
- **[K2 Audit](URL)**
  - Prize: $135,000 USD | 25 days remaining
  - Chain: Stellar (prize > $5k exception)
  - Notes: Live judging phase
```

**Include a "Cross-Chain Opportunities" subsection** listing any LayerZero/Kite AI/AgentEscrow flags.

3. **Ongoing Bug Bounties** (if any found):
```markdown
### 🏃 Notable Ongoing Bug Bounties (Timeless — Not Contest Format)
| Protocol | Platform | Pool | Chain |
|---|---|---|---|
| Uniswap | Cantina | $15,500,000 USDC | Ethereum |
| Morpho | Cantina | $2,500,000 USDC | Ethereum |
```
These are perpetual programs on primary chains worth tracking even though they have no deadline.

---

## Automation & Scheduling

**Cron schedule:** Daily at 09:00 UTC

**Cron command template:**
```bash
0 9 * * * cd /root/vaults/gentech && hermes run --skill security-contest-monitoring --prompt "Scan all platforms and post to Gentech Labs group" 2>&1 | tee /tmp/contest-scan-$(date +\%Y\%m\%d).log
```

**Telegram destination:** GenTech Labs (-1003872552815)

---

## Environment Setup

### Dependencies

```bash
# Required system tools
curl --version        # >= 7.0
python3 --version     # >= 3.9 (for Playwright fallback)
jq                   # JSON processing (optional but helpful)

# Python packages (if using Playwright extraction)
pip install playwright
playwright install chromium
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PLAYWRIGHT_BROWSERS_PATH` | Override browser install path | `~/.cache/ms-playwright` |
| `HOME` | Affects Playwright cache resolution | `/root/.hermes/profiles/dmob/home` |

**Critical pitfall:** In Hermes Agent sandbox, Playwright may look for browsers under `$HOME/.cache/ms-playwright` but the actual install is at `/root/.cache/ms-playwright`. Always export `PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright` before launching.

### Vault Files

- Assessment doc: `02-Labs/Assessment-bug-bounty-platforms-YYYYMMDD.md`
- Raw scrapes: `/tmp/cantina_full.html`, `/tmp/c4_contests.html`, etc.
- Decoded state: `/tmp/cantina_full_decoded.txt`, `/tmp/c4_decoded_56.txt`
- Report: `/tmp/active_contests_report.json`

---

## Troubleshooting

### Subagent delegation fails (API key / model errors)
**Cause:** `delegate_task` may fail if the subagent model (e.g., stepfun/step-3.5-flash) has API issues, quota limits, or is unavailable.
**Fix:** Fall back to direct execution — run all platform scans yourself using `browser_navigate` and `browser_console`. The skill's browser-first approaches work reliably without subagents.

### Code4rena: Push segment returns HTML, not data
**Cause:** Selected the wrong `<script>` tag; some scripts contain inline code or templates, not `self.__next_f.push` data.
**Fix:**
1. Find **all** occurrences of `self.__next_f.push` in the raw HTML (there are typically 32+).
2. Extract the **longest** segment (usually > 10KB); the main app state payload is always in the longest push.
3. URL-decode and bracket-balance from `"audits":{"Active":[` to extract the full contests array.

### Code4rena: Decoded push segment is still garbled or JSON parse fails
**Cause:** Next.js push payloads are URL-escaped/unicode-escaped, not pure JSON. Keys may be unquoted in the JS array representation.
**Fix:**
- Apply `urllib.parse.unquote()` then `.encode('utf-8').decode('unicode_escape')`.
- Use bracket-counting to isolate the full `Active` array substring, then `json.loads()` that substring alone (not the entire push string).
- Reference script: `scripts/extract_nextjs_push.py` (handles all decoding, ordering, and bracket balancing).

### Cantina returns 403 or login page via curl
**Cause:** Cantina blocks non-browser user agents and requires JavaScript execution to render competition data (TanStack Query client-side hydration).
**Fix:**
- Use Playwright with a full Chromium browser and a realistic user-agent string.
- Wait for DOM ready: `await page.wait_for_selector('.competition-card')`.
- Extract via `page.content()` or `page.query_selector_all()`.
- Ensure `PLAYWRIGHT_BROWSERS_PATH` is set correctly (see Environment Setup).

### IGNITION (or any Devpost hackathon) shows an outdated deadline in page text
**Cause:** Devpost loads timeline/via API after initial HTML; visible static text may be from a previous cycle or placeholder.
**Fix:**
- Fetch the API endpoint: `https://devpost.com/api/hackathons/<ID>` and parse the `deadline` field.
- If API is inaccessible, use Playwright to wait for the timeline section: `await page.wait_for_selector('.timeline-section')` and extract the date from rendered DOM.
- Always cross-check with `submission_period_dates.start/end` from the API response.

### No contests found, only bounties or empty results
**Cause:** Platform separates "competitions" (time-boxed audits) from "bounties" (ongoing programs). You may be scanning the wrong endpoint/page.
**Fix:**
- Check both `/competitions` and `/bounties` paths on Cantina.
- On Code4rena, verify you're parsing the correct push segment index (audits vs. bounties live in different pushes).
- On Devpost, use both `search=` keywords and direct API for known hackathon IDs.

### Chain field ambiguous or missing
**Cause:** Platform abstracts chain as "EVM", "Multi-chain", or leaves blank.
**Fix:**
- Cross-reference project name with known mainnet deployments (e.g., Uniswap → Ethereum, Monad → Monad/EVM, Morpho → Ethereum).
- Scan page content for chain keywords: "Solana", "Base", "Ethereum", "Stellar", "Hyperliquid".
- Check sponsor/partner logos (Solana Foundation, Base, etc.).
- If still uncertain, mark as "Multi-chain" or "Unknown" and include a note; do not guess.

### Colosseum (colosseum.build) DNS fails (NXDOMAIN)
**Cause:** Domain may be temporarily down or restricted; official Solana hackathon site has moved/redirects.
**Fix:**
- Use `https://colosseum.com/hackathon` as the public fallback.
- The arena login is at `https://arena.colosseum.org`.
- Registration is required to view track-specific prize pools and deadlines; schedule manual inspection if automation blocked.

### Playwright launch fails: "Executable doesn't exist"
**Cause:** Browser path mismatch with `$HOME` in sandboxed environment.
**Fix:**
```bash
export PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
# Or in Python before launch:
import os
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/root/.cache/ms-playwright'
```

### Deadline calculation off by a day (timezone issues)
**Cause:** Deadline strings may be in PST/PT, UTC, or local time; naive date subtraction ignores timezone offset.
**Fix:**
- Parse with `dateutil.parser` (handles timezone abbreviations like PST).
- Normalize to UTC before subtracting from `datetime.now(timezone.utc)`.
- Report both UTC deadline and days-remaining (rounded down).

### Cantina date fields ambiguous (multiple dates in page)
**Cause:** Cantina displays separate dates for registration open, submission opens, and deadline (e.g., 2026-04-29, 2026-04-30, 2026-05-10).
**Fix:**
- Look for `datetime` attributes or structured data (`application/ld+json`) indicating which date is `submission_deadline`.
- If unclear, use the **latest** date as the deadline (conservative estimate for "days remaining").
- Cross-check with the page's "Timeline" or "Important Dates" section.

### Devpost JSON-LD missing prize or deadline
**Cause:** Some hackathon pages omit structured data or use custom schema.
**Fix:**
- Fall back to API: `https://devpost.com/api/hackathons/<ID>` always returns `deadline` and `prizes` array.
- If API also missing, scrape visible text: regex for `\$[\d,]+` (prizes) and date patterns like `\w+ \d{1,2}, \d{4}`.

---

## References

- [Platform extraction patterns](references/platform-extraction-patterns.md) ← **session patterns + code snippets**
- [Sherlock extraction pattern](references/sherlock-extraction-pattern.md) ← **subdomain, push segment index 17, items path**
- [Next.js push segment decoder](scripts/extract_nextjs_push.py)
- [TanStack dehydrated state parser](scripts/parse_tanstark_dehydrate.py)
- [Filter criteria reference](references/filter-criteria.md)
- [Platform API endpoints](references/platform-endpoints.md)

---

## Revision History

- v1.2 — Code4rena bounties tab may not be visible in DOM (2026-05-07 observation); added caveat to avoid blocking on missing bounties data
- v1.1 — browser-first approach for Code4rena/Sherlock/Cantina, bounties vs competitions distinction, ongoing bounties output section, Hack and Pro DNS status, subagent fallback pitfall, Code4rena URL redirect (2026-05-05)
- v1.0 — initial skill (created 2026-05-02 after multi-platform scan session)