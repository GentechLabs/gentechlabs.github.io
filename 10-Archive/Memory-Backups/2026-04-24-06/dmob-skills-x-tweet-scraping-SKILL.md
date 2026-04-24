---
name: x-tweet-scraping
description: Scrape X/Twitter posts and long web pages without authentication using browser tools. Includes paginated extraction for long docs when web_extract/web_search hit rate limits.
category: social-media
---

# X/Twitter Post Scraping (No Auth)

Use when you need to read a tweet's content but don't have X/Twitter auth configured.

## Workflow

### Step 1: Try web_extract first (usually fails)
```python
web_extract(urls=["https://x.com/i/status/XXXXXXXXX"])
# Expect: Unauthorized error
```

### Step 2: Fall back to browser_navigate
```python
browser_navigate(url="https://x.com/i/status/XXXXXXXXX")
# Returns snapshot with interactive elements + ref IDs
```

### Step 3: If snapshot is truncated, use browser_console
The snapshot often truncates long threads. Use JS to extract the full article text:
```python
browser_console(expression="document.querySelector('article')?.innerText || 'not found'")
```

### Step 4: For full page content, scroll + re-snapshot
```python
browser_scroll(direction="down")
browser_snapshot(full=true)
```

### Step 5: For visual context, use browser_vision
```python
browser_vision(question="What is shown in this tweet?")
```

## Long Page Extraction (GitHub READMEs, Docs)

For long pages (GitHub repos, docs sites) where the snapshot is truncated:

### Paginated browser_console extraction
Extract content in chunks using `substring()` to avoid hitting output limits:
```python
# First chunk (0-3000 chars)
browser_console(expression="document.querySelector('article')?.innerText?.substring(0, 3000) || 'not found'")

# Second chunk (2000-5000 chars — overlap for context continuity)
browser_console(expression="document.querySelector('article')?.innerText?.substring(2000, 5000) || 'not found'")

# For README sections, target specific containers
browser_console(expression="document.querySelector('[class*=\"readme\"]')?.innerText?.substring(0, 3000) || 'not found'")
```

### When web_extract AND web_search both hit rate limits
Browser tools become the only option. This happened 5x in one session when rate-limited:
1. `web_extract` → rate limit error
2. `web_search` → rate limit error
3. Fall back to `browser_navigate` → snapshot → `browser_console` for content
4. Works for any URL (GitHub READMEs, docs, blogs), not just X/Twitter

### GitHub repo discovery
When you don't know the exact repo URL, navigate to the org page and search:
```python
browser_navigate(url="https://github.com/OpenZeppelin?q=contracts-cli&type=repositories")
```

## Pitfalls
- **Login walls:** X shows a "Log in" prompt — you can still read the main tweet but not replies or thread continuations
- **Image-only tweets:** Text extraction misses images — use `browser_get_images` then `vision_analyze` on individual image URLs
- **Rate limiting:** Too many rapid browser_navigate calls may trigger bot detection
- **Thread depth:** Can only see the root tweet without auth, not full threads

## What you get without auth
- ✅ Tweet text content
- ✅ Engagement metrics (replies, reposts, likes, bookmarks, views)
- ✅ Quoted tweets (partial)
- ✅ Images (URLs only)
- ❌ Replies / thread
- ❌ Full conversation context
- ❌ DM-protected accounts
