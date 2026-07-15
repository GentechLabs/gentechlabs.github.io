# GenTech Atlas — Crowdsourced AR Travel Intelligence

**Status:** 🟢 Active Design
**Owner:** Jordan (GenTech Labs)
**Version:** 1.0.0
**Date:** 2026-07-08

---

## Executive Summary

GenTech Atlas is a two-sided AR travel platform built for Meta Ray-Ban Display glasses. It turns every traveler into a sensor, collecting street-level intelligence that feeds virtual experiences for people who can't travel. The result is a self-reinforcing data flywheel: more travelers → more data → better virtual experiences → more revenue → better tools for travelers.

**The core insight:** Google Maps is a walled garden. Every traveler wearing smart glasses is a potential data contributor. Their photos, routes, and local knowledge are worth more than any subscription fee.

---

## The Two-Sided Model

### Side A: Virtual Explorer (Revenue)
*For people who can't travel*

| Feature | Description | Price |
|---------|-------------|-------|
| **City Packs** | Immersive AR tours of Tokyo, Paris, Manila, etc. | $0.01-0.05 per pack (x402) |
| **Live Walks** | Follow a real traveler's route in real-time | $0.10 per session |
| **Memory Library** | Browse crowdsourced photos and tips by location | Free (ad-supported) |
| **Trip Planning** | AI-generated itineraries based on real traveler data | $0.025 per plan |

### Side B: Field Agent (Data Source)
*For people who can travel — linked via Earn App / Work Fund*

| Feature | Description | Reward |
|---------|-------------|--------|
| **Photo Contribution** | Snap street-level photos through glasses | Free premium access |
| **POI Verification** | Confirm hours, prices, menus at locations | Data credits |
| **Route Recording** | Share walking routes with notes | Name on the map |
| **Local Tips** | Add insider knowledge (cash only, best time, etc.) | Revenue share |
| **📢 Request Bounties** | Someone posts "map this street in Kyoto" → agent accepts → captures → gets paid via Work Fund | Earn App payout |

---

## The Data Flywheel

```
                    ┌─────────────────────┐
                    │  Field Agents        │
                    │  (Travelers w/ AR)   │
                    └──────────┬──────────┘
                               │
                    Contribute photos, routes, POI data
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Atlas Dataset       │ ◄── OpenStreetMap
                    │  (Our Map + Intel)  │ ◄── Mapillary-style imagery
                    └──────────┬──────────┘
                               │
                    Feed virtual experiences
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Virtual Explorers  │
                    │  (Pay per city)     │
                    └──────────┬──────────┘
                               │
                    Revenue funds better tools
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Better AR Tools     │──► More agents → More data
                    └─────────────────────┘
```

**The moat:** Every contribution makes the dataset more valuable. Google can't replicate this because they don't have glasses on the ground. We do.

---

## Open Source Stack

We don't build from scratch. We stand on the shoulders of giants.

| Layer | Tool | What It Gives Us | License |
|-------|------|------------------|---------|
| **Glasses SDK** | [meta-wearables-webapp](https://github.com/facebookincubator/meta-wearables-webapp) (⭐153) | Official Meta toolkit for Ray-Ban Display web apps. Python/HTML/JS. Fresh from Meta (Jun 2026) | MIT |
| **Map Data** | [OpenStreetMap](https://www.openstreetmap.org) | Crowdsourced global map data. 10M+ contributors. Free and open | ODbL |
| **Offline Maps** | [Organic Maps](https://github.com/organicmaps/organicmaps) (⭐10k+) | 6M travelers using offline maps. No ads, no tracking. Reference for our data model | Apache 2.0 |
| **Street Imagery** | [Mapillary](https://github.com/mapillary) | Street-level photo crowdsourcing (acquired by Meta for ~$400M). Proves the model works | Various |
| **Travel Planning** | [OpenTripPlanner](https://github.com/opentripplanner/opentripplanner) (⭐2k+) | Multi-modal trip planner. Public transit + walking | LGPL |
| **Payment Rails** | [x402 Protocol](https://x402.org) | Our own micropayment system. $0.001-0.10 per call | Open |
| **Agent Identity** | [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) | On-chain agent registration. Trustless reputation | Open |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Meta Ray-Ban Display                   │
│                    (600×600 HUD)                         │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Atlas Web App (PWA)                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Explorer │  │ Food     │  │ Phrases  │  │ Packing│ │
│  │ Mode     │  │ Finder   │  │ Helper   │  │ List   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──┬─────┘ │
│       │             │             │            │        │
│       └─────────────┴─────────────┴────────────┘        │
│                         │                                │
│                  Data Layer (JSON)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              GenTech Backend (x402 Gateway)               │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐ │
│  │ City Packs │  │ Contribution│  │ AI Briefings     │ │
│  │ API        │  │ API        │  │ (Llama 3.1 8B)   │ │
│  └────────────┘  └────────────┘  └──────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  OpenStreetMap Integration Layer                  │   │
│  │  (Read: map data | Write: contributions)          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Data Model

```json
{
  "city": "Tokyo",
  "version": 1,
  "contributors": 47,
  "districts": [
    {
      "id": "shibuya",
      "name": "Shibuya",
      "emoji": "🚦",
      "fact": "Shibuya Crossing...",
      "photos": 12,
      "tips": ["Visit at night", "Hachiko statue is meeting spot"],
      "last_verified": "2026-07-08",
      "verified_by": "field_agent_42"
    }
  ],
  "food": [...],
  "phrases": [...],
  "packing": [...]
}
```

---

## Business Model

### Revenue Streams

| Stream | How | Target |
|--------|-----|--------|
| **City Pack Sales** | x402 micropayments per city ($0.01-0.05) | $500/mo at 10K downloads |
| **Data Licensing** | Sell anonymized travel data to hotels, airlines, tourism boards | $2,000-5,000/mo per partner |
| **Premium Field Agent** | $5/mo for priority contribution rewards | $1,000/mo at 200 subscribers |
| **Sponsored City Packs** | Tourism boards pay for featured destinations | $500-2,000 per pack |
| **AI Briefing API** | x402 endpoint for AI-generated travel briefs ($0.025/call) | $300/mo |

### Cost Structure

| Cost | Monthly | Notes |
|------|---------|-------|
| Cloudflare Workers | $0 (included) | x402 gateway runs on Workers free tier |
| AI Inference (Llama 3.1) | $0 (included) | Cloudflare Workers AI free tier |
| Storage (KV + R2) | ~$5 | City pack data, user contributions |
| **Total** | **~$5/mo** | Near-zero marginal cost per user |

### Projected Revenue (Year 1)

| Month | City Packs | Data Licensing | Premium Agents | Total |
|-------|------------|----------------|---------------|-------|
| 1-3 | $0 | $0 | $0 | $0 (building) |
| 4-6 | $150 | $0 | $50 | $200 |
| 7-9 | $500 | $1,000 | $200 | $1,700 |
| 10-12 | $1,500 | $3,000 | $500 | $5,000 |

---

## Roadmap

### Phase 1: Engine (Now — Jul 2026)
- [x] Vanito's Travel Companion prototype (Tokyo Explorer)
- [ ] Fork `meta-wearables-webapp` as base framework
- [ ] Port existing 4 modes to official Meta SDK
- [ ] Deploy to GitHub Pages for Vanito to test on glasses

### Phase 2: Data Layer (Aug 2026)
- [ ] OpenStreetMap integration (read POI data)
- [ ] Contribution API (photo upload, tip submission)
- [ ] City pack marketplace (x402 payments)
- [ ] Field agent reward system (data credits)

### Phase 3: Virtual Experiences (Sep 2026)
- [ ] AI-generated city briefings (Llama 3.1)
- [ ] Live walk following (real-time route sharing)
- [ ] Memory library (crowdsourced photo browser)
- [ ] Trip planning AI

### Phase 4: Scale (Q4 2026)
- [ ] 10 city packs (Tokyo, Osaka, Kyoto, Manila, Paris, London, NYC, Bangkok, Seoul, Singapore)
- [ ] Data licensing partnerships
- [ ] Sponsored city packs (tourism boards)
- [ ] Open source the engine (pull in contributors)

---

## Competitive Moat

| Competitor | Weakness | Our Advantage |
|------------|----------|---------------|
| **Google Maps** | Walled garden, no glasses integration, no contribution rewards | Open data, AR-native, contributors get paid |
| **Mapillary** | Acquired by Meta, stagnant development, no consumer app | Active development, consumer-first, x402 payments |
| **Organic Maps** | No AR, no virtual experiences, no revenue model | AR-native, two-sided marketplace, sustainable |
| **TripAdvisor** | Web-only, no real-time data, no glasses | Real-time, glasses-native, verified by travelers |

---

## The Pitch

> **GenTech Atlas turns every pair of smart glasses into a sensor.**
>
> Travelers wearing Meta Ray-Bans contribute street-level photos, routes, and local knowledge. That data feeds immersive virtual experiences for people who can't travel. The more people use it, the more valuable the dataset becomes.
>
> We don't compete with Google Maps. We replace the need for it.
>
> Open source engine. Crowdsourced data. x402 micropayments. No ads. No tracking. Just people helping people explore the world.

---

## Next Steps

1. **Fork `meta-wearables-webapp`** — Build on Meta's official SDK
2. **Port Vanito's Tokyo Explorer** — Move from vanilla JS to Meta SDK
3. **Deploy to GitHub Pages** — Vanito tests on actual glasses
4. **Add OpenStreetMap integration** — Pull real POI data
5. **Launch first city pack** — Tokyo, $0.01 via x402

---

*"People love experiences. Not everyone can travel. We bridge the gap."*
