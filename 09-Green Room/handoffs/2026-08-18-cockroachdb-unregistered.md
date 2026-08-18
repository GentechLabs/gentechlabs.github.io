# CockroachDB Hackathon — UNREGISTERED (Aug 18, 2026)

**Decision (Jordan, Aug 18):** Not finishing the CockroachDB × AWS "Build with
Agentic Memory" hackathon. Jordan unregistered us. We could not complete it in time.

## What was cleared
- ❌ Docker container `cockroach-mem` (cockroachdb v24.3.4) — **stopped + removed**,
  freed ~1GB RAM. No longer running.
- ❌ `09-Green Room/submissions/cockroachdb-submission-package.md` → moved to
  `_archive/submissions/` (kept for reference, not active).

## What was KEPT (still useful, NOT hackathon-collateral)
- ✅ `10-Labs/cockroachdb-agentic-memory/` project code — the build itself
  (src/, tests/, Lambda handler, MCP server). The 9/9 passing tests + the
  agentic-memory concept remain reusable; only the hackathon entry is dropped.
- ✅ `agentmemory-mcp` process — a SEPARATE tool, untouched (not part of this hackathon).

## Note
The build was fully verified (9/9 tests) but we chose not to submit. The working
agentic-memory layer is still there if we ever want it for a future submission or
internal use — the unregistration only ends the hackathon entry, not the code.
