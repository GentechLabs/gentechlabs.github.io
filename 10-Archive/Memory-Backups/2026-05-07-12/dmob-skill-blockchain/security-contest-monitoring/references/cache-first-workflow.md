# Cache-First Scanner Workflow — Session 2026-05-02

## Principle
When live platform endpoints are flaky or restructuring (C4 push segments gone, Cantina requires Playwright), **use validated cached data** for daily scans and fall back to live fetch only when cache miss.

## Cache Directory Structure
```
02-Labs/Contest-Scans/
├── c4_cached.json          # Code4rena active contests (validated list)
├── cantina_cached.json     # Cantina qualifying competitions
├── devpost_cached.json     # Devpost hackathons (IGNITION, Agents Assemble)
├── colosseum_cached.json   # Colosseum Frontier note (until PAT refreshed)
├── c4_raw_YYYY-MM-DD.html  # Optional: raw HTML for future parser updates
├── devpost_YYYY-MM-DD.json # Optional: raw API response
└── summary_YYYY-MM-DD.md   # Human-readable daily summary
```

## Cache Format (per file)
Each `_cached.json` contains a **list of contest objects**:
```json
[
  {
    "platform": "Code4rena",
    "name": "K2",
    "prize": "$135,000 USDC",
    "days_left": 999,          // placeholder; compute from deadline at read time
    "deadline": "2026-08-01",
    "chain": "Stellar",
    "link": "https://code4rena.com/contests/2026-04-k2"
  }
]
```

## Loader Pattern
```python
def load_cache(key):
    p = SCAN_DIR / f"{key}_cached.json"
    if p.exists():
        try: return json.loads(p.read_text())
        except: return []
    return []

def scan():
    all = []
    all.extend(load_cache("c4"))
    all.extend(load_cache("cantina"))
    all.extend(load_cache("devpost"))
    all.extend(load_cache("colosseum"))

    # Recompute days_left from deadline if cached as 999
    for c in all:
        if c.get("days_left",999) == 999 and c.get("deadline"):
            c["days_left"] = days_left(c["deadline"])

    # Dedupe by (platform,name), sort, output
    ...
```

## Refresh Policy
- **Manual refresh:** After each manual deep-scan of a platform, overwrite the corresponding `_cached.json`.
- **Automatic fallback:** If live fetch fails (HTTP error, parse error), scanner automatically uses cache.
- **Staleness guard:** Log warning if cache > 7 days old; consider manual rescan.

## Rationale (from session)
- C4: Push segment decoder broke after site update; HTML card parsing works but not yet robust → use manual validated cache until parser fixed.
- Cantina: Playwright rendering costs ~3s per scan; cached Reserve Governor entry sufficient for daily monitoring until new contests appear.
- Devpost: API works consistently; still cache to reduce network calls.
- Colosseum: Arena requires login; Copilot API needs valid PAT → cache Frontier note until PAT regenerated.

## Next Actions
1. Fix C4 HTML parser to auto-detect card structure changes (weekly validation of `c4_raw_*.html`)
2. Add Playwright-based Cantina scrape to automatically refresh cache when new competition count changes
3. Implement PAT auto-refresh check: call `/status` before scan; if `authenticated:false`, alert and skip Colosseum live fetch

## References
- Main scanner: `02-Labs/scripts/opportunity_scanner_daily.py`
- Sprint plan context: `02-Labs/sprint-plan-solana-frontier-kite-ai.md`
- Daily logs: `02-Labs/Contest-Scans/scan_*.log`
