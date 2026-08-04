"""
x402 API Gateway v2.0 — Unified payment gateway for GenTech Labs x402 endpoints
Serves on port 8090 behind api.gentechlabs.net
"""

import json
import os
import base64
import hmac
import hashlib
import time
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal

app = FastAPI(title="GenTech x402 Gateway", version="2.0.0", openapi_url=None, docs_url=None, redoc_url=None)

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
# Maps manifest service key -> (backend base, public path prefix, backend path prefix)
# The FastAPI route splits /v1/{service}/{path}; `path` arrives as e.g.
# "score/0x..." for token_security or "price/ETH" for market_intelligence.
BACKEND_ROUTES = {
    "token_security": ("http://127.0.0.1:8088", "score/", "/v1/score/"),
    "market_intelligence": ("http://127.0.0.1:8082", "price/", "/v1/price/"),
    "agent_discovery": ("http://127.0.0.1:8091", "search", "/v1/agents/search"),
    "defi_lp_analytics": ("http://127.0.0.1:8092", "lp/", "/v1/defi/lp/"),
    "wallet_analysis": ("http://127.0.0.1:8093", "portfolio/", "/v1/wallet/portfolio/"),
    "nft_search": ("http://127.0.0.1:8094", "search", "/v1/nft/search"),
    "treasury_defender": ("http://127.0.0.1:8096", "defender/", "/v1/defender/"),
    "lineage_guard": ("http://127.0.0.1:8095", "lineage/", "/v1/lineage/"),
}

# Public URL segment (first path element after /v1/) -> manifest service key
URL_TO_SERVICE = {
    "security": "token_security",
    "market": "market_intelligence",
    "agents": "agent_discovery",
    "defi": "defi_lp_analytics",
    "wallet": "wallet_analysis",
    "nft": "nft_search",
    "defender": "treasury_defender",
    "lineage": "lineage_guard",
}


def build_payment_required(service_name: str, price_usd: float) -> dict:
    """Build x402 v2 PaymentRequired payload — compliant with Agentic Market validator"""
    price_atomic = int(price_usd * 1000000)  # USDC has 6 decimals
    return {
        "x402Version": 2,
        "resource": {
            "url": f"https://api.gentechlabs.net/v1/{service_name.lower().replace(' ', '-')}",
            "description": f"GenTech Labs x402 — {service_name}",
            "mimeType": "application/json"
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": "eip155:8453",
                "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "amount": str(price_atomic),
                "payTo": os.getenv("X402_PAYTO_ADDRESS", "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734"),
                "maxTimeoutSeconds": 300,
                "extra": {
                    "name": "USD Coin",
                    "version": "2"
                }
            }
        ],
        "extensions": {
            "bazaar": {
                "bazaarResourceServerExtension": True,
                "discoveryUrl": "https://api.gentechlabs.net/.well-known/x402-bazaar",
                "info": {
                    "title": "GenTech Labs x402 Gateway",
                    "description": "Pay-per-call API gateway with 7 services across Base Network. Token security, wallet analysis, agent discovery, market intelligence, DeFi LP analytics, NFT search, treasury defense.",
                    "version": MANIFEST.get("version", "9.0.0"),
                    "x402Version": 2,
                    "seller": {
                        "name": "GenTech Labs",
                        "website": "https://gentechlabs.net"
                    },
                    "input": {
                        "example": {
                            "address": "0x1234567890abcdef1234567890abcdef12345678"
                        }
                    },
                    "output": {
                        "description": "Returns a JSON object with the requested service result or an error message.",
                        "example": {
                            "success": True,
                            "data": {
                                "risk": "low",
                                "score": 85
                            }
                        }
                    }
                },
                "schema": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "object"},
                        "error": {"type": "string"}
                    }
                }
            }
        }
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


def extract_proof(request: Request) -> str | None:
    """Extract a payment proof from standard x402 headers.

    Accepts the v2 convention (Authorization: x402 <json>), the CDP SDK
    PAYMENT-SIGNATURE header (base64 JSON), and the earlier X-Payment
    convention. Returns the raw proof string or None.
    """
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("x402 "):
        return auth[5:].strip()
    # CDP SDK v2 sends the payment payload here (base64-encoded JSON)
    psig = request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("payment-signature")
    if psig:
        return psig.strip()
    # X-Payment header may carry the proof directly (older convention)
    xpay = request.headers.get("X-Payment") or request.headers.get("X-PAYMENT")
    if xpay:
        return xpay.strip()
    # Legacy private header (kept for backward compat with our own SDK v1)
    legacy = request.headers.get("x-402-token") or request.headers.get("X-402-Token")
    if legacy:
        return legacy.strip()
    return None


def verify_proof_via_cdp(proof_str: str, expected_price: float) -> tuple[bool, str]:
    """Verify a payment proof against the CDP x402 facilitator.

    Returns (valid, reason). This is the production path — the facilitator
    confirms the EIP-3009 signature and settlement validity on-chain.
    """
    cdp_key = os.getenv("CDP_API_KEY", "")
    cdp_secret = os.getenv("CDP_API_KEY_SECRET", "")
    cdp_key_id = os.getenv("CDP_API_KEY_ID", "")
    if not cdp_key:
        return False, "CDP_API_KEY not configured"

    # The x402 proof sent by a client is a JSON envelope. The CDP SDK
    # (PAYMENT-SIGNATURE header) base64-encodes it; the Authorization: x402
    # convention sends it raw. Handle both.
    try:
        proof = json.loads(proof_str)
    except json.JSONDecodeError:
        # Not raw JSON — try base64-decoding (CDP SDK v2 PAYMENT-SIGNATURE)
        try:
            import base64 as _b64
            decoded = _b64.b64decode(proof_str + "=" * (-len(proof_str) % 4)).decode("utf-8")
            proof = json.loads(decoded)
        except Exception:
            return False, "proof is not valid JSON or base64 JSON"

    # If it's already the facilitator-style payload, pass through; otherwise
    # wrap it as paymentPayload. The CDP /verify endpoint accepts the full
    # envelope (paymentPayload + paymentRequirements).
    payload = proof if "paymentPayload" in proof else {"paymentPayload": proof}

    # Build the full CDP envelope. CDP /verify and /settle require
    # { x402Version, paymentPayload, paymentRequirements }. The payment
    # payload (paymentPayload) already carries the accepted payment option;
    # paymentRequirements must be THAT accepted option object directly
    # (with scheme at the top level) — not wrapped in an "accepts" array.
    try:
        _pp = payload.get("paymentPayload", payload)
        _ver = _pp.get("x402Version", 2)
        _accepted_opt = _pp.get("accepted", {})
        if _accepted_opt:
            payload = {
                "x402Version": _ver,
                "paymentPayload": _pp,
                "paymentRequirements": _accepted_opt,
            }
    except Exception:
        pass

    # Build the requirements side from our known challenge (cheap local check
    # before hitting the facilitator)
    try:
        accepted = payload["paymentPayload"].get("accepted", payload["paymentPayload"])
        amount = str(accepted.get("amount", "0"))
        pay_to = accepted.get("payTo", "")
    except (KeyError, TypeError):
        return False, "proof missing accepted fields"

    # Local structural checks (fast fail before remote call)
    if Decimal(amount) < Decimal(str(int(expected_price * 1000000))):
        return False, f"amount {amount} below required price"

    headers = {}
    if cdp_secret:
        # CDP requires a JWT (EdDSA for Ed25519 keys, ES256 for EC PEM keys),
        # signed with the API key secret, with a `uris` claim binding the
        # request method/host/path. The JWT is PATH-BOUND — a token minted for
        # /verify will be rejected on /settle, so we mint one per path.
        try:
            import base64 as _b64, secrets as _secrets
            from nacl.signing import SigningKey

            def _b64url(data: bytes) -> str:
                return _b64.urlsafe_b64encode(data).rstrip(b"=").decode()

            # Detect key type: base64 Ed25519 (64 bytes) vs PEM EC
            try:
                decoded = _b64.b64decode(cdp_secret)
                is_ed25519 = len(decoded) == 64
            except Exception:
                is_ed25519 = False

            def _jwt(op_path: str) -> str:
                nonlocal _b64url
                now = int(time.time())
                nonce = _secrets.token_hex(16)
                host = "api.cdp.coinbase.com"
                method = "POST"
                if is_ed25519:
                    seed = decoded[:32]
                    signing_key = SigningKey(seed)
                    header = {"alg": "EdDSA", "kid": cdp_key_id, "typ": "JWT", "nonce": nonce}
                    claims = {
                        "sub": cdp_key_id, "iss": "cdp", "aud": "cdp_service",
                        "uris": [f"{method} {host}{op_path}"],
                        "iat": now, "nbf": now, "exp": now + 120,
                    }
                    signing_input = f"{_b64url(json.dumps(header).encode())}.{_b64url(json.dumps(claims).encode())}"
                    sig = signing_key.sign(signing_input.encode()).signature
                    return f"{signing_input}.{_b64url(sig)}"
                else:
                    # PEM EC key → ES256
                    from cryptography.hazmat.primitives import serialization, hashes
                    from cryptography.hazmat.primitives.asymmetric import ec, utils
                    from cryptography.hazmat.backends import default_backend
                    _raw_key = serialization.load_pem_private_key(cdp_secret.encode(), password=None, backend=default_backend())
                    key = _raw_key  # type: ignore[assignment]
                    assert isinstance(key, ec.EllipticCurvePrivateKey)
                    header = {"alg": "ES256", "kid": cdp_key_id, "typ": "JWT", "nonce": nonce}
                    claims = {
                        "sub": cdp_key_id, "iss": "cdp", "aud": "cdp_service",
                        "uris": [f"{method} {host}{op_path}"],
                        "iat": now, "nbf": now, "exp": now + 120,
                    }
                    signing_input = f"{_b64url(json.dumps(header).encode())}.{_b64url(json.dumps(claims).encode())}"
                    der_sig = key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
                    r, s = utils.decode_dss_signature(der_sig)
                    sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
                    return f"{signing_input}.{_b64url(sig)}"

            headers = {"Authorization": f"Bearer {_jwt('/platform/v2/x402/verify')}"}
        except Exception as e:
            return False, f"CDP JWT generation failed: {e}"
    else:
        headers = {"Authorization": f"Bearer {cdp_key}"}

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                "https://api.cdp.coinbase.com/platform/v2/x402/verify",
                json=payload,
                headers={**headers, "Content-Type": "application/json"},
            )
        if resp.status_code == 200:
            # Verify succeeded. Now SETTLE so the CDP Bazaar indexes us —
            # indexing runs after settle completes, verify alone is not enough.
            # MUST use a fresh JWT bound to /settle (the /verify JWT is rejected).
            try:
                settle_headers = {"Authorization": f"Bearer {_jwt('/platform/v2/x402/settle')}"}
                with httpx.Client(timeout=30) as client:
                    settle_resp = client.post(
                        "https://api.cdp.coinbase.com/platform/v2/x402/settle",
                        json=payload,
                        headers={**settle_headers, "Content-Type": "application/json"},
                    )
                if settle_resp.status_code == 200:
                    return True, "verified + settled"
                return True, f"verified (settle returned {settle_resp.status_code})"
            except Exception as e:
                return True, f"verified (settle failed: {e})"
        return False, f"facilitator returned {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, f"facilitator unreachable: {e}"


def verify_proof_simulation(proof_str: str, expected_price: float) -> tuple[bool, str]:
    """Verify a proof using the local HMAC secret (simulation mode).

    Matches the proof format produced by our SDK / ARC gateway in dev:
    HMAC(amount:recipient:nonce:validAfter:validBefore, GATEWAY_SECRET).
    """
    secret = os.getenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    try:
        proof = json.loads(proof_str)
    except json.JSONDecodeError:
        return False, "proof is not valid JSON"

    amount = str(proof.get("amount", "0"))
    recipient = proof.get("recipient", "")
    nonce = str(proof.get("nonce", ""))
    valid_after = int(proof.get("validAfter", 0) or 0)
    valid_before = int(proof.get("validBefore", 0) or 0)
    signature = proof.get("signature", "")

    now = int(time.time())
    if valid_after and now < valid_after:
        return False, "not yet valid"
    if valid_before and now > valid_before:
        return False, "expired"

    if Decimal(amount) < Decimal(str(int(expected_price * 1000000))):
        return False, "amount below required price"

    expected = hmac.new(
        secret.encode(),
        f"{amount}:{recipient}:{nonce}:{valid_after}:{valid_before}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False, "invalid signature"
    return True, "verified (simulation)"


@app.get("/.well-known/x402-bazaar")
async def serve_manifest():
    return Response(
        content=json.dumps(MANIFEST),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


@app.get("/.well-known/x402")
async def serve_x402_discovery():
    """Canonical x402 discovery endpoint (v2 spec)."""
    try:
        with open("/var/www/gentechlabs/.well-known/x402.json") as f:
            return Response(
                content=f.read(),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
    except FileNotFoundError:
        raise HTTPException(status_code=404)


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
    """Full OpenAPI spec — free endpoints marked security:[], paid endpoints
    carry the x402 security scheme so x402scan can probe them correctly."""
    free = {"security": []}
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "GenTech Labs x402 Gateway",
            "version": MANIFEST.get("version", "9.0.0"),
            "description": "Pay-per-call API gateway with 7 services across Base Network. Token security, wallet analysis, agent discovery, market intelligence, DeFi LP analytics, NFT search, treasury defense.",
            "contact": {"email": "jordanjones0902@gmail.com", "name": "GenTech Labs", "url": "https://gentechlabs.net"},
        },
        "servers": [{"url": "https://api.gentechlabs.net"}],
        "security": [{"x402": []}],
        "components": {
            "securitySchemes": {
                "x402": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "x402 payment proof. Call without a proof to receive HTTP 402 with payment requirements (USDC on Base). Pay via EIP-3009 and retry with Authorization: x402 <proof>.",
                }
            }
        },
        "paths": {
            "/": {"get": {"summary": "Root", "security": []}},
            "/health": {"get": {"summary": "Health check", "security": []}},
            "/status": {"get": {"summary": "Backend status", "security": []}},
            "/openapi.json": {"get": {"summary": "OpenAPI spec", "security": []}},
            "/.well-known/x402": {"get": {"summary": "x402 discovery", "security": []}},
            "/.well-known/x402-bazaar": {"get": {"summary": "x402 bazaar manifest", "security": []}},
            "/.well-known/agent-card.json": {"get": {"summary": "Agent card", "security": []}},
            "/v1/{service}/{path}": {
                "parameters": [
                    {"name": "service", "in": "path", "required": True, "schema": {"type": "string"}},
                    {"name": "path", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "get": {"summary": "Paid x402 endpoint (service/path)", "responses": {"402": {"description": "Payment required"}, "200": {"description": "OK"}}},
                "post": {"summary": "Paid x402 endpoint (service/path)", "responses": {"402": {"description": "Payment required"}, "200": {"description": "OK"}}},
            },
        },
    }
    return spec


# Dynamic paid endpoint routing
@app.api_route("/v1/{service}/{path:path}", methods=["GET", "POST"])
async def paid_endpoint(service: str, path: str, request: Request):
    service_key = URL_TO_SERVICE.get(service, service)
    service_name = service.replace("_", " ").title()
    service_config = SERVICES.get(service_key)

    price = float(service_config.get("price_usd", 0.01)) if service_config else 0.01
    proof = extract_proof(request)

    # No proof → return 402 with payment requirements
    if not proof:
        return payment_required_response(service_name, price)

    # Verify the proof — production path via CDP facilitator, simulation
    # fallback via local HMAC (matches our SDK/ARC gateway dev flow).
    mode = os.getenv("PAYMENT_VERIFY_MODE", "auto")
    if mode == "simulation":
        valid, reason = verify_proof_simulation(proof, price)
    elif mode == "cdp":
        valid, reason = verify_proof_via_cdp(proof, price)
    else:
        # auto: try CDP when a key exists, else simulation
        if os.getenv("CDP_API_KEY"):
            valid, reason = verify_proof_via_cdp(proof, price)
            if not valid and "CDP_API_KEY not configured" not in reason:
                # CDP said invalid — do NOT fall back to simulation, reject
                return Response(
                    status_code=402,
                    content=json.dumps({"error": "payment_proof_invalid", "reason": reason}),
                    media_type="application/json",
                    headers={"Access-Control-Allow-Origin": "*"},
                )
        valid, reason = verify_proof_simulation(proof, price)

    if not valid:
        return Response(
            status_code=402,
            content=json.dumps({"error": "payment_proof_invalid", "reason": reason}),
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    # Route to backend service
    backend = BACKEND_ROUTES.get(service_key)
    if not backend:
        return {"service": service_key, "path": path, "status": "available",
                "price_usd": price, "paid": True}

    # Proxy to backend
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            backend_base, public_prefix, backend_prefix = backend
            # strip the known public prefix from the path segment, then apply
            # the backend prefix. `path` arrives as e.g. "score/0x..." or "price/ETH"
            rel = path
            if rel.startswith(public_prefix):
                rel = rel[len(public_prefix):]
            backend_path = f"{backend_prefix}{rel}" if rel else backend_prefix.rstrip("/")
            url = f"{backend_base}{backend_path}"
            params = dict(request.query_params)
            headers = {
                "X-Real-IP": request.client.host if request.client else "unknown",
                "X-402-Token": proof or "",
                # Backend expects the proof on this header (rugcheck MVP gate)
                "X-Payment-Proof": proof or "",
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
    for name, route in BACKEND_ROUTES.items():
        base = route[0]  # tuple (base, public_prefix, backend_prefix)
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                # Backends expose health at /v1/health (not /health). Fix Aug 2026.
                r = await c.get(f"{base}/v1/health")
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
