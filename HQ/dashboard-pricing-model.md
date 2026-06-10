# GenTech Dashboard — Pricing Model

**Last updated:** June 10, 2026
**Status:** Approved by Jordan

## Product Vision

General-purpose data visualization platform. Agent-driven dashboards for gaming, crypto, bowling, work, and custom categories. Both auto-pull from APIs and user-driven input.

**Differentiator:** Customizability. Nobody else lets you build personalized data dashboards with an AI agent.

## Pricing Tiers

### Free Tier
| Feature | Limit |
|---------|-------|
| Dashboards | 1 |
| Auto-updates | 3 per day (morning, afternoon, evening) |
| Templates | Basic (gaming, crypto) |
| Manual input | Unlimited |
| Templates | Community only |
| Data sources | Pre-configured only |
| Voice alerts | No |
| Priority refresh | No |

### Agent Pass — $15/mo
| Feature | Limit |
|---------|-------|
| Dashboards | Unlimited |
| Auto-updates | Real-time (every 5-15 min) |
| Templates | Basic + Custom (build your own) |
| Manual input | Unlimited |
| Templates | Community + Custom |
| Data sources | Any API, any URL |
| Voice alerts | Yes (Steve Harvey, custom) |
| Priority refresh | Yes |

## Conversion Strategy

**The hook:** Free users get 3 auto-updates/day. Enough to see value, not enough to be addicted without paying.

**The conversion moment:** When someone sees their crypto portfolio update 3x/day, they'll want real-time. "I want it faster" → Agent Pass.

**The lock-in:** Custom templates. Once someone builds their perfect dashboard layout, they're not leaving.

**The engagement loop:** Auto-updates drive daily opens. Check dashboard → see new data → interact → come back tomorrow.

## Revenue Projections (Conservative)

| Users | Free | Agent Pass ($15) | Monthly Revenue |
|-------|------|-------------------|-----------------|
| 100 | 90 | 10 | $150 |
| 500 | 425 | 75 | $1,125 |
| 1,000 | 850 | 150 | $2,250 |
| 5,000 | 4,250 | 750 | $11,250 |

## Category Roadmap

### Phase 1 — Gaming (Now)
- POE2 builds, meta tracking, progression
- Skill synergy trees
- Character comparison
- PoB2 import/export

### Phase 2 — Crypto
- Portfolio tracking
- DeFi position monitoring
- Price alerts
- LP position dashboards

### Phase 3 — Bowling
- Average tracking
- League stats
- Improvement trends
- Frame-by-frame analysis

### Phase 4 — Work/Productivity
- Schedule visualization
- Goal tracking
- Productivity metrics
- Custom KPIs

### Phase 5 — Custom
- User-defined data sources
- Custom templates
- API integrations
- Community template marketplace

## Technical Architecture

### Data Sources (Auto-Update)
- **Gaming:** POE2 API, poe2db, Maxroll, Reddit
- **Crypto:** CoinGecko, DexScreener, on-chain RPC
- **Bowling:** League APIs, manual input
- **Work:** Calendar APIs, task managers
- **Custom:** User-provided URLs/APIs

### Dashboard Engine
- HTML/CSS/JS (static, fast, no server needed)
- JSON data files (agent updates via GitHub)
- GitHub Pages hosting (free, reliable)
- Template system (reusable components)

### Update Flow
1. Cron job runs on schedule (3x/day free, real-time paid)
2. Agent fetches data from configured sources
3. Agent updates JSON data files
4. GitHub Actions rebuilds dashboard
5. User sees updated dashboard on next visit

## Customizability Features

### Template System
- Pre-built layouts per category
- Drag-and-drop component placement
- Color theme customization
- Font selection
- Widget sizing

### Data Binding
- Connect any API endpoint
- Map JSON fields to dashboard components
- Set refresh intervals
- Configure alerts

### Sharing
- Share dashboard URLs
- Export dashboard configs
- Community template marketplace
- Clone others' dashboards

## Integration with AAE

- AAE provides the payment layer ($15/mo Agent Pass)
- AAE provides ERC-8004 identity (who owns the dashboard)
- AAE provides x402 micropayments (per-data-source fees)
- Dashboard provides the visual layer (what users see)

## Success Metrics

| Metric | Free Target | Paid Target |
|--------|-------------|-------------|
| Daily active users | 60% of registered | 80% of subscribers |
| Auto-update engagement | 3 checks/day | 10+ checks/day |
| Template creation | 0 | 1+ custom template |
| Retention (30-day) | 40% | 75% |
| Free → Paid conversion | — | 10-15% |
