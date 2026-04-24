---
name: extract-x-twitter
description: Extract content from X/Twitter posts when web scraping fails — browser console JS evaluation fallback for bot-detected pages.
category: research
---

# Extract Content from X/Twitter Posts

## When to Use
When the user shares an X/Twitter link and you need to extract the post content, replies, or quoted tweets.

## Problem
- `web_extract` fails with `AUTH_ERROR` — X blocks scraping
- `browser_snapshot` returns truncated content or login gates
- Box-drawing characters from terminal UIs clutter the text

## Solution

### Step 1: Navigate with browser
```python
browser_navigate(url="https://x.com/i/status/POST_ID")
```

### Step 2: Accept cookies if prompted
Click `@e4` ("Accept all cookies") to dismiss the cookie banner.

### Step 3: Extract post content via JS console
The most reliable method is `browser_console` with JS evaluation:

```python
browser_console(expression="""(() => {
    const body = document.body.innerText;
    const lines = body.split('\\n').filter(l => l.trim().length > 0);
    const meaningful = lines.filter(l => {
        const trimmed = l.trim();
        return trimmed.length > 20 && !/^[┌─┬┐│├┼┤└┴┘❯\\s]+$/.test(trimmed);
    });
    return [...new Set(meaningful)].slice(0, 40).join('\\n');
})()""")
```

### Step 4: For specific sections
Target known text anchors to extract focused content:
```python
browser_console(expression="""(() => {
    const body = document.body.innerText;
    const idx = body.indexOf('SECTION_HEADER');
    if (idx > -1) {
        let text = body.substring(idx, idx + 3000);
        text = text.replace(/[\\t]+/g, ' ');
        text = text.replace(/\\n\\s*\\n\\s*\\n/g, '\\n\\n');
        return text.trim();
    }
    return "section not found";
})()""")
```

### Step 5: For replies/threads
Click the replies button, then extract again. Note: replies often require login — if a login dialog appears, close it and note that replies are unavailable.

### Step 6: Scroll for longer content
If the post is long, use `browser_scroll(direction="down")` then re-extract with JS.

## Pitfalls
- **Bot detection**: X runs WITHOUT residential proxies by default. Login-gated content may not be accessible.
- **Rate limiting**: `web_search` has tight rate limits. Use `browser_console` as fallback.
- **Image content**: Post images contain text not in the DOM. Use `browser_vision` to analyze attached images.
- **SPA rendering**: X is a SPA — DOM state changes on scroll/interaction. Re-extract after any navigation action.

## Output Format
Always provide:
- Author handle + display name
- Post date
- Engagement metrics (views, likes, reposts, bookmarks)
- Full post text (or translation if non-English)
- Any quoted tweets or attached media description
