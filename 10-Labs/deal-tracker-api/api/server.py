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
async def list_deals():
    return {
        "deals": [],
        "count": 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
