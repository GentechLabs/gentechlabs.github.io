"""Gas Price API — Real-time gas prices."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gas Price API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "gas-price"}

@app.get("/v1/gas")
async def gas():
    return {"gas_prices": {"ethereum": 0, "base": 0, "polygon": 0}, "source": "placeholder"}
