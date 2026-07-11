# GenTech Travel Agent

**Status:** 🟢 Building (Week 1-2)
**Stack:** Travala MCP + LetsFG + Organic Maps (OSM) + x402 Payments
**Deploy Target:** Cloudflare Workers

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    travel.py (Unified CLI)                    │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ travel_agent │  letsfg.py   │ organic_maps │ x402_payment  │
│ (Travala     │ (LetsFG      │ (OpenStreet  │ (x402 micro-  │
│  MCP)        │  MCP)        │  Map POIs)   │  payments)    │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## Modules

| Module | Source | What It Does |
|--------|--------|-------------|
| `travel_agent.py` | Travala MCP | Hotel search, packages, booking, cancellation |
| `letsfg.py` | LetsFG MCP | Flight search (400+ airlines), cheapest finder |
| `organic_maps.py` | OpenStreetMap | POI search, geocoding, route planning (free, no API key) |
| `x402_payment.py` | x402 Gateway | Per-call micropayments, invoice generation, verification |
| `travel.py` | Unified CLI | One-shot trip planner combining all sources |
| `travel_mcp.py` | Local MCP Server | HTTP server exposing tools for Hermes/Forge |

## Pricing

| Tool | Price (USDC) |
|------|-------------|
| `search_hotel` | $0.005 |
| `search_package` | $0.01 |
| `search_flights` | $0.005 |
| `search_cheapest` | $0.01 |
| `book` | $0.05 |
| `cancel_booking` | $0.01 |
| `manage_booking` | $0.005 |
| `get_airline` | $0.001 |
| `nearby_pois` | $0.003 |
| `route_plan` | $0.01 |

**Free tier:** 10 searches/month per user. Upgrade: $15/mo premium.

## Usage

```bash
# One-shot trip planner
python travel.py plan --dest Tokyo --in 2026-09-01 --out 2026-09-07 --origin CVG

# Hotels only
python travel.py hotels --dest Tokyo --in 2026-09-01 --out 2026-09-07

# Flights only
python travel.py flights --origin CVG --dest NRT --date 2026-09-01

# POIs near a location
python travel.py pois --location Tokyo --radius 2000

# Route between two points
python travel.py route --from-lat 35.6 --from-lon 139.7 --to-lat 35.7 --to-lon 139.8

# Pricing info
python travel.py pricing --json

# Status
python travel.py status --user my-agent
```

## Tests

```bash
python -m unittest test_travel -v
```

16 tests covering: UsageTracker, x402 payments, geocoding, POI search, routing, params.

## Deploy

The MCP server (`travel_mcp.py`) runs locally on port 3010.
For Cloudflare Workers deploy, see `workers/` directory.

## Network

- **Travala MCP:** `https://travel-mcp.travala.com/mcp`
- **LetsFG MCP:** `https://letsfg-mcp.vercel.app/mcp`
- **x402 Gateway:** `https://gentech-x402-gateway.jordanjones0902.workers.dev`
- **OSM Overpass:** `https://overpass-api.de/api/interpreter`
- **OSRM Routing:** `https://router.project-osrm.org`
