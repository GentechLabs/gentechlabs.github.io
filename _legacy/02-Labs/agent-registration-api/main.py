"""
GenTech Agent Registration API
ERC-8004 Standard with x402 Monetization

Endpoints:
1. POST /register - Register new agent
2. GET /agents/{id} - Get agent by ID
3. GET /agents - List all agents
4. PUT /agents/{id} - Update agent metadata
5. DELETE /agents/{id} - Deactivate agent

Pricing: $0.01 per request via x402
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import os
from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware
import json
import hashlib

app = FastAPI(
    title="GenTech Agent Registration API",
    description="ERC-8004 compliant agent registration with x402 payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Load config
AVALANCHE_RPC_URL = os.getenv("AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc")
ERC8004_CONTRACT_ADDRESS = os.getenv("ERC8004_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")

# Web3 setup
w3 = Web3(Web3.HTTPProvider(AVALANCHE_RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Contract (would load from deployed contract)
# contract = w3.eth.contract(address=w3.to_checksum_address(ERC8004_CONTRACT_ADDRESS), abi=ERC8004_ABI)

# Local storage for demo (would use contract in production)
agents_db = {}

# x402 Pricing
PRICE_PER_REQUEST = "0.000001"  # ~$0.01 in ETH/AVAX equivalent

# Pydantic models
class AgentRegistration(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    owner_address: str = Field(..., min_length=42, max_length=42)
    agent_type: str = Field(..., description="Agent type: assistant, worker, coordinator, etc.")
    capabilities: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    pricing_model: str = Field(default="fixed", description="fixed, subscription, usage-based")
    base_price: str = Field(default="0", description="Base price in ETH/AVAX")
    metadata: Optional[dict] = None

    @field_validator('owner_address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum address format')
        return v

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    pricing_model: Optional[str] = None
    base_price: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|deprecated)$")

class AgentResponse(BaseModel):
    id: str
    name: str
    owner_address: str
    agent_type: str
    capabilities: List[str]
    description: Optional[str]
    pricing_model: str
    base_price: str
    status: str
    registered_at: datetime
    updated_at: datetime
    metadata: Optional[dict]

# x402 Payment Verification
async def verify_x402_payment(payment_address: str, amount: str = PRICE_PER_REQUEST):
    """
    Verify x402 payment was made
    In production, check chain for payment transaction
    For demo, we'll skip verification but keep the structure
    """
    # TODO: Implement actual chain verification
    # Check payment_address sent >= amount to x402 receiver
    return True

# Helper: Generate agent ID
def generate_agent_id(name: str, owner: str) -> str:
    """Generate unique agent ID from name and owner"""
    data = f"{name}-{owner}-{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

@app.get("/")
async def root():
    return {
        "service": "GenTech Agent Registration API",
        "standard": "ERC-8004",
        "pricing": f"${PRICE_PER_REQUEST} per request",
        "endpoints": {
            "POST /register": "Register new agent",
            "GET /agents/{id}": "Get agent by ID",
            "GET /agents": "List all agents",
            "PUT /agents/{id}": "Update agent",
            "DELETE /agents/{id}": "Deactivate agent"
        },
        "docs": "/docs"
    }

@app.post("/register", response_model=AgentResponse)
async def register_agent(
    agent: AgentRegistration,
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Register a new agent on the network"""
    
    # Verify x402 payment
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Generate ID
    agent_id = generate_agent_id(agent.name, agent.owner_address)
    
    # Check if exists
    if agent_id in agents_db:
        raise HTTPException(status_code=400, detail="Agent already exists")
    
    # Store agent
    now = datetime.utcnow()
    agents_db[agent_id] = {
        "id": agent_id,
        "name": agent.name,
        "owner_address": agent.owner_address,
        "agent_type": agent.agent_type,
        "capabilities": agent.capabilities,
        "description": agent.description,
        "pricing_model": agent.pricing_model,
        "base_price": agent.base_price,
        "status": "active",
        "registered_at": now,
        "updated_at": now,
        "metadata": agent.metadata or {}
    }
    
    # TODO: Register on-chain via ERC-8004 contract
    # contract.functions.registerAgent(agent_id, agent.name, agent.owner_address).transact()
    
    return agents_db[agent_id]

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """Get agent details by ID"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify payment for read
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    return agents_db[agent_id]

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    limit: int = 50,
    offset: int = 0,
    agent_type: Optional[str] = None,
    status: str = "active",
    x_x402_payment: Optional[str] = Header(None, alias="x-x402-payment")
):
    """List all registered agents with pagination"""
    
    # Verify payment
    if x_x402_payment:
        await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Filter agents
    filtered_agents = [
        agent for agent in agents_db.values()
        if agent["status"] == status and (agent_type is None or agent["agent_type"] == agent_type)
    ]
    
    # Sort by registration date (newest first)
    filtered_agents.sort(key=lambda x: x["registered_at"], reverse=True)
    
    # Paginate
    return filtered_agents[offset:offset + limit]

@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    update: AgentUpdate,
    x_x402_payment: str = Header(..., alias="x-x402-payment")
):
    """Update agent metadata (owner only)"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify payment
    await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Update fields
    agent = agents_db[agent_id]
    for field, value in update.dict(exclude_unset=True).items():
        if value is not None:
            agent[field] = value
    
    agent["updated_at"] = datetime.utcnow()
    
    # TODO: Update on-chain if applicable
    # contract.functions.updateAgentMetadata(agent_id, update.metadata).transact()
    
    return agent

@app.delete("/agents/{agent_id}")
async def deactivate_agent(
    agent_id: str,
    x_x402_payment: str = Header(..., alias="x-x402-payment"),
    owner_signature: str = Header(..., alias="x-owner-signature")
):
    """Deactivate an agent (owner only, requires signature)"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify payment
    await verify_x402_payment(x_x402_payment, PRICE_PER_REQUEST)
    
    # Verify owner signature
    # TODO: Implement proper signature verification
    # owner_address = agents_db[agent_id]["owner_address"]
    # verify_signature(owner_address, owner_signature, f"deactivate:{agent_id}")
    
    # Deactivate
    agents_db[agent_id]["status"] = "inactive"
    agents_db[agent_id]["updated_at"] = datetime.utcnow()
    
    # TODO: Update on-chain status
    # contract.functions.setAgentStatus(agent_id, "inactive").transact()
    
    return {"id": agent_id, "status": "deactivated"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agent-registration-api",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_registered": len(agents_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)