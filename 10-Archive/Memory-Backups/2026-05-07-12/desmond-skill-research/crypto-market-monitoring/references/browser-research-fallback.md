# Browser Research Fallback Patterns

## When Search Engines Are All Blocked

Discovered May 5, 2026 during RWA sector research. All three major search backends failed:
- **Google**: CAPTCHA on any query (not just News)
- **Bing**: Cloudflare challenge iframe on general search
- **DuckDuckGo API**: Empty results for complex crypto queries

## Reliable Fallback: Direct Website Visiting

When search fails, go directly to known project websites. This is slower but deterministic.

### Crypto Project Research Starting Points
| Source | URL Pattern | What You Get |
|--------|-------------|--------------|
| Project homepage | `https://<project>.io` or `.finance` | Value prop, TVL, product list, chain support |
| DeFiLlama | `https://defillama.com/protocol/<name>` | TVL history, chain breakdown (may have Cloudflare) |
| DexScreener | `https://dexscreener.com/<chain>/<address>` | Token price, pool data, trading volume |
| X/Twitter | `https://x.com/<handle>` | Recent activity, community engagement, shutdown signals |
| CoinGecko | `https://coingecko.com/en/coins/<id>` | Market cap, price history, exchange listings |
| Docs/GitBook | `https://docs.<project>.io` | Technical details, tokenomics, supported chains |

### Research Workflow (No Search)
1. Start with known project names from memory or prior context
2. Visit each project's homepage — extract: TVL, chains, products, status signals
3. Check X/Twitter for recent activity (engagement levels indicate project health)
4. Cross-reference on DeFiLlama or CoinGecko for quantitative data
5. Compile findings into structured report

### Health Signals to Watch
- **Dead blog** (no posts in 3+ months) → project may be winding down
- **Low tweet engagement** (views <1% of follower count) → community has left
- **Website still up but no recent updates** → possible zombie project
- **Partnership announcements with big names** → legitimate signal (e.g., Ondo + Binance, Centrifuge + Monad)

### Telegram Report Format
When posting research to Strategies group, use this structure:
```
[Topic] — [Scope] — [Date]

## Context
[Why this research was requested]

## ✅ Active & Strong
[Project 1, 2, 3 with key metrics]

## ⚠️ Uncertain / Winding Down
[Fading projects]

## 🔍 Worth Watching
[Emerging or adjacent]

## 💡 Takeaway
[Actionable summary with "if Jordan wants X → do Y" structure]
```
