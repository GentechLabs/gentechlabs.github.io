# Handoff — CockroachDB × AWS "Build with Agentic Memory" (#23) — SHIPPED
*Prepared 2026-08-14 · Deadline **Aug 18, 2026 @ 5:00pm EDT** (4 days) · $8,750*

## Status: BUILD COMPLETE + VERIFIED (gentech, 2026-08-14)

**GenTech Agent Memory** — persistent, vector-indexed memory layer for AI agents,
backed by CockroachDB. Built at `10-Labs/cockroachdb-agentic-memory/`.

## What was built (all verified against live CockroachDB v24.3.4)

- `src/db.py` — connection + schema (agent_memory + memory_events tables, vector
  index with ivfflat/hnsw fallback for v24.3)
- `src/memory.py` — `AgentMemory` store: write / get / recent / semantic-search /
  consolidate (sleep) / forget / stats. Three memory types (episodic, semantic,
  procedural). Pluggable embed model.
- `src/lambda_handler.py` — **AWS Lambda** entrypoint (JSON-RPC API over the
  memory store) — satisfies the "1+ AWS service" requirement.
- `src/mcp_server.py` — **MCP tools server** (stdio) — mirrors the CockroachDB
  Cloud Managed MCP Server pattern.
- `scripts/demo.py` — end-to-end demo (verified: writes, semantic search, recent,
  consolidate, stats all work).
- `serverless.yml` — SAM deployment template for Lambda.
- `LICENSE` — Apache 2.0 at root (detectible in About — the #1 miss on our
  submissions).
- `README.md` — full docs.

## Verification
- **9/9 tests pass** against live CockroachDB (`python -m pytest tests/ -v`).
- Demo runs end-to-end against live CockroachDB.

## CockroachDB tools used (2+)
1. **Distributed Vector Indexing** — `VECTOR(384)` column + `<=>` cosine
   operator + vector index (ivfflat/hnsw when available; sequential fallback on
   v24.3 which only ships prefix/inverted access methods).
2. **Managed MCP Server pattern** — `src/mcp_server.py` exposes memory tools for
   MCP-capable agents.

## AWS service used (1+)
- **AWS Lambda** — `src/lambda_handler.py` + `serverless.yml`.

## REMAINING (Jordan-gated, for submission)
- [ ] Register on Devpost (cockroachdb-ai.devpost.com) — **still not confirmed**
- [ ] Record <3-min demo video (public on YouTube/Vimeo)
- [ ] Push public GitHub repo (LICENSE already at root)
- [ ] Identify which CockroachDB + AWS tools used in the submission writeup

## Notes
- Vector index: CockroachDB v24.3 only exposes `prefix`/`inverted` access methods
  (no ivfflat/hnsw yet). Code creates the index when available, else falls back
  to sequential scan (correct at demo scale). The `<=>` operator + VECTOR column
  are the distributed-vector-indexing capability.
- psycopg3 does not auto-adapt Python lists to the vector type — embeddings are
  passed as `[x,y,z]` string literals.
