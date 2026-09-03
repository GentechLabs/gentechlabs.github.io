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

# =============================================================================
# HUMAN API-KEY TIER (Priority #1 income — converts x402-only to human-payable)
# -----------------------------------------------------------------------------
# Humans can't hold agent wallets, so they can't pay via x402. This tier lets a
# human buy an API key (card via Stripe, or self-serve issue) and call the same
# 13 endpoints with `Authorization: Bearer <api_key>`. x402 stays intact for
# agents — this is purely additive.
#
# Key store: a JSON file keyed by api-key-id → {key_hash, tier, email, plan,
# monthly_limit, used_this_month, month_key, revoked, created_at}. Only the
# SHA-256 hash of the key is stored (never the plaintext). Usage is tracked
# per key+month for rate limiting.
# =============================================================================
import secrets as _secrets
import threading as _threading

_KEYS_DIR = os.getenv("HUMAN_KEYS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "human-keys"))
_KEYS_FILE = os.path.join(_KEYS_DIR, "api_keys.json")
os.makedirs(_KEYS_DIR, exist_ok=True)
_KEYS_LOCK = _threading.Lock()

# Pricing tiers (mirrors handoff recommendation)
HUMAN_PLANS = {
    "free":   {"monthly_calls": 50,    "desc": "Free trial — 50 calls/mo"},
    "basic":  {"monthly_calls": 5000,  "desc": "$19/mo — 5,000 calls"},
    "unlimited": {"monthly_calls": None, "desc": "$99/mo — unlimited"},
}


def _load_keys() -> dict:
    try:
        with open(_KEYS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_keys(keys: dict):
    tmp = _KEYS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(keys, f, indent=2)
    os.replace(tmp, _KEYS_FILE)


def _month() -> str:
    return time.strftime("%Y-%m")


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def issue_human_key(plan: str = "free", label: str = "") -> dict | None:
    """Create a new human API key. Returns the plaintext key ONCE (the caller
    must deliver it to the buyer). Only the hash is stored.
    Returns None if the plan is unknown."""
    if plan not in HUMAN_PLANS:
        return None
    raw = "gt_" + _secrets.token_hex(24)
    key_hash = hash_key(raw)
    key_id = "k_" + _secrets.token_hex(6)
    now = int(time.time())
    with _KEYS_LOCK:
        keys = _load_keys()
        keys[key_id] = {
            "hash": key_hash,
            "plan": plan,
            "label": label,
            "enabled": True,
            "used_this_month": 0,
            "month": _month(),
            "created_at": now,
        }
        _save_keys(keys)
    return {"id": key_id, "key": raw, "plan": plan, **HUMAN_PLANS[plan]}


def revoke_human_key(key_id: str) -> bool:
    with _KEYS_LOCK:
        keys = _load_keys()
        if key_id not in keys:
            return False
        keys[key_id]["enabled"] = False
        _save_keys(keys)
    return True


def list_human_keys() -> list[dict]:
    with _KEYS_LOCK:
        keys = _load_keys()
    out = []
    for k, v in keys.items():
        out.append({
            "id": k, "plan": v.get("plan"), "label": v.get("label"),
            "enabled": v.get("enabled"), "used_this_month": v.get("used_this_month", 0),
            "month": v.get("month"), "created_at": v.get("created_at"),
        })
    return out


def verify_human_key(raw_key: str) -> dict | None:
    """Validate a raw key against the store, enforce plan monthly limit, and
    increment usage. Returns a normalized {key_id, plan} dict or None."""
    if not raw_key:
        return None
    key_hash = hash_key(raw_key)
    with _KEYS_LOCK:
        keys = _load_keys()
        for k, v in keys.items():
            if v.get("hash") != key_hash:
                continue
            if not v.get("enabled", True):
                return None
            limit = HUMAN_PLANS.get(v.get("plan", "free"), {}).get("monthly_calls")
            m = _month()
            if v.get("month") != m:
                v["month"] = m
                v["used_this_month"] = 0
            if limit is not None and v.get("used_this_month", 0) >= limit:
                return {"key_id": k, "plan": v.get("plan"), "quota_exceeded": True}
            v["used_this_month"] = v.get("used_this_month", 0) + 1
            _save_keys(keys)
            return {"key_id": k, "plan": v.get("plan"), "quota_exceeded": False}
    return None


def extract_human_key(request: Request) -> str | None:
    """Read the API key from `Authorization: Bearer <key>` or `X-API-Key: <key>`."""
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    xk = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if xk:
        return xk.strip()
    return None


def admin_authorized(request: Request) -> bool:
    """Gate the admin key-management endpoints behind the configured admin key."""
    admin = os.getenv("GATEWAY_ADMIN_KEY", "")
    if not admin:
        return False
    supplied = extract_human_key(request)
    if not supplied:
        return False
    return hmac.compare_digest(supplied, admin)



# --- OKX Pay SDK integration (Sep 3, 2026 — Treasury Steward directive) -------------
# OKX's test agent now auto-pays and expects settlement via THEIR facilitator
# (/api/v6/pay/x402/*), verified on their stack. The official SDK
# (`okxweb3-app-x402`) ships OKXFacilitatorClient; we wire it additively:
#   - Gate: OKX_PAY_SDK=1 env (rollback = unset → PayAI path resumes)
#   - Creds: OKX_API_KEY / OKX_SECRET_KEY / OKX_PASSPHRASE in gentech .env
#     (Jordan-gated — portal application; absent creds → PayAI fallback)
#   - Scope: /v1/okx/* alias only; generic routes keep the multi-rail proof rails.

async def verify_settle_via_okx(proof: str, price: float, resource_url: str):
    """Verify + settle a payment payload via the OKX facilitator.

    Returns (valid: bool, reason: str, settled: bool). Uses the official
    `okxweb3-app-x402` SDK (OKXFacilitatorClient). Credentials from env;
    if the SDK or creds are missing, returns (False, "okx_sdk_unavailable")
    so the caller can fall back to the PayAI rail (multi-rail stays intact).
    """
    api_key = os.getenv("OKX_API_KEY", "")
    secret_key = os.getenv("OKX_SECRET_KEY", "")
    passphrase = os.getenv("OKX_PASSPHRASE", "")
    if not (api_key and secret_key and passphrase):
        return False, "okx_credentials_missing"
    try:
        from x402.http.okx_facilitator_client import (
            OKXFacilitatorClient,
            OKXFacilitatorConfig,
        )
        from x402.http.okx_auth import OKXAuthConfig
    except ImportError:
        return False, "okx_sdk_unavailable"

    try:
        import httpx as _httpx
        payload = json.loads(proof) if proof.strip().startswith("{") else {
            "x402Version": 2,
            "resource": {"url": resource_url},
            "payload": proof,
        }
        network = os.getenv("OKX_SETTLEMENT_NETWORK", "eip155:196")
        asset = os.getenv("OKX_SETTLEMENT_ASSET", "0x779ddc60ec685bcbec1ea0d1a7094293e5cfd736")
        pay_to = os.getenv("PAY_TO_XLAYER", os.getenv("PAY_TO_EVM", "0x7ebff188f2Eba16518C02864589b1403a5d1296a"))
        amount_units = str(int(price * 1_000_000))
        requirements = {
            "scheme": "exact",
            "network": network,
            "asset": asset,
            "amount": amount_units,
            "payTo": pay_to,
            "resource": resource_url,
        }
        config = OKXFacilitatorConfig(
            auth=OKXAuthConfig(api_key=api_key, secret_key=secret_key, passphrase=passphrase),
            sync_settle=True,
        )
        client = OKXFacilitatorClient(config)
        try:
            verify_resp = await client.verify(payload, requirements)
            if not getattr(verify_resp, "isValid", False):
                reason = getattr(verify_resp, "invalidReason", None) or "verify_failed"
                return False, f"okx_verify_failed: {reason}"
            settle = await client.settle(payload, requirements)
            success = getattr(settle, "success", False)
            tx = getattr(settle, "transaction", None) or getattr(settle, "transactionHash", "")
            if not success:
                reason = getattr(settle, "errorReason", None) or "settle_failed"
                return False, f"okx_settle_failed: {reason}"
            return True, tx or "okx_settled"
        finally:
            await client.aclose()
    except Exception as e:  # noqa: BLE001 — facilitator errors must never 500 the gateway
        return False, f"okx_facilitator_error: {str(e)[:200]}"


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
    "sie_inference": ("http://127.0.0.1:8097", "", "/v1/"),
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
    "sie": "sie_inference",
}


# --- Multi-network payment support -------------------------------------
# CAIP-2 network registry. Each entry describes one settlement rail we can
# actually receive USDC on. A network is only advertised in `accepts` when a
# payTo address is configured for it — never advertise a rail we can't settle.
NETWORKS = {
    "base": {
        "network": "eip155:8453",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "decimals": 6,
        "payto_env": "X402_PAYTO_ADDRESS",
        "payto_default": "0x7ebff188f2Eba16518C02864589b1403a5d1296a",
        "extra": {"name": "USD Coin", "version": "2"},
    },
    "algorand": {
        # CAIP-2 genesis hash prefix for Algorand mainnet. MUST match the full
        # string the GoPlausible facilitator advertises (/supported) so proofs
        # verify — a truncated genesis-hash segment makes the rail unmatchable.
        "network": "algorand:wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8=",
        # USDC on Algorand is ASA (asset id), not a contract address
        "asset": "31566704",
        "decimals": 6,
        "payto_env": "X402_PAYTO_ALGORAND",
        "payto_default": "",
        "extra": {"name": "USD Coin", "assetType": "ASA", "assetId": 31566704,
                  "tag": "x402-global-challenge"},
    },
    "avalanche": {
        # Avalanche C-Chain mainnet. Settled via the PayAI facilitator
        # (facilitator.payai.network) — the rail that lets our Avalanche-listed
        # services (AgentScan #1770, ERC-8004 identities) actually receive USDC.
        "network": "eip155:43114",
        # Native USDC on Avalanche C-Chain (Circle-issued, 6 decimals)
        "asset": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "decimals": 6,
        "payto_env": "X402_PAYTO_AVALANCHE",
        "payto_default": "",
        "extra": {"name": "USD Coin", "version": "2"},
    },
    "xlayer": {
        # X Layer mainnet (OKX). Settled via the PayAI facilitator. Our ERC-8004
        # agent identities live on XLayer — this rail lets those services settle.
        "network": "eip155:196",
        # USDT0 (OKX's official settlement stablecoin on X Layer, 6 decimals).
        # OKX A2MCP spec requires this exact asset for X Layer settlement.
        "asset": "0x779ded0c9e1022225f8e0630b35a9b54be713736",
        "decimals": 6,
        "payto_env": "X402_PAYTO_XLAYER",
        "payto_default": "",
        "extra": {"name": "USD₮0", "version": "1"},
    },
    "solana": {
        # Solana mainnet. Settled via the PayAI facilitator (supports
        # solana:5eykt4...). USDC on Solana is an SPL token (mint EPjFWdd5...),
        # not a contract address — payTo is a Solana address.
        "network": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
        "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint on Solana
        "decimals": 6,
        "payto_env": "X402_PAYTO_SOLANA",
        "payto_default": "",
        "extra": {"name": "USD Coin", "version": "2"},
    },
}

# Order matters — first entry is the preferred rail for clients that take
# accepts[0] blindly. X Layer first (OKX requires it for ERC-8004 services).
_DEFAULT_NETWORKS = "xlayer"


def enabled_networks() -> list[dict]:
    """Resolve X402_NETWORKS into concrete, settleable network configs.

    Unknown names are ignored rather than fatal. Networks without a payTo
    address are dropped. Always falls back to Base so the gateway can never
    end up advertising zero rails.
    """
    raw = os.getenv("X402_NETWORKS", _DEFAULT_NETWORKS)
    names = [n.strip().lower() for n in raw.split(",") if n.strip()]
    resolved = []
    for name in names:
        cfg = NETWORKS.get(name)
        if cfg is None:
            continue  # unknown network — ignore, don't crash the gateway
        payto = os.getenv(cfg["payto_env"], cfg["payto_default"])
        if not payto:
            continue  # can't receive here — don't advertise it
        resolved.append({**cfg, "payTo": payto})
    if not resolved:
        base = NETWORKS["base"]
        resolved = [{**base, "payTo": os.getenv(base["payto_env"], base["payto_default"])}]
    return resolved


def is_network_accepted(network: str | None) -> bool:
    """True when a proof's CAIP-2 network is one we currently accept.

    Proofs that omit `network` are accepted for backward compatibility with
    older clients that predate multi-network support.
    """
    if not network:
        return True
    return any(n["network"] == network for n in enabled_networks())


def build_payment_required(service_name: str, price_usd: float, request_url: str | None = None, okx: bool | None = None) -> dict:
    """Build x402 v2 PaymentRequired payload — compliant with Agentic Market validator.

    OKX-compliant mode: OKX's A2MCP validator rejects multi-network accepts and
    unknown extension blocks (3rd rejection, Aug 25). When enabled, emit a
    SINGLE-network X Layer challenge with resource.url set to the exact probed
    request URL and NO extensions block — matching OKX's documented schema
    (web3.okx.com/onchainos/dev-docs/okxai/howtomcp).

    `okx` resolution order: explicit arg > X_OKX_COMPLIANT env > False.
    The /v1/okx/* alias routes pass okx=True unconditionally so OKX probes get
    the single-rail challenge even while normal routes serve multi-rail
    challenges for Dexter / CDP Bazaar (Aug 30 multi-rail requirement).
    """
    price_atomic = int(price_usd * 1000000)  # USDC has 6 decimals

    if okx is None:
        okx = os.getenv("X_OKX_COMPLIANT", "").lower() in ("1", "true", "yes", "on")
    if okx:
        # OKX validator: exactly one network (X Layer / eip155:196), no extensions.
        xlayer = NETWORKS["xlayer"]
        payto = os.getenv(xlayer["payto_env"], xlayer["payto_default"])
        if not payto:
            payto = NETWORKS["base"]["payto_default"]  # same settlement wallet
        amount = str(int(round(price_usd * (10 ** xlayer["decimals"]))))
        resource_url = request_url or f"https://api.gentechlabs.net/v1/{service_name.lower().replace(' ', '-')}"
        return {
            "x402Version": 2,
            "resource": {
                "url": resource_url,
                "description": f"GenTech Labs x402 - {service_name}",
                "mimeType": "application/json",
            },
            "accepts": [{
                "scheme": "exact",
                "network": xlayer["network"],
                "asset": xlayer["asset"],
                "amount": str(int(round(price_usd * (10 ** xlayer["decimals"])))),
                "payTo": payto,
                "maxTimeoutSeconds": 300,
                "extra": xlayer["extra"],
            }],
        }

    accepts = []
    for net in enabled_networks():
        accepts.append({
            "scheme": "exact",
            "network": net["network"],
            "asset": net["asset"],
            "amount": str(int(round(price_usd * (10 ** net["decimals"])))),
            "payTo": net["payTo"],
            "maxTimeoutSeconds": 300,
            "extra": net["extra"],
        })
    return {
        "x402Version": 2,
        "resource": {
            "url": f"https://api.gentechlabs.net/v1/{service_name.lower().replace(' ', '-')}",
            "description": f"GenTech Labs x402 - {service_name}",
            "mimeType": "application/json",
            "serviceName": f"GenTech {service_name}",
            "tags": ["x402", "treasury", "defi", "yield", "intelligence"],
            "iconUrl": "https://gentechlabs.net/gentech-logo.png"
        },
        "accepts": accepts,
        "extensions": {
            "bazaar": {
                "bazaarResourceServerExtension": True,
                "discoveryUrl": "https://api.gentechlabs.net/.well-known/x402-bazaar",
                "info": {
                    "title": "GenTech Labs x402 Gateway",
                    "description": "Cross-chain agentic treasury + x402 payment infrastructure for the agent economy. Pay-per-call DeFi intelligence, yield scanning, wallet analysis, agent identity/trust, and market data across 7 chains - the infrastructure layer agents hire to manage capital and route payments, not another chatbot. Treasury-first, utility-second, backed by real on-chain revenue.",
                    "version": MANIFEST.get("version", "9.0.0"),
                    "x402Version": 2,
                    "seller": {
                        "name": "GenTech Labs",
                        "website": "https://gentechlabs.net"
                    },
                    "input": {
                        "type": "http",
                        "method": "GET",
                        "pathParams": {
                            "address": {"type": "string", "description": "Token or wallet address to score"}
                        },
                        "example": {
                            "address": "0x1234567890abcdef1234567890abcdef12345678"
                        }
                    },
                    "output": {
                        "type": "json",
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
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "type": {"const": "http", "type": "string"},
                                "method": {"enum": ["GET", "HEAD", "DELETE"], "type": "string"},
                                "queryParams": {"type": "object", "additionalProperties": True},
                                "pathParams": {"type": "object", "additionalProperties": True},
                                "headers": {"type": "object", "additionalProperties": True}
                            },
                            "required": ["type", "method"]
                        },
                        "output": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "example": {"type": "object"}
                            },
                            "required": ["type"]
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    }


def payment_required_response(service_name: str, price_usd: float, request_url: str | None = None, okx: bool | None = None) -> Response:
    """Return HTTP 402 with PAYMENT-REQUIRED header and body.

    x402 v2 only. NOTE (Aug 24, 2026): we previously ALSO emitted a
    `WWW-Authenticate: Payment` (MPP) challenge here for dual-rail support.
    That broke OKX A2MCP review — OKX's validator branches to the
    WWW-Authenticate path first (Priority 1 in their protocol), and our MPP
    challenge was incomplete (no `request=` payload, no `expires=`), so the
    sandbox reported "did not return the x402 challenge in the response
    header." Fix: emit ONLY the PAYMENT-REQUIRED x402 v2 header so the
    validator parses the correct challenge. See okx-a2a-daemon-ops skill ref
    2026-08-24-challenge-header-not-detected.md.

    X_OKX_COMPLIANT=1 additionally collapses the challenge to a single X Layer
    network with no extensions block (see build_payment_required). The okx arg
    overrides the env — the /v1/okx/* alias passes okx=True unconditionally.
    """
    payload = build_payment_required(service_name, price_usd, request_url, okx=okx)
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    return Response(
        status_code=402,
        content=json.dumps(payload),
        media_type="application/json",
        headers={
            "PAYMENT-REQUIRED": payload_b64,
            "Access-Control-Allow-Origin": "*",
        },
    )


def extract_mpp_credential(request: Request) -> dict | None:
    """Extract an MPP credential from `Authorization: Payment <credential>`.

    MPP (Machine Payments Protocol) uses the HTTP `Payment` auth scheme:
    `Authorization: Payment <base64-json-credential>`. Returns the parsed
    credential dict, or None if the header is absent / not an MPP credential.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("payment "):
        return None
    raw = auth.split(" ", 1)[1].strip()
    if not raw:
        return None
    try:
        cred = json.loads(base64.b64decode(raw).decode())
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(cred, dict):
        return None
    cred["scheme"] = "Payment"
    cred["credential"] = raw
    return cred


def verify_mpp_simulation(credential_str: str, expected_price: float) -> tuple[bool, str]:
    """Verify an MPP credential using the local HMAC secret (simulation mode).

    Mirrors verify_proof_simulation: HMAC(amount:recipient:nonce:validAfter:
    validBefore, GATEWAY_SECRET). MPP is payment-method agnostic; we accept
    the EVM method (settles via our USDC rails). This is the dev/simulation
    path — production MPP settlement would go through a facilitator.
    """
    secret = os.getenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    try:
        cred = json.loads(credential_str)
    except json.JSONDecodeError:
        return False, "credential is not valid JSON"

    method = cred.get("method", "")
    if method != "evm":
        return False, f"unsupported MPP method {method!r} (only 'evm' supported)"

    amount = str(cred.get("amount", "0"))
    recipient = cred.get("recipient", "")
    nonce = str(cred.get("nonce", ""))
    valid_after = int(cred.get("validAfter", 0) or 0)
    valid_before = int(cred.get("validBefore", 0) or 0)
    signature = cred.get("signature", "")

    if not is_network_accepted(cred.get("network")):
        return False, f"network {cred.get('network')!r} not accepted"

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
    return True, "verified (mpp simulation)"


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
        proof_network = accepted.get("network")
    except (KeyError, TypeError):
        return False, "proof missing accepted fields"

    # Reject proofs settled on a rail we don't accept, BEFORE any remote call.
    if not is_network_accepted(proof_network):
        return False, f"network {proof_network!r} not accepted"

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


def _proof_network(proof_str: str) -> str | None:
    """Extract the CAIP-2 network a proof claims to be settled on.

    Reads `network` from the accepted payment option (v2 envelope) or the flat
    proof. Used to route a proof to the facilitator that handles its rail.
    """
    try:
        proof = json.loads(proof_str)
    except json.JSONDecodeError:
        try:
            import base64 as _b64
            decoded = _b64.b64decode(proof_str + "=" * (-len(proof_str) % 4)).decode("utf-8")
            proof = json.loads(decoded)
        except Exception:
            return None
    pp = proof.get("paymentPayload", proof) if isinstance(proof, dict) else {}
    accepted = pp.get("accepted", {}) if isinstance(pp, dict) else {}
    if isinstance(accepted, dict) and accepted.get("network"):
        return accepted.get("network")
    if isinstance(pp, dict) and pp.get("network"):
        return pp.get("network")
    if isinstance(proof, dict):
        return proof.get("network")
    return None


GOPLAUSIBLE_FACILITATOR = os.getenv(
    "GOPLAUSIBLE_FACILITATOR_URL",
    "https://facilitator.goplausible.xyz",
)

# PayAI x402 facilitator — settles Avalanche (and other EVM) rails. This is the
# rail that lets our Avalanche-listed services actually receive USDC. Free tier
# $0/mo up to 10K settlements/mo, then $0.001/tx. No API key required.
PAYAI_FACILITATOR = os.getenv(
    "PAYAI_FACILITATOR_URL",
    "https://facilitator.payai.network",
)


def verify_proof_via_payai(proof_str: str, expected_price: float) -> tuple[bool, str]:
    """Verify + settle a proof against the PayAI x402 facilitator.

    Handles Avalanche (eip155:43114) and any other PayAI-supported EVM rail.
    Same {paymentPayload, paymentRequirements} envelope as the GoPlausible path.
    PayAI /verify returns {isValid, invalidReason, invalidMessage}; /settle
    returns {success, transaction, network, payer}.
    """
    try:
        proof = json.loads(proof_str)
    except json.JSONDecodeError:
        try:
            import base64 as _b64
            decoded = _b64.b64decode(proof_str + "=" * (-len(proof_str) % 4)).decode("utf-8")
            proof = json.loads(decoded)
        except Exception:
            return False, "proof is not valid JSON or base64 JSON"

    payload = proof if "paymentPayload" in proof else {"paymentPayload": proof}
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

    # Local structural guard: reject proofs on a rail we don't advertise.
    try:
        accepted = payload["paymentPayload"].get("accepted", payload["paymentPayload"])
        network = accepted.get("network")
    except (KeyError, TypeError):
        network = None
    if not is_network_accepted(network):
        return False, f"network {network!r} not accepted"

    try:
        with httpx.Client(timeout=20) as client:
            v = client.post(
                f"{PAYAI_FACILITATOR}/verify",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        if v.status_code != 200:
            return False, f"payai verify {v.status_code}: {v.text[:200]}"
        body = v.json()
        if not body.get("isValid", False):
            return False, body.get("invalidReason", "invalid")
        # Verify OK → settle so the payment actually lands.
        try:
            with httpx.Client(timeout=30) as client:
                s = client.post(
                    f"{PAYAI_FACILITATOR}/settle",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            if s.status_code == 200 and s.json().get("success"):
                return True, "verified + settled (payai)"
            return True, f"verified (payai settle {s.status_code})"
        except Exception as e:
            return True, f"verified (payai settle failed: {e})"
    except Exception as e:
        return False, f"payai unreachable: {e}"


def verify_proof_via_goplausible(proof_str: str, expected_price: float) -> tuple[bool, str]:
    """Verify + settle a proof against the GoPlausible x402 facilitator.

    Handles Algorand (AVM) and any non-CDP rail. The GoPlausible /verify and
    /settle endpoints take the same {paymentPayload, paymentRequirements}
    envelope the CDP path already builds, and require no auth. This is the
    path the Algorand Global x402 Challenge counts: settlements must land via
    the GoPlausible facilitator, with the challenge tag on the resource.
    """
    try:
        proof = json.loads(proof_str)
    except json.JSONDecodeError:
        try:
            import base64 as _b64
            decoded = _b64.b64decode(proof_str + "=" * (-len(proof_str) % 4)).decode("utf-8")
            proof = json.loads(decoded)
        except Exception:
            return False, "proof is not valid JSON or base64 JSON"

    payload = proof if "paymentPayload" in proof else {"paymentPayload": proof}
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

    # Local structural guard: reject proofs on a rail we don't advertise.
    try:
        accepted = payload["paymentPayload"].get("accepted", payload["paymentPayload"])
        network = accepted.get("network")
    except (KeyError, TypeError):
        network = None
    if not is_network_accepted(network):
        return False, f"network {network!r} not accepted"

    try:
        with httpx.Client(timeout=20) as client:
            v = client.post(
                f"{GOPLAUSIBLE_FACILITATOR}/verify",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        if v.status_code != 200:
            return False, f"goplausible verify {v.status_code}: {v.text[:200]}"
        body = v.json()
        if not body.get("isValid", False):
            return False, body.get("invalidReason", "invalid")
        # Verify OK → settle so the Bazaar indexes us and the leaderboard counts.
        try:
            with httpx.Client(timeout=30) as client:
                s = client.post(
                    f"{GOPLAUSIBLE_FACILITATOR}/settle",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            if s.status_code == 200 and s.json().get("success"):
                return True, "verified + settled (goplausible)"
            return True, f"verified (goplausible settle {s.status_code})"
        except Exception as e:
            return True, f"verified (goplausible settle failed: {e})"
    except Exception as e:
        return False, f"goplausible unreachable: {e}"


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

    if not is_network_accepted(proof.get("network")):
        return False, f"network {proof.get('network')!r} not accepted"

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
            "description": "Cross-chain agentic treasury + x402 payment infrastructure for the agent economy. Pay-per-call DeFi intelligence, yield scanning, wallet analysis, agent identity/trust, and market data across 7 chains — the infrastructure layer agents hire to manage capital and route payments. Treasury-first, utility-second, backed by real on-chain revenue.",
            "contact": {"email": "jordanjones0902@gmail.com", "name": "GenTech Labs", "url": "https://gentechlabs.net"},
            "x-guidance": "Call /v1/{service}/{path} with a JSON body. Services: token_security (risk score an address), wallet_analysis (portfolio P&L), agent_discovery (search on-chain agents), market_intelligence (token price/volume), defi_lp_analytics (LP position scoring), nft_search (Magic Eden search), treasury_defender (token quarantine). Unauthenticated calls return HTTP 402 with x402 payment requirements (USDC on Base). Pay via EIP-3009 and retry with Authorization: x402 <proof>.",
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
                "get": {
                    "summary": "Paid x402 endpoint (service/path)",
                    "x-payment-info": {
                        "price": {"mode": "fixed", "currency": "USD", "amount": "0.010000"},
                        "protocols": [{"x402": {}}],
                    },
                    "responses": {"402": {"description": "Payment required"}, "200": {"description": "OK"}},
                },
                "post": {
                    "summary": "Paid x402 endpoint (service/path)",
                    "x-payment-info": {
                        "price": {"mode": "fixed", "currency": "USD", "amount": "0.010000"},
                        "protocols": [{"x402": {}}],
                    },
                    "responses": {"402": {"description": "Payment required"}, "200": {"description": "OK"}},
                },
            },
        },
    }
    return spec


# --- Human API-key management endpoints (Priority #1 income) ---------------


@app.post("/v1/human/signup")
async def human_signup(request: Request):
    """Self-serve signup — issue a key. Intended to be called from the
    subscribe page after (or during) a card checkout. Paid plans are issued
    post-Stripe-webhook; free tier can be issued immediately."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    plan = (body.get("plan") or "free").lower()
    label = body.get("label", "")
    # Only allow free self-serve issuance (paid plans go through payment).
    if plan != "free":
        return Response(
            status_code=402,
            content=json.dumps({"error": "paid_plans_require_checkout",
                                "message": f"{plan} is a paid plan — complete checkout first."}),
            media_type="application/json",
        )
    key = issue_human_key("free", label)
    if key is None:
        return Response(status_code=400, content=json.dumps({"error": "unknown_plan"}),
                        media_type="application/json")
    # Return the plaintext key exactly once.
    return Response(
        content=json.dumps({"api_key": key["key"], "id": key["id"], "plan": key["plan"],
                            "monthly_calls": key["monthly_calls"]}),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


@app.get("/v1/human/keys")
async def list_keys(request: Request):
    if not admin_authorized(request):
        return Response(status_code=401, content=json.dumps({"error": "unauthorized"}),
                        media_type="application/json")
    return Response(content=json.dumps({"keys": list_human_keys()}),
                    media_type="application/json",
                    headers={"Access-Control-Allow-Origin": "*"})


@app.post("/v1/human/keys/{key_id}/revoke")
async def revoke_key(key_id: str, request: Request):
    if not admin_authorized(request):
        return Response(status_code=401, content=json.dumps({"error": "unauthorized"}),
                        media_type="application/json")
    ok = revoke_human_key(key_id)
    if not ok:
        return Response(status_code=404, content=json.dumps({"error": "key_not_found"}),
                        media_type="application/json")
    return {"ok": True, "revoked": key_id}


@app.post("/v1/human/keys/issue")
async def issue_key(request: Request):
    """Admin-issued key for any plan (called by a payment webhook or admin)."""
    if not admin_authorized(request):
        return Response(status_code=401, content=json.dumps({"error": "unauthorized"}),
                        media_type="application/json")
    try:
        body = await request.json()
    except Exception:
        body = {}
    plan = (body.get("plan") or "basic").lower()
    label = body.get("label", "")
    key = issue_human_key(plan, label)
    if key is None:
        return Response(status_code=400, content=json.dumps({"error": "unknown_plan"}),
                        media_type="application/json")
    return Response(content=json.dumps({"api_key": key["key"], "id": key["id"], "plan": key["plan"]}),
                    media_type="application/json")


# Dynamic paid endpoint routing
@app.api_route("/v1/okx/{service}/{path:path}", methods=["GET", "POST"])
async def paid_endpoint_okx_alias(service: str, path: str, request: Request):
    """OKX A2MCP probe alias (Sep 2, 2026).

    Serves the SAME paid services as /v1/{service}/* but ALWAYS emits the
    single-network X Layer challenge (okx=True), regardless of the
    X_OKX_COMPLIANT env. Needed because the Aug 30 Dexter settlement fix
    re-enabled multi-rail accepts on normal routes — which OKX's validator
    rejects ("did not return the x402 challenge in the header"). OKX probes
    only the endpoints listed in each agent's serviceList; those now point at
    /v1/okx/* URLs. Payment proofs on X Layer (eip155:196) settle via PayAI
    exactly as before.
    """
    return await paid_endpoint(service, path, request, okx_alias=True)


@app.api_route("/v1/{service}/{path:path}", methods=["GET", "POST"])
async def paid_endpoint(service: str, path: str, request: Request, okx_alias: bool = False):
    service_key = URL_TO_SERVICE.get(service, service)
    service_name = service.replace("_", " ").title()
    service_config = SERVICES.get(service_key)

    price = float(service_config.get("price_usd", 0.01)) if service_config else 0.01
    proof = extract_proof(request)
    mpp_cred = extract_mpp_credential(request)

    # HUMAN API-KEY tier (Priority #1 income). A valid human key skips the 402
    # challenge entirely and routes straight to the backend — the additive path
    # that lets humans buy our APIs. x402/MPP stay for agents.
    human_key = extract_human_key(request)
    if human_key:
        human = verify_human_key(human_key)
        if human is None:
            return Response(
                status_code=401,
                content=json.dumps({"error": "invalid_api_key"}),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        if human.get("quota_exceeded"):
            return Response(
                status_code=429,
                content=json.dumps({"error": "quota_exceeded", "plan": human.get("plan")}),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        return await _route_to_backend(service_key, path, request, f"human:{human.get('key_id')}")

    # No proof → return 402 with payment requirements (dual-rail: x402 + MPP)
    if not proof and not mpp_cred:
        resp = payment_required_response(service_name, price, str(request.url), okx=True if okx_alias else None)
        # MPP dual-rail (Sep 3, Jordan GO): add WWW-Authenticate: Payment challenge
        # ONLY on the generic multi-rail path. The /v1/okx/* alias stays x402-only
        # (OKX validator priority-branches on WWW-Authenticate; incomplete MPP
        # challenges failed our Aug 24 review — see payment_required_response docstring).
        if not okx_alias:
            import base64 as _b64
            mpp_challenge = {
                "intent": "charge",
                "amount": str(int(price * 1_000_000)),
                "currency": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "recipient": os.getenv("PAY_TO_EVM", "0x7ebff188f2Eba16518C02864589b1403a5d1296a"),
                "methodDetails": {"chainId": 8453, "feePayer": False},
            }
            req_b64 = _b64.urlsafe_b64encode(json.dumps(mpp_challenge).encode()).decode().rstrip("=")
            resp.headers["WWW-Authenticate"] = (
                f'Payment realm="api.gentechlabs.net", method="evm", '
                f'intent="charge", request="{req_b64}"'
            )
        return resp

    # MPP credential present → verify via the MPP rail (simulation for now).
    # MPP is payment-method agnostic; we accept the EVM method which settles
    # via our existing USDC rails. Production MPP settlement would go through
    # a facilitator (PayAI etc.) — simulation covers the dev/ARC flow.
    if mpp_cred and not proof:
        valid, reason = verify_mpp_simulation(
            json.dumps({k: v for k, v in mpp_cred.items() if k not in ("scheme", "credential")}),
            price,
        )
        if not valid:
            return Response(
                status_code=402,
                content=json.dumps({"error": "mpp_credential_invalid", "reason": reason}),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        # MPP settled — route to backend (same path as x402 proof)
        return await _route_to_backend(service_key, path, request, proof or mpp_cred.get("credential", ""))

    # Verify the proof — route by the proof's settlement network.
    # - Algorand/other non-EVM rails → GoPlausible facilitator (challenge path)
    # - Avalanche (eip155:43114) → PayAI facilitator (settles our Avalanche rail)
    # - EVM (Base) → CDP facilitator
    # - simulation fallback via local HMAC (matches our SDK/ARC gateway dev flow).
    mode = os.getenv("PAYMENT_VERIFY_MODE", "auto")
    proof_network = _proof_network(proof)
    is_avm = proof_network is not None and proof_network.startswith("algorand:")
    is_avalanche = proof_network == "eip155:43114"
    is_xlayer = proof_network == "eip155:196"
    # OKX Pay SDK path (Sep 3): on the okx alias, verify+settle via THEIR facilitator first.
    if (
        okx_alias
        and is_xlayer
        and os.getenv("OKX_PAY_SDK", "").lower() in ("1", "true", "yes", "on")
    ):
        okx_valid, okx_reason = await verify_settle_via_okx(
            proof, price, str(request.url)
        )
        if okx_valid:
            return await _route_to_backend(service_key, path, request, okx_reason)
        # fall through to PayAI ONLY when creds/SDK are unavailable — an actual
        # verify/settle failure is a rejection, not a fallback (no double-spend risk).
        if okx_reason not in ("okx_credentials_missing", "okx_sdk_unavailable"):
            return Response(
                status_code=402,
                content=json.dumps({"error": "payment_proof_invalid", "reason": okx_reason}),
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
    is_solana = proof_network is not None and proof_network.startswith("solana:")
    if mode == "simulation":
        valid, reason = verify_proof_simulation(proof, price)
    elif mode == "cdp":
        valid, reason = verify_proof_via_cdp(proof, price)
    elif is_avm:
        # Algorand proof → GoPlausible facilitator (required for the x402
        # Global Challenge — settlements must land through GoPlausible).
        valid, reason = verify_proof_via_goplausible(proof, price)
    elif is_avalanche or is_xlayer or is_solana:
        # Avalanche / X Layer / Solana proof → PayAI facilitator (settles our
        # rails so AgentScan-listed + XLayer-identity + Solana services can
        # actually receive USDC). PayAI supports solana:5eykt4... mainnet.
        valid, reason = verify_proof_via_payai(proof, price)
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
        else:
            # no CDP key → simulation (HMAC dev/ARC gateway proof format)
            valid, reason = verify_proof_simulation(proof, price)

    if not valid:
        return Response(
            status_code=402,
            content=json.dumps({"error": "payment_proof_invalid", "reason": reason}),
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    # Route to backend service
    return await _route_to_backend(service_key, path, request, proof or "")


async def _route_to_backend(service_key: str, path: str, request: Request, payment_token: str):
    """Proxy a paid request to the backend service for `service_key`.

    Shared by the x402 proof path and the MPP credential path. `payment_token`
    is the proof/credential string forwarded to the backend on the standard
    x402 headers so downstream services can validate the payment themselves.
    """
    backend = BACKEND_ROUTES.get(service_key)
    if not backend:
        return {"service": service_key, "path": path, "status": "available",
                "paid": True}

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
                "X-402-Token": payment_token,
                # Backend expects the proof on this header (rugcheck MVP gate)
                "X-Payment-Proof": payment_token,
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
        return {"error": f"Backend unavailable: {str(e)}", "service": service_key,
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
            "/v1/{service}/{path}": "Paid endpoint (x402 proof OR human API key)",
            "/v1/human/signup": "Self-serve free trial key (POST {plan, label})",
            "/v1/human/keys": "Admin: list keys (GATEWAY_ADMIN_KEY)",
            "/v1/human/keys/{key_id}/revoke": "Admin: revoke key",
        },
        "human": {
            "auth": "Authorization: Bearer <api_key>",
            "plans": HUMAN_PLANS,
        },
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
