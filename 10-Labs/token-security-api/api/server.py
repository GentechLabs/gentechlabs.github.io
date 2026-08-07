"""Token Security API — Token risk scoring.

Fixed (Aug 3): was returning hardcoded score:0 placeholder.
Now proxies to the working Rugcheck v2 engine (port 8088) which returns real
Solana token risk scores. This avoids duplicating the scoring logic.
"""
import json
import urllib.error
import urllib.request
import urllib.parse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Token Security API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TIMEOUT = 20
# The Rugcheck v2 engine already returns proper 402 payment challenges.
RUGCHECK_BASE = "http://127.0.0.1:8088"


@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.1.0", "service": "token-security", "backend": "rugcheck-v2"}


@app.get("/v1/score/{mint}")
async def score(mint: str):
    """Token risk score for a Solana mint. Proxies the Rugcheck engine."""
    try:
        url = f"{RUGCHECK_BASE}/v1/score/{urllib.parse.quote(mint)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode()
            return json.loads(body)
    except urllib.error.HTTPError as e:
        # Preserve the 402 payment challenge from the backend so we're x402-compliant
        try:
            return json.loads(e.read().decode()), e.code
        except Exception:
            return {"error": "backend_error", "status_code": e.code}, e.code
    except Exception as e:
        return {"error": str(e), "mint": mint}, 502


@app.get("/v1/stats")
async def stats():
    try:
        req = urllib.request.Request(f"{RUGCHECK_BASE}/v1/stats", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}
