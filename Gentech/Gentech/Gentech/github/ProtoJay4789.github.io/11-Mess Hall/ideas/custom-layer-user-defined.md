# Custom Layer — User-Defined Dashboards

> GenTech Labs · June 2026
> The long-tail of the platform

---

## Vision

**Users build what we never thought of — and the best ideas become permanent layers.**

The Custom layer is the open frontier. Any data source, any template, any vision. Users create dashboards we never imagined. When a custom category gains enough traction, the governance agent elects it to a permanent layer — and the creator earns the Pioneer badge.

**The insight:** We can't predict every use case. But we can build a system where the community discovers them for us.

---

## Core Features

### 1. Template Builder
- Visual dashboard builder (drag-and-drop or JSON config)
- Connect any API endpoint, CSV file, or JSON data source
- Map fields to dashboard components (stats, cards, timelines, tables)
- Preview in real-time before publishing
- Share as template to marketplace

### 2. Template Marketplace
- Browse community-created templates
- Clone any template to your own dashboard
- Rate, review, upvote templates
- Creator earns reputation for popular templates
- Revenue share: 70% creator / 30% platform on paid templates

### 3. Governance & Election
- Templates that hit 100+ active users get flagged for election
- Governance agent monitors usage, upvotes, and community signals
- Agent elects popular templates to permanent layers
- Creator earns:
  - **Pioneer Badge** (legendary rarity)
  - **Revenue share** from the new permanent layer (5% of layer revenue for 12 months)
  - **Governance weight** (more influence on future elections)
- Permanent layers get:
  - Dedicated icon and branding
  - Agent auto-detection (agent recognizes the topic from conversations)
  - Integration with other layers (Milestones, Predictions, Social)
  - Full pricing tier ($5/mo individual, included in Agent Pass)

### 4. Data Import
- CSV upload (spreadsheet data → dashboard)
- JSON import (API responses → dashboard)
- URL monitoring (watch a URL for changes → dashboard)
- RSS feed aggregation → dashboard
- Manual input (form-based data entry)

### 5. Sharing & Forking
- Share dashboard URL (public or private)
- Fork someone else's template (remix culture)
- Template versioning (track changes, rollback)
- Community showcase (featured templates on homepage)

---

## Governance Election Process

### How a Custom Category Becomes Permanent

```
User creates template → Shares in marketplace
                ↓
Community uses it → 100+ active users
                ↓
Governance agent monitors → Flags for election
                ↓
Community votes (upvotes, usage signals)
                ↓
Agent elects → Template becomes permanent layer
                ↓
Creator gets Pioneer badge + revenue share
                ↓
New layer gets agent auto-detection + cross-layer integration
```

### Election Criteria (Agent-Evaluated)
| Signal | Weight | Description |
|--------|--------|-------------|
| Active users | 40% | 100+ users in 30 days |
| Upvote ratio | 25% | 80%+ positive rating |
| Usage depth | 20% | Users return 3+ times/week |
| Creator reputation | 10% | Prior contributions, community trust |
| Cross-layer potential | 5% | Can integrate with Milestones, Predictions, Social |

### Pioneer Badge Rewards
- **Legendary rarity** — gold border, animated glow
- **5% revenue share** from the new layer for 12 months
- **Governance weight** — 2x voting power on future elections
- **Profile badge** — permanent "Pioneer" on their profile page
- **Feature spot** — template highlighted in marketplace

---

## JSON Data Format

```json
{
  "custom": {
    "id": "custom-pet-tracker",
    "name": "Pet Health Tracker",
    "creator": "jordan",
    "created": "2026-07-15",
    "template": {
      "dataSources": [
        {
          "type": "manual",
          "fields": ["pet_name", "weight", "food", "notes", "date"]
        }
      ],
      "sections": [
        { "type": "stats", "dataSource": "summary" },
        { "type": "table", "dataSource": "entries" },
        { "type": "timeline", "dataSource": "entries" }
      ],
      "theme": {
        "colors": { "--bg": "#1a1a2e", "--accent": "#e94560" }
      }
    },
    "marketplace": {
      "listed": true,
      "price": "free",
      "upvotes": 47,
      "users": 89,
      "rating": 4.6
    },
    "election": {
      "eligible": false,
      "threshold": 100,
      "signals": {
        "activeUsers": 89,
        "upvoteRatio": 0.82,
        "returnRate": 0.35
      }
    }
  }
}
```

---

## Dashboard Sections

1. **Header** — Template name, creator, upvotes, user count
2. **Data Source Config** — API URL, CSV upload, manual input form
3. **Field Mapping** — Map data fields to dashboard components
4. **Preview** — Live preview of the dashboard
5. **Publish** — Share to marketplace or keep private
6. **Marketplace Listing** — Browse, rate, clone other templates
7. **Election Status** — Progress toward permanent layer (if applicable)

---

## Revenue Model

### Template Marketplace
- **Free templates:** $0 (open source, community-driven)
- **Paid templates:** Creator sets price (e.g., $2-10 one-time)
- **Revenue split:** 70% creator / 30% platform
- **Agent Pass:** All templates free (included in subscription)

### Permanent Layer Revenue
- Once elected: $5/mo individual, included in $20/mo Agent Pass
- Creator gets 5% of layer revenue for 12 months
- After 12 months: 2% ongoing (incentivizes continued contribution)

### Revenue Projections (Conservative)
| Permanent Layers | Users/Layer | Monthly Revenue |
|-----------------|-------------|----------------|
| 5 layers | 200 | $5,000 |
| 10 layers | 150 | $7,500 |
| 20 layers | 100 | $10,000 |

---

## Connections to Other Layers

| Layer | Connection |
|-------|-----------|
| 🏆 Milestones | "Created first template" milestone → prediction market |
| 📊 Predictions | "Will this template hit 100 users?" → community bet |
| 🤝 Social | Share templates, follow creators, community showcase |
| 🎓 Education | "Learn to build dashboards" tutorial module |
| 💰 Finance | Premium templates, revenue share tracking |

---

## The Forza Model — Templates as Social Currency

### What Jordan realized:
Templates aren't just layouts — they're **shareable creations**. Like Forza Horizon liveries:
1. You customize your car (dashboard)
2. Upload it for others to download
3. Others download, modify, re-upload
4. You earn reputation for popular designs

### Three template tiers:

| Tier | Price | Revenue Split | When |
|------|-------|---------------|------|
| **Community** | Free | 0% (reputation only) | Default for all uploads |
| **Premium** | Creator sets ($1-20) | 70/30 (creator/platform) | 100+ active users, 80%+ rating |
| **Custom Build** | Negotiated | 85/15 (creator/platform) | One-off commissions |

### Copy Trade Pattern (Finance Layer):
- User A has a DeFi yield dashboard that's earning 12% APY
- User B sees it → "Copy Trade" button
- Agent replicates the strategy in User B's portfolio
- User A earns reputation for every copier
- User B gets a working strategy without building it

### Template Marketplace Mechanics:
1. **Discover** — Browse by category, popularity, rating, recency
2. **Preview** — See the dashboard before installing
3. **Install** — One click to add to your profile
4. **Customize** — Modify colors, sections, data sources
5. **Re-upload** — Your modified version goes back to marketplace
6. **Earn** — Reputation, revenue, governance weight

### Revenue from Templates:
- **Marketplace fees:** 30% on premium templates
- **Custom build fees:** 15% on commissioned dashboards
- **Promoted listings:** Creators pay to feature their templates
- **Template bundles:** Curated collections for Agent Pass users

### Why this is the moat:
- Users build on our platform → lock-in
- Creators earn → they stay and recruit others
- More templates → more reasons to join
- Community self-organizes → free R&D
- Every template = a potential permanent layer

### The full loop:
```
User creates template → Community uses it → 100+ users
→ Governance agent elects it → Becomes permanent layer
→ Creator earns Pioneer badge + revenue share
→ More creators join → More templates → Flywheel spins
```

---

## Origin

- **Jun 12, 2026:** Jordan proposes Custom layer with community-elected categories. "People feel like they have a voice."
- **Jun 12, 2026:** Jordan realizes templates = social currency. "Like Forza Horizon — customize your car, upload for others to download."
- **Jun 12, 2026:** Copy trade pattern emerges. Finance dashboards become shareable strategies.
- First templates: Finance (copy trade), Gaming (build sharing), Cookbook (recipe collections)

---

*GenTech Custom Layer — Build. Share. Earn. Govern.*
