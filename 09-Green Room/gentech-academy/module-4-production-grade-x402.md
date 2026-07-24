# Module 4: Building Production-Grade x402 Services

**Course:** Ship Paid APIs in a Weekend  
**Duration:** 5 lessons + 1 hands-on exercise  
**Target:** Web3 / dev-focused developers  
**Style:** Practical, concise, real examples

---

## Lesson 4.1: CORS, Rate Limiting, and Security Headers

### Why This Matters Before Anything Else

The moment you deploy a paid API, bots will probe it. Scrapers will hit it. Agents with malformed payment proofs will retry 40 times a second. If you don't harden your service *before* going live, you won't just lose money — you'll lose your reputation as a reliable provider.

Your security posture is your product. A production x402 service needs three layers:

| Layer | What It Protects | Cost |
|-------|-----------------|------|
| **CORS** | Browser-based abuse (cross-origin requests) | Free (one config block) |
| **Rate limiting** | Brute-force payment probing | Free (in-Worker or middleware) |
| **Security headers** | Injection, clickjacking, MIME sniffing | Free (response headers) |

### CORS — Only Allow What You Need

CORS (Cross-Origin Resource Sharing) tells browsers which domains can call your API. Since most x402 traffic comes from server-side agents (not browsers), you can be extremely restrictive:

```json
{
  "Access-Control-Allow-Origin": "https://your-frontend.com",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Payment-Proof, X-Payment-Token",
  "Access-Control-Max-Age": "86400"
}
```

**The CORS trap:** Don't use `*` for production. It lets any website exfiltrate your API. Use `*` only during development, and pin it to your actual domain before launch.

**Preflight OPTIONS handler** — Every CORS-compliant browser sends an OPTIONS request before the real request. Your 402 response handler must also handle OPTIONS:

```js
// Worker: always handle OPTIONS first
if (method === 'OPTIONS') {
  return new Response(null, {
    headers: corsHeaders,
  });
}
```

```python
# FastAPI: CORS middleware handles this automatically
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://your-frontend.com"])
```

### Rate Limiting — Protect Your Payment Verification

Payment verification hits an RPC endpoint, which has its own rate limits. You need two tiers:

| Tier | Limit | Purpose |
|------|-------|---------|
| **Soft** | 10 req/s per IP | Normal agent traffic |
| **Hard** | 1 req/s per IP on /verify | Payment proof verification (expensive) |

**In a Cloudflare Worker**, use the built-in Rate Limiting binding:

```toml
# wrangler.toml
[[unsafe_metadata.bindings]]
type = "rate_limit"
name = "API_RATE_LIMITER"
```

```js
async handleRequest(request) {
  const { success } = await API_RATE_LIMITER.limit({ key: request.headers.get('CF-Connecting-IP') });
  if (!success) {
    return new Response('Rate limit exceeded', { status: 429 });
  }
  // ... normal handling
}
```

**Without Cloudflare**, implement token-bucket rate limiting in your app middleware:

```python
import time
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate=10, burst=20):
        self.rate = rate
        self.burst = burst
        self.tokens = defaultdict(lambda: burst)
        self.last = defaultdict(time.time)

    def check(self, key: str) -> bool:
        now = time.time()
        elapsed = now - self.last[key]
        self.tokens[key] = min(self.burst, self.tokens[key] + elapsed * self.rate)
        self.last[key] = now
        if self.tokens[key] >= 1:
            self.tokens[key] -= 1
            return True
        return False
```

### Security Headers — The Minimum Viable Set

| Header | Value | Why |
|--------|-------|-----|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `Strict-Transport-Security` | `max-age=31536000` | Forces HTTPS |
| `Content-Security-Policy` | `default-src 'none'` | Blocks all inline injection (API-only) |

For a paid API that returns JSON, CSP can be `default-src 'none'` because you have no images, scripts, or styles to load. This is the most restrictive — and safest — setting.

---

## Lesson 4.2: Request Validation and Error Handling

### The Cost of Bad Validation

Every malformed request that reaches your payment verification logic costs you:
- RPC call fees (if you pay per request)
- CPU time
- Log noise that buries real issues

**Validate before you verify.** Always.

### Input Validation Checklist

```
[Request arrives]
  ↓
1. METHOD check ───────── GET/POST only?
  ↓
2. PATH sanity ────────── Known endpoint?
  ↓
3. HEADERS present ────── Content-Type, optional auth?
  ↓
4. BODY parse ─────────── Valid JSON? Size < 1MB?
  ↓
5. PARAM validation ───── Types, bounds, charset?
  ↓
6. PAYMENT proof ──────── Present? Well-formed?
  ↓
[Payment verification (expensive)]
```

### Error Handling That Doesn't Leak

The number-one bug in production x402 services: **leaking stack traces to the client.**

```python
# ❌ BAD — leaks internal state
try:
    result = verify_on_chain(proof)
except Exception as e:
    return {"error": str(e)}, 402

# ✅ GOOD — log the detail, return a clean message
import logging
logger = logging.getLogger(__name__)

try:
    result = verify_on_chain(proof)
except Exception as e:
    logger.error("Payment verification failed", exc_info=True)
    return {"error": "Payment verification failed. Contact support with your tx hash."}, 402
```

**The `str(e)` rule:** Never include `str(e)` in a response body. Log it. Return a generic message. A malformed payment proof could contain injection payloads or chain state that reveals private information.

### Structured Error Responses

All errors should return the same shape so agents can parse them programmatically:

```json
{
  "status": 402,
  "error": "payment_verification_failed",
  "detail": "Insufficient payment: 0.0001 USDC transferred, 0.005 required",
  "request_id": "rct_a1b2c3d4e5f6"
}
```

| Field | Always? | Purpose |
|-------|---------|---------|
| `status` | ✅ | HTTP status code mirrored in body |
| `error` | ✅ | Machine-readable error code |
| `detail` | ✅ | Human-readable explanation |
| `request_id` | ✅ | Traceable ID for support (use `uuid.uuid4()`) |

### Async Exception Isolation

When your service orchestrates multiple independent operations (identity check + MCP scan + payment verification), wrap each in its own try/except:

```python
# ❌ BAD — one failure kills everything
try:
    identity = check_identity(request)
    mcp = scan_mcp_tools(request)
    payment = verify_payment(proof)
except Exception:
    return {"error": "processing failed"}, 500

# ✅ GOOD — each operation is independent
identity = None
mcp = None
payment = None

try:
    identity = check_identity(request)
except Exception as e:
    logger.error("Identity check failed", exc_info=True)

try:
    mcp = scan_mcp_tools(request)
except Exception as e:
    logger.error("MCP scan failed", exc_info=True)

try:
    payment = verify_payment(proof)
except Exception as e:
    logger.error("Payment verification failed", exc_info=True)
```

If payment verification fails, you still have identity + MCP data for the error log. A single wrapper loses everything.

---

## Lesson 4.3: Logging and Analytics

### What to Log (and What Not to)

**Log this:**
- Request path, method, duration, status code
- Payment amount, sender (truncated: `0x7ebf...6a3`), chain
- Error codes (not full stack traces in production)
- Rate limit hits
- Unknown endpoints (probing bots)

**Never log:**
- Full payment proof contents (signature, nonce)
- API keys or tokens
- Wallet private keys (obvious, but it happens)
- Raw request bodies that contain user data

### Structured Logging Format

```json
{
  "timestamp": "2026-07-23T12:00:00Z",
  "level": "INFO",
  "service": "x402-gateway",
  "request_id": "rct_a1b2c3d4e5f6",
  "method": "POST",
  "path": "/v1/agent/scan",
  "duration_ms": 342,
  "status": 200,
  "payment": {
    "amount": 0.01,
    "sender": "0x7ebf...6a3",
    "chain": "base"
  }
}
```

In Python, use the built-in `logging` module with structured formatting:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry)

logger = logging.getLogger("x402-gateway")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Revenue Tracking

Your x402 gateway should log every successful payment to a revenue tracker:

```
Revenue DB (SQLite or JSON file):
  tx_hash | sender | amount | chain | endpoint | timestamp
```

The minimal revenue tracker is a single JSON file:

```python
import json
from pathlib import Path

TRACKER = Path("revenue.json")

def log_payment(tx_hash, sender, amount, chain, endpoint):
    data = {"transactions": [], "total": 0.0}
    if TRACKER.exists():
        data = json.loads(TRACKER.read_text())
    
    data["transactions"].append({
        "tx_hash": tx_hash,
        "sender": sender,
        "amount": amount,
        "chain": chain,
        "endpoint": endpoint,
        "timestamp": datetime.utcnow().isoformat(),
    })
    data["total"] = sum(tx["amount"] for tx in data["transactions"])
    
    TRACKER.write_text(json.dumps(data, indent=2))
```

This is what GenTech Labs' revenue monitor uses — simple, auditable, and easy to verify against on-chain data.

---

## Lesson 4.4: VPS Proxying for Non-Worker-Compatible Projects

### When Cloudflare Workers Aren't Enough

Workers are great for lightweight APIs, but they have limits:

| Limitation | Worker Cap | When You Hit It |
|-----------|-----------|-----------------|
| CPU time | 30s per request | Heavy ML inference, PDF generation |
| Memory | 128 MB | Large model loading, image processing |
| Network | HTTP(S) only | Database connections, WebSocket |
| Runtime | V8 isolates | Python/Ruby/Go services |

**Solution:** Run your backend on a VPS, use a Worker as the x402 payment gateway in front of it.

### Architecture: Worker → VPS Proxy

```
Agent → Cloudflare Worker (x402 gateway)
                  ↓
           Payment verified?
           ┌─ YES ─→ Proxy to VPS: api.yourdomain.com/v1/search
           └─ NO  ─→ 402 Payment Required
```

### The Worker Proxy Pattern

```js
// In your Cloudflare Worker
async function proxyToVPS(path, request) {
  const url = new URL(`http://YOUR_VPS_IP:80${path}`);

  const proxyRequest = new Request(url, request);
  proxyRequest.headers.set('Host', 'api.yourdomain.com');
  proxyRequest.headers.set('X-Forwarded-Proto', 'https');

  try {
    const response = await fetch(proxyRequest);
    // Add CORS headers to the proxied response
    const newResponse = new Response(response.body, response);
    newResponse.headers.set('Access-Control-Allow-Origin', '*');
    return newResponse;
  } catch {
    return new Response(
      JSON.stringify({ error: 'Backend unavailable' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

// In your fetch handler, after payment verification:
if (result.valid) {
  return await proxyToVPS(request.url.pathname, request);
}
```

### The Nginx Reverse Proxy

On the VPS, nginx routes traffic to your backend services:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

You can run multiple backend services on different ports:

| Port | Service | Domain |
|------|---------|--------|
| 8080 | Deal tracker | deals.yourdomain.com |
| 8082 | Price API | prices.yourdomain.com |
| 8084 | Gas API | gas.yourdomain.com |
| 8088 | Rugcheck API | rugcheck.yourdomain.com |

### Import Path Gotcha

When running a FastAPI service behind uvircorn on a VPS, imports can break depending on how you start the server:

```python
# ❌ If api/server.py imports from sibling cache.py:
from cache import ScoreCache  # Fails when run as `uvicorn api.server:app`

# ✅ Fix: add the project root to sys.path at the TOP of api/server.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cache import ScoreCache  # Now works
```

This is the most common deployment failure. The `uvicorn api.server:app` command resolves imports relative to the `api` package, not the project root. Always add the `sys.path` fix before FastAPI imports.

---

## Lesson 4.5: Health Checks and Uptime Monitoring

### The Health Endpoint

Every production service needs a `/health` endpoint that returns within 100ms:

```python
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "your-service-name",
        "uptime": round(time.time() - START_TIME, 1),
        "checks": {
            "database": check_db(),
            "rpc": check_rpc(),
            "cache": check_cache(),
        }
    }
```

**What to check in `/health`:**
- Database connectivity (if applicable)
- RPC endpoint responsiveness (ping with `eth_blockNumber`)
- Cache reachability (Redis/memcached)
- Disk space (for logging services)
- Last successful payment verification time

Do **not** include sensitive info in health checks — no API keys, no pending payment amounts, no internal IPs.

### Monitoring Setups

**Option 1: Better Uptime (Free)**
- Monitor: `https://api.yourdomain.com/health`
- Alert: Email/Slack/Telegram if 3 consecutive failures
- Check interval: 1 minute
- Cost: Free tier covers 50 monitors

**Option 2: Self-hosted with cron**
```bash
#!/bin/bash
# /etc/cron.d/health-check
* * * * * root curl -sf https://api.yourdomain.com/health || \
  curl -s -X POST https://ntfy.sh/your-topic \
    -H "Title: API Down" \
    -d "Health check failed for your-service"
```

**Option 3: GenTech Labs' approach — revenue monitor**
We combine health checks with revenue tracking in one script that runs on cron:

```python
SERVICES = {
    "x402-gateway":     {"url": "https://api.gentechlabs.net",      "health": "/health"},
    "price-api":        {"url": "https://prices.gentechlabs.net",   "health": "/v1/health"},
    "defi-intel":       {"url": "https://defi.gentechlabs.net",     "health": "/health"},
}

def check_health():
    results = []
    for name, svc in SERVICES.items():
        url = f"{svc['url']}{svc['health']}"
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True, text=True, timeout=10
            )
            code = result.stdout.strip()
            results.append((name, "ok" if code == "200" else f"HTTP {code}"))
        except Exception as e:
            results.append((name, f"error: {e}"))
    return results
```

### The Deployment Checklist

Before deploying any x402 service, run this:

```
[ ] CORS headers configured (not *)
[ ] Rate limiting enabled
[ ] Security headers set (X-Content-Type-Options, HSTS, CSP)
[ ] Input validation before payment verification
[ ] Error messages sanitized (no str(e) in responses)
[ ] Structured logging configured
[ ] Revenue tracking file created
[ ] Health endpoint returns within 100ms
[ ] Uptime monitor configured (Better Uptime or cron)
[ ] DNS records set (api.yourdomain.com → VPS IP)
[ ] SSL certificate valid (LetsEncrypt auto-renew)
[ ] `sys.path` fix applied for uvicorn imports
```

---

## Hands-On: Take a FastAPI Service and Wrap It Behind x402

**Goal:** Convert an existing FastAPI service into a production-grade x402-gated API.

**Time:** 30-45 minutes

### Step 1: Get a FastAPI Service

Use this minimal price service:

```python
# prices.py
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Price API", version="1.0.0")

# 💡 Add sys.path fix if running through uvicorn
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

PRICE_CACHE = {}

@app.get("/v1/health")
async def health():
    return {"status": "ok", "service": "price-api"}

@app.get("/v1/price/{symbol}")
async def get_price(symbol: str):
    symbol = symbol.upper()
    if symbol in PRICE_CACHE:
        return {"symbol": symbol, "price": PRICE_CACHE[symbol], "source": "cache"}
    # Fetch from CoinGecko
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={"ids": symbol.lower(), "vs_currencies": "usd"}
        )
        data = resp.json()
        if symbol.lower() not in data:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        price = data[symbol.lower()]["usd"]
        PRICE_CACHE[symbol] = price
        return {"symbol": symbol, "price": price, "source": "coingecko"}
```

Save it as `prices.py` and run:
```bash
pip install fastapi uvicorn httpx
uvicorn prices:app --host 0.0.0.0 --port 8080
```

Verify: `curl http://localhost:8080/v1/health` → `{"status":"ok"}`

### Step 2: Add CORS + Rate Limiting + Security Headers

Create a middleware module `middleware.py`:

```python
# middleware.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

# ── Token Bucket Rate Limiter ──
class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, rate=10, burst=20):
        super().__init__(app)
        self.rate = rate
        self.burst = burst
        self.tokens = defaultdict(lambda: burst)
        self.last = defaultdict(time.time)

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.time()
        elapsed = now - self.last[client]
        self.tokens[client] = min(self.burst, self.tokens[client] + elapsed * self.rate)
        self.last[client] = now
        if self.tokens[client] < 1:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"error": "rate_limit_exceeded", "detail": "Too many requests"},
                status_code=429,
            )
        self.tokens[client] -= 1
        response = await call_next(headers=request.scope)
        return response

# ── Security Headers ──
class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response

# ── Apply to app ──
def add_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://your-frontend.com"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Payment-Proof", "X-Payment-Token"],
    )
    app.add_middleware(SecurityHeaders)
    app.add_middleware(RateLimiter, rate=10, burst=20)
```

Add to your app:

```python
# prices.py (updated)
from middleware import add_middleware
# ... after app = FastAPI(...)
add_middleware(app)
```

### Step 3: Add x402 Payment Verification

Create a `x402.py` payment module:

```python
# x402.py
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# GenTech Labs' payment address
RECIPIENT = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913"

def verify_x402_payment(proof_header: str | None, required_amount: float) -> dict:
    """
    Verify an x402 payment proof header.
    Returns {"valid": True, "tx": ...} or {"valid": False, "error": ...}
    """
    if not proof_header:
        return {"valid": False, "error": "missing_header"}

    try:
        # 1. Decode base64 proof
        import base64
        proof = json.loads(base64.b64decode(proof_header))

        # 2. Check required fields
        required = ["signature", "sender", "timestamp", "amount", "nonce"]
        for field in required:
            if field not in proof:
                return {"valid": False, "error": f"missing_field:{field}"}

        # 3. Check timestamp window (5 minutes)
        now = int(datetime.utcnow().timestamp())
        if abs(now - int(proof["timestamp"])) > 300:
            return {"valid": False, "error": "proof_expired"}

        # 4. Check amount
        if float(proof["amount"]) < required_amount:
            return {"valid": False, "error": f"insufficient_amount"}

        # 5. Verify on-chain (simplified — in production, check tx receipt)
        # For a full implementation, see Module 2's verification code
        logger.info(f"Payment verified: {proof['signature'][:10]}... "
                    f"{proof['sender'][:10]}... ${required_amount}")

        return {"valid": True, "tx": {
            "hash": proof["signature"],
            "from": proof["sender"],
            "amount": required_amount,
        }}

    except Exception as e:
        logger.error("Payment verification error", exc_info=True)
        return {"valid": False, "error": "verification_error"}
```

### Step 4: Create the 402 Response Handler

Add a helper for returning 402 Payment Required:

```python
# x402.py (continued)

def payment_required_response(endpoint: str, amount: float):
    return {
        "status": 402,
        "error": "payment_required",
        "detail": f"This endpoint costs ${amount:.3f} USDC",
        "payment": {
            "protocol": "x402",
            "amount": amount,
            "currency": "USDC",
            "network": "base",
            "recipient": RECIPIENT,
            "usdc_contract": USDC_BASE,
            "header": "X-Payment-Proof",
        },
    }, 402
```

### Step 5: Protect Your Paid Endpoint

```python
# prices.py (final)
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from middleware import add_middleware
from x402 import verify_x402_payment, payment_required_response

app = FastAPI(title="Price API — x402", version="1.1.0")
add_middleware(app)

@app.get("/v1/health")
async def health():
    return {"status": "ok", "service": "price-api", "version": "1.1.0"}

@app.get("/v1/price/{symbol}")
async def get_price(symbol: str, request: Request):
    # Require x402 payment
    proof = request.headers.get("X-Payment-Proof")
    result = verify_x402_payment(proof, required_amount=0.001)

    if not result["valid"]:
        return JSONResponse(*payment_required_response("/v1/price/{symbol}", 0.001))

    symbol = symbol.upper()
    if symbol in PRICE_CACHE:
        return {"symbol": symbol, "price": PRICE_CACHE[symbol], "source": "cache"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={"ids": symbol.lower(), "vs_currencies": "usd"}
        )
        data = resp.json()
        if symbol.lower() not in data:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        price = data[symbol.lower()]["usd"]
        PRICE_CACHE[symbol] = price
        return {"symbol": symbol, "price": price, "source": "coingecko", "payment": result["tx"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Step 6: Test It

```bash
# Health check (free)
curl http://localhost:8080/v1/health
# → {"status":"ok","service":"price-api","version":"1.1.0"}

# Price without payment (expect 402)
curl http://localhost:8080/v1/price/bitcoin
# → {"status":402,"error":"payment_required","detail":"This endpoint costs $0.001 USDC",...}

# Price with payment (use a real signed x402 proof)
curl -H "X-Payment-Proof: $(echo '{"signature":"0x...","sender":"0x...","timestamp":1234,"amount":"0.001","nonce":"abc"}' | base64)" \
  http://localhost:8080/v1/price/bitcoin
# → {"symbol":"BTC","price":...}
```

### Verification Checklist

```
[ ] Health endpoint returns HTTP 200 within 100ms
[ ] Free endpoint (health) works without payment header
[ ] Paid endpoint returns 402 without payment header
[ ] Paid endpoint returns 200 with valid payment proof
[ ] Rate limiting returns 429 after burst limit
[ ] CORS headers present on all responses
[ ] Security headers present on all responses
[ ] Error messages are sanitized (no stack traces)
[ ] Both curl and browser testing pass
```

---

### Summary

| Lesson | Key Takeaway |
|--------|-------------|
| 4.1 | CORS, rate limiting, and security headers are free — apply them before going live |
| 4.2 | Validate everything before verification; never leak `str(e)` to clients |
| 4.3 | Structured JSON logging + a simple revenue tracker cover 90% of monitoring needs |
| 4.4 | VPS proxying via Workers + nginx handles anything Workers can't run directly |
| 4.5 | A `/health` endpoint + cron-based uptime checks are the minimum production setup |

**Coming up in Module 5:** Making your API discoverable by AI agents — MCP tools, pay-skills catalog, and ERC-8004 agent registration.
