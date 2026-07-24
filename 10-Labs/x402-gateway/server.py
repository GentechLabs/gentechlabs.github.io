"""
x402 API Gateway v2.0 — Unified payment gateway for GenTech Labs x402 endpoints
Serves on port 8090 behind api.gentechlabs.net
"""

import json
import os
import base64
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal

app = FastAPI(title="GenTech x402 Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load service manifest
MANIFEST_PATH = "/var/www/gentechlabs/.well-known/x402-bazaar"
try:
    with open(MANIFEST_PATH) as f:
        MANIFEST = json.load(f)
    SERVICES = MANIFEST.get("services", {})
except (FileNotFoundError, json.JSONDecodeError):
    MANIFEST = {}
    SERVICES = {}

# Internal service routing for paid endpoints
BACKEND_ROUTES = {
    "security": "http://127.0.0.1:8088",
    "deals": "http://127.0.0.1:8080",
    "prices": "http://127.0.0.1:8082",
    "gas": "http://127.0.0.1:8084",
    "tokens": "http://127.0.0.1:8086",
}


def build_payment_required(service_name: str, price_usd: float) -> dict:
    """Build x402 v2 PaymentRequired payload"""
    return {
        "version": "2.0",
        "accepts": [{"scheme": "x402", "network": "base", "asset": "USDC"}],
        "price": {"amount": str(price_usd), "currency": "USD"},
        "payTo": os.getenv("X402_PAYTO_ADDRESS", ""),
        "maxTimeoutSeconds": 300,
        "description": f"Payment for {service_name}",
    }


def payment_required_response(service_name: str, price_usd: float) -> Response:
    """Return HTTP 402 with PAYMENT-REQUIRED header and body"""
    payload = build_payment_required(service_name, price_usd)
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    return Response(
        status_code=402,
        content=json.dumps(payload),
        media_type="application/json",
        headers={"PAYMENT-REQUIRED": payload_b64, "Access-Control-Allow-Origin": "*"},
    )


@app.get("/.well-known/x402-bazaar")
async def serve_manifest():
    return Response(
        content=json.dumps(MANIFEST),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


@app.get("/.well-known/agent-card.json")
async def serve_agent_card():
    try:
        with open("/var/www/gentechlabs/.well-known/agent-card.json") as f:
            return Response(
                content=f.read(),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
    except FileNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/health")
async def health():
    return {"status": "ok", "gateway": "x402-v2", "services": len(SERVICES)}


@app.get("/openapi.json")
async def openapi():
    return {"openapi": "3.0.0", "info": {"title": "GenTech x402 Gateway", "version": "2.0.0"}}


# Dynamic paid endpoint routing
@app.api_route("/v1/{service}/{path:path}", methods=["GET", "POST"])
async def paid_endpoint(service: str, path: str, request: Request):
    service_name = service.replace("_", " ").title()
    service_config = SERVICES.get(service.replace("-", "_"))

    price = float(service_config.get("price_usd", 0.01)) if service_config else 0.01
    x402_token = request.headers.get("x-402-token") or request.headers.get("X-402-Token")

    # No token → return 402 with payment requirements
    if not x402_token:
        return payment_required_response(service_name, price)

    # Verify token (simplified — in production validate via Bazaar API)
    try:
        parts = x402_token.split(".")
        if len(parts) < 2:
            return payment_required_response(service_name, price)

        payload_b64 = parts[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload_b64).decode())

        # Check cost matches
        token_cost = Decimal(str(decoded.get("cost", 0)))
        if token_cost < Decimal(str(price)):
            return payment_required_response(service_name, price)

    except Exception:
        return payment_required_response(service_name, price)

    # Route to backend service
    backend = BACKEND_ROUTES.get(service)
    if not backend:
        return {"service": service, "path": path, "status": "available",
                "price_usd": price, "paid": True}

    # Proxy to backend
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            backend_path = f"/{path}" if path else "/"
            url = f"{backend}{backend_path}"
            params = dict(request.query_params)
            headers = {
                "X-Real-IP": request.client.host if request.client else "unknown",
                "X-402-Token": x402_token,
            }

            if request.method == "GET":
                resp = await client.get(url, params=params, headers=headers)
            else:
                body = await request.body()
                resp = await client.post(url, content=body,
                                         headers=headers,
                                         params=params)

            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type", "application/json"),
            )

    except httpx.RequestError as e:
        return {"error": f"Backend unavailable: {str(e)}", "service": service,
                "status": "degraded"}


@app.get("/status")
async def status():
    backend_status = {}
    for name, url in BACKEND_ROUTES.items():
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                r = await c.get(f"{url}/health")
                backend_status[name] = "ok" if r.status_code == 200 else "degraded"
        except Exception:
            backend_status[name] = "down"

    return {
        "gateway": "x402-v2",
        "status": "operational",
        "services": list(SERVICES.keys()),
        "backends": backend_status,
    }


@app.get("/")
async def root():
    return {
        "name": "GenTech x402 Gateway",
        "version": "2.0.0",
        "endpoints": {
            "/health": "Health check",
            "/status": "Backend status",
            "/.well-known/x402-bazaar": "Service manifest",
            "/v1/{service}/{path}": "Paid endpoint (requires x-402-token header)",
        },
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
