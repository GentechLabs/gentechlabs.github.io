---
name: crypto-twitter-highlights
description: Aggregate crypto/tech Twitter highlights from news sources when direct X API access is unavailable. For weekly/daily content inspiration runs.
version: 1.0.0
---

# Crypto Twitter Highlights Aggregator

Collect trending crypto and tech content relevant to Gentech's focus areas: DeFi, smart contracts, hackathons, AI agents.

## Prerequisites Check

Before running, verify what's available:

```bash
xurl --help      # X/Twitter CLI (preferred)
xurl auth status # Must show authenticated app
```

If `xurl` is installed and authenticated, use direct Twitter search (see Approach A).
If not, fall back to news aggregator scraping (Approach B).

---

## Approach A: Direct X/Twitter Search (preferred)

```bash
# Search per topic area
xurl search "DeFi hack exploit" -n 10
xurl search "AI agent crypto" -n 10
xurl search "smart contract audit" -n 10
xurl search "hackathon web3" -n 10
xurl search "tokenization RWA" -n 10

# Check specific accounts
xurl user @TheDeFiant
xurl user @CoinDesk
xurl search "from:DefiantNews" -n 5
```

Parse JSON output, extract tweet text + URLs, deduplicate by conversation_id.

## Approach B: Browser Fallback (when xurl unavailable)

Use `browser_navigate` to scrape crypto news sites that curate Twitter content:

**Priority order (tested working):**
1. `https://www.coindesk.com/` — main page has latest news with sentiment tags
2. `https://www.coindesk.com/tag/defi/` — DeFi-specific
3. `https://www.coindesk.com/tag/ai/` — AI + crypto intersection
4. `https://www.coindesk.com/tag/hackathon/` — hackathon/builder content
5. `https://thedefiant.io/` — DeFi-focused, good headlines
6. `https://cointelegraph.com/` — broad crypto (may be blocked)

**What to extract per article:**
- Headline + subheading
- Sentiment tag (Positive/Negative/Neutral) if available
- Timestamp
- URL for sourcing

**Avoid:**
- `nitter.*` instances — consistently 403 blocked
- `x.com/search` — requires login redirect
- `web_search` in rapid succession — rate limits hit quickly (max ~10 queries)

## Content Organization

Save to `04-Entertainment/crypto-tech-twitter-highlights-YYYY-MM-DD.md` with sections:
1. Top Story (biggest DeFi/hack event)
2. AI Agents & Trading
3. Smart Contracts & Tokenization
4. Hackathon / Builder Scene
5. Market Context (prices, fund flows)
6. Content Inspiration Angles (5 suggested hooks)

## Pitfalls

- **Rate limits:** `web_search` and `web_extract` share a quota. Space calls 90s+ apart or use browser instead.
- **CoinDesk paywall:** Free tier allows ~2 articles/month. Workaround: read headlines + subheadings from listing pages (no wall).
- **The Defiant:** Full content behind premium, but headlines are descriptive enough.
- **xurl setup:** User must run `xurl auth oauth2` manually (involves browser OAuth flow). Agent cannot do this.
- **Stale content:** Always check timestamps. Cron runs should filter to last 24-48h.
