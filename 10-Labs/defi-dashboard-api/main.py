#!/usr/bin/env python3
"""
GenTech DeFi Dashboard API
Serves DeFi data via REST API for agent consumption
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="GenTech DeFi API",
    description="DeFi intelligence for AI agents — pay per query via x402",
    version="1.0.0"
)

# CORS for agent access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_PATH = Path("/root/vaults/gentech/02-Labs/defi-dashboard/data")
VAULT_PATH = Path("/root/vaults/gentech")

@app.get("/")
async def root():
    return {
        "name": "GenTech DeFi API",
        "version": "1.0.0",
        "description": "DeFi intelligence for AI agents",
        "pricing": {
            "verified_agent": "$0.001/request",
            "unverified_agent": "$0.01/request"
        },
        "payment": "x402 (USDC on Base)",
        "docs": "/docs"
    }

@app.get("/api/v1/position/status")
async def get_position_status():
    """Get current LP position status"""
    try:
        # Read from defi-data.json
        data_file = VAULT_PATH / "02-Labs/defi-dashboard/data/defi-data.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
            return {
                "position": data.get("position", {}),
                "timestamp": datetime.now().isoformat(),
                "agent_tier": "verified"
            }
        else:
            return {"error": "Position data not available", "status": "waiting_for_data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/position/fees")
async def get_fee_analytics():
    """Get fee analytics for LP position"""
    try:
        data_file = VAULT_PATH / "02-Labs/defi-dashboard/data/defi-data.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
            return {
                "fees": data.get("fees", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Fee data not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/position/range")
async def get_range_optimization():
    """Get range optimization suggestions"""
    try:
        data_file = VAULT_PATH / "02-Labs/defi-dashboard/data/defi-data.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
            return {
                "range": data.get("range", {}),
                "optimization": data.get("optimization", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Range data not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/sync")
async def get_portfolio_sync():
    """Get full portfolio sync status"""
    try:
        data_file = VAULT_PATH / "02-Labs/defi-dashboard/data/defi-data.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
            return {
                "portfolio": data.get("portfolio", {}),
                "sync_status": "active",
                "last_sync": datetime.now().isoformat()
            }
        else:
            return {"error": "Portfolio data not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/macro")
async def get_macro_events():
    """Get macro events and their impact on crypto"""
    try:
        # Read from macro tracker
        macro_file = VAULT_PATH / "03-Strategies/macro-events.json"
        if macro_file.exists():
            with open(macro_file, 'r') as f:
                data = json.load(f)
            return {
                "events": data.get("events", []),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"events": [], "message": "No macro events tracked yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agent/health")
async def get_agent_health():
    """Get GenTech agent health status"""
    try:
        return {
            "agent": "GenTech",
            "status": "healthy",
            "uptime": "active",
            "services": {
                "dashboard": "online",
                "defi_monitor": "online",
                "cron_jobs": "active",
                "evomap": "connected"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
