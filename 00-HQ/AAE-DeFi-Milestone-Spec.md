---
title: AAE DeFi Milestone — Presentation Layer Spec
date: 2026-06-03
status: Draft
owner: Gentech (CEO)
priority: P0
---

## Overview

The **AAE DeFi Milestone** is the user-facing visual layer for AAE's yield farming agents. It transforms raw on-chain data into a story — milestone journeys, passive income projections, and real-time position health.

**Core insight:** Users don't want to read raw DEX data. They want to see progress, milestones, and a path to financial freedom. This is that view.

---

## Architecture

### Three-Layer Stack

```
┌─────────────────────────────────────────────────┐
│           PRESENTATION LAYER (this spec)         │
│   HTML dashboards → Screenshot → Telegram/Web    │
├─────────────────────────────────────────────────┤
│              AGENT LAYER (AAE Agents)            │
│   Strategy execution, rebalancing, compounding   │
├─────────────────────────────────────────────────┤
│               DATA LAYER (Oracles)               │
│   On-chain RPC, CMC API, DexScreener, DeBank    │
└─────────────────────────────────────────────────┘
```

### Data Flow

```
User types /d5
    ↓
Agent checks: wallet connected? Position open?
    ↓
Data Layer pulls: LP position, fees, rewards, prices
    ↓
Agent populates HTML template with live data
    ↓
Headless browser renders PNG screenshot
    ↓
Screenshot sent to user (Telegram/Web/App)
```

---

## Dashboard Types

### 1. Milestone Tracker (Primary)
**Purpose:** Show the user's journey from $0 → financial freedom

**Sections:**
- Header: Pool name, APR, status
- Current position: Total value, token breakdown, composition bar
- Milestone ladder: Scout → Raider → Warlord → Sovereign
- Progress bars with percentages
- Projection table: Month-by-month path
- DCA schedule and recommendations
- Birthday/freedom goal banners

**Data needed:**
- Position value (from RPC/DeBank)
- Token amounts and prices
- Fee accrual (24h, cumulative)
- Rewards APR and claimable amount
- Range status (in/out)
- Time since deposit

### 2. Yield Farm Tracker (Detailed)
**Purpose:** Deep-dive into position mechanics

**Sections:**
- Pool info (address, platform, network, fee tier)
- Token composition with visual bar
- Fees earned breakdown (24h AVAX, 24h USDC, total)
- Range configuration (min/max price, active bin, width)
- Rewards breakdown (APR, daily emission, claimable)
- DCA schedule
- Strategy notes

**Data needed:**
- All of Milestone Tracker +
- Range details (bin step, strategy type, bin count)
- Pool TVL
- Detailed fee history

### 3. Agent Performance (Future)
**Purpose:** Show what the AAE agent is doing

**Sections:**
- Agent status (active, idle, rebalancing)
- Last actions (rebalance, compound, DCA)
- Performance vs benchmark
- Risk metrics (IL, drawdown,Sharpe)
- Upcoming actions

---

## Trigger Methods

### On-Demand (User-Initiated)
| Command | Response |
|---------|----------|
| `/d5` or `/milestone` | Milestone Tracker screenshot |
| `/farm` or `/position` | Yield Farm Tracker screenshot |
| `/status` | Quick text summary + screenshot |
| `/dca` | DCA schedule + next action |

### Scheduled (Cron-Generated)
- Daily snapshot at 8 AM ET (position health check)
- On milestone achievement (auto-celebration)
- On rebalance (before/after comparison)
- Weekly summary (7-day performance)

### Event-Driven (Agent-Triggered)
- Position goes out of range → alert with screenshot
- Milestone hit → celebration banner
- Compound ready → notification with amount
- DCA day → reminder with projection update

---

## Screenshot Pipeline

### Implementation Options

**Option A: Headless Browser (Recommended)**
```
HTML template → Puppeteer/Playwright → PNG → Send
```
- Pros: Pixel-perfect, works offline, fast
- Cons: Requires browser runtime

**Option B: HTML-to-Image API**
```
HTML template → API call (htmlcsstoimage.com) → PNG → Send
```
- Pros: No local browser needed
- Cons: External dependency, costs money at scale

**Option C: Canvas Rendering**
```
Data → Canvas API → PNG → Send
```
- Pros: Lightweight, no browser
- Cons: More code, harder to maintain

### Recommended: Option A (Headless Browser)

```python
# Pseudo-code for screenshot generation
def generate_dashboard(dashboard_type, wallet_address):
    # 1. Fetch live data from Data Layer
    position = fetch_lp_position(wallet_address)
    prices = fetch_prices(["AVAX", "USDC"])
    fees = fetch_fee_history(wallet_address)
    
    # 2. Populate HTML template
    html = render_template(dashboard_type, {
        "position": position,
        "prices": prices,
        "fees": fees,
        "milestones": calculate_milestones(position),
        "projections": generate_projections(position)
    })
    
    # 3. Screenshot with headless browser
    screenshot = browser.screenshot(html, width=1400, height=900)
    
    # 4. Return PNG path
    return screenshot
```

---

## Template System

### File Structure
```
03-Strategies/Defi-Monitor/
├── templates/
│   ├── milestone-tracker.html    (Template with {{placeholders}})
│   ├── yield-farm-tracker.html
│   └── agent-performance.html
├── data/
│   ├── {wallet}-config.json      (Position config)
│   └── {wallet}-state.json       (Runtime state)
├── screenshots/
│   └── {wallet}-{timestamp}.png  (Generated images)
└── scripts/
    └── generate-dashboard.py     (Screenshot pipeline)
```

### Template Variables
```html
<!-- Example: milestone-tracker.html -->
<div class="stat-value">{{position.total_usd}}</div>
<div class="stat-value">{{position.avax_amount}}</div>
<div class="stat-value">{{rewards.apr}}%</div>
<div class="stat-value">{{fees.24h_usd}}</div>

<!-- Milestone progress -->
<div class="progress-bar-fill" style="width:{{milestone.progress}}%">
  {{milestone.progress}}%
</div>

<!-- Projection table -->
{{#each projections}}
<tr>
  <td>{{this.month}}</td>
  <td>{{this.start_value}}</td>
  <td>{{this.dca_added}}</td>
  <td>{{this.compounded}}</td>
</tr>
{{/each}}
```

---

## User Experience Flow

### First-Time Setup
```
1. User: /connect wallet
2. Agent: "Wallet connected. Scanning for LP positions..."
3. Agent: "Found AVAX/USDC position on LFJ. Generating dashboard..."
4. [Screenshot sent]
5. Agent: "Your DeFi Milestone dashboard is ready. Use /d5 anytime for updates."
```

### Daily Check-In
```
1. User: /d5
2. Agent: Fetching live data...
3. [Screenshot sent with current position]
4. Agent: "Position at $X. You're Y% to your next milestone. Keep farming!"
```

### Milestone Achievement
```
1. [Cron detects milestone hit]
2. Agent: [Celebration screenshot with banner]
3. Agent: "You hit Scout! $5/day achieved. Next stop: Raider ($20/day)."
```

---

## Integration Points

### With AAE Agent Layer
- Agent calls `generate_dashboard()` after each action
- Dashboard shows agent's impact (before/after rebalance)
- User can see what agent is doing in real-time

### With AAE Data Layer
- Dashboard pulls from same data sources as agents
- Consistent data between agent decisions and user view
- Single source of truth for position data

### With AAE Notification System
- Dashboard screenshots attach to alerts
- Rich visual context for every notification
- Users can tap screenshot to see full dashboard

---

## Future Enhancements

### Phase 2: Interactive Dashboards
- Web-based dashboard (not just screenshots)
- Click to compound, rebalance, or DCA
- Real-time updates without refresh

### Phase 3: Social Features
- Share dashboard to Twitter/Telegram
- Compare performance with friends
- Squad dashboards (group farming)

### Phase 4: Mobile App
- Native iOS/Android dashboard
- Push notifications for milestones
- Widget for home screen

---

## Success Metrics

- **Adoption:** % of AAE users who use /d5 weekly
- **Engagement:** Average sessions per user per week
- **Retention:** Users who stay active after 30 days
- **Conversion:** Users who upgrade to paid tier for advanced dashboards

---

## Open Questions

1. **Free vs Paid:** Should basic dashboard be free, advanced paid?
2. **Customization:** Can users customize colors/sections?
3. **Multiple wallets:** Support for users with positions across chains?
4. **Historical data:** Store past dashboards for trend analysis?
5. **API access:** Let users build their own dashboards on top of AAE data?

---

*This spec defines the Presentation Layer for AAE's DeFi Milestone feature. Ready for agent layer and data layer integration.*
