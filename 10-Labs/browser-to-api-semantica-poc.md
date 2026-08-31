# Browser-to-API + Semantica — PoC Findings

**Date:** 2026-08-16
**Status:** ✅ PoC complete — both tools verified working
**Source:** Shubham Saboo X post (Aug 15) + Jordan greenlight (Aug 16)

---

## 1. `browser-to-api` — Website → OpenAPI spec (VERIFIED WORKING)

**What it does:** Captures a browser session's network traffic, then auto-generates an OpenAPI 3.1 spec + a zero-dependency JS client + an HTML report. Two skills compose:

```
browser-trace   →  .o11y/<run>/cdp/network/{requests,responses}.jsonl
browser-to-api  →  .o11y/<run>/api-spec/{openapi.yaml, client.mjs, index.html, report.md}
```

**PoC result (our own deal-tracker API, port 8080):**
- Captured 4 real endpoints: `/v1/deals`, `/v1/health`, `/v1/games/price-watch`, `/v1/games/release-radar`
- Generated a valid OpenAPI 3.1 spec with inferred JSON schemas (Deals, Items components)
- Generated a working `client.mjs` — **verified it calls the live API and returns real data** (10 deals, health status, price-watch)
- Output at `/root/poc-browser-api/.o11y/deal-tracker-poc/api-spec/`

**Install notes (pitfalls hit):**
- `browse` CLI is NOT the `/usr/bin/browse` (that's a symlink to `xdg-open`). Install the real one: `npm install -g browse`
- The Hermes skill installer **missed support files** — `browser-trace` was missing `lib.mjs` + `snapshot-loop.mjs`; `browser-to-api` was missing 5 scripts + the `lib/` dir. Fixed by copying from upstream `github.com/browserbase/skills`. **This is a skill-installer bug worth reporting.**
- Chrome as root needs `--no-sandbox`
- `browse network on` is required to capture response bodies (CDP firehose alone has request bodies only)

**Strategic fit (Jordan's insight — "we did the opposite, we have a website and put APIs there"):**
- This is the **inverse** of our current flow. We hand-write APIs and expose them. This tool auto-discovers an API from a website's traffic.
- **GenTech Hub match:** our Hub surfaces (Treasury, Arcade, Cookbook, Travel, Gaming) are websites with APIs behind them. This tool can auto-generate OpenAPI specs for them → makes them **discoverable + integrable** by other agents → feeds the x402 gateway.
- **Academy fit:** "Ship Paid APIs in a Weekend" course gets a new chapter — "turn any website into an API in 5 minutes" → then drop x402 on top. Much lower barrier for non-technical people (Jocelyn-level).
- **x402 Gateway fit:** auto-generated OpenAPI spec → wrap with x402 payment middleware → billable endpoint. The "website → paid API" pipeline.

---

## 2. Semantica — Graph-native context + decision provenance (VERIFIED WORKING)

**What it does:** Graph-native infrastructure for context and accountable AI. Knowledge graphs, W3C PROV-O provenance, decision audit trails, causal reasoning, SHACL/OWL governance. "The open-source Palantir for AI agents."

**PoC result:**
- `ContextGraph` records decisions as first-class nodes with reasoning + confidence
- `ProvenanceManager` tracks entity provenance (source, extractor)
- `RDFExporter` produces W3C PROV-O-style RDF audit trails — verified working (Turtle output)
- Output at `/tmp/semantica-audit.ttl`

**Strategic fit:**
- **GTA provenance:** every trade becomes a queryable, auditable decision node with a "why" a regulator would accept. Directly strengthens our trust substrate.
- **Agent Credit Score:** decision history + provenance = the raw material for scoring agent reliability. Semantica gives us the structured, queryable decision log.
- **Fleet context:** shared knowledge graph across agents instead of per-agent vaults.
- **Hackathon angle:** "auditable AI decisions" is a strong submission theme (CockroachDB agentic-memory, BOT Chain RWA).

**Caveat:** semantica pulls a **heavy dependency tree** (torch, transformers, spacy, faiss, ~2GB). It bumped `requests` 2.33→2.34. For a production GTA integration, we'd want to isolate it (separate venv/container) rather than pollute the main hermes env.

---

## Next steps (Labs)

- [x] **Wire `deal_tracker` into x402 gateway** — LIVE (v9.2.0). `/v1/deals/{path}` → backend `/v1/{path}`, $0.005/call, USDC on Base. Verified 402 challenge.
- [x] **Animated explainer** — 30s GSAP → extended to 57s with a cloned voiceover. `explainer/gentech-website-to-api-narrated.mp4`
- [x] **Live demo** — real browser capture of deals API → x402 challenge → OpenAPI spec → client. `live-demo/live-demo.mp4`
- [x] **Cloned voiceover** — `dwPf6y3q42Kdh7xBSGKx` (Jocelyn-English asset), 5 segments, `eleven_multilingual_v2`, stability 0.60/similarity 0.85/speed 0.95. Muxed into narrated explainer.
- [x] **Deployed to demo site** — both videos live at `gentechlabs.net/videos/`, embedded in `demo.html` (video section + "Website → Paid API" card in Payment Infrastructure). Verified HTTP 200 + content.
- [ ] Report the skill-installer bug (missing support files) to Nous
- [ ] Decide: use browser-to-api to auto-generate OpenAPI specs for our Hub surfaces → feed x402 gateway
- [ ] Add "website → API" chapter to GenTech Academy course
- [ ] Scope semantica as GTA provenance layer (isolated venv) — map against Agent Credit Score
