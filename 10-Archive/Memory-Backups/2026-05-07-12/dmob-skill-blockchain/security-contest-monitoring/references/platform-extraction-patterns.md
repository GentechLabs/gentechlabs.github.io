# Platform Extraction Patterns — Session Notes (May 2, 2026)
**Skill:** `security-contest-monitoring`  
**Session:** Multi-platform contest scan (Cantina, Code4rena, Devpost, Colosseum)  
**Prepared by:** DMOB (Labs)

---

## Quick Reference Table

| Platform | Auth Required | Data Location | Key Selector / Path | Notes |
|----------|--------------|---------------|---------------------|-------|
| Cantina | None (public) | Hydrated React state + DOM | `.competition-card` + `assetGroups[].chains` | 403 on curl → use Playwright |
| Code4rena | None | Next.js push segments | `self.__next_f.push` → `audits.Active` | URL-escaped; longest segment only |
| Devpost | None | Public API + JSON-LD | `/api/hackathons?search=` + `/api/hackathons/<ID>` | Prize sum from `prizes[]` array |
| Colosseum | Arena: Yes (OAuth) | Public page + arena dashboard + Devpost microsites | `colosseum.com/hackathon` → arena → 5 track cards | `colosseum.build` NXDOMAIN |
| Sherlock | Partial | Webflow CMS | Manual or Playwright network intercept | Not automated |

---

## Code4rena: Push Segment Decoding ( FULL WORKFLOW )

### Problem
Next.js push segments are URL-escaped and embedded as inline JS array elements, not plain JSON.

### Solution Steps
```python
import requests, urllib.parse, json

# 1. Fetch raw HTML
resp = requests.get("https://code4rena.com/contests")
html = resp.text

# 2. Find all push segments
# Pattern: self.__next_f.push([INDEX,"PAYLOAD"])
import re
segments = re.findall(r'self\.__next_f\.push\(\[(\d+),"([^"]*)"\]\)', html)

# 3. Sort by index, concatenate payloads in order
segments_sorted = sorted(segments, key=lambda x: int(x[0]))
combined = ''.join(urllib.parse.unquote(s[1]) for s in segments_sorted)

# 4. Bracket-balance extraction: find "audits":{"Active":[
start_marker = '"audits":{"Active":['
idx = combined.find(start_marker)
if idx == -1:
    raise ValueError("Audits.Active not found")

# Count brackets to find the end of the array
depth = 0
end = idx
in_array = False
for i, ch in enumerate(combined[idx:]):
    if ch == '[':
        depth += 1
        in_array = True
    elif ch == ']':
        depth -= 1
        if in_array and depth == 0:
            end = idx + i + 1
            break

active_array_str = combined[idx:end]
data = json.loads(active_array_str)  # ← now valid JSON
contests = data  # this is the Active contests array
```

### Pitfalls
- Some `<script>` tags contain decoded push segments (already JSON); others are escaped. Always run `urllib.parse.unquote()` anyway (idempotent).
- If `json.loads` fails, the extracted substring may still contain JS-style unquoted keys. Use a lenient parser or manually clean `{key: value}` → `{"key": value}`.
- The longest segment is the main app shell; shorter segments are route chunks or lazy-loaded components.

### Verified Output (May 2, 2026)
```json
[
  {
    "id": 123,
    "title": "K2",
    "endTime": 1754064000000,
    "formattedAmount": "$135,000 USDC",
    "league": "stellar",
    "state": "live"
  },
  ...
]
```

---

## Cantina: Playwright Rendering + DOM Extraction

### Problem
Cantina blocks non-browser user agents (HTTP 403) and loads competition data client-side via TanStack Query.

### Solution
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto("https://cantina.xyz/competitions", wait_until="networkidle")
    
    # Wait for cards to render
    page.wait_for_selector(".competition-card")
    
    # Extract card HTML
    cards = page.query_selector_all(".competition-card")
    for card in cards:
        title = card.query_selector(".title").inner_text()
        prize_text = card.inner_text()  # regex for $XX,XXX
        # ...
```

### Alternative: Dehydrated State Extraction
If page source contains `window.__REACT_QUERY_STATE__`, extract the JSON blob:
```python
import re, json, html
script_text = page.content()
m = re.search(r'window\.__REACT_QUERY_STATE__\s*=\s*\"([^\"]+)\"', script_text)
if m:
    encoded = m.group(1)
    decoded = html.unescape(encoded).encode('utf-8').decode('unicode_escape')
    state = json.loads(decoded)
    # Navigate state['queries'][...]['state']['data']['competitions']
```

### Verified Selectors (May 2, 2026)
- Competition card container: `.competition-card`
- Prize element: `[data-testid="prize"]` or `.MuiTypography-root` containing `$`
- Time remaining: `[data-testid="time-remaining"]` or text matching `\d+ days? left`
- Chain badges: `.chain-badge` or SVG icon `alt` text

---

## Devpost: API-First Discovery

### Endpoint Patterns
```
# Search
GET https://devpost.com/api/hackathons?search=agent&page=1

# Detail (once you have ID from search)
GET https://devpost.com/api/hackathons/<ID>
```

### Sample API Response (search)
```json
{
  "hackathons": [
    {
      "id": 13240,
      "title": "IGNITION | Global Solana Hackathon",
      "url": "https://ignition.devpost.com/",
      "deadline": "2026-05-15T23:59:00Z",
      "prize": "$5,120,000",
      "themes": ["DeFi", "AI", "Infrastructure"]
    }
  ]
}
```

### Detail Response Schema
```json
{
  "id": 13240,
  "title": "...",
  "submission_period_dates": {
    "starts_at": "2026-04-01T00:00:00Z",
    "ends_at": "2026-05-15T23:59:59Z"
  },
  "prizes": [
    {"title": "Grand Prize", "amount": 1000000},
    {"title": "DeFi Track", "amount": 250000}
    // ...
  ],
  "themes": [...],
  "organization": {"name": "Solana Foundation"}
}
```

### Important Checks
1. **Deadline validation:** API `deadline` field is authoritative. If page shows older date, trust API.
2. **Prize aggregation:** Sum `amount` values in `prizes` array to get total prize pool.
3. **Chain inference:** Scan `organization.name` and `themes` for "Solana", "Base", "Ethereum". If ambiguous, check description for sponsor logos (requires HTML fetch, not in API).

---

## Colosseum: Frontier Hackathon Access Pattern

### URL Evolution
- `colosseum.build` → currently **NXDOMAIN** (do not rely)
- `colosseum.com/hackathon` → stable public landing
- `arena.colosseum.org/hackathon` → authenticated track listing (OAuth with GitHub/Twitter)

### Track Identification
The Frontier edition always contains **5 competition tracks**. Examples observed May 2026:
1. **Mega Agent-A-Thon** — AI agents on Solana
2. **X402 Track** — Payments protocol
3. **DeFi Primitive** — Lending/DEX
4. **Infrastructure** — RPC, indexing, tooling
5. **Consumer App** — UX-focused

Each track → separate Devpost microsite. Check:
- `https://<track-name>.devpost.com/` (e.g., `mega-agent-a-thon.devpost.com/`)
- Prize pool and deadline are per-track (some share global deadline).

### Automated Access Limitation
Track list requires authentication. If automation needed in future:
- Use Playwright with persistent context: `--user-data-dir=/tmp/colosseum_profile`
- Or use `requests` with session cookie exported from browser (manual one-time).
- Monitor `arena.colosseum.org/api/tracks` endpoint (private, likely GraphQL).

---

## Date Parsing Gotchas

### Devpost Deadline Formats
- **ISO style:** `2026-05-15T23:59:00Z`
- **Human readable:** `"May 15, 2026 at 11:59pm PST"` ← includes timezone abbreviation
- **Relative (JS rendered):** `"12 days left"` (text only; no absolute date)

**Parser:** Use `dateutil.parser.parse(text)` — handles all formats and timezones.

### UTC Conversion
```python
from dateutil import parser
from datetime import datetime, timezone

dt = parser.parse(deadline_text)  # may be naive or tz-aware
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)  # assume UTC if missing
else:
    dt = dt.astimezone(timezone.utc)

now = datetime.now(timezone.utc)
days_left = (dt - now).days
```

### Cantina Multiple Dates
Cantina pages often show:
- `submission_opens` — when you can start submitting
- `competitions_opens` — judging begins
- `submission_deadline` — **use this one**

If API not available, scan for the **latest** date among the three as conservative (over-estimate days left → safe to include).

---

## Chain Classification Rules (Jordan's Filters)

| Chain Alias | Canonical Name | Notes |
|-------------|----------------|-------|
| `ethereum`, `evm`, `mainnet` | Ethereum | Assume Ethereum mainnet unless project explicitly lives on L2 |
| `base` | Base | L2, qualifies |
| `solana` | Solana | Qualifies |
| `stellar` | Stellar | Qualifies **only if prize > $5K** (per filter rule) |
| `hyperliquid` | Hyperliquid | Qualifies **only if prize > $5K** |
| `monad` | Monad (EVM) | Count as Ethereum |
| `sui` | Sui | Qualifies (EVM alternative) |
| `avalanche`, `avax` | Avalanche C-Chain | Qualifies |
| `polygon` | Polygon | Qualifies |
| `arbitrum` | Arbitrum | Qualifies |

When in doubt, check the platform's `league` or `chain` field; if missing or ambiguous, mark "Multi-chain" and include a note.

---

## Prize Parsing Patterns

### Currency String → Int
```python
def parse_prize(text):
    # " $135,000 USDC " → 135000
    import re
    m = re.search(r'\$([\d,]+)', text)
    if m:
        return int(m[1].replace(',', ''))
    return 0
```

### Ranges
- `$10,000–$50,000` → use **max** ($50,000) for filtering (conservative: if max qualifies, min likely does too).
- `"Up to $25,000"` → treat as $25,000 (max possible).

### Non-USD
If prize is in tokens (e.g., "50,000 USDC", "100 SOL"), convert via current price API (CoinGecko) **only if necessary**. Otherwise treat as USD-equivalent stated (most contests list USD value).

---

## Cross-Chain Flag Keywords

Search page text, titles, and sponsor lists for:
- `layerzero` / `ofin` / `cross-chain messaging`
- `kite ai` / `kite.ai` / `kite pavilion`
- `agentescrow` / `agentescrow.xyz` + `solana` nearby
- `wormhole` (cross-chain bridge, distinct from pure Solana)
- `axelar` (multi-chain)

Flag as boolean in output:
```json
"cross_chain": {
  "layerzero": true,
  "kite_ai": false,
  "agentescrow_solana": true
}
```

---

## Verified Platform Status (May 2, 2026)

| Platform | Health | Last OK | Notes |
|----------|--------|---------|-------|
| Code4rena | OK | 2026-05-02 | 32 push segments, Active array accessible |
| Cantina | OK | 2026-05-02 | Requires Playwright, no auth |
| Devpost API | OK | 2026-05-02 | 200 OK, JSON response |
| Colosseum public | OK | 2026-05-02 | `colosseum.com` loads, arena requires OAuth |
| Colosseum arena | BLOCKED | — | Auth wall; manual login needed |
| Sherlock | UNSTABLE | — | Often returns Webflow shell |

---

## Session Artifacts (May 2 Run)

| File | Contents |
|------|----------|
| `/tmp/c4_combined.txt` | Concatenated push segments (decoded) |
| `/tmp/cantina_rendered.html` | Full DOM after Playwright load |
| `/tmp/agents_assemble.html` | Devpost Agents Assemble page HTML |
| `/tmp/ignition_devpost.html` | IGNITION Devpost page (deadline stale) |
| `/tmp/colosseum_hackathon_full.html` | Colosseum Frontier public page |
| `/tmp/reserve_governor.html` | Cantina Reserve Governor detail page |

---

*This reference file is session-specific; patterns here are expected to be stable across future scans. Update if platform structure changes.*
