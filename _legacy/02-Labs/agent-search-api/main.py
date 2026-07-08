"""
GenTech Agent Search API
Multi-protocol agent discovery with x402 monetization

Endpoints:
1. GET /search - Search agents across protocols (x402scan, Agentic.Market, custom registry)
2. GET /agents/{id} - Get agent details by ID
3. GET /categories - List agent categories
4. GET /featured - Get featured/verified agents
5. GET /stats - Get agent marketplace statistics

Pricing: $0.01 per request via x402
Data Sources: x402scan, Agentic.Market, local registry
"""

from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import os
import asyncio
import aiohttp
import re

app = FastAPI(
    title="GenTech Agent Search API",
    description="Multi-protocol agent discovery across x402scan, Agentic.Market, and custom registries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Data sources
X402SCAN_API = "https://api.x402scan.com"
AGENTIC_MARKET_API = "https://api.agentic.market"
LOCAL_REGISTRY_URL = os.getenv("LOCAL_REGISTRY_URL", "http://localhost:8001")

# x402 Pricing
PRICE_PER_REQUEST = "0.000001"

# Cache TTL (seconds)
CACHE_TTL = 600  # 10 minutes

# In-memory cache
cache: Dict[str, tuple[Dict[str, Any], datetime]] = {}

# Pydantic models
class AgentSource(BaseModel):
    protocol: str  # x402scan, agentic-market, local
    agent_id: str
    url: Optional[str] = None

class Agent(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    capabilities: List[str]
    pricing: Dict[str, Any]
    sources: List[AgentSource]
    verified: bool = False
    rating: Optional[float] = None
    total_calls: Optional[int] = None

class SearchResults(BaseModel):
    total: int
    page: int
    per_page: int
    agents: List[Agent]

class Category(BaseModel):
    id: str
    name: str
    count: int
    description: Optional[str] = None

class Stats(BaseModel):
    total_agents: int
    verified_agents: int
    total_calls_last_24h: int
    top_categories: List[Dict[str, Any]]

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

# Helper: Fetch from external APIs
async def fetch_external_api(url: str) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
    """Fetch data from external API"""
    cache_key = get_cache_key("external", url=url)
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
                    # Return None on error to allow fallback to other sources
                    return None
    except (asyncio.TimeoutError, aiohttp.ClientError):
        # Return None on error to allow fallback
        return None
    except Exception:
        return None

# Helper: Search x402scan
async def search_x402scan(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search agents on x402scan"""
    url = f"{X402SCAN_API}/api/v2/agents/search"
    params = {"q": query}
    if category:
        params["category"] = category
    
    # Build query string
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    data = await fetch_external_api(f"{url}?{query_str}")
    return data if isinstance(data, list) else []

# Helper: Search Agentic.Market
async def search_agentic_market(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search agents on Agentic.Market"""
    url = f"{AGENTIC_MARKET_API}/agents"
    params = {"search": query}
    if category:
        params["category"] = category
    
    # Build query string
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    data = await fetch_external_api(f"{url}?{query_str}")
    return data if isinstance(data, list) else []

# Helper: Search local registry
async def search_local_registry(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search local agent registry"""
    url = f"{LOCAL_REGISTRY_URL}/agents"
    params = {"search": query, "limit": "50"}
    if category:
        params["agent_type"] = category
    
    # Build query string
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    data = await fetch_external_api(f"{url}?{query_str}")
    return data if isinstance(data, list) else []

# Helper: Normalize agent from different sources
def normalize_agent(raw: Dict[str, Any], source: str) -> Optional[Agent]:
    """Normalize agent data from different sources"""
    try:
        # Handle different source formats
        if source == "x402scan":
            agent_id = str(raw.get("id", raw.get("agent_id", "")))
            name = str(raw.get("name", ""))
            description = raw.get("description", raw.get("about"))
            category = str(raw.get("category", raw.get("type", "other")))
            capabilities = raw.get("capabilities", raw.get("tools", []))
            pricing = raw.get("pricing", {"model": "per-call", "price": raw.get("price", "0.01")})
            verified = bool(raw.get("verified", raw.get("is_verified", False)))
            rating = raw.get("rating")
            total_calls = raw.get("total_calls")
            agent_url = raw.get("url")
        elif source == "agentic-market":
            agent_id = str(raw.get("id", raw.get("slug", "")))
            name = str(raw.get("name", raw.get("title", "")))
            description = raw.get("description", raw.get("summary"))
            category = str(raw.get("category", raw.get("type", "other")))
            capabilities = raw.get("capabilities", raw.get("tags", []))
            pricing = raw.get("pricing", {"model": "per-call", "price": "0.01"})
            verified = bool(raw.get("verified", False))
            rating = raw.get("rating", raw.get("score"))
            total_calls = raw.get("usage", raw.get("calls"))
            agent_url = f"{AGENTIC_MARKET_API}/agents/{agent_id}"
        else:  # local registry
            agent_id = str(raw.get("id", ""))
            name = str(raw.get("name", ""))
            description = raw.get("description")
            category = str(raw.get("agent_type", "other"))
            capabilities = raw.get("capabilities", [])
            pricing = raw.get("pricing_model", {"model": "fixed", "price": raw.get("base_price", "0")})
            verified = False
            rating = None
            total_calls = None
            agent_url = None
        
        if not agent_id or not name:
            return None
        
        return Agent(
            id=agent_id,
            name=name,
            description=description,
            category=category,
            capabilities=list(capabilities) if capabilities else [],
            pricing=pricing if isinstance(pricing, dict) else {"model": "unknown", "price": str(pricing)},
            sources=[AgentSource(protocol=source, agent_id=agent_id, url=agent_url)],
            verified=verified,
            rating=float(rating) if rating is not None else None,
            total_calls=int(total_calls) if total_calls is not None else None
        )
    except Exception:
        return None

# x402 Payment Verification
async def verify_x402_payment(payment_address: str, amount: str = PRICE_PER_REQUEST):
    """Verify x402 payment was made"""
    # TODO: Implement chain verification
    return True

@app.get("/")
async def root():
    return {
        "service": "GenTech Agent Search API",
        "data_sources": ["x402scan", "Agentic.Market", "Local Registry"],
        "pricing": f"${PRICE_PER_REQUEST} per request",
        "endpoints": {
            "GET /search": "Search agents across protocols",
            "GET /agents/{id}": "Get agent details by ID",
            "GET /categories": "List agent categories",
            "GET /featured": "Get featured/verified agents",
            "GET /stats": "Get marketplace statistics"
        },
        "docs": "/docs"
    }

@app.get("/search", response_model=SearchResults)
async def search_agents(
    query: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = None,
    sources: Optional[str] = Query(None, description="Comma-separated sources: x402scan,agentic-market,local"),
    verified_only: bool = False,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Search agents across multiple protocols"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Parse sources
    source_list = []
    if sources:
        source_list = [s.strip().lower() for s in sources.split(",")]
    else:
        source_list = ["x402scan", "agentic-market", "local"]
    
    # Search each source in parallel
    tasks = []
    if "x402scan" in source_list:
        tasks.append(search_x402scan(query, category))
    if "agentic-market" in source_list:
        tasks.append(search_agentic_market(query, category))
    if "local" in source_list:
        tasks.append(search_local_registry(query, category))
    
    results_lists = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Normalize all agents
    all_agents = []
    for i, result in enumerate(results_lists):
        if isinstance(result, Exception) or not isinstance(result, list):
            continue
        
        source = source_list[i]
        for raw in result:
            if isinstance(raw, dict):
                agent = normalize_agent(raw, source)
                if agent:
                    all_agents.append(agent)
    
    # Filter by verified if requested
    if verified_only:
        all_agents = [a for a in all_agents if a.verified]
    
    # Deduplicate by ID (keep first occurrence, which has priority from source list)
    seen_ids = set()
    unique_agents = []
    for agent in all_agents:
        if agent.id not in seen_ids:
            seen_ids.add(agent.id)
            unique_agents.append(agent)
    
    # Sort by verified status, then rating, then total calls
    unique_agents.sort(
        key=lambda a: (
            not a.verified,  # Verified first
            -(a.rating or 0),  # Higher rating first
            -(a.total_calls or 0)  # More calls first
        )
    )
    
    # Paginate
    total = len(unique_agents)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_agents = unique_agents[start:end]
    
    return SearchResults(
        total=total,
        page=page,
        per_page=per_page,
        agents=paginated_agents
    )

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get agent details by ID (searches all sources)"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Search all sources for this agent
    tasks = [
        search_x402scan(agent_id),
        search_agentic_market(agent_id),
        search_local_registry(agent_id)
    ]
    
    results_lists = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Find and normalize the agent
    for i, result in enumerate(results_lists):
        if isinstance(result, Exception) or not isinstance(result, list):
            continue
        
        source = ["x402scan", "agentic-market", "local"][i]
        for raw in result:
            if isinstance(raw, dict):
                agent = normalize_agent(raw, source)
                if agent and agent.id == agent_id:
                    return agent
    
    raise HTTPException(status_code=404, detail="Agent not found")

@app.get("/categories", response_model=List[Category])
async def list_categories(
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """List all agent categories"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Predefined categories (would be dynamic from sources in production)
    categories = [
        Category(id="assistant", name="Assistant", count=0, description="General purpose AI assistants"),
        Category(id="worker", name="Worker", count=0, description="Task execution agents"),
        Category(id="coordinator", name="Coordinator", count=0, description="Multi-agent orchestration"),
        Category(id="defi", name="DeFi", count=0, description="DeFi and finance agents"),
        Category(id="trading", name="Trading", count=0, description="Trading and arbitrage agents"),
        Category(id="data", name="Data", count=0, description="Data analysis and research agents"),
        Category(id="dev", name="Development", count=0, description="Code and DevOps agents"),
        Category(id="security", name="Security", count=0, description="Security and audit agents")
    ]
    
    return categories

@app.get("/featured", response_model=List[Agent])
async def get_featured_agents(
    limit: int = Query(10, ge=1, le=50),
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get featured/verified agents"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Search for verified agents across sources
    tasks = [
        search_x402scan("", None),
        search_agentic_market("", None),
        search_local_registry("", None)
    ]
    
    results_lists = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Normalize and filter verified
    verified_agents = []
    for i, result in enumerate(results_lists):
        if isinstance(result, Exception) or not isinstance(result, list):
            continue
        
        source = ["x402scan", "agentic-market", "local"][i]
        for raw in result:
            if isinstance(raw, dict):
                agent = normalize_agent(raw, source)
                if agent and agent.verified:
                    verified_agents.append(agent)
    
    # Sort by rating
    verified_agents.sort(key=lambda a: -(a.rating or 0))
    
    return verified_agents[:limit]

@app.get("/stats", response_model=Stats)
async def get_stats(
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get agent marketplace statistics"""
    
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Return mock stats (would fetch from sources in production)
    return Stats(
        total_agents=1523,
        verified_agents=342,
        total_calls_last_24h=45823,
        top_categories=[
            {"category": "DeFi", "count": 345},
            {"category": "Assistant", "count": 287},
            {"category": "Trading", "count": 213},
            {"category": "Data", "count": 198},
            {"category": "Development", "count": 156}
        ]
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agent-search-api",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_size": len(cache),
        "data_sources": ["x402scan", "Agentic.Market", "Local Registry"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)