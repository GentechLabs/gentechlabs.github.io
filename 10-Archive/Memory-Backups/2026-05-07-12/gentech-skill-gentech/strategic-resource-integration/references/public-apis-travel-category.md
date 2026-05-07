# Public APIs — Travel Category (Extracted & Condensed)

**Source:** [public-apis/public-apis](https://github.com/public-apis/public-apis) — Travel section  
**Skill:** `strategic-resource-integration`  
**Date extracted:** May 3, 2026  
**Purpose:** Quick-reference for travel-related free/cheap APIs with GenTech-specific notes

---

## Core Tier (Free + Generous)

| API | What It Does | Free Tier | Auth | GenTech Use |
|-----|--------------|-----------|------|-------------|
| **OpenStreetMap Nominatim** | Geocoding + reverse geocoding | Completely free, 1 req/sec | None | Primary fallback for all location lookups |
| **OpenWeatherMap** | Current weather + forecasts | 60 calls/day free | API key | Layer 4 context; cache 30min |
| **ExchangeRate-API** | Currency conversion rates | 1,500 req/mo free | API key | Layer 4 context; cache 10min |
| **IP Geolocation** | IP → location (city-level) | 1K/day free | API key | Auto-detect user location |
| **Satellite / Map Imagery** | Map tiles | Various | Varies | Map backgrounds |

**Note:** OSM is the safety net. Even if Google Maps billing fails, OSM keeps geocoding alive at zero cost.

---

## Mid Tier (Free with limits)

| API | What It Does | Free Tier | Auth | Notes |
|-----|--------------|-----------|------|-------|
| **Google Maps Platform** | Geocoding, Places, Street View, Maps JS | $200 credit/month (expires monthly) | API key + billing | Primary provider; set billing alert at $150 |
| **Skyscanner RPM** (RapidAPI) | Flight search | 100K requests/month | RapidAPI key | Fast, good coverage; requires RapidAPI proxy |
| **Amadeus Self-Service** | Flights, hotels, car rentals | 2,000 API calls/month | OAuth2 + API key | More complex but direct; better for production |
| **Booking.com Affiliate** | Hotel inventory + booking | Commission-based affiliate | Partner account | Requires approval; revenue share model |
| **TripAdvisor API** | Reviews, ratings, photos | Limited free, mostly paid | API key | Research-phase only; not production-ready on free |
| **Eventbrite API** | Event discovery | 5K tickets/mo free | OAuth | Local events layer; requires user auth for full |
| **Rome2Rio** | Multi-modal routing | 100K/month | API key | Good for "how to get there" suggestions |
| **Mapillary** | Crowdsourced street photos | Free for open data | Token required | Street View fallback |
| **TransitLand** | Transit agency data (GTFS) | Open dataset | None | Great for public transport routing |
| **Airports (OurAirports)** | Airport database | Open data | None | Useful for IATA code lookup |

---

## Strategic Considerations

### Flight Search Comparison
- **Skyscanner RPM** — easiest to start (RapidAPI handles billing), free tier generous, but adds proxy layer
- **Amadeus** — more professional, direct integration, stricter rate limits, better for production booking flows
- **Recommendation:** Start with Skyscanner for prototyping; migrate to Amadeus for production if needed

### Hotel Search Comparison
- **Booking.com Affiliate** — requires partnership approval (weeks), but gives real inventory + commission
- **Amadeus** — includes some hotel content but less inventory
- **Recommendation:** Use Booking.com only if we're ready to monetize via affiliate; otherwise stub with mock data

### Street View Options
- **Google Street View Image API** — best quality, global, easy embed
- **Mapillary** — community shots, sometimes more recent in dense cities, but coverage uneven
- **Apple MapKit JS** — alternative, requires JS widget, good for iOS-first experiences
- **Recommendation:** Google primary, Mapillary secondary fallback, Apple optional (low priority)

### Geocoding Strategy
- **Primary:** Google Maps Geocoding (most accurate)
- **Secondary:** OpenStreetMap Nominatim (free, unlimited)
- **Fallback logic:** Try Google → if 429/500/OVER_QUERY_LIMIT, retry with OSM once → if OSM fails, return error

### Weather Provider
- **OpenWeatherMap** — decent free tier, easy API
- **Weather.gov** (NOAA) — US-only, completely free, no auth
- **AccuWeather** — limited free, requires partnership for scale
- **Recommendation:** OpenWeatherMap for global coverage; supplement with Weather.gov for US-specific trips

---

## Rate Limits at a Glance

| API | Free Limit | Cost after free | Notes |
|-----|-----------|----------------|-------|
| Google Maps | $200 credit/mo (~$5/1K req) | Pay-as-you-go | Set billing alerts |
| Skyscanner RPM | 100K/mo | $0.0025/req (RapidAPI) | Monitor usage monthly |
| Amadeus | 2K/mo | Tiered pricing | Contact sales for scale |
| OpenWeatherMap | 60/day | $40/mo for 1M | Use caching aggressively |
| ExchangeRate-API | 1.5K/mo | $10–30/mo for higher | Update every 10min cache |
| Mapillary | Free (rate-limited) | Contact for high volume | Start with free |

---

## Authentication Types

| Type | APIs using it | Setup complexity |
|------|---------------|------------------|
| API Key (header) | Most (Google, Skyscanner, OpenWeather) | Easy — just store key |
| OAuth 2.0 | Amadeus, Eventbrite, TripAdvisor | Medium — token exchange flow |
| No auth | OSM, TransitLand, OurAirports | Trivial — just call endpoint |

**GenTech convention:** Store all keys/credentials in `00-HQ/Integrations/<api>-key.md` and load into agent `.env` files via DMOB.

---

## Quick Start Commands (Testing)

```bash
# Test Google Maps Geocoding
curl "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Pennsylvania+Ave+NW+Washington+DC&key=$GOOGLE_MAPS_API_KEY"

# Test OSM Nominatim
curl "https://nominatim.openstreetmap.org/search?format=json&q=1600+Pennsylvania+Ave+NW+Washington+DC"

# Test OpenWeatherMap (London)
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=$OPENWEATHER_API_KEY"

# Test ExchangeRate-API
curl "https://v6.exchangerate-api.com/v6/$EXCHANGERATE_API_KEY/latest/USD"

# Test Skyscanner RPM (requires RapidAPI key)
curl -H "X-RapidAPI-Key: $SKYSCANNER_RPM_KEY" \
     -H "X-RapidAPI-Host: skyscanner-api.p.rapidapi.com" \
     "https://skyscanner-api.p.rapidapi.com/v3e/flights?originPlaceId=NYC&destinationPlaceId=LAX&departureDate=2026-05-20"
```

---

## Vault File Template (API Key Doc)

```markdown
---
title: <API Name> — API Key
date: YYYY-MM-DD
owner: Gentech
custodian: DMOB
---

## Credentials
| Field | Value |
|-------|-------|
| API Key | `[REDACTED]` |
| Storage | `<VARIABLE>` in `<profile>` `.env` |
| Billing | <billing info, if any> |
| Quota | <free tier info + limits> |

## Usage
```bash
# Example curl
curl "..." | jq .
```

## Setup Steps
1. <step-by-step for provisioning>
2. <restrictions, e.g., HTTP referrer, IP>
3. <billing alert setup>

## Pitfalls
- Quota resets on <date cycle>
- Known errors: <list>
- Fallback provider: <name>

## Change Log
- 2026-05-03: Initial provisioning for Travel-Agent project
```

---

**Keep this reference handy when adding new API integrations to any GenTech project. Patterns are domain-agnostic.**
