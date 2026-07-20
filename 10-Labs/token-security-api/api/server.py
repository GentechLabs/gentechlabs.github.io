"""Token Security API — Token risk scoring."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Token Security API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "token-security"}

@app.get("/v1/score/{mint}")
async def score(mint: str):
    return {"mint": mint, "score": 0, "level": "unknown", "risk_factors": {}, "source": "placeholder"}
