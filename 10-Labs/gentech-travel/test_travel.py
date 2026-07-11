"""
Tests for GenTech Travel Agent modules.
"""
import sys, os, json, tempfile, unittest
from datetime import date
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

from travel_agent import HotelSearchParams, PackageSearchParams, BookingParams, UsageTracker
from x402_payment import X402Client, PaymentMiddleware, PRICING
from organic_maps import geocode, search_pois, get_route, OrganicMapsError


class TestUsageTracker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump({"users": {"test": {"searches": 3}}}, self.tmp)
        self.tmp.close()
        self.tracker = UsageTracker(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_get_usage(self):
        self.assertEqual(self.tracker.get_usage("test"), 3)

    def test_increment(self):
        self.tracker.increment("test")
        self.assertEqual(self.tracker.get_usage("test"), 4)

    def test_new_user(self):
        self.assertEqual(self.tracker.get_usage("new"), 0)

    def test_premium(self):
        self.assertFalse(self.tracker.is_premium("test"))
        self.tracker.set_premium("test", True)
        self.assertTrue(self.tracker.is_premium("test"))

    def test_free_limit(self):
        for _ in range(10):
            self.tracker.increment("test")
        self.assertEqual(self.tracker.get_usage("test"), 13)


class TestX402Payment(unittest.TestCase):
    def setUp(self):
        self.client = X402Client()

    def test_get_invoice(self):
        inv = self.client.get_invoice("search_hotel", "agent-1")
        self.assertEqual(inv["tool"], "search_hotel")
        self.assertEqual(inv["amount_usdc"], 0.005)
        self.assertEqual(inv["network"], "eip155:8453")
        self.assertIn("invoice_id", inv)
        self.assertIn("expires_at", inv)

    def test_pricing_all_tools(self):
        pricing = self.client.get_pricing()
        self.assertIn("pricing", pricing)
        for tool in ["search_hotel", "search_flights", "book", "nearby_pois"]:
            self.assertIn(tool, pricing["pricing"])

    def test_payment_middleware_free_tools(self):
        mw = PaymentMiddleware()
        result = mw.require_payment("status", "agent-1")
        self.assertTrue(result["free"])

    def test_payment_middleware_paid_tools(self):
        mw = PaymentMiddleware()
        result = mw.require_payment("search_hotel", "agent-1")
        self.assertFalse(result["free"])
        self.assertEqual(result["price_usdc"], 0.005)
        self.assertIn("payment_url", result)
        self.assertIn("invoice_id", result)


class TestOrganicMaps(unittest.TestCase):
    @patch("organic_maps.urlopen")
    def test_geocode(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps([{"lat": "35.6762", "lon": "139.6503"}]).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        lat, lon = geocode("Tokyo")
        self.assertAlmostEqual(lat, 35.6762)
        self.assertAlmostEqual(lon, 139.6503)

    @patch("organic_maps.urlopen")
    def test_geocode_not_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps([]).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        with self.assertRaises(OrganicMapsError):
            geocode("Nowhereland")

    @patch("organic_maps.urlopen")
    def test_search_pois(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "elements": [{
                "tags": {"name": "Tokyo Tower", "tourism": "attraction"},
                "lat": 35.6586, "lon": 139.7454,
            }]
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        pois = search_pois(35.6762, 139.6503, 2000)
        self.assertEqual(len(pois), 1)
        self.assertEqual(pois[0].name, "Tokyo Tower")

    @patch("organic_maps.urlopen")
    def test_get_route(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "code": "Ok",
            "routes": [{"distance": 5000, "duration": 300, "geometry": {"type": "LineString", "coordinates": []}}]
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        route = get_route((35.6, 139.7), (35.7, 139.8))
        self.assertEqual(route["distance_km"], 5.0)
        self.assertEqual(route["duration_min"], 5.0)


class TestTravelAgent(unittest.TestCase):
    def test_hotel_search_params(self):
        p = HotelSearchParams("Tokyo", date(2026, 9, 1), date(2026, 9, 7), 2, 500.0)
        self.assertEqual(p.destination, "Tokyo")
        self.assertEqual(p.guests, 2)
        self.assertEqual(p.max_price, 500.0)

    def test_flight_search_params(self):
        from letsfg import FlightSearchParams
        p = FlightSearchParams("CVG", "NRT", date(2026, 9, 1), 1, "economy", "USD")
        self.assertEqual(p.origin, "CVG")
        self.assertEqual(p.destination, "NRT")

    def test_booking_params(self):
        p = BookingParams("hotel-1", "room-1", date(2026, 9, 1), date(2026, 9, 7), 2, "Jordan", "j@test.com")
        self.assertEqual(p.hotel_id, "hotel-1")
        self.assertEqual(p.guest_email, "j@test.com")


if __name__ == "__main__":
    unittest.main()
