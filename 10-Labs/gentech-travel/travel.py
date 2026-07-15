"""
GenTech Travel Agent — Unified CLI
Combines Travala hotels, LetsFG flights, Organic Maps POIs, and x402 payments.
"""

import json, os, sys
from datetime import date, datetime
from typing import Optional

from travel_agent import (
    HotelSearchParams, PackageSearchParams, BookingParams,
    search_hotel, search_package, book, cancel_booking, manage_booking,
    UsageTracker, TravalaError,
)
from letsfg import (
    FlightSearchParams, search_flights, search_cheapest, get_airline_info, LetsFGError,
)
from organic_maps import (
    geocode, search_pois, get_route, OrganicMapsError,
)
from x402_payment import X402Client, PaymentMiddleware, PRICING


# ──────────────────────────────────────────────
#  Unified Agent
# ──────────────────────────────────────────────

class TravelAgent:
    """Unified travel agent — hotels, flights, POIs, payments."""

    def __init__(self):
        self.tracker = UsageTracker()
        self.payments = PaymentMiddleware()
        self.x402 = X402Client()

    def plan_trip(self, destination: str, check_in: str, check_out: str,
                  origin: str = None, guests: int = 1, agent_id: str = "anonymous") -> dict:
        """One-shot trip planner: hotels + flights + POIs."""
        result = {"destination": destination, "date": f"{check_in} → {check_out}"}

        # Hotels
        try:
            hotels = search_hotel(HotelSearchParams(
                destination=destination,
                check_in=date.fromisoformat(check_in),
                check_out=date.fromisoformat(check_out),
                guests=guests,
            ))
            result["hotels"] = [
                {"name": h.get("name", h.get("hotelName", "?")),
                 "price": h.get("price", h.get("totalPrice", "?"))}
                for h in hotels[:5]
            ]
        except TravalaError as e:
            result["hotels"] = {"error": str(e)}

        # Flights
        if origin:
            try:
                flights = search_flights(FlightSearchParams(
                    origin=origin.upper(),
                    destination=destination.upper(),
                    date=date.fromisoformat(check_in),
                    passengers=guests,
                ))
                result["flights"] = [
                    {"airline": f.get("airline", "?"),
                     "price": f.get("price", {}).get("total", "?"),
                     "stops": f.get("stops", 0)}
                    for f in flights[:5]
                ]
            except LetsFGError as e:
                result["flights"] = {"error": str(e)}

        # POIs
        try:
            lat, lon = geocode(destination)
            pois = search_pois(lat, lon, 2000)
            result["pois"] = [
                {"name": p.name, "category": p.category}
                for p in pois[:8]
            ]
        except OrganicMapsError as e:
            result["pois"] = {"error": str(e)}

        # Pricing
        result["pricing"] = PRICING

        return result

    def get_pricing(self) -> dict:
        return self.x402.get_pricing()


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GenTech Travel Agent — Unified CLI")
    parser.add_argument("action", choices=[
        "plan", "hotels", "flights", "pois", "route",
        "book", "cancel", "status", "pricing",
    ])
    parser.add_argument("--dest", help="Destination")
    parser.add_argument("--origin", help="Origin airport code")
    parser.add_argument("--in", dest="check_in", help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("--out", dest="check_out", help="Check-out date (YYYY-MM-DD)")
    parser.add_argument("--guests", type=int, default=1)
    parser.add_argument("--date", help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--location", help="Location for POIs")
    parser.add_argument("--radius", type=int, default=1000)
    parser.add_argument("--from-lat", type=float)
    parser.add_argument("--from-lon", type=float)
    parser.add_argument("--to-lat", type=float)
    parser.add_argument("--to-lon", type=float)
    parser.add_argument("--user", default="default")
    parser.add_argument("--agent", default="anonymous")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    agent = TravelAgent()

    try:
        if args.action == "plan":
            if not all([args.dest, args.check_in, args.check_out]):
                print("Usage: travel.py plan --dest Tokyo --in 2026-09-01 --out 2026-09-07 [--origin CVG]")
                sys.exit(1)
            result = agent.plan_trip(args.dest, args.check_in, args.check_out,
                                     args.origin, args.guests, args.agent)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n{'='*50}")
                print(f"🧳 Trip Plan: {result['destination']} ({result['date']})")
                print(f"{'='*50}")
                if "hotels" in result and isinstance(result["hotels"], list):
                    print(f"\n🏨 Hotels ({len(result['hotels'])}):")
                    for h in result["hotels"]:
                        print(f"  • {h['name']} — ${h['price']}")
                if "flights" in result and isinstance(result["flights"], list):
                    print(f"\n✈️ Flights ({len(result['flights'])}):")
                    for f in result["flights"]:
                        print(f"  • {f['airline']} — ${f['price']} ({f['stops']} stop(s))")
                if "pois" in result and isinstance(result["pois"], list):
                    print(f"\n📍 Attractions ({len(result['pois'])}):")
                    for p in result["pois"]:
                        print(f"  • {p['name']} ({p['category']})")

        elif args.action == "hotels":
            if not all([args.dest, args.check_in, args.check_out]):
                print("Usage: travel.py hotels --dest Tokyo --in 2026-09-01 --out 2026-09-07")
                sys.exit(1)
            results = search_hotel(HotelSearchParams(
                destination=args.dest,
                check_in=date.fromisoformat(args.check_in),
                check_out=date.fromisoformat(args.check_out),
                guests=args.guests,
            ))
            if args.json:
                print(json.dumps(results[:10], indent=2))
            else:
                print(f"🏨 {len(results)} hotels in {args.dest}:")
                for h in results[:10]:
                    print(f"  • {h.get('name', h.get('hotelName', '?'))} — ${h.get('price', h.get('totalPrice', '?'))}")

        elif args.action == "flights":
            if not all([args.origin, args.dest, args.date]):
                print("Usage: travel.py flights --origin CVG --dest NRT --date 2026-09-01")
                sys.exit(1)
            results = search_flights(FlightSearchParams(
                origin=args.origin.upper(),
                destination=args.dest.upper(),
                date=date.fromisoformat(args.date),
                passengers=args.guests,
            ))
            if args.json:
                print(json.dumps(results[:10], indent=2))
            else:
                print(f"✈️ {len(results)} flights {args.origin} → {args.dest}:")
                for f in results[:10]:
                    price = f.get("price", {}).get("total", "?")
                    print(f"  • {f.get('airline', '?')} — ${price} | {f.get('stops', 0)} stop(s)")

        elif args.action == "pois":
            if not args.location and not (args.from_lat and args.from_lon):
                print("Usage: travel.py pois --location Tokyo [--radius 1000]")
                sys.exit(1)
            if args.location:
                lat, lon = geocode(args.location)
            else:
                lat, lon = args.from_lat, args.from_lon
            pois = search_pois(lat, lon, args.radius)
            if args.json:
                print(json.dumps([{"name": p.name, "category": p.category, "lat": p.lat, "lon": p.lon} for p in pois], indent=2))
            else:
                print(f"📍 {len(pois)} POIs near {args.location or f'({lat:.4f}, {lon:.4f})'}:")
                for p in pois[:10]:
                    print(f"  • {p.name} ({p.category})")

        elif args.action == "route":
            if not all([args.from_lat, args.from_lon, args.to_lat, args.to_lon]):
                print("Usage: travel.py route --from-lat 35.6 --from-lon 139.7 --to-lat 35.7 --to-lon 139.8")
                sys.exit(1)
            route = get_route((args.from_lat, args.from_lon), (args.to_lat, args.to_lon))
            if args.json:
                print(json.dumps(route, indent=2))
            else:
                print(f"🚗 {route['distance_km']} km — {route['duration_min']} min")

        elif args.action == "pricing":
            pricing = agent.get_pricing()
            if args.json:
                print(json.dumps(pricing, indent=2))
            else:
                print("💰 GenTech Travel Pricing:")
                for tool, price in pricing["pricing"].items():
                    print(f"  • {tool}: ${price} USDC")
                print(f"\n  Free tier: {pricing.get('free_tier_searches', 10)} searches/mo")
                print(f"  Network: {pricing['network']}")

        elif args.action == "status":
            usage = agent.tracker.get_usage(args.user)
            remaining = 10 - usage
            print(f"👤 User: {args.user}")
            print(f"🔍 Searches: {usage}/10 used ({remaining} remaining)")

    except (TravalaError, LetsFGError, OrganicMapsError) as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
