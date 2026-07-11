"""
GenTech Travel Agent — Travala MCP Client
Connects to Travala's MCP server for hotel search, booking, and management.
5 tools: search_hotel, search_package, book, cancel_booking, manage_booking
"""
import json, os, sys
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

MCP_URL = os.environ.get("TRAVALA_MCP_URL", "https://travel-mcp.travala.com/mcp")
FREE_SEARCHES = 10
PREMIUM_PRICE = 15  # $15/mo


class TravalaError(Exception):
    pass


@dataclass
class HotelSearchParams:
    destination: str
    check_in: date
    check_out: date
    guests: int = 1
    max_price: Optional[float] = None
    currency: str = "USD"


@dataclass
class PackageSearchParams:
    destination: str
    check_in: date
    check_out: date
    guests: int = 1
    origin: Optional[str] = None
    currency: str = "USD"


@dataclass
class BookingParams:
    hotel_id: str
    room_id: str
    check_in: date
    check_out: date
    guests: int
    guest_name: str
    guest_email: str


def _mcp_call(tool: str, params: dict) -> dict:
    """Call a Travala MCP tool via HTTP POST."""
    payload = json.dumps({"tool": tool, "params": params}).encode()
    req = Request(
        MCP_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except URLError as e:
        raise TravalaError(f"MCP call failed: {e}")


def search_hotel(params: HotelSearchParams) -> list[dict]:
    """Search hotels by destination, dates, and budget."""
    p = {
        "destination": params.destination,
        "checkIn": params.check_in.isoformat(),
        "checkOut": params.check_out.isoformat(),
        "guests": params.guests,
        "currency": params.currency,
    }
    if params.max_price:
        p["maxPrice"] = params.max_price
    return _mcp_call("search_hotel", p).get("results", [])


def search_package(params: PackageSearchParams) -> list[dict]:
    """Search hotel + flight packages."""
    p = {
        "destination": params.destination,
        "checkIn": params.check_in.isoformat(),
        "checkOut": params.check_out.isoformat(),
        "guests": params.guests,
        "currency": params.currency,
    }
    if params.origin:
        p["origin"] = params.origin
    return _mcp_call("search_package", p).get("results", [])


def book(params: BookingParams) -> dict:
    """Book a hotel room."""
    p = {
        "hotelId": params.hotel_id,
        "roomId": params.room_id,
        "checkIn": params.check_in.isoformat(),
        "checkOut": params.check_out.isoformat(),
        "guests": params.guests,
        "guestName": params.guest_name,
        "guestEmail": params.guest_email,
    }
    return _mcp_call("book", p)


def cancel_booking(booking_id: str) -> dict:
    """Cancel an existing booking."""
    return _mcp_call("cancel_booking", {"bookingId": booking_id})


def manage_booking(booking_id: str) -> dict:
    """Get booking details and management options."""
    return _mcp_call("manage_booking", {"bookingId": booking_id})


# ── Freemium Tier ──────────────────────────────────────────────

class UsageTracker:
    """Tracks free-tier usage. Stores in JSON file."""

    def __init__(self, path: str = None):
        self.path = path or os.path.expanduser("~/.gentech-travel-usage.json")
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"users": {}}

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_usage(self, user_id: str) -> int:
        return self.data["users"].get(user_id, {}).get("searches", 0)

    def increment(self, user_id: str):
        u = self.data["users"].setdefault(user_id, {"searches": 0})
        u["searches"] += 1
        self._save()

    def is_premium(self, user_id: str) -> bool:
        return self.data["users"].get(user_id, {}).get("premium", False)

    def set_premium(self, user_id: str, active: bool = True):
        self.data["users"].setdefault(user_id, {})["premium"] = active
        self._save()


# ── CLI ─────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GenTech Travel Agent")
    parser.add_argument("action", choices=["search", "package", "book", "cancel", "manage", "status"])
    parser.add_argument("--dest", help="Destination")
    parser.add_argument("--in", dest="check_in", help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("--out", dest="check_out", help="Check-out date (YYYY-MM-DD)")
    parser.add_argument("--guests", type=int, default=1)
    parser.add_argument("--max-price", type=float)
    parser.add_argument("--user", default="default")
    parser.add_argument("--booking-id", help="Booking ID for cancel/manage")
    args = parser.parse_args()

    tracker = UsageTracker()
    usage = tracker.get_usage(args.user)

    if args.action in ("search", "package") and not tracker.is_premium(args.user):
        if usage >= FREE_SEARCHES:
            print(f"❌ Free tier limit reached ({FREE_SEARCHES}/mo). Upgrade: $15/mo")
            return
        tracker.increment(args.user)
        remaining = FREE_SEARCHES - tracker.get_usage(args.user)
        print(f"📊 Free tier: {usage + 1}/{FREE_SEARCHES} searches used ({remaining} remaining)")

    try:
        if args.action == "search":
            if not all([args.dest, args.check_in, args.check_out]):
                print("Usage: travel_agent.py search --dest Tokyo --in 2026-09-01 --out 2026-09-07")
                return
            params = HotelSearchParams(
                destination=args.dest,
                check_in=date.fromisoformat(args.check_in),
                check_out=date.fromisoformat(args.check_out),
                guests=args.guests,
                max_price=args.max_price,
            )
            results = search_hotel(params)
            print(f"🏨 Found {len(results)} hotels in {args.dest}")
            for h in results[:5]:
                name = h.get("name", h.get("hotelName", "Unknown"))
                price = h.get("price", h.get("totalPrice", "?"))
                print(f"  • {name} — ${price}")

        elif args.action == "package":
            if not all([args.dest, args.check_in, args.check_out]):
                print("Usage: travel_agent.py package --dest Tokyo --in 2026-09-01 --out 2026-09-07")
                return
            params = PackageSearchParams(
                destination=args.dest,
                check_in=date.fromisoformat(args.check_in),
                check_out=date.fromisoformat(args.check_out),
                guests=args.guests,
            )
            results = search_package(params)
            print(f"🎒 Found {len(results)} packages in {args.dest}")
            for pkg in results[:5]:
                print(f"  • {pkg.get('name', 'Package')} — ${pkg.get('totalPrice', '?')}")

        elif args.action == "status":
            remaining = FREE_SEARCHES - usage if not tracker.is_premium(args.user) else "Unlimited"
            tier = "Premium" if tracker.is_premium(args.user) else "Free"
            print(f"👤 User: {args.user}")
            print(f"🎫 Tier: {tier}")
            print(f"🔍 Searches: {usage}/{FREE_SEARCHES if not tracker.is_premium(args.user) else '∞'} remaining ({remaining})")

    except TravalaError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
