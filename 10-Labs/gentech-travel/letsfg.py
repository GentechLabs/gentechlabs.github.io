"""
GenTech Travel Agent — LetsFG Flight Integration
Adds flight search to the Travala MCP travel agent.
LetsFG: 400+ airlines, 5-second search, MCP-native.
"""
import json, os, subprocess, sys
from dataclasses import dataclass
from datetime import date
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

LETSFG_MCP = os.environ.get("LETSFG_MCP_URL", "https://letsfg-mcp.vercel.app/mcp")


class LetsFGError(Exception):
    pass


@dataclass
class FlightSearchParams:
    origin: str
    destination: str
    date: date
    passengers: int = 1
    cabin: str = "economy"
    currency: str = "USD"


def _mcp_call(tool: str, params: dict) -> dict:
    """Call LetsFG MCP tool."""
    payload = json.dumps({"tool": tool, "params": params}).encode()
    req = Request(
        LETSFG_MCP,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except URLError as e:
        raise LetsFGError(f"LetsFG MCP call failed: {e}")


def search_flights(params: FlightSearchParams) -> list[dict]:
    """Search flights by origin, destination, and date."""
    p = {
        "origin": params.origin,
        "destination": params.destination,
        "date": params.date.isoformat(),
        "passengers": params.passengers,
        "cabin": params.cabin,
        "currency": params.currency,
    }
    return _mcp_call("search_flights", p).get("results", [])


def search_cheapest(origin: str, destination: str, flex_days: int = 3) -> list[dict]:
    """Find cheapest flights within a flexible date range."""
    p = {
        "origin": origin,
        "destination": destination,
        "flexDays": flex_days,
        "currency": "USD",
    }
    return _mcp_call("search_cheapest", p).get("results", [])


def get_airline_info(airline_code: str) -> dict:
    """Get airline details by IATA code."""
    return _mcp_call("get_airline", {"code": airline_code})


# ── CLI ─────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GenTech Travel — LetsFG Flights")
    parser.add_argument("action", choices=["search", "cheapest", "airline"])
    parser.add_argument("--from", dest="origin", help="Origin airport code (e.g. CVG)")
    parser.add_argument("--to", dest="destination", help="Destination airport code (e.g. NRT)")
    parser.add_argument("--date", help="Flight date (YYYY-MM-DD)")
    parser.add_argument("--flex", type=int, default=3, help="Flexible days for cheapest search")
    parser.add_argument("--code", help="Airline IATA code")
    args = parser.parse_args()

    try:
        if args.action == "search":
            if not all([args.origin, args.destination, args.date]):
                print("Usage: letsfg.py search --from CVG --to NRT --date 2026-09-01")
                return
            params = FlightSearchParams(
                origin=args.origin.upper(),
                destination=args.destination.upper(),
                date=date.fromisoformat(args.date),
            )
            results = search_flights(params)
            print(f"✈️ Found {len(results)} flights from {params.origin} to {params.destination}")
            for f in results[:10]:
                price = f.get("price", {}).get("total", "?")
                airline = f.get("airline", "?")
                dep = f.get("departure", {}).get("time", "?")
                arr = f.get("arrival", {}).get("time", "?")
                stops = f.get("stops", 0)
                print(f"  • {airline} — ${price} | {dep} → {arr} | {stops} stop(s)")

        elif args.action == "cheapest":
            if not all([args.origin, args.destination]):
                print("Usage: letsfg.py cheapest --from CVG --to NRT --flex 3")
                return
            results = search_cheapest(args.origin.upper(), args.destination.upper(), args.flex)
            print(f"✈️ Cheapest flights from {args.origin.upper()} to {args.destination.upper()}")
            for f in results[:10]:
                price = f.get("price", {}).get("total", "?")
                date_found = f.get("date", "?")
                airline = f.get("airline", "?")
                print(f"  • {date_found} — {airline} — ${price}")

        elif args.action == "airline":
            if not args.code:
                print("Usage: letsfg.py airline --code AA")
                return
            info = get_airline_info(args.code.upper())
            print(json.dumps(info, indent=2))

    except LetsFGError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
