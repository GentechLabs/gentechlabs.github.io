from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Deal Tracker API", version="1.0.0")

# CORS middleware — allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import os, json, urllib.request, urllib.parse

from . import games
from . import physical_media

ROBINHOOD_CLIENT_ID = "LtLiNmbs9owbYfWgBlC68Z2VujIPuvGoAiSYr8xW"
ROBINHOOD_TOKEN_FILE = "/root/repos/hyperliquid-python-sdk/robinhood_token.json"
ROBINHOOD_CRED_FILE = "/root/repos/hyperliquid-python-sdk/robinhood_cred.json"
CALLBACK_CODE = None


@app.get("/robinhood-callback")
async def robinhood_callback(request: Request):
    global CALLBACK_CODE
    code = request.query_params.get("code")
    if code:
        CALLBACK_CODE = code
        # Try to exchange immediately
        try:
            with open(ROBINHOOD_CRED_FILE) as f:
                cred = json.load(f)
            verifier = cred["code_verifier"]
            data = urllib.parse.urlencode({
                "client_id": ROBINHOOD_CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://api.gentechlabs.net/robinhood-callback",
                "code_verifier": verifier,
            }).encode()
            req = urllib.request.Request(
                "https://api.robinhood.com/oauth2/token/",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                token_data = json.loads(resp.read())
            if "access_token" in token_data:
                with open(ROBINHOOD_TOKEN_FILE, "w") as f:
                    json.dump(token_data, f, indent=2)
                return {"status": "success", "message": "Token saved! GTA can now trade on Robinhood."}
            else:
                return {"status": "error", "detail": token_data}
        except Exception as e:
            return {"status": "error", "detail": str(e)}
    return {"status": "waiting", "message": "No authorization code received yet."}


@app.get("/v1/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "deal-tracker",
    }


@app.get("/v1/deals")
async def list_deals(title: str = "", upper_price: float = 9999, limit: int = 10):
    """Search game deals by title (CheapShark). Returns real, data-backed results."""
    try:
        result = games.search_deals(title, upper_price=upper_price, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e), "query": title, "count": 0, "deals": []}


@app.post("/v1/games/price-watch")
async def create_price_watch(title: str, target_price: float, max_price: float = 9999):
    """Create/update a target-price watch for a game title."""
    return games.add_price_watch(title, target_price, max_price)


@app.get("/v1/games/price-watch")
async def get_price_watch():
    """List price watches and scan for deals at/below target price."""
    return games.check_price_watches()


@app.get("/v1/games/release-radar")
async def get_release_radar(notes: str = ""):
    """Tracked titles with beta windows / launch dates."""
    return games.release_radar(notes or None)


@app.get("/v1/games/preorder-advisor")
async def get_preorder_advisor(title: str):
    """'Is this pre-order worth it?' — value judgment."""
    return games.preorder_advisor(title)


# --- Physical Media Scarcity Tracker (Jordan-confirmed Aug 16) ---
@app.get("/v1/physical/search")
async def physical_search(title: str = "", limit: int = 20):
    """Search the physical media scarcity catalog (4K, steelbook, vinyl, boutique)."""
    return physical_media.search(title=title, limit=limit)


@app.get("/v1/physical/leaderboard")
async def physical_leaderboard(limit: int = 10):
    """Top-scarcity titles — the 'buy now' list."""
    return physical_media.scarcity_leaderboard(limit=limit)


@app.post("/v1/physical/watch")
async def physical_add_watch(title: str, target_score: int = 70):
    """Track a physical media title; alert when scarcity crosses target_score."""
    return physical_media.add_watch(title, target_score)


@app.get("/v1/physical/watch")
async def physical_check_watches():
    """Scan watched physical media titles for scarcity alerts."""
    return physical_media.check_watches()


@app.post("/v1/physical/title")
async def physical_add_title(
    title: str, format: str, label: str, msrp: float, scarcity: int, note: str = ""
):
    """Add a new title to the scarcity catalog (curated intelligence)."""
    return physical_media.add_title(title, format, label, msrp, scarcity, note)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
