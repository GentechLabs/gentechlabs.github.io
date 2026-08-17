# CockroachDB × AWS — Agentic Memory Submission Package

> **Deadline:** Aug 18, 2026 (TODAY)
> **Devpost:** cockroachdb-ai.devpost.com
> **Prize:** $8,750 total ($5K / $2.5K / $1.25K)
> **Repo:** Gentech-Labs/cockroachdb-agentic-memory (public)
> **Status:** Build SHIPPED + verified (9/9 tests, live CockroachDB v24.3.4)

---

## 1. Submission Text (paste into Devpost)

### Project Title
**GenTech Agent Memory — Persistent, Vector-Indexed Memory for AI Agents on CockroachDB**

### Elevator Pitch
A production-grade memory layer that gives AI agents reliable, persistent recall — backed by CockroachDB's distributed vector indexing and deployed on AWS Lambda. Agents that think, act, and remember at scale.

### What it does
Agents get three memory types, all persisted in CockroachDB:
- **Episodic** — what happened ("User asked about yield on Base")
- **Semantic** — facts/knowledge ("Treasury rebalances stablecoin LP on Base")
- **Procedural** — how to do things ("To bridge, call avax_bridge_adapter")

Core operations: write memories with embeddings, semantic search via CockroachDB's `<=>` cosine operator on a VECTOR column (no separate vector store), recent recall, consolidation (the "sleep" step that merges old episodic memories into durable semantic summaries), forget (privacy/correction), and stats.

### CockroachDB tools used (2+)
1. **Distributed Vector Indexing** — `VECTOR(384)` column + `<=>` cosine operator + vector index. Semantic retrieval at scale with no separate vector DB.
2. **Managed MCP Server pattern** — `src/mcp_server.py` exposes the memory store as MCP tools (`memory_write`, `memory_search`, `memory_recent`, `memory_consolidate`, `memory_forget`, `memory_stats`) so any MCP-capable agent connects directly — mirroring the CockroachDB Cloud Managed MCP Server flow.

### AWS service used (1+)
- **AWS Lambda** — `src/lambda_handler.py` is the deployment entrypoint, exposing a JSON-RPC API over the memory store (write/search/recent/consolidate/forget/stats/health) for invocation via API Gateway or a Lambda URL. Connection cached across warm invocations for low latency.

### Why it matters
Most AI agents are stateless — they forget everything between sessions. This gives agents durable memory that scales, with semantic retrieval built into the database itself. It's the difference between an agent that answers and an agent that *remembers*.

### Tech stack
Python, CockroachDB v24.3.4 (distributed vector indexing + MCP server), AWS Lambda, Apache 2.0.

### Repo
https://github.com/Gentech-Labs/cockroachdb-agentic-memory

---

## 2. Demo Video Script (~2.5 min)

### Shot 1 — Hook (0:00–0:20)
- Terminal: `python scripts/demo.py`
- Show the memory layer writing 6 memories (3 episodic, 3 semantic)
- Voice: "Most AI agents forget everything between sessions. This is a memory layer that doesn't — backed by CockroachDB."

### Shot 2 — Semantic search (0:20–0:50)
- Run the semantic search: "how to move money across chains"
- Show it returning the relevant memories with similarity scores
- Voice: "Semantic search runs on CockroachDB's distributed vector indexing — the `<=>` cosine operator on a VECTOR column. No separate vector database needed."

### Shot 3 — Consolidation / sleep (0:50–1:20)
- Run the consolidate step
- Show old episodic memories merging into a durable semantic summary
- Voice: "The 'sleep' step — consolidation merges old low-importance memories into durable knowledge, just like a human consolidating memories overnight."

### Shot 4 — MCP + AWS (1:20–1:50)
- Show `src/mcp_server.py` exposing the MCP tools
- Show `src/lambda_handler.py` (AWS Lambda entrypoint)
- Voice: "Any MCP-capable agent connects directly. And it deploys to AWS Lambda for serverless, low-latency access."

### Shot 5 — Tests + close (1:50–2:30)
- Run `python -m pytest tests/ -v` → 9/9 pass
- Voice: "Nine tests, all passing against live CockroachDB. Persistent, vector-indexed memory for AI agents — built on CockroachDB and AWS."

---

## 3. Submission Checklist
- [ ] Register on Devpost (cockroachdb-ai.devpost.com)
- [ ] Push public repo (Gentech-Labs/cockroachdb-agentic-memory)
- [ ] Record <3min demo video (script above)
- [ ] Paste submission text
- [ ] Submit before Aug 18 deadline
