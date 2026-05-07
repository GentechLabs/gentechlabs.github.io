# GitHub API Rate Limit Bypass Techniques

## Problem
Unauthenticated GitHub API has very low rate limits (~10-60 requests/hour). Authenticated requests require a token that may not be available in all contexts (cron jobs, agent sessions). During extensive protocol research you will exhaust the quota quickly.

## Bypass Hierarchy

### Tier 1: raw.githubusercontent.com (Preferred)
For README, package.json, and other source file content, bypass the API entirely:

```bash
# Instead of (API-limited):
curl "https://api.github.com/repos/x402-foundation/x402/contents/README.md"

# Use (no rate limit, same content):
curl "https://raw.githubusercontent.com/x402-foundation/x402/main/README.md"
```

**Applicable files:** `*.md`, `package.json`, `tsconfig.json`, `.env.example`, source code files (`.ts`, `.sol`, `.py`, `.go`).

**Caveat:** You cannot get directory listings this way; only direct file content.

### Tier 2: HTML scraping (for human-readable data)
For GitHub Pages, README previews, advisory details:

```bash
# Fetch full advisory instead of sparse API JSON
curl -s "https://github.com/x402-foundation/x402/security/advisories/GHSA-qr2g-p6q7-w82m" \
  | grep -A50 'Description' \
  | sed 's/<[^>]*>//g'  # strip HTML tags
```

### Tier 3: Search API with careful query scoping
If you must use search, restrict to minimal result sets and prioritize critical queries first:

```bash
# Get only 1 result to preserve quota
curl -s "https://api.github.com/search/repositories?q=x402+protocol&per_page=1"
```

### Tier 4: Accept partial data and switch domains
When 403 (rate limit) or 404 occurs:
1. Log the hit as a data gap
2. Switch to alternative source (npm, docs site, ecosystem page)
3. Do NOT retry the same endpoint in same session

## x402 Session Pattern
During x402 research we encountered 403s on:
- `api.github.com/repos/x402-foundation/x402/contents/...` → switched to raw.githubusercontent.com
- `api.github.com/repos/.../security-advisories` (HTML page accessible, rich details)
- `api.github.com/search/code` → 401 even with minimal auth; we fell back to ecosystem page data extraction

## Monitoring Your Quota
```bash
# Check remaining requests (authenticated)
curl -I -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit | jq '.rate.remaining'
```

Unauthenticated requests share IP-level quota; if one agent exhausts it, all agents on same IP are blocked until reset (~1 hour).

## Best Practice
**Default to raw.githubusercontent.com for all file content needs.** Reserve API calls for:
- Repository metadata (stars, description, pushed_at)
- Issues/PR enumeration
- Release listings
- Security advisory API (when HTML scraping is insufficient)

Keep a local "quota budget" — each research session should budget ~20 API calls max, use raw for everything else.
