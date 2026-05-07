# Sherlock Contests Extraction Notes

## Critical Discovery (2026-05-03)

### URL Correction
Sherlock contests are NOT at `sherlock.xyz/contests` (404). The correct endpoint is:

```
https://audits.sherlock.xyz/contests
```

The `audits.` subdomain hosts the actual contest listings (Next.js SPA). The main domain uses Webflow and shows a 404.

### Data Location
After fetching the page, push segments contain query state. Segment **index 17** (of 19 total) contains the contests array.

```javascript
// Segment pattern
7:["$","div",null,{"children":[[…],"$L17",null,{"state":{"mutations":[],"queries":[{"state":{"data":{"pages":[{"page":1,"nextPage":2,"items":[{…contest object…}]}]}}}}]}]}]}]}]}]}
```

### Extraction Path (bracket-counting)
1. Decode segment: `urllib.parse.unquote()` → `encode().decode('unicode_escape')`
2. Locate `"pages":[` → extract pages array
3. Inside first pages element, locate `"items":[` → extract items array
4. Parse items as JSON

### Item Schema
```json
{
  "id": 1260,
  "title": "XRP Ledger - April 2026",
  "prizePool": 519000,
  "rewards": 550000,
  "startsAt": 1776092400,
  "status": "SHERLOCK_JUDGING",
  "typeLabel": "Public Bug Bounty",
  "protocol": { "chain": "Unknown" }
}
```

- `startsAt`: Unix timestamp (seconds). Convert: `datetime.fromtimestamp(ts, tz=UTC)`
- `prizePool` / `rewards`: integer USD equivalent
- `status`: active values include `SHERLOCK_JUDGING`, `SHERLOCK_SUBMISSION`; exclude `FINISHED`, `COMPLETED`
- `typeLabel`: e.g., "Public Bug Bounty", "Public", "Public Best Efforts"
- `protocol.chain`: may be null; cross-reference title for chain hints (Ethereum, Optimism, Base, etc.)

### Pitfalls
- All 10 contests retrieved on 2026-05-03 showed `startsAt` in the past → `days_remaining = 0` (either finished or in judging phase).
- "Base" mentions in page refer to financial terms ("base variable borrow rate"), NOT the Base chain.
- Chain field often "Unknown" → must infer from title/description if needed.
- No authentication required for list view; detail pages optional.

### Quick Script
```python
import re, json, urllib.parse, datetime, subprocess
html = subprocess.run(['curl','-s','-L','-H','User-Agent: Mozilla/5.0',
                       'https://audits.sherlock.xyz/contests'],
                      capture_output=True, text=True).stdout
pushes = re.findall(r'self\.__next_f\.push\(\[1,\"(.+?)]\)', html, re.DOTALL)
seg = urllib.parse.unquote(pushes[17]).encode('utf-8').decode('unicode_escape')
# Extract pages via bracket-counting from "pages":[ then items from inside
# Parse items[json.loads(items_str)] → contest objects
```

## Chain Detection Enhancement
When `protocol.chain` is "Unknown" or not in target set (Ethereum, Base, Solana), scan `title` and `shortDescription` for chain keywords:

```python
chain_keywords = ['ethereum', 'eth', 'base', 'solana', 'sol', 'stellar', 'xrp', 'ripple',
                  'optimism', 'arbitrum', 'polygon', 'avalanche', 'hyperliquid', 'suinami']
title_lower = title.lower()
detected = [c for c in chain_keywords if c in title_lower]
# Prefer higher-confidence mapping: 'eth'/'ethereum' → Ethereum, 'base' → Base, 'sol'/'solana' → Solana
```

If detected chain is **Stellar** or **XRP**, include under prize > $5K exception (not in primary chain set).