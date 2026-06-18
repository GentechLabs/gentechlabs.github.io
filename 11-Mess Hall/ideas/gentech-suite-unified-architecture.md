# 🌐 GenTech Suite — Unified Architecture

> Updated: 2026-06-14
> Vision: Everything ties together through the dashboard

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENTECH DASHBOARD ENGINE                      │
│                 (38KB zero-dep, 8 section types)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ TRAVEL   │  │ COOKBOOK │  │ GAMING   │  │ DEFI     │       │
│  │ Intel    │  │ Recipes  │  │ Builds   │  │ Portfolio│       │
│  │ Flights  │  │ Food     │  │ POE2     │  │ LP       │       │
│  │ Safety   │  │ Family   │  │ Vanito   │  │ Scouts   │       │
│  └────┬─────┘  └────┬─────┘  └──────────┘  └──────────┘       │
│       │              │                                          │
│       └──────┬───────┘                                          │
│              │                                                  │
│  ┌───────────▼───────────────────────────────────────────┐     │
│  │              TRAVEL + FOOD INTEL LAYER                 │     │
│  │                                                        │     │
│  │  🍜 "Best pad thai in Bangkok" → Cookbook recipe match │     │
│  │  🍺 "Local brewery with cheap beer" → Price intel     │     │
│  │  🍲 "Street food stall near hotel" → Recipe + safety  │     │
│  │  🍛 "Cooking class in Chiang Mai" → Activity intel    │     │
│  │                                                        │     │
│  │  Intel flows: Travel → Food → Dashboard → User         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  AGENT INTELLIGENCE LAYER                │   │
│  │                                                          │   │
│  │  Safety Agent ──► Price Agent ──► Verification Agent    │   │
│  │       │                │                │                │   │
│  │       └────────────────┴────────────────┘                │   │
│  │                      │                                   │   │
│  │              Intel Marketplace (x402)                    │   │
│  │              ERC-8004 Identity                           │   │
│  │              On-chain Reputation                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## How Travel + Food Connect

### The Flow:
1. **Traveler lands in Bangkok**
   - Dashboard shows: safety intel, price checks, hidden gems
   - Agent says: "Street food on Khao San Road is $1-3/meal"

2. **Traveler asks about food**
   - Dashboard shows: Cookbook recipes from Christel's database
   - Intel says: "Local pad thai stall uses tamarind sauce, not ketchup"
   - Agent: "This matches Christel's Pad Thai recipe — want to see it?"

3. **Traveler finds a cooking class**
   - Intel marketplace: "Thai cooking class in Chiang Mai — $25"
   - Dashboard: "Book via Travala (x402 payment)"
   - Cookbook: "Learn to make Tom Yum — recipe in vault"

4. **Traveler comes home**
   - Dashboard: "Here's what you learned abroad"
   - Cookbook: "Add your travel recipes to the vault"
   - Reputation: "You contributed 15 intel tips — you're a Local Expert"

### Data Connections:

| Travel Intel | Cookbook Link | Dashboard Section |
|-------------|---------------|-------------------|
| Restaurant recommendation | Recipe match | Intel Feed + Recipe Card |
| Street food price | Cost per serving | Price Tracker |
| Cooking class | Recipe source | Activity Feed |
| Food safety tip | Ingredient warning | Safety Alert |
| Local ingredient | Recipe substitution | Ingredient Database |

## Monetization Flow:

```
Traveler pays $0.01 for intel → Intel author gets $0.008 (80%)
                                → Platform gets $0.002 (20%)

Traveler books hotel via Travala → x402 payment
                                   → GenTech gets referral fee

Traveler buys Cookbook recipe book → $5 one-time
                                    → Christel gets 70%
                                    → Platform gets 30%
```

## Dashboard Sections (Unified):

| Section | Data Sources | Intel Type |
|---------|-------------|------------|
| **🏠 Home** | All layers | Summary, alerts, updates |
| **✈️ Travel** | Intel marketplace, Travala | Safety, prices, gems |
| **🍜 Food** | Cookbook, local intel | Recipes, restaurants, cooking |
| **💰 Finance** | DexScreener, LP positions | Portfolio, yields |
| **🎮 Gaming** | POE2, Vanito's builds | Characters, progress |
| **📊 Intel Feed** | All agents | Real-time updates |
| **🏆 Reputation** | ERC-8004, on-chain | Trust score, badges |
| **⚙️ Settings** | User prefs | Notifications, privacy |

## Hackathon Play:

**Lepton Agents (Jun 29):**
- Deploy IntelMarketplace on Base Sepolia
- Circle for USDC micropayments
- Submit as "Decentralized Travel + Food Intelligence"

**The Pitch:**
> "We're building the travel layer for the agent economy. Real intel from real travelers, verified by AI agents, settled via micropayments. When you land in Bangkok, you don't just get safety tips — you get the best pad thai recipe, matched to Christel's Cookbook, booked via Travala, all in one dashboard. Don't land clueless."

## Next Steps:
1. [ ] Add IntelMarketplace.sol to gentech-travels repo
2. [ ] Connect Cookbook database to travel intel feed
3. [ ] Build unified dashboard section for Travel + Food
4. [ ] Deploy to Base Sepolia for Lepton submission
5. [ ] Get 10 beta travelers to provide intel + recipes
