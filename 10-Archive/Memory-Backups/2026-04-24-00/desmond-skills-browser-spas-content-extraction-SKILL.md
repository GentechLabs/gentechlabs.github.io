---
name: browser-spas-content-extraction
description: Extract readable content from JS-rendered SPA docs when browser_snapshot only returns navigation shells
triggers: browser_snapshot shows sidebar nav but not page content, JS-rendered documentation sites, SPAs with dynamic content loading
category: browser
---

# Extracting Content from JS-Rendered SPAs

## Problem
Some documentation sites (especially SPAs built with React, Next.js, Mintlify, etc.) render content dynamically. When using `browser_snapshot`, you only see the navigation sidebar — the main article content is missing from the accessibility tree.

## Solution
Use `browser_console` with DOM selectors to extract the rendered text directly.

### Step 1: Try browser_snapshot first
Always start with normal `browser_snapshot(full=true)` — most sites work fine.

### Step 2: If content is missing, use browser_console
```javascript
// Try these selectors in order:
document.querySelector('article')?.innerText
document.querySelector('main')?.innerText
document.querySelector('[class*="content"]')?.innerText
document.body.innerText.substring(0, 10000)  // fallback
```

### Step 3: Browser vision as fallback
If console extraction fails (e.g., content is in iframes or shadow DOM), use `browser_vision` with a specific question to get an AI-readable summary.

## Known Working Sites
- **Mintlify docs** (docs.genlayer.com): `document.querySelector('article')?.innerText` works
- Most docs sites using `article` or `main` semantic elements

## Pitfalls
- `browser_snapshot` truncates at ~8000 chars — use `browser_console` for full content
- `web_extract` may be rate-limited on docs sites — browser bypasses this
- Always navigate first with `browser_navigate` before calling `browser_console`
- If content is paginated, you may need to scroll then re-extract
