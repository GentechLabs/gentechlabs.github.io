# GenTech Dashboard — Pricing Model

**Last updated:** June 14, 2026
**Status:** Approved by Jordan — 5 free dashboards tier confirmed

## Product Vision

General-purpose data visualization platform. Agent-driven dashboards for gaming, crypto, travel, cooking, work, and custom categories. Both auto-pull from APIs and user-driven input.

**Differentiator:** Customizability. Nobody else lets you build personalized data dashboards with an AI agent. You describe what you want, agent builds it.

## Pricing Tiers

### Free Tier — $0
| Feature | Limit |
|---------|-------|
| Dashboards | **5 active** (archive to free slots) |
| Auto-updates | 3 per day (morning, afternoon, evening) |
| Templates | Basic (gaming, crypto, travel, cookbook) |
| Manual input | Unlimited |
| Data sources | Pre-configured only |
| Voice alerts | No |
| Priority refresh | No |
| Export | HTML only |

### Agent Pass — $15/mo
| Feature | Limit |
|---------|-------|
| Dashboards | **Unlimited** |
| Auto-updates | Real-time (every 5-15 min) |
| Templates | Basic + Custom (build your own) |
| Manual input | Unlimited |
| Data sources | Any API, any URL |
| Voice alerts | Yes (Steve Harvey, custom) |
| Priority refresh | Yes |
| Export | HTML + PDF + API |
| White-label | Custom branding |

### Pro — $49/mo (future)
| Feature | Limit |
|---------|-------|
| Dashboards | Unlimited + Client dashboards |
| Auto-updates | Real-time + Webhooks |
| Templates | Custom + Marketplace access |
| Data sources | Custom API integrations |
| Voice alerts | Yes |
| Priority refresh | Yes |
| Export | All formats |
| White-label | Full rebrand |
| Support | Priority |

## Conversion Strategy

**The hook:** Free users get 5 dashboards. Enough to build a complete personal hub (travel, cooking, gaming, portfolio, health). Not enough to run a business.

**The conversion moment:** When someone hits 5 dashboards and wants a 6th — or wants real-time updates instead of 3x/day. "I need more" → Agent Pass.

**The lock-in:** Custom templates. Once someone builds their perfect dashboard layout, they're not leaving. Data compounds over time — historical trends, archives, archives.

**The engagement loop:** Auto-updates drive daily opens. Check dashboard → see new data → interact → come back tomorrow.

## Revenue Projections (Conservative)

| Users | Free (5 dash) | Agent Pass ($15) | Pro ($49) | Monthly Revenue |
|-------|---------------|------------------|-----------|-----------------|
| 100 | 85 | 12 | 3 | $327 |
| 500 | 400 | 75 | 25 | $2,350 |
| 1,000 | 780 | 150 | 70 | $5,680 |
| 5,000 | 3,800 | 800 | 400 | $31,600 |

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
