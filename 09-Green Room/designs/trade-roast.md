# TradeRoast — AI Trading Performance Roaster

**Date:** 2026-05-28
**Status:** 🟡 Draft
**Working Token:** $ROAST

## Problem

Most crypto traders have no idea how bad (or good) they actually are. They check their portfolio balance but never analyze their behavior. The data exists (on-chain transactions) but nobody's making it fun to consume.

## Proposed Solution

Connect your wallet → AI scans your trade history → roasts your performance → generates a shareable card. Token-gated premium roasts for $ROAST holders.

## Why It Works

- **Viral by nature** — people share their losses more than wins ("look how dumb I was")
- **Social proof disguised as entertainment** — every share = free marketing
- **pump.fun native** — rewards virality, not utility
- **AAE integration** — the roast layer we already discussed for bad trades becomes standalone

## Multichain Architecture

### Layer 0 — Chain-Agnostic Core (Python)
```
trade_roast/
├── core/
│   ├── analyzer.py          # Performance calculation
│   ├── roast_engine.py      # AI roast generation
│   ├── card_renderer.py     # Shareable card generation
│   └── models.py            # TradeMetrics, RoastResult
```

### Layer 1 — Chain Adapters
```
trade_roast/
├── chains/
│   ├── solana/
│   │   ├── client.py        # Solana RPC + Helius
│   │   ├── parser.py        # Transaction parsing
│   │   └── jupiter.py       # DEX swap detection
│   ├── base/
│   │   ├── client.py        # Base RPC
│   │   └── parser.py        # Uniswap/Base swap parsing
│   └── evm/
│       ├── client.py        # Generic ethers.js wrapper
│       └── parser.py        # EVM transaction parsing
```

### Layer 2 — API + Frontend
```
trade_roast/
├── api/
│   ├── server.py            # FastAPI
│   ├── routes/
│   │   ├── roast.py         # POST /roast — generate roast
│   │   ├── card.py          # GET /card/:id — render card
│   │   └── health.py        # GET /health
│   └── middleware/
│       └── rate_limit.py    # Free tier limiting
├── web/
│   ├── index.html           # Landing page
│   ├── roast.html           # Roast result page
│   └── card.html            # Shareable card view
```

## Core Data Models

```python
@dataclass
class TradeMetrics:
    # Volume & Activity
    total_trades: int
    total_volume_usd: float
    first_trade_date: datetime
    last_trade_date: datetime
    
    # Performance
    win_rate: float              # % profitable trades
    total_pnl_usd: float         # Net profit/loss
    roi_percentage: float        # Return on investment
    sharpe_ratio: float          # Risk-adjusted return
    
    # Behavior
    avg_hold_time_hours: float   # Average position duration
    biggest_win_usd: float
    biggest_loss_usd: float
    biggest_win_pct: float
    biggest_loss_pct: float
    
    # Red Flags (roast fuel)
    buy_high_sell_low_count: int # Times bought > sold
    rug_count: int               # Tokens that went to 0
    overleveraged_count: int     # Liquidated positions
    fomo_buys: int               # Bought after 100%+ pump
    panic_sells: int             # Sold after 50%+ drop
    
    # Green Flags (sarcastic roast fuel)
    diamond_hands_count: int     # Held through volatility
    perfect_timings: int         # Bought near bottom, sold near top
    
    # Token Diversity
    unique_tokens: int
    most_traded_token: str
    least_profitable_token: str
    most_profitable_token: str

@dataclass
class RoastResult:
    metrics: TradeMetrics
    roast_text: str              # The actual roast
    severity: str                # "mild", "medium", "brutal"
    shareable_card_url: str      # Link to rendered card
    token: str                   # Chain detected
```

## Roast Severity Levels

### 🟢 Mild (Win Rate > 60%, Positive PnL)
> "You're actually profitable? Did you forget to connect your real wallet?"
> "Your win rate is better than a coin flip. Barely."
> "You might know what you're doing. Don't tell anyone."

### 🟡 Medium (Win Rate 40-60%, Break-even)
> "Your win rate is 52%. A slot machine would be more exciting."
> "You broke even. Congrats, you invented a really expensive hobby."
> "You're basically a high-frequency donation machine to market makers."

### 🔴 Brutal (Win Rate < 40%, Negative PnL)
> "You bought high and sold low 47 times. That's not trading, that's charity with extra steps."
> "Your portfolio looks like a crime scene. Red everywhere."
> "You lost money in a bull market. That takes genuine talent."
> "You've been rugged more times than a toddler learning to walk."
> "Your biggest win was selling before it went to zero. That's not skill, that's luck."

### 🟣 Special Categories
**The Diamond Hand (held too long)**
> "You held a token from ATH to -90%. That's not diamond hands, that's denial."

**The Paper Hand (sold too early)**
> "You sold a 10x at 2x. Your future self is writing you a hate letter."

**The FOMO King**
> "You bought every top. Every single one. It's almost impressive."

**The Rug Magnet**
> "You've been rugged 12 times. At this point, check if YOU'RE the honeypot."

**The Zero Trader**
> "You have zero profitable trades. Zero. The universe is trying to tell you something."

## AI Roast Generation

### Prompt Template
```python
ROAST_SYSTEM_PROMPT = """You are a savage crypto trading roaster. 
Analyze the trader's metrics and deliver a personalized roast.
Be funny, be brutal, but don't be mean-spirited.
The goal is entertainment, not depression.
Use crypto slang naturally (rekt, diamond hands, paper hands, ape, etc.)
Keep it under 200 words.
Format: 3-4 paragraphs with the best line first."""

ROAST_USER_TEMPLATE = """Roast this crypto trader:

Win Rate: {win_rate}%
Total PnL: ${total_pnl:,.2f}
ROI: {roi}%
Total Trades: {total_trades}
Biggest Win: ${biggest_win:,.2f} ({biggest_win_pct}%)
Biggest Loss: ${biggest_loss:,.2f} ({biggest_loss_pct}%)
Buy High/Sell Low Count: {bhsl_count}
Rugged Count: {rug_count}
Overleveraged: {overleveraged_count}
FOMO Buys: {fomo_buys}
Panic Sells: {panic_sells}
Avg Hold Time: {avg_hold_hours:.1f} hours
Diamond Hands: {diamond_hands}
Perfect Timings: {perfect_timings}
Unique Tokens: {unique_tokens}
Most Traded: {most_traded}
"""
```

## Shareable Card Design

### Visual Style
- Dark background with neon accents (pink/purple/green)
- AAE brand colors for consistency
- Trader's biggest win highlighted in green
- Biggest loss highlighted in red
- Roast text prominently displayed
- QR code linking to full roast page
- Share buttons: X/Twitter, Telegram, Farcaster

### Card Dimensions
- Twitter: 1200x675px
- Instagram: 1080x1080px
- Story: 1080x1920px

## pump.fun Launch Strategy

### Pre-Launch (Week 1)
1. Build MVP: wallet connect + trade history + basic roast
2. Deploy to simple domain (roast.trade or trade-roast.fun)
3. Generate 10-20 roast cards from known wallets (anonymized)
4. Post roast cards on X/Twitter with " roast me" CTA
5. Build waitlist for $ROAST token

### Launch (Week 2)
1. Deploy $ROAST on pump.fun
2. Token holders get:
   - Premium roasts (longer, funnier, more detailed)
   - Custom roast templates
   - Historical roast tracking
   - "Roast Score" leaderboard
3. Free tier: basic roast, limited detail

### Post-Launch (Week 3+)
1. Integrate with AAE — roast players after matches
2. Add "Roast a Friend" feature (connect their wallet with permission)
3. Roast battles — compare roasts, community votes
4. API for other projects to use roast engine

## Integration with AAE

- After each Agent Arena match, offer to roast the player's performance
- Bad trades in AAE trigger roast messages from bot advisors
- $ROAST token holders get premium bot advisor personalities
- Roast leaderboard ties into AAE reputation system

## Tech Stack

- **Backend:** Python (FastAPI)
- **AI:** OpenAI GPT-4 or Claude for roast generation
- **Solana:** @solana/web3.js (via Python solders)
- **Cards:** Pillow + cairosvg for image generation
- **Frontend:** Simple HTML/CSS/JS (pump.fun aesthetic)
- **Token:** pump.fun launch (Solana SPL)
- **Hosting:** Vercel/Cloudflare Pages (frontend), Railway/Fly.io (API)

## MVP Scope

### Phase 1 — MVP (This Build)
- [ ] Wallet connection (Phantom via deep link)
- [ ] Solana trade history fetch (Helius RPC)
- [ ] Performance calculation (core metrics)
- [ ] AI roast generation (basic templates)
- [ ] Shareable card (single format)
- [ ] Simple landing page

### Phase 2 — Post-MVP
- [ ] Base chain support
- [ ] Premium roasts (token-gated)
- [ ] Roast leaderboard
- [ ] "Roast a Friend" feature
- [ ] Multiple card formats

### Phase 3 — AAE Integration
- [ ] Post-match roasts
- [ ] Bot advisor roast personalities
- [ ] $ROAST staking for premium features
- [ ] Roast battles

## Success Criteria

- [ ] Wallet connects and trade history loads
- [ ] Metrics calculated correctly
- [ ] AI generates funny, personalized roast
- [ ] Card renders and is shareable
- [ ] Works on mobile (Telegram browser)
- [ ] Pump.fun aesthetic (dark, neon, crypto-native)

## Bankr Exploit Connection

TradeRoast is safe by design:
- **Read-only** — we never execute trades or move funds
- **No private keys** — wallet connection is view-only
- **No prompt injection risk** — we don't process untrusted input into commands
- **The roast is the product** — not the trading

This is the anti-Bankr: we make fun of your trades instead of making them for you.
