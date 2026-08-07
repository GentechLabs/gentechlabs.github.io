"""Gas Price API — Real-time gas prices for Ethereum, Base, Polygon.

Fixed (Aug 3): was returning hardcoded all-zero gas prices.
Now pulls live gas data from chain-specific sources.
"""
import json
import urllib.request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gas Price API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TIMEOUT = 12


def _rpc_gas_price(rpc_url: str) -> float:
    """Call eth_gasPrice on an EVM RPC, return price in gwei."""
    req = urllib.request.Request(
        rpc_url,
        data=json.dumps({"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        d = json.loads(resp.read())
    wei = int(d["result"], 16)
    return round(wei / 1e9, 2)  # gwei


def _fetch_ethereum() -> float:
    # Etherscan V2 requires a key; fall back to public RPC.
    return _rpc_gas_price("https://ethereum-rpc.publicnode.com")


def _fetch_base() -> float:
    return _rpc_gas_price("https://mainnet.base.org")


def _fetch_polygon() -> float:
    """Polygon gas station V2 — standard maxFee gwei."""
    req = urllib.request.Request(
        "https://gasstation.polygon.technology/v2",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        d = json.loads(resp.read())
    return round(d["standard"]["maxFee"], 2)


@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.1.0", "service": "gas-price"}


@app.get("/v1/gas")
async def gas():
    """Live gas prices (gwei) for ethereum, base, polygon."""
    result: dict = {"ethereum": 0, "base": 0, "polygon": 0}
    errors: dict = {}

    try:
        result["ethereum"] = _fetch_ethereum()
    except Exception as e:
        errors["ethereum"] = str(e)
    try:
        result["base"] = _fetch_base()
    except Exception as e:
        errors["base"] = str(e)
    try:
        result["polygon"] = _fetch_polygon()
    except Exception as e:
        errors["polygon"] = str(e)

    out = {"gas_prices": result, "unit": "gwei", "source": "live-rpc"}
    if errors:
        out["errors"] = errors
    return out


@app.get("/v1/gas/{chain}")
async def gas_chain(chain: str):
    """Live gas price for a single chain: ethereum | base | polygon."""
    chain = chain.lower()
    fetchers = {
        "ethereum": _fetch_ethereum,
        "eth": _fetch_ethereum,
        "base": _fetch_base,
        "polygon": _fetch_polygon,
        "matic": _fetch_polygon,
    }
    fn = fetchers.get(chain)
    if not fn:
        return {"error": f"unsupported chain '{chain}'", "supported": list(fetchers.keys())}
    try:
        gwei = fn()
        return {"chain": chain, "gas_price_gwei": gwei, "unit": "gwei", "source": "live-rpc"}
    except Exception as e:
        return {"chain": chain, "error": str(e)}
