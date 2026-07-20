from fastapi import FastAPI
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
