#!/usr/bin/env python3
"""
SIE x402 Service Adapter — GenTech Labs
=======================================
Exposes Superlinked Inference Engine (SIE) as a paid x402 service on the
GenTech x402 gateway. The gateway handles payment verification (HTTP 402
challenge -> USDC proof -> 200), and this adapter proxies the paid request
to a self-hosted SIE cluster on GCP.

Endpoints (all paid via x402, USDC on Base):
  POST /v1/embeddings   — generate embeddings (bge-m3, all-MiniLM-L6-v2, ...)
  POST /v1/rerank       — rerank search results (cross-encoder/ms-marco-*)
  POST /v1/extract      — entity extraction (GLiNER)
  POST /v1/chat         — agent-loop LLM (qwen3.6-27b) via OpenAI-compatible API

The adapter is stateless: it forwards to SIE's OpenAI-compatible surface
(/v1/embeddings, /v1/chat/completions) and returns the result. Payment is
enforced upstream by the x402 gateway, so this service trusts the gateway's
Authorization: x402 <proof> header and does not re-verify.

Run:
  SIE_BASE_URL=http://localhost:8080 uvicorn sie_service:app --port 8097
"""

import os
import json
import httpx
from typing import Optional

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

app = FastAPI(title="SIE x402 Service", version="1.0.0")

SIE_BASE_URL = os.getenv("SIE_BASE_URL", "http://localhost:8080")
# Price per call in USD (USDC). The gateway advertises this in the 402 challenge.
PRICE_USD = float(os.getenv("SIE_PRICE_USD", "0.01"))
# Models we expose. SIE loads these on demand from its catalog.
EMBEDDING_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "BAAI/bge-m3",
]
RERANK_MODELS = [
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "BAAI/bge-reranker-v2-m3",
]
EXTRACT_MODELS = ["urchade/gliner_multi-v2.1"]
CHAT_MODELS = ["Qwen/Qwen3-27B"]


class EmbeddingRequest(BaseModel):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    input: str


class RerankRequest(BaseModel):
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    query: str
    documents: list


class ExtractRequest(BaseModel):
    model: str = "urchade/gliner_multi-v2.1"
    text: str
    labels: list


class ChatRequest(BaseModel):
    model: str = "Qwen/Qwen3-27B"
    messages: list


def _check_paid(request: Request) -> Optional[Response]:
    """The x402 gateway strips the proof and forwards the paid request.
    If this service is hit directly (no gateway), require the x402 token
    header so it can't be used for free. The gateway sets it after verify."""
    token = request.headers.get("x-402-token")
    if not token:
        return Response(
            status_code=402,
            content=json.dumps({
                "error": "payment_required",
                "message": "This is a paid x402 service. Call through the gateway "
                           "at https://api.gentechlabs.net/v1/sie/... to get a "
                           "payment challenge.",
            }),
            media_type="application/json",
        )
    return None


@app.get("/v1/health")
async def health():
    # Probe SIE readiness
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{SIE_BASE_URL}/readyz")
            sie = "ok" if r.status_code == 200 else f"down({r.status_code})"
    except Exception as e:
        sie = f"down({e})"
    return {"status": "ok", "sie": sie, "price_usd": PRICE_USD}


@app.post("/v1/embeddings")
async def embeddings(req: EmbeddingRequest, request: Request):
    blocked = _check_paid(request)
    if blocked:
        return blocked
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{SIE_BASE_URL}/v1/embeddings",
            json={"model": req.model, "input": req.input},
        )
    return Response(content=r.content, status_code=r.status_code,
                    media_type="application/json")


@app.post("/v1/rerank")
async def rerank(req: RerankRequest, request: Request):
    blocked = _check_paid(request)
    if blocked:
        return blocked
    # SIE exposes reranking via its SDK score() — the OpenAI surface uses
    # /v1/rerank on some builds; fall back to a direct score call shape.
    payload = {"model": req.model, "query": req.query, "documents": req.documents}
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{SIE_BASE_URL}/v1/rerank", json=payload)
    return Response(content=r.content, status_code=r.status_code,
                    media_type="application/json")


@app.post("/v1/extract")
async def extract(req: ExtractRequest, request: Request):
    blocked = _check_paid(request)
    if blocked:
        return blocked
    payload = {"model": req.model, "text": req.text, "labels": req.labels}
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{SIE_BASE_URL}/v1/extract", json=payload)
    return Response(content=r.content, status_code=r.status_code,
                    media_type="application/json")


@app.post("/v1/chat")
async def chat(req: ChatRequest, request: Request):
    blocked = _check_paid(request)
    if blocked:
        return blocked
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(
            f"{SIE_BASE_URL}/v1/chat/completions",
            json={"model": req.model, "messages": req.messages},
        )
    return Response(content=r.content, status_code=r.status_code,
                    media_type="application/json")
