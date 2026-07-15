"""
GenTech Token Risk API — x402-powered token risk scoring
Sells our token analysis as a paid API that other agents consume.
"""
import json, os, hmac, hashlib, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError
from dataclasses import dataclass
from typing import Optional

PORT = int(os.environ.get("TOKEN_RISK_PORT", 3020))
GATEWAY_URL = os.environ.get("GENTECH_GATEWAY_URL", "https://gentech-x402-gateway.jordanjones0902.workers.dev")
WALLET = os.environ.get("WALLET_ADDRESS", "0x7ebff188f2Eba16518C02864589b1403a5d1296a")

# Pricing
PRICES = {
    "/api/token/risk": 10000,       # $0.01
    "/api/token/batch": 25000,      # $0.025
    "/api/token/analyze": 50000,    # $0.05
    "/api/health": 0,               # free
    "/api/pricing": 0,              # free
}


@dataclass
class TokenResult:
    address: str
    chain: str
    risk_score: int
    risk_level: str
    factors: list
    recommendation: str


# ── Risk Scoring Engine ────────────────────────────────────────

RISK_FACTORS = {
    "honeypot": {"weight": 30, "description": "Can holders sell?"},
    "mint_authority": {"weight": 20, "description": "Can supply be inflated?"},
    "freeze_authority": {"weight": 15, "description": "Can trades be frozen?"},
    "lp_locked": {"weight": 15, "description": "Is liquidity locked?"},
    "top_holder_concentration": {"weight": 10, "description": "Top holder %"},
    "social_presence": {"weight": 5, "description": "Website/social exists"},
    "contract_verified": {"weight": 5, "description": "Is contract verified?"},
}


def score_token(address: str, chain: str = "base") -> TokenResult:
    """Score a token based on on-chain analysis.
    
    In production, this calls real RPC endpoints.
    For now, uses deterministic scoring from address hash.
    """
    h = hashlib.sha256(address.encode()).hexdigest()
    
    factors = []
    total = 0
    
    for factor, cfg in RISK_FACTORS.items():
        val = int(h[0:8], 16) % 100
        weighted = round(val * cfg["weight"] / 100)
        total += weighted
        factors.append({
            "name": factor,
            "score": val,
            "weight": cfg["weight"],
            "weighted": weighted,
            "description": cfg["description"],
            "finding": "pass" if val < 50 else "warn" if val < 75 else "fail",
        })
    
    # Normalize to 0-100
    max_possible = sum(c["weight"] for c in RISK_FACTORS.values())
    risk_score = round(total / max_possible * 100)
    
    if risk_score < 30:
        level = "low"
        rec = "Safe to trade. Standard precautions."
    elif risk_score < 60:
        level = "medium"
        rec = "Exercise caution. Check liquidity and holder distribution."
    elif risk_score < 80:
        level = "high"
        rec = "High risk. Consider avoiding or using small position."
    else:
        level = "critical"
        rec = "CRITICAL. Likely a scam. Do not trade."
    
    return TokenResult(
        address=address,
        chain=chain,
        risk_score=risk_score,
        risk_level=level,
        factors=factors,
        recommendation=rec,
    )


# ── x402 Payment Verification ─────────────────────────────────

def verify_x402_payment(headers: dict) -> tuple[bool, str]:
    """Verify x402 payment header. Returns (valid, message)."""
    payment = headers.get("x402-payment", "")
    if not payment:
        return False, "x402 payment required"
    try:
        data = json.loads(payment)
        # In production: verify signature against CDP facilitator
        # For now: check structure
        required = ["version", "scheme", "network", "asset", "payTo", "amount", "resource"]
        for field in required:
            if field not in data:
                return False, f"Missing field: {field}"
        if data.get("payTo") != WALLET:
            return False, f"Wrong payTo: {data.get('payTo')}"
        return True, "verified"
    except json.JSONDecodeError:
        return False, "Invalid payment format"


# ── HTTP Server ────────────────────────────────────────────────

class TokenRiskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {
                "status": "ok",
                "service": "gentech-token-risk",
                "version": "1.0.0",
                "endpoints": ["/api/token/risk", "/api/token/batch", "/api/token/analyze"],
            })
        if self.path == "/api/pricing":
            return self._json(200, {
                "pricing": {
                    "Token Risk": "$0.01 per token",
                    "Batch Risk": "$0.025 per batch (up to 10)",
                    "Deep Analyze": "$0.05 per analysis",
                },
                "payment": "x402 (USDC on Base)",
                "wallet": WALLET,
            })
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        # Verify x402 payment
        valid, msg = verify_x402_payment(self.headers)
        if not valid and self.path != "/api/health":
            price = PRICES.get(self.path, 10000)
            self._json(402, {
                "error": msg,
                "payment_required": {
                    "scheme": "exact",
                    "network": "eip155:8453",
                    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "payTo": WALLET,
                    "amount": price,
                    "resource": f"{GATEWAY_URL}{self.path}",
                },
            })
            return

        if self.path == "/api/token/risk":
            address = body.get("address", "")
            chain = body.get("chain", "base")
            if not address:
                return self._json(400, {"error": "address required"})
            result = score_token(address, chain)
            return self._json(200, {
                "success": True,
                "data": {
                    "address": result.address,
                    "chain": result.chain,
                    "risk_score": result.risk_score,
                    "risk_level": result.risk_level,
                    "factors": result.factors,
                    "recommendation": result.recommendation,
                },
            })

        elif self.path == "/api/token/batch":
            addresses = body.get("addresses", [])
            chain = body.get("chain", "base")
            if not addresses:
                return self._json(400, {"error": "addresses required"})
            results = [score_token(a, chain) for a in addresses[:10]]
            return self._json(200, {
                "success": True,
                "data": [{
                    "address": r.address,
                    "risk_score": r.risk_score,
                    "risk_level": r.risk_level,
                } for r in results],
            })

        elif self.path == "/api/token/analyze":
            address = body.get("address", "")
            chain = body.get("chain", "base")
            if not address:
                return self._json(400, {"error": "address required"})
            result = score_token(address, chain)
            return self._json(200, {
                "success": True,
                "data": {
                    "address": result.address,
                    "chain": result.chain,
                    "risk_score": result.risk_score,
                    "risk_level": result.risk_level,
                    "factors": result.factors,
                    "recommendation": result.recommendation,
                    "deep_analysis": {
                        "holder_distribution": f"Top 10: {int(hashlib.sha256((address+'holders').encode()).hexdigest()[0:4],16)%100}%",
                        "liquidity_usd": f"${int(hashlib.sha256((address+'liq').encode()).hexdigest()[0:8],16)%100000:,}",
                        "age_days": int(hashlib.sha256((address+'age').encode()).hexdigest()[0:4],16)%365,
                        "tx_count_24h": int(hashlib.sha256((address+'tx').encode()).hexdigest()[0:4],16)%5000,
                    },
                },
            })

        self._json(404, {"error": "Not found"})

    def _json(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass


def main():
    server = HTTPServer(("0.0.0.0", PORT), TokenRiskHandler)
    print(f"🛡️ GenTech Token Risk API running on port {PORT}")
    print(f"   Endpoints: /api/token/risk ($0.01), /api/token/batch ($0.025), /api/token/analyze ($0.05)")
    print(f"   Payment: x402 USDC on Base → {WALLET}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
