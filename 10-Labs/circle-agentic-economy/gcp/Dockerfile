# SIE x402 Service — Dockerfile
# Runs the SIE inference engine + the x402 service adapter in one container.
# SIE serves OpenAI-compatible /v1/embeddings, /v1/chat/completions, etc.
# The adapter (sie_service.py) exposes a subset as paid x402 endpoints.
#
# Build:  docker build -t gcr.io/<PROJECT>/sie-x402:latest .
# Run:    docker run -p 8080:8080 -p 8097:8097 gcr.io/<PROJECT>/sie-x402:latest

FROM python:3.12-slim AS sie
# SIE server (CPU image — no GPU needed for embeddings/rerank/structured output)
# https://github.com/superlinked/sie
RUN pip install --no-cache-dir "sie-server[local]"

FROM python:3.12-slim
WORKDIR /app

# --- SIE server ---
COPY --from=sie /usr/local/bin/sie-server /usr/local/bin/sie-server
COPY --from=sie /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# --- x402 service adapter ---
COPY sie-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY sie-service/sie_service.py /app/sie_service.py

ENV SIE_BASE_URL=http://127.0.0.1:8080
ENV SIE_PRICE_USD=0.01

# SIE server + adapter
EXPOSE 8080 8097

# Start SIE in background, then the adapter
CMD ["sh", "-c", "sie-server serve --host 0.0.0.0 --port 8080 & \
    uvicorn sie_service:app --host 0.0.0.0 --port 8097"]
