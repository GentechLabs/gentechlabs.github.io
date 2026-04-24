---
name: web-research-browser-fallback
category: research
description: Use browser automation as fallback when web_search and web_extract fail
triggers:
  - web_search returns AUTH_ERROR
  - web_extract rate limited or blocked
  - Search engines CAPTCHA-block headless browser
  - Documentation site research needed
---

# Web Research With Browser Fallback

When standard web tools fail, use browser automation as fallback for research tasks.

## Steps

### 1. Try Standard Tools First
- `web_search(query)` for quick lookup
- `web_extract(urls)` for direct page content

### 2. If Blocked, Parallelize Browser Exploration
When search tools fail, don't guess the right URL — try multiple candidates simultaneously:
- `browser_navigate` to 2-3 likely URLs (docs.site.com, site.com/developers, github.com/org)
- Check snapshots to identify which is the real product vs competitors with similar names
- Example: "Beams SDK" returned TWO products — Teleport Beams (beams.sh) vs Beam blockchain (onbeam.com)

### 3. Extract Page Content With JavaScript
Browser snapshots of documentation sites typically only return **sidebar navigation**, not article content. Use `browser_console` to extract actual text:

```javascript
// Get article content
document.querySelector('article')?.innerText

// Fallback to main
document.querySelector('main')?.innerText

// Last resort
document.body.innerText.substring(0, 5000)
```

This returns the readable page content that snapshots miss.

### 4. Combine Sources
- Use browser snapshots for navigation structure (what sections exist)
- Use browser_console for actual content (what each section says)
- Use browser_navigate to follow links found in navigation

## Pitfalls
- Google/DuckDuckGo frequently CAPTCHA-block headless browsers — skip search engines, go direct to URLs
- web_extract has rate limits (10 requests/period) — budget your calls
- Browser navigation is slower than web_extract — use it as fallback, not first choice
- Some sites block private/internal network addresses in web_extract but work in browser
- `browser_snapshot(full=true)` still may not capture article content — always try browser_console too
- Rate limits reset — check `retryAfter` value in error response before retrying web_extract

## Example Flow: Researching "Beams SDK"
1. web_search → AUTH_ERROR
2. web_extract → rate limited
3. browser Google → CAPTCHA
4. browser DuckDuckGo → CAPTCHA  
5. browser_navigate("beams.sh") → Teleport Beams (wrong product)
6. browser_navigate("onbeam.com") → Beam blockchain (correct!)
7. browser_navigate("onbeam.com/developers") → found SDK link
8. browser_navigate("docs.onbeam.com/sdk") → navigation only in snapshot
9. browser_console(article.innerText) → got full SDK docs ✅
