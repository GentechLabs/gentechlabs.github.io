# 💡 Idea: Gentech Travel — AI Concierge Layer

**Date:** 2026-04-22 (updated 2026-05-22)
**Author:** Jordan
**Category:** Premium Tier Feature
**Status:** Green-lit — scaffold as real project

---

## The Concept

AI-powered travel concierge that handles everything — flights, hotels, navigation, itineraries — via voice or text commands. Crypto-native payments, offline maps, and an agent that knows your preferences.

## Why It's Unique

**No one does agent + travel + crypto + offline maps together.**

| Competitor | What They Do | What They Don't |
|-----------|-------------|----------------|
| Expedia/Booking | Web-only search | No agent, no crypto, markups |
| Travala | Crypto payments | No AI agent, no offline maps |
| Google Travel | Good search | No booking agent, no crypto, tracking |
| **Gentech Travel** | **Full agent stack** | — |

**Our edges:**
1. **Agent-native** — book via voice/text, not a website. "Find me a flight to Tokyo under $500"
2. **Crypto payments** — SOL/USDC via x402, zero FX fees, global access
3. **Offline maps** — Organic Maps integration. Download maps before travel, navigate without data roaming
4. **Escrow protection** — AgentEscrow holds funds until flight confirmed. No charge-then-cancel scams
5. **AI itinerary** — agent plans your entire trip, not just flights. Day-by-day with local tips
6. **No markups** — raw airline prices via LetsFG (200+ connectors)

---

## Freemium Model

### Free Tier (10 searches/month)
- Flight search via agent (text only)
- Basic price comparison
- View 3 destinations/day
- Organic Maps: download 1 map/month

### Premium ($15/mo)
- **Unlimited** flight/hotel searches
- **Agent books for you** — voice + text
- **Crypto payments** — SOL/USDC/x402
- **AgentEscrow** protection on all bookings
- **AI itinerary** — full trip planning with day-by-day schedule
- **Offline maps** — unlimited downloads, pre-cached for your trip
- **Destination brief** — local customs, safety, weather, emergency contacts
- **Auto-receipts** — expense tracking + export
- **Booking decision engine** — reliability ratings, price comparison, smart recommendations
- **Preference learning** — "Always book airline direct" vs "OTA if savings > $75"
- **Risk assessment** — what happens if cancelled, rebooking ease, refund policies

---

## Architecture

```
User → Agent (voice/text)
    ├── LetsFG MCP → 200+ flight/hotel connectors → Best price
    ├── Organic Maps → Offline map download + navigation
    ├── x402 → Crypto payment (SOL/USDC)
    ├── AgentEscrow → Hold funds until confirmed
    └── Gemini/Perplexity → Destination research + itinerary
```

## The "Stand Out" Features

### 1. Trip Intelligence
Agent doesn't just book — it *briefs* you:
- "Your hotel is 12 min from Shibuya Station. Here's the metro map."
- "Weather in Barcelona: 78°F, sunny. Pack light layers."
- "Local emergency: 112 (EU). Your hotel concierge speaks English."

### 5. Smart Booking Decisions
Agent rates every booking channel:
- Airlines direct: ⭐⭐⭐⭐⭐ (best for rebooking)
- Major OTAs: ⭐⭐⭐⭐ (good for price)
- Budget OTAs: ⭐⭐⭐ (use caution)
- Unknown: ⭐⭐ (avoid for international)

Your preference: "Always airline direct" or "OTA if savings > $75"

### 2. Offline-First Travel
- Pre-download maps for your destination before you fly
- Navigate without data roaming (Organic Maps)
- Agent caches your itinerary offline too

### 3. Crypto-Native = Borderless
- No FX conversion fees
- Pay with SOL/USDC from anywhere
- Escrow means you're protected even with crypto

### 4. Voice Concierge
- "Book me the cheapest flight to Lisbon next Friday"
- "Add a restaurant near my hotel for Tuesday dinner"
- "What's the weather at my destination?"

---

## Next Steps

- [x] Travel rules framework created (`travel-rules-framework.md`)
- [x] Philippines trip planner built (`philippines-trip-planner.md`)
- [x] Thailand, Bali, Vietnam rules added
- [ ] Scaffold GitHub repo (gentech-travel)
- [ ] Integrate LetsFG MCP connector
- [ ] Integrate Organic Maps API
- [ ] Add location-aware cultural alerts
- [ ] Build notification system for travel rules
- [ ] Prototype voice concierge flow
- [ ] Test with Jordan's Philippines trip (August 2026)

---

## Tags
`#idea` `#premium` `#travel` `#concierge` `#x402` `#solana` `#organic-maps` `#letsfg` `#freemium`
