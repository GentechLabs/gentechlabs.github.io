"""
GenTech Travel Agent — MCP Server Wrapper
Exposes Travala tools as a local MCP server for Hermes/Forge to call.
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from travel_agent import (
    HotelSearchParams, PackageSearchParams, BookingParams,
    search_hotel, search_package, book, cancel_booking, manage_booking,
    UsageTracker, FREE_SEARCHES,
)
from datetime import date

PORT = int(os.environ.get("GENTECH_TRAVEL_PORT", 3010))
tracker = UsageTracker()


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.read(length) if length else b"{}"
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        tool = req.get("tool")
        params = req.get("params", {})
        user = params.get("user", "default")

        # Freemium check
        if tool in ("search_hotel", "search_package") and not tracker.is_premium(user):
            usage = tracker.get_usage(user)
            if usage >= FREE_SEARCHES:
                self._respond(402, {
                    "error": "Free tier limit reached",
                    "usage": usage,
                    "limit": FREE_SEARCHES,
                    "upgrade": "$15/mo premium",
                })
                return
            tracker.increment(user)

        try:
            result = self._dispatch(tool, params)
            self._respond(200, {"success": True, "data": result})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _dispatch(self, tool: str, params: dict):
        if tool == "search_hotel":
            p = HotelSearchParams(
                destination=params["destination"],
                check_in=date.fromisoformat(params["checkIn"]),
                check_out=date.fromisoformat(params["checkOut"]),
                guests=params.get("guests", 1),
                max_price=params.get("maxPrice"),
            )
            return search_hotel(p)
        elif tool == "search_package":
            p = PackageSearchParams(
                destination=params["destination"],
                check_in=date.fromisoformat(params["checkIn"]),
                check_out=date.fromisoformat(params["checkOut"]),
                guests=params.get("guests", 1),
            )
            return search_package(p)
        elif tool == "book":
            p = BookingParams(
                hotel_id=params["hotelId"],
                room_id=params["roomId"],
                check_in=date.fromisoformat(params["checkIn"]),
                check_out=date.fromisoformat(params["checkOut"]),
                guests=params["guests"],
                guest_name=params["guestName"],
                guest_email=params["guestEmail"],
            )
            return book(p)
        elif tool == "cancel_booking":
            return cancel_booking(params["bookingId"])
        elif tool == "manage_booking":
            return manage_booking(params["bookingId"])
        elif tool == "status":
            usage = tracker.get_usage(params.get("user", "default"))
            return {
                "usage": usage,
                "limit": FREE_SEARCHES,
                "remaining": FREE_SEARCHES - usage,
                "premium": tracker.is_premium(params.get("user", "default")),
            }
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _respond(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass  # quiet


def main():
    server = HTTPServer(("0.0.0.0", PORT), MCPHandler)
    print(f"🧳 GenTech Travel MCP Server running on port {PORT}")
    print(f"   Tools: search_hotel, search_package, book, cancel_booking, manage_booking, status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
