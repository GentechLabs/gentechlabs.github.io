---
name: web-research-fallback
description: Fallback chain for web research when APIs and search engines fail due to auth errors or CAPTCHAs.
tags: [research, browser, fallback, news-monitoring]
---

# Web Research Fallback Chain

Use this when `web_search` returns Unauthorized and `web_extract` can't scrape pages.

## Step-by-Step Fallback

### 1. Try direct URL extraction
If you know the likely URL pattern (e.g. `bbc.co.uk/news/articles/...`), try `web_extract` first.

### 2. Try search engines via browser
- Navigate to `https://duckduckgo.com/?q=SEARCH+TERMS`
- If DDG hits CAPTCHA, try Google
- If both blocked, skip to step 3

### 3. Go to the target site's own search (RELIABLE)
Most major news sites have their own search that works without CAPTCHAs:

**BBC:**
```
https://www.bbc.co.uk/search?q=SEARCH+TERMS&d=NEWS_PS
```
Returns structured results with titles, URLs, descriptions, and publish dates.

**Other sites:** Look for `/search?q=` or site-specific search endpoints.

### 4. Read article via browser
- `browser_navigate` to the article URL
- Dismiss cookie/sign-in dialogs (look for "Maybe later", "Reject additional cookies")
- `browser_snapshot(full=true)` to get full content
- `browser_scroll` + re-snapshot for long articles

### 5. Set up monitoring (for ongoing stories)
Use `cronjob` to track breaking stories:
```
Schedule: 0 */6 * * * (every 6 hours)
Prompt: Search [site] for updates on [topic], report new developments only
```

## Pitfalls
- Google and DuckDuckGo often CAPTCHA headless browsers — don't waste time on them
- `web_extract` has auth issues with many sites — browser is more reliable
- BBC search returns truncated snapshots — scroll and re-snapshot for full article
- Always dismiss overlays before reading content
