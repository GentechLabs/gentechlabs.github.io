"""
GenTech Credit Score SDK — Python Client
=========================================
Scores AI agents on payment behavior, reputation, and reliability.
0-850 scale, 5 dimensions. x402-ready.

Usage:
    from gentech_credit import CreditScoreClient

    client = CreditScoreClient()
    score = client.score("0x7ebff188f2Eba16518C02864589b1403a5d1296a")
    print(f"Score: {score.overall} ({score.tier})")
    print(f"Payment History: {score.payment_history}")
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError


# ── Config ──

DEFAULT_API_URL = "https://gentech-credit-score.jordanjones0902.workers.dev"
DEFAULT_TIMEOUT = 10


# ── Types ──

@dataclass
class CreditScore:
    """Agent credit score result."""
    address: str
    overall: int
    tier: str
    payment_history: int = 0
    reliability: int = 0
    reputation: int = 0
    activity: int = 0
    diversity: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "CreditScore":
        dims = d.get("dimensions", {})
        return cls(
            address=d.get("address", ""),
            overall=d.get("overall", 0),
            tier=d.get("tier", "unknown"),
            payment_history=dims.get("payment_history", 0),
            reliability=dims.get("reliability", 0),
            reputation=dims.get("reputation", 0),
            activity=dims.get("activity", 0),
            diversity=dims.get("diversity", 0),
        )

    def __repr__(self) -> str:
        return f"CreditScore({self.address[:10]}... → {self.overall} ({self.tier}))"


@dataclass
class BatchResult:
    """Batch credit score result."""
    results: list[dict] = field(default_factory=list)

    def scores(self) -> list[CreditScore]:
        return [CreditScore(address=r["address"], overall=r["overall"], tier=r["tier"]) for r in self.results]


# ── Client ──

class CreditScoreClient:
    """Client for the GenTech Credit Score API."""

    def __init__(self, api_url: str = DEFAULT_API_URL, timeout: int = DEFAULT_TIMEOUT):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, data: dict) -> dict:
        """Make a POST request to the API."""
        url = f"{self.api_url}{path}"
        body = json.dumps(data).encode()
        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; GentechCreditSDK/1.0)")

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except URLError as e:
            if hasattr(e, "code") and e.code == 402:
                raise PaymentRequiredError(f"x402 payment required: {e.read().decode()}")
            raise CreditScoreError(f"API request failed: {e}")
        except Exception as e:
            raise CreditScoreError(f"Request failed: {e}")

    def score(self, address: str) -> CreditScore:
        """Get credit score for a single address."""
        result = self._post("/api/credit/score", {"address": address})
        if not result.get("success"):
            raise CreditScoreError(f"API error: {result.get('error', 'unknown')}")
        return CreditScore.from_dict(result["data"])

    def batch(self, addresses: list[str]) -> BatchResult:
        """Get credit scores for multiple addresses (max 10)."""
        result = self._post("/api/credit/batch", {"addresses": addresses})
        if not result.get("success"):
            raise CreditScoreError(f"API error: {result.get('error', 'unknown')}")
        return BatchResult(results=result.get("data", []))

    def health(self) -> dict:
        """Check API health."""
        req = Request(f"{self.api_url}/health")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; GentechCreditSDK/1.0)")
        with urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())

    def pricing(self) -> dict:
        """Get pricing info."""
        req = Request(f"{self.api_url}/pricing")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; GentechCreditSDK/1.0)")
        with urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())


# ── Errors ──

class CreditScoreError(Exception):
    """Base error for credit score operations."""
    pass

class PaymentRequiredError(CreditScoreError):
    """x402 payment is required for this endpoint."""
    pass


# ── CLI ──

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GenTech Credit Score CLI")
    parser.add_argument("action", choices=["score", "batch", "health", "pricing"],
                        help="Action to perform")
    parser.add_argument("--address", "-a", help="Wallet address to score")
    parser.add_argument("--addresses", "-l", nargs="+", help="Multiple addresses for batch")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")

    args = parser.parse_args()
    client = CreditScoreClient(api_url=args.api_url)

    if args.action == "health":
        print(client.health())
    elif args.action == "pricing":
        print(json.dumps(client.pricing(), indent=2))
    elif args.action == "score":
        if not args.address:
            parser.error("--address required for score")
        s = client.score(args.address)
        print(f"Address: {s.address}")
        print(f"Score:   {s.overall}/850 ({s.tier})")
        print(f"  Payment History: {s.payment_history}")
        print(f"  Reliability:     {s.reliability}")
        print(f"  Reputation:      {s.reputation}")
        print(f"  Activity:        {s.activity}")
        print(f"  Diversity:       {s.diversity}")
    elif args.action == "batch":
        if not args.addresses:
            parser.error("--addresses required for batch")
        result = client.batch(args.addresses)
        for r in result.results:
            print(f"  {r['address'][:10]}... → {r['overall']} ({r['tier']})")


if __name__ == "__main__":
    main()
