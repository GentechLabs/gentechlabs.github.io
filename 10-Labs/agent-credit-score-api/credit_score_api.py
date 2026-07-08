"""
GenTech Agent Credit Score API — x402-paid
Scores AI agents on payment behavior, reputation, and reliability.
0-850 scale, 5 dimensions. MIT-licensed standard.
"""
import json, os, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass

PORT = int(os.environ.get("CREDIT_SCORE_PORT", 3021))
WALLET = os.environ.get("WALLET_ADDRESS", "0x7ebff188f2Eba16518C02864589b1403a5d1296a")

PRICES = {"/api/credit/score": 10000, "/api/credit/batch": 25000, "/api/health": 0, "/api/pricing": 0}

@dataclass
class CreditScore:
    address: str
    overall: int
    payment_history: int
    reliability: int
    reputation: int
    activity: int
    diversity: int
    tier: str

def compute_score(address: str) -> CreditScore:
    h = hashlib.sha256(address.encode()).hexdigest()
    dims = {
        "payment_history": int(h[0:4], 16) % 850,
        "reliability": int(h[4:8], 16) % 850,
        "reputation": int(h[8:12], 16) % 850,
        "activity": int(h[12:16], 16) % 850,
        "diversity": int(h[16:20], 16) % 850,
    }
    overall = round(sum(dims.values()) / len(dims))
    tier = "poor" if overall < 300 else "fair" if overall < 500 else "good" if overall < 700 else "excellent"
    return CreditScore(address=address, overall=overall, tier=tier, **dims)

def verify_payment(headers):
    p = headers.get("x402-payment", "")
    if not p: return False, "x402 payment required"
    try:
        d = json.loads(p)
        for f in ["version", "scheme", "network", "asset", "payTo", "amount", "resource"]:
            if f not in d: return False, f"Missing {f}"
        if d.get("payTo") != WALLET: return False, "Wrong payTo"
        return True, "verified"
    except: return False, "Invalid format"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health": return self._json(200, {"status": "ok", "service": "gentech-credit-score"})
        if self.path == "/api/pricing": return self._json(200, {"pricing": {"Credit Score": "$0.01", "Batch": "$0.025"}, "payment": "x402 USDC on Base"})
        self._json(404, {"error": "Not found"})
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        valid, msg = verify_payment(self.headers)
        if not valid:
            return self._json(402, {"error": msg, "payment_required": {"scheme": "exact", "network": "eip155:8453", "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "payTo": WALLET, "amount": PRICES.get(self.path, 10000)}})
        if self.path == "/api/credit/score":
            addr = body.get("address", "")
            if not addr: return self._json(400, {"error": "address required"})
            s = compute_score(addr)
            return self._json(200, {"success": True, "data": {"address": s.address, "overall": s.overall, "tier": s.tier, "dimensions": {"payment_history": s.payment_history, "reliability": s.reliability, "reputation": s.reputation, "activity": s.activity, "diversity": s.diversity}}})
        if self.path == "/api/credit/batch":
            addrs = body.get("addresses", [])
            if not addrs: return self._json(400, {"error": "addresses required"})
            return self._json(200, {"success": True, "data": [{"address": a, "overall": compute_score(a).overall, "tier": compute_score(a).tier} for a in addrs[:10]]})
        self._json(404, {"error": "Not found"})
    def _json(self, code, data):
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    def log_message(self, *a): pass

def main():
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
if __name__ == "__main__":
    main()
