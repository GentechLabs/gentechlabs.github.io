"""Crypto Price API — Real-time crypto prices."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crypto Price API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "crypto-price"}

@app.get("/v1/price/{symbol}")
async def price(symbol: str):
    return {"symbol": symbol.upper(), "price": 0.0, "source": "placeholder"}
