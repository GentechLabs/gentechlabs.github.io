"""
GenTech DeFi Intelligence API
DeFi protocol data and analytics with x402 monetization

Endpoints:
1. GET /protocols - List all DeFi protocols
2. GET /protocols/{id}/tvl - Get protocol TVL over time
3. GET /yields - Get best yield opportunities across chains
4. GET /pools - Get high-value LP pools
5. GET /chains - List supported chains

Pricing: $0.01 per request via x402
Data Source: DefiLlama
"""

from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import os
import asyncio
import aiohttp

app = FastAPI(
    title="GenTech DeFi Intelligence API",
    description="Real-time DeFi protocol data and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Data sources
DEFILLAMA_API = "https://api.llama.fi"

# x402 Pricing
PRICE_PER_REQUEST = "0.000001"

# Cache TTL (seconds)
CACHE_TTL = 300  # 5 minutes

# In-memory cache
cache: Dict[str, tuple[Dict[str, Any], datetime]] = {}

# Pydantic models
class Protocol(BaseModel):
    id: str
    name: str
    chain: str
    category: str
    tvl: float
    change_1h: Optional[float] = None
    change_1d: Optional[float] = None
    change_7d: Optional[float] = None

class TVLPoint(BaseModel):
    date: str
    tvl: float

class YieldOpportunity(BaseModel):
    protocol: str
    pool: str
    chain: str
    token: str
    apy: float
    tvl: float
    risk_level: str

class Pool(BaseModel):
    protocol: str
    pool: str
    chain: str
    token0: str
    token1: Optional[str] = None
    tvl: float
    volume_24h: float
    apy: float

# Helper: Cache management
def get_cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key"""
    parts = [prefix] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
    return "|".join(parts)

def get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    """Get from cache if not expired"""
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
            return data
        else:
            del cache[key]
    return None

def set_cache(key: str, data: Dict[str, Any]) -> None:
    """Set cache with timestamp"""
    cache[key] = (data, datetime.now())

# Helper: Fetch from DefiLlama
async def fetch_defillama(endpoint: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Fetch data from DefiLlama API"""
    url = f"{DEFILLAMA_API}{endpoint}"
    
    cache_key = get_cache_key("defillama", endpoint=endpoint)
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    set_cache(cache_key, data)  # type: ignore
                    return data
                else:
                    text = await response.text()
                    raise HTTPException(status_code=502, detail=f"DefiLlama API error: {response.status} - {text}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="DefiLlama API timeout")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"DefiLlama connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# x402 Payment Verification
async def verify_x402_payment(payment_address: str, amount: str = PRICE_PER_REQUEST):
    """Verify x402 payment was made"""
    # TODO: Implement chain verification
    return True

@app.get("/")
async def root():
    return {
        "service": "GenTech DeFi Intelligence API",
        "data_sources": ["DefiLlama"],
        "pricing": f"${PRICE_PER_REQUEST} per request",
        "endpoints": {
            "GET /protocols": "List all DeFi protocols",
            "GET /protocols/{id}/tvl": "Get protocol TVL over time",
            "GET /yields": "Get best yield opportunities",
            "GET /pools": "Get high-value LP pools",
            "GET /chains": "List supported chains"
        },
        "docs": "/docs"
    }

@app.get("/protocols", response_model=List[Protocol])
async def list_protocols(
    chain: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """List all DeFi protocols with filtering"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Fetch protocols from DefiLlama
    data = await fetch_defillama("/protocols")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid API response format")
    
    # Filter and format
    protocols = []
    for p in data:
        # Ensure p is a dict
        if not isinstance(p, dict):
            continue
            
        # Apply filters
        if chain and p.get("chain") != chain:
            continue
        if category and p.get("category") != category:
            continue
        
        protocols.append(Protocol(
            id=str(p.get("id", "")),
            name=str(p.get("name", "")),
            chain=str(p.get("chain", "unknown")),
            category=str(p.get("category", "unknown")),
            tvl=float(p.get("tvl", 0)),
            change_1h=float(p["change_1h"]) if p.get("change_1h") is not None else None,
            change_1d=float(p["change_1d"]) if p.get("change_1d") is not None else None,
            change_7d=float(p["change_7d"]) if p.get("change_7d") is not None else None
        ))
    
    # Sort by TVL and limit
    protocols.sort(key=lambda x: x.tvl, reverse=True)
    return protocols[:limit]

@app.get("/protocols/{protocol_id}/tvl", response_model=List[TVLPoint])
async def get_protocol_tvl(
    protocol_id: str,
    days: int = Query(30, ge=1, le=365),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get protocol TVL over time"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Fetch TVL data
    data = await fetch_defillama(f"/protocol/{protocol_id}")
    
    if not isinstance(data, dict) or "tvl" not in data:
        raise HTTPException(status_code=404, detail="Protocol not found or invalid data")
    
    # Format TVL data
    tvl_points = []
    tvl_data = data.get("tvl", [])
    
    if isinstance(tvl_data, list):
        for point in tvl_data[:days]:
            if isinstance(point, dict):
                tvl_points.append(TVLPoint(
                    date=str(point.get("date", "")),
                    tvl=float(point.get("totalLiquidityUSD", 0))
                ))
    
    return tvl_points

@app.get("/yields", response_model=List[YieldOpportunity])
async def get_yields(
    min_apy: float = Query(5.0, ge=0),
    chain: Optional[str] = None,
    min_tvl: float = Query(1000000, ge=0),
    limit: int = Query(50, ge=1, le=200),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get best yield opportunities across chains"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Fetch yields from DefiLlama
    data = await fetch_defillama("/yields")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid API response format")
    
    # Filter and format
    yields = []
    for y in data:
        if not isinstance(y, dict):
            continue
            
        apy = float(y.get("apy", 0))
        tvl = float(y.get("tvlUsd", 0))
        
        if apy < min_apy:
            continue
        if min_tvl and tvl < min_tvl:
            continue
        if chain and y.get("chain") != chain:
            continue
        
        # Determine risk level based on APY
        risk_level = "low" if apy < 10 else "medium" if apy < 30 else "high"
        
        yields.append(YieldOpportunity(
            protocol=str(y.get("project", "")),
            pool=str(y.get("pool", "")),
            chain=str(y.get("chain", "unknown")),
            token=str(y.get("symbol", "")),
            apy=apy,
            tvl=tvl,
            risk_level=risk_level
        ))
    
    # Sort by APY and limit
    yields.sort(key=lambda x: x.apy, reverse=True)
    return yields[:limit]

@app.get("/pools", response_model=List[Pool])
async def get_pools(
    chain: Optional[str] = None,
    min_tvl: float = Query(100000, ge=0),
    min_volume: float = Query(10000, ge=0),
    limit: int = Query(50, ge=1, le=200),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get high-value LP pools"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Fetch pool data from DefiLlama
    data = await fetch_defillama("/yields")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid API response format")
    
    # Filter and format
    pools = []
    for p in data:
        if not isinstance(p, dict):
            continue
            
        tvl = float(p.get("tvlUsd", 0))
        volume = float(p.get("volumeUsd1d", 0))
        
        if min_tvl and tvl < min_tvl:
            continue
        if min_volume and volume < min_volume:
            continue
        if chain and p.get("chain") != chain:
            continue
        
        # Get underlying token
        underlying_tokens = p.get("underlyingTokens", [])
        token1 = str(underlying_tokens[0]) if underlying_tokens and len(underlying_tokens) > 0 else None
        
        pools.append(Pool(
            protocol=str(p.get("project", "")),
            pool=str(p.get("pool", "")),
            chain=str(p.get("chain", "unknown")),
            token0=str(p.get("symbol", "")),
            token1=token1,
            tvl=tvl,
            volume_24h=volume,
            apy=float(p.get("apy", 0))
        ))
    
    # Sort by TVL and limit
    pools.sort(key=lambda x: x.tvl, reverse=True)
    return pools[:limit]

@app.get("/chains")
async def list_chains(
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """List supported chains"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Fetch chain data from DefiLlama
    data = await fetch_defillama("/chains")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid API response format")
    
    chains = []
    for c in data:
        if not isinstance(c, dict):
            continue
        
        chains.append({
            "name": str(c.get("name", "")),
            "chain_id": str(c.get("chainId", "")),
            "tvl": float(c.get("tvl", 0))
        })
    
    return {
        "chains": chains,
        "total_chains": len(chains)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "defi-intelligence-api",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_size": len(cache),
        "data_sources": ["DefiLlama"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)