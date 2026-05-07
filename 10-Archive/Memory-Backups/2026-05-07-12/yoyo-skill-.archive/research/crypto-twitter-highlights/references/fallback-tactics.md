# Crypto Twitter Fallback Tactics — Session Notes

**Date:** 2026-05-03  
**Context:** xurl unauthenticated; browser_navigate unavailable → needed curl-based scraping fallback

## Tool Availability Matrix

| Tool | Status | Notes |
|------|--------|-------|
| `xurl` | Present, no auth | `auth status` → "No apps registered"; requires manual `oauth2` setup |
| `browser_navigate` | Unusable | `/usr/bin/env: 'node': No such file or directory` — node/npm missing |
| `web_search` | Unusable | FIRECRAWL_API_KEY not configured (all queries failed) |
| `curl` | Available | Used successfully for GitHub API calls + site scrapes |

## Workflow Sequence (Working)

### 1. Check xurl authentication first
```bash
xurl auth status
# If "No apps registered" → skip Approach A
```

### 2. Probe browser_navigate availability
```bash
which node || echo "node missing → skip Approach B"
# If node missing, use curl fallback (Approach C)
```

### 3. Curl-based scraping (Approach C)
```bash
# Generic pattern
curl -s -L "<URL>" -A "Mozilla/5.0 (compatible; Gentech-Intel)" \
  | grep -oP '(?<=<h[1-3][^>]*>).*?(?=</h[1-3]>)' \
  | grep -i "agent\|escrow\|ai\|crypto\|hackathon"
```

**Sites tested:**
- `https://www.coindesk.com/` → returns HTML (headlines extractable)
- `https://thedefiant.io/` → returns HTML (headlines extractable)  
- `https://cointelegraph.com/` → blocked/redirected (unreliable)

**Headline regex:** `<h[1-3][^>]*>.*?</h[1-3]>` captures most news headlines.

### 4. GitHub API for target-specific intelligence
When specific developer handles known (e.g., `@ProtoJay4789` → GitHub `ProtoJay4789`):

```bash
# User profile
curl -s "https://api.github.com/users/ProtoJay4789" \
  | jq '{login, bio, public_repos, html_url}'

# Recent repositories
curl -s "https://api.github.com/users/ProtoJay4789/repos?sort=updated&per_page=10" \
  | jq '.[] | {name, description, pushed_at, html_url}'

# Search code for mentions
curl -s "https://api.github.com/search/code?q=user:ProtoJay4789+agent+commerce" \
  | jq '.items[].html_url'
```

**GitHub → Twitter correlation:** Devs often announce on Twitter after repo updates. Monitor `pushed_at` for recent activity; cross-reference with X handle.

## Error Encounters

| Error | Root Cause | Fix |
|-------|------------|-----|
| `Error: unknown flag: --json` (xurl) | Version doesn't support JSON output flag | Use plain text output; avoid JSON parsing |
| `Unauthorized` (xurl search) | OAuth not configured | Requires user intervention: `xurl auth oauth2` |
| `No such file or directory: node` (browser_navigate) | Node/npm not installed | Use curl fallback (Approach C) |
| `FIRECRAWL_API_KEY not configured` (web_search) | Missing env var | Skip web_search; use direct curl calls |

## Output Format Template

```
=== CRYPTO TWITTER INTELLIGENCE ===
Date: YYYY-MM-DD
Direct X API: [AUTH REQUIRED] / Available

1. TARGET ACTIVITY (e.g., ProtoJay4789)
   - GitHub: login, public_repos
   - Recent repos: name (pushed date) — description
   - Relevant projects: list

2. HEADLINE TRENDS (scraped)
   [Source] Headline text
   → Relevant snippet

3. CONTENT OPPORTUNITIES
   - Collaboration topic
   - Content angle / hook
   - Thread seed idea

4. RECOMMENDED NEXT STEPS
   - Enable xurl auth
   - Monitor specific repo
   - Reach-out opportunity (who/why)
```

## Quick Reference Commands

```bash
# Toolchain status
which xurl && xurl auth status
which node && which browser_navigate
echo $FIRECRAWL_API_KEY

# ProtoJay GitHub summary
curl -s https://api.github.com/users/ProtoJay4789 | jq '{login, bio, repos: .public_repos}'
curl -s "https://api.github.com/users/ProtoJay4789/repos?sort=pushed&per_page=5" \
  | jq -r '.[] | "\(.name) (\(.pushed_at[0:10]\)): \(.description // "N/A" | .[0:70])"'

# Scrape headlines + filter
curl -s -L "https://www.coindesk.com/" -A "Mozilla/5.0" \
  | grep -oP '(?<=<h[2][^>]*>).*?(?=</h[2]>)' \
  | head -10 | sed 's/<[^>]*>//g'
```