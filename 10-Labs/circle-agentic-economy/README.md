# GenTech Labs — Circle Agentic Economy Prize Submission

**An AI agent autonomously paying another agent's inference service in USDC.**

This is our entry for the **Circle Agentic Economy Prize** ($50K, funded by
Circle) — a bonus prize inside the **Build with Gemini XPRIZE**.

## The thesis

Software is starting to pay for itself. This submission makes it real: a
**Circle Agent Stack** agent creates its own wallet on Base, discovers a
self-hosted **Superlinked Inference Engine (SIE)** service, and pays for it
with a **USDC nanopayment** — genuinely agent-driven, no human checkout.

The service being paid is our own **x402 gateway** (`api.gentechlabs.net`),
which exposes SIE's inference (embeddings, rerank, entity extraction, agent
loop) as pay-per-call endpoints. One agent pays another agent's service.
That's the machine-money loop.

## Architecture

```
┌─────────────────────────┐        ┌──────────────────────────────┐
│  Circle Agent Stack      │        │  GenTech x402 Gateway        │
│  (paying agent)          │        │  api.gentechlabs.net         │
│                          │        │                              │
│  • Agent Wallet (Base)   │  USDC  │  • HTTP 402 challenge        │
│  • Discovers service     │ ─────► │  • Verifies EIP-3009 proof   │
│  • Pays nanopayment      │        │  • Routes to backend         │
└─────────────────────────┘        └──────────────┬───────────────┘
                                                  │
                                          ┌───────▼────────┐
                                          │  SIE Service   │
                                          │  (GCP, self-   │
                                          │   hosted)      │
                                          │  /v1/embeddings│
                                          │  /v1/rerank    │
                                          │  /v1/extract   │
                                          │  /v1/chat      │
                                          └────────────────┘
```

## Repo layout

```
sie-service/          SIE x402 service adapter (FastAPI) + tests
  sie_service.py      paid endpoints, 402 gating, proxies to SIE
  test_sie_service.py  verifies 402 gate + paid path
  requirements.txt
circle-agent/         Circle Agent Stack paying agent
  circle_agent.py     wallet → discover → inspect → pay → call loop
gcp/                  GCP deployment
  Dockerfile          SIE + adapter in one container
  docker-compose.yml  local dev / Cloud Run
proof/                submission proof items (see below)
```

## The 3 proof items (prize requirement)

1. **Public GitHub repo** — this repo (integration verified).
2. **Recorded demo** — a real, verifiable USDC transaction executed by the
   agent (see `proof/demo.md` for the shot list).
3. **Agent's Circle wallet address + clickable block-explorer URL** — the
   wallet that paid, with the on-chain tx visible (see `proof/wallet.md`).

## Judging criteria (how we score)

| Criterion | Our answer |
|-----------|-----------|
| **Creativeness & Innovation** | An agent paying another agent's inference service — the machine-money loop |
| **Centrality to Business** | Payment *is* the product: pay-per-call inference, not a bolted-on feature |
| **Technical Depth & Autonomy** | Agent discovers, evaluates, and pays on its own within policy |
| **Customer Experience** | A real service a real agent would use, gas-free sub-cent payments |

## GCP hosting (base competition rule)

SIE + the adapter deploy to **Google Cloud Run** (see `gcp/`). The Circle
agent uses the **Google ADK** runtime with a Gemini model (`GOOGLE_API_KEY`).

## Status

- [x] SIE x402 service adapter — built + tested (402 gate verified)
- [x] GCP deploy config — Dockerfile + docker-compose validated
- [x] Circle agent scaffold — wallet→discover→pay→call loop
- [ ] Register main Build with Gemini XPRIZE (Jordan)
- [ ] Deploy SIE to GCP (needs gcloud creds)
- [ ] Install Circle CLI + fund agent wallet (Jordan)
- [ ] Run real USDC nanopayment, capture demo + wallet proof

## License

Apache-2.0
