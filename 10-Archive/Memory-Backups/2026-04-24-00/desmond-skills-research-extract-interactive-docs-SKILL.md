---
name: extract-interactive-docs
description: Extract meaningful text from interactive documentation pages (SPAs, terminal demos, heavy formatting) that resist standard scraping.
trigger: When web_extract fails or browser snapshot is dominated by interactive elements, terminal output, or decorative characters.
---

# Extract Text From Interactive Documentation Pages

Use this when standard scraping fails and browser snapshots are noisy with terminal output, box-drawing characters, or interactive widgets.

## Problem
Some developer docs (Gemini, Vercel, etc.) render interactive terminals and demos that consume most of the visible text. Standard `web_extract` may fail (auth errors), and `browser_snapshot` returns cluttered accessibility trees.

## Strategy

### Step 1: Try web_extract first
```python
web_extract(urls=[url])
```
If it works → done. If AUTH_ERROR or empty → proceed.

### Step 2: Browser navigate + scroll
```python
browser_navigate(url=url)
# Click any relevant section anchor if available
browser_click(ref=section_ref)
browser_scroll(direction="down")
```

### Step 3: Console extraction — the key trick
Use `browser_console` with JavaScript to extract meaningful lines:
```javascript
(() => {
    const body = document.body.innerText;
    const lines = body.split('\n');
    const meaningful = lines.filter(l => {
        const trimmed = l.trim();
        return trimmed.length > 20 && !/^[┌─┬┐│├┼┤└┴┘❯\s]+$/.test(trimmed);
    });
    return [...new Set(meaningful)].slice(0, 80).join('\n');
})()
```

### Step 4: If section-specific content needed
Find a unique string marker (e.g., "MCP server", "Agentic") and extract surrounding text:
```javascript
(() => {
    const body = document.body.innerText;
    const idx = body.indexOf('MARKER_STRING');
    if (idx > -1) {
        let text = body.substring(idx, idx + 3000);
        text = text.replace(/[┌─┬┐│├┼┤└┴┘]/g, '');  // Remove box-drawing
        text = text.replace(/[ \t]+/g, ' ');          // Collapse spaces
        text = text.replace(/\n\s*\n\s*\n/g, '\n\n'); // Collapse blank lines
        return text.trim();
    }
    return "not found";
})()
```

### Step 5: Get links for navigation
If the page has sub-sections in nav:
```javascript
(() => {
    const links = Array.from(document.querySelectorAll('a'));
    return links.filter(a => {
        const href = a.getAttribute('href') || '';
        return href.includes('target_keyword');
    }).map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href') }));
})()
```

## Pitfalls
- Terminal output with box-drawing chars (┌─┬┐│) makes up 90%+ of visible text on some pages
- `browser_snapshot(full=true)` may still truncate — console extraction gets more
- Removing duplicates (`[...new Set()]`) is important when the same text appears in sidebar + main
- Some pages render content lazily — scroll first, then extract
