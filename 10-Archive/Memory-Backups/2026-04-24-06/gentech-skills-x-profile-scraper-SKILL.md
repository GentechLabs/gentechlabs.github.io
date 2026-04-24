---
name: x-profile-scraper
description: Extract X/Twitter profile data without authentication by parsing the __INITIAL_STATE__ JSON embedded in page HTML. Fallback for when xurl CLI is unavailable. Includes cross-platform intel gathering via GitHub, AllMyLinks, and other linked profiles.
category: social-media
---

# X Profile Scraper (No Auth)

When `xurl` is not installed or authenticated, public X profiles can be read by scraping the HTML. X embeds user data in a `window.__INITIAL_STATE__` JSON blob.

## When to Use
- xurl CLI is not available and cannot be installed
- Quick profile/bio lookup without full API setup
- Checking a public pinned tweet or bio links
- Gathering intel before deciding whether to set up xurl

## Method: curl + grep

Fetch a profile and extract key fields:

```bash
curl -s "https://x.com/USERNAME" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -L 2>&1 | grep -oP '"screen_name":"[^"]*"'
```

## Method: Full JSON extraction

The HTML contains `window.__INITIAL_STATE__=` followed by a large JSON object. Extract with Python:

```python
import json, re

# html = result from curl call
match = re.search(r'window\.__INITIAL_STATE__=({.*?});', html, re.DOTALL)
state = json.loads(match.group(1))
users = state["entities"]["users"]["entities"]
```

## Readable Fields
- `name`, `screen_name`, `description` (bio)
- `location`, `followers_count`, `friends_count`, `statuses_count`
- `favourites_count`, `media_count`, `created_at`
- `pinned_tweet_ids_str`, `profile_image_url_https`
- `entities.url.urls` (links in bio)

## View a Public Tweet
Use `browser_navigate` to `https://x.com/USERNAME/status/TWEET_ID` — public tweets render in the accessibility snapshot without login. The page title contains the tweet text.

## Extended Intel Gathering (Cross-Platform Fallback)

When X tweets are inaccessible (login wall, rate limits, CAPTCHAs), cross-reference linked platforms for richer intel:

### 1. Extract Bio Links → Follow Them
The `__INITIAL_STATE__` JSON contains `entities.url.urls` (bio links). Also check for link-in-bio services like `allmylinks.com/USERNAME` — these aggregate all platform links.

### 2. GitHub Profile (Often Most Valuable)
```bash
# Browser snapshot of repos sorted by recent activity
browser_navigate("https://github.com/USERNAME?tab=repositories&type=updated")
```
**What to extract:** recent repo names, descriptions, languages, update timestamps, fork sources, topics/tags. This reveals:
- What they're actively building (commit recency)
- Tech stack (Solidity, TypeScript, etc.)
- Hackathon participation (ETHGlobal, Solana Superteam, etc.)
- Collaboration signals (forking related repos)

### 3. Cross-Reference Other Platforms
- **YouTube** (`youtube.com/@USERNAME`) — channel content, recent uploads
- **AllMyLinks/Linktree** — full platform map
- **LinkedIn** — professional context
- **GitHub Stars** (`github.com/USERNAME?tab=stars`) — what they follow/curate

### 4. Compile Intel Report
Combine findings into a structured brief: profile stats, recent activity, tech focus, engagement level, collaboration potential.

## Limitations
- No search capability (requires auth)
- Cannot read private/protected accounts
- Rate-limited by X's anti-bot systems
- HTML structure may change — grep patterns are fragile
- No write actions (post, like, repost, DM)
- X login wall blocks tweet content without auth (xurl or browser session needed)
- Search engines (Google, Bing, DuckDuckGo) frequently CAPTCHA headless browsers
