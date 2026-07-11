"""
GenTech Travel Agent — x402 Payment Integration
Adds per-call x402 micropayments to the travel MCP server.
Agents pay per query instead of monthly subscription.
"""

import json, os, hashlib, time
from dataclasses import dataclass
from typing import Optional

# ──────────────────────────────────────────────
#  Pricing
# ──────────────────────────────────────────────

PRICING = {
    "search_hotel": 0.005,      # $0.005 per search
    "search_package": 0.01,     # $0.01 per package search
    "search_flights": 0.005,    # $0.005 per flight search
    "search_cheapest": 0.01,    # $0.01 for flexible search
    "book": 0.05,               # $0.05 per booking
    "cancel_booking": 0.01,     # $0.01 per cancellation
    "manage_booking": 0.005,    # $0.005 per lookup
    "get_airline": 0.001,       # $0.001 for airline info
    "nearby_pois": 0.003,       # $0.003 for POI search
    "route_plan": 0.01,         # $0.01 for route planning
}

# x402 gateway endpoint
X402_GATEWAY = os.environ.get(
    "X402_GATEWAY_URL",
    "https://gentech-x402-gateway.jordanjones0902.workers.dev"
)


# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

@dataclass
class PaymentReceipt:
    tx_hash: str
    amount: float
    tool: str
    timestamp: int
    status: str  # "confirmed" | "pending"

class X402Error(Exception):
    pass


# ──────────────────────────────────────────────
#  Payment Client
# ──────────────────────────────────────────────

class X402Client:
    """Handles x402 payment verification and receipts."""

    def __init__(self, gateway_url: str = None):
        self.gateway = gateway_url or X402_GATEWAY

    def get_invoice(self, tool: str, agent_id: str) -> dict:
        """Get an x402 invoice for a tool call."""
        price = PRICING.get(tool, 0.01)
        invoice_id = hashlib.sha256(
            f"{tool}:{agent_id}:{time.time()}".encode()
        ).hexdigest()[:16]

        return {
            "invoice_id": invoice_id,
            "tool": tool,
            "amount_usdc": price,
            "network": "eip155:8453",  # Base
            "recipient": "0x7ebff188f2Eba16518C02864589b1403a5d1296a",
            "status": "pending",
            "expires_at": int(time.time()) + 300,  # 5 min
        }

    def verify_payment(self, invoice_id: str, tx_hash: str) -> bool:
        """Verify a payment with the x402 gateway."""
        try:
            from urllib.request import Request, urlopen
            req = Request(
                f"{self.gateway}/api/v1/verify",
                data=json.dumps({
                    "invoice_id": invoice_id,
                    "tx_hash": tx_hash,
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                return result.get("verified", False)
        except Exception as e:
            raise X402Error(f"Payment verification failed: {e}")

    def get_pricing(self) -> dict:
        """Return current pricing for all tools."""
        return {
            "pricing": PRICING,
            "currency": "USDC",
            "network": "Base (eip155:8453)",
            "gateway": self.gateway,
            "free_tier_searches": 10,
        }


# ──────────────────────────────────────────────
#  Payment Middleware
# ──────────────────────────────────────────────

class PaymentMiddleware:
    """Middleware that enforces x402 payment for premium tools."""

    FREE_TOOLS = {"status", "get_pricing", "nearby_pois"}

    def __init__(self):
        self.client = X402Client()
        self._invoices = {}  # invoice_id -> invoice data

    def require_payment(self, tool: str, agent_id: str = "anonymous") -> dict:
        """Generate an invoice for a paid tool call.
        Returns the invoice. Caller must pay and then call verify."""
        if tool in self.FREE_TOOLS:
            return {"free": True, "tool": tool}

        invoice = self.client.get_invoice(tool, agent_id)
        self._invoices[invoice["invoice_id"]] = invoice
        return {
            "free": False,
            "tool": tool,
            "price_usdc": invoice["amount_usdc"],
            "invoice_id": invoice["invoice_id"],
            "payment_required": True,
            "payment_url": f"{X402_GATEWAY}/pay/{invoice['invoice_id']}",
            "network": "eip155:8453",
            "recipient": invoice["recipient"],
            "expires_at": invoice["expires_at"],
        }

    def verify(self, invoice_id: str, tx_hash: str) -> bool:
        """Verify a payment and return result."""
        if invoice_id not in self._invoices:
            raise X402Error(f"Unknown invoice: {invoice_id}")

        verified = self.client.verify_payment(invoice_id, tx_hash)
        if verified:
            self._invoices[invoice_id]["status"] = "confirmed"
        return verified


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    client = X402Client()

    if len(sys.argv) > 1 and sys.argv[1] == "pricing":
        print(json.dumps(client.get_pricing(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "invoice":
        tool = sys.argv[2] if len(sys.argv) > 2 else "search_hotel"
        agent = sys.argv[3] if len(sys.argv) > 3 else "test-agent"
        invoice = client.get_invoice(tool, agent)
        print(json.dumps(invoice, indent=2))
    else:
        print("Usage: x402_payment.py [pricing|invoice <tool> <agent_id>]")
