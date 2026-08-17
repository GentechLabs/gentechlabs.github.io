# GenTech Agent Memory — CockroachDB × AWS

**Persistent, vector-indexed memory layer for AI agents, backed by CockroachDB.**

This is the GenTech vault/session-memory architecture re-homed onto CockroachDB
as a production-grade storage layer. Agents that think, act, and remember
reliably at scale.

Built for the **CockroachDB × AWS "Build with Agentic Memory"** hackathon
(Devpost: cockroachdb-ai.devpost.com, deadline Aug 18, 2026).

## What it does

Agents get three memory types, all persisted in CockroachDB:

| Type | Meaning | Example |
|------|---------|---------|
| `episodic` | What happened | "User asked about yield on Base" |
| `semantic` | Facts / knowledge | "Treasury rebalances stablecoin LP on Base" |
| `procedural` | How to do things | "To bridge, call avax_bridge_adapter" |

- **Write** memories with embeddings (pluggable embed model)
- **Semantic search** via CockroachDB's distributed vector indexing (`<=>` cosine
  operator on a `VECTOR` column) — no separate vector store
- **Recent recall** (episodic timeline)
- **Consolidation** — the "sleep" step: merges old low-importance episodic
  memories into a durable semantic summary
- **Forget** — privacy / correction
- **Stats** — memory profile per agent

## CockroachDB tools used (2+)

1. **Distributed Vector Indexing** — `VECTOR(384)` column + `<=>` cosine
   operator + vector index (ivfflat/hnsw when the access method is available;
   sequential scan fallback on v24.3). Semantic retrieval at scale, no separate
   vector DB.
2. **Managed MCP Server pattern** — `src/mcp_server.py` exposes the memory store
   as MCP tools (`memory_write`, `memory_search`, `memory_recent`,
   `memory_consolidate`, `memory_forget`, `memory_stats`) so any MCP-capable
   agent connects directly, mirroring the CockroachDB Cloud Managed MCP Server
   flow.

## AWS service used (1+)

- **AWS Lambda** — `src/lambda_handler.py` is the deployment entrypoint. It
  exposes a JSON-RPC API over the memory store (write/search/recent/consolidate/
  forget/stats/health) for invocation via API Gateway or a Lambda URL. The
  connection is cached across warm invocations for low latency.

## Quick start

```bash
# 1. Start a local CockroachDB (or use CockroachDB Cloud)
docker run -d --name cockroach-mem -p 26257:26257 -p 18080:8080 \
    cockroachdb/cockroach:v24.3.4 start-single-node --insecure \
    --store=type=mem,size=1GiB

# 2. Install deps
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 3. Run the tests (against live CockroachDB)
python -m pytest tests/ -v

# 4. Use it
python scripts/demo.py
```

## Deploy to AWS Lambda

See `serverless.yml` for a SAM/Serverless template. Set the `COCKROACH_DSN`
environment variable to your CockroachDB Cloud connection string
(`postgresql://<user>@<host>:26257/<db>?sslmode=verify-full`).

## Project layout

```
src/
  __init__.py        package version
  db.py              connection + schema (tables, vector index)
  memory.py          AgentMemory store (write/search/recent/consolidate/forget/stats)
  lambda_handler.py  AWS Lambda entrypoint (JSON-RPC API)
  mcp_server.py      MCP tools server (stdio)
tests/
  test_memory.py     9 tests against live CockroachDB
scripts/
  demo.py            end-to-end demo
serverless.yml       AWS Lambda deployment template
LICENSE              Apache 2.0
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
