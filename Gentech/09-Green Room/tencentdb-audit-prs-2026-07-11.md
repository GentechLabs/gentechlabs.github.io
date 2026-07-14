# TencentDB Agent Memory — Hermes Plugin Audit 🔍

**Repo:** TencentCloud/TencentDB-Agent-Memory
**Audit Date:** 2026-07-11
**Auditor:** Gentech
**Target:** `hermes-plugin/memory/memory_tencentdb/`
**Status:** High quality — 3 PR opportunities identified

---

## Overall Assessment

This is a **production-grade Hermes plugin**. The code shows real battle scars — circuit breakers, watchdog threads, shutdown-leak regression tests, API key rotation. Tencent put serious engineering into this.

---

## What They Got Right ✅

| Area | Notes |
|------|-------|
| **Plugin interface** | Uses `agent.memory_provider.MemoryProvider` — the canonical Hermes contract |
| **Backward compat** | Aliases `tdai` and `memory-tencentdb` so existing configs keep working |
| **Circuit breaker** | 5 failures → 60s cooldown — prevents cascading failures |
| **Watchdog thread** | 10s polling for Gateway health, auto-resurrects |
| **Thread safety** | Bounded thread pool (max 4), proper join timeouts, daemonized threads |
| **Memory management** | `_RECOVER_COOLDOWN_SECS` (15s) < `_BREAKER_COOLDOWN_SECS` (60s) — can recover within a breaker window |
| **Env var design** | `MEMORY_TENCENTDB_*` namespace with `TDAI_*` fallbacks for backward compat |
| **API key support** | Bearer token auth with whitespace-stripping (handles env var edge cases) |
| **Subprocess mgmt** | Tracks `start_new_session=True` so it knows whether it owns the Gateway — won't kill external processes |
| **Shutdown leak fix** | Regression-tested: orphan Gateway processes used to survive Hermes restarts |
| **Docker** | All-in-one Dockerfile that installs Hermes + plugin + Gateway in one layer |
| **Skills ecosystem** | 4 SKILL files (SKILL.md, SKILL-MIGRATION.md, SKILL-DIAGNOSTIC-EXPORT.md) |
| **Documentation** | Comprehensive README, Chinese README, CONTRIBUTING docs |

---

## Identified Opportunities for PRs

### PR 1: `presidio-hardened-x402-mcp`-style — Security Hardening (Medium, 2-3h)

**What:** The auth key has a single fallback chain (`MEMORY_TENCENTDB_GATEWAY_API_KEY` → `TDAI_GATEWAY_API_KEY`). No rotation signal, no key expiry warning. We've seen this pattern before in the agent ecosystem (Injective npm attack).

**Suggested improvement:**
- Add `MEMORY_TENCENTDB_GATEWAY_API_KEY_LAST_ROTATED` env var
- Log a warning when the key is >90 days old
- Add a `get_auth_health()` method that reports key age
- Bind the API key env vars to the Dockerfile with `--secret` instead of `-e`

**Why us:** We wrote `presidio-hardened-x402-mcp` guard patterns. This is our lane.

**Source files:** `client.py` (auth handling), `__init__.py` (env var parsing), `Dockerfile.hermes`

---

### PR 2: Python SDK Examples (Easy, 1h)

**What:** The repo has a full Python Hermes plugin but **no standalone Python examples** of calling the Gateway directly. The SDK client (`client.py`) is clean and reusable. Add an `examples/python/` directory with:

- `examples/python/quickstart.py` — Connect to Gateway, write a memory, read it back
- `examples/python/list-memories.py` — List recent memories via L0/L1/L2/L3 endpoints
- `examples/python/health-check.py` — Verify Gateway health

**Why us:** We're Python-first. Our Agent Kit is Python. We can provide the first Python usage examples.

**Source files:** `client.py` (the SDK is already there, just needs examples)

---

### PR 3: Docker Compose for Vault-Integrated Deployment (Medium, 2h)

**What:** The Dockerfile is air-gapped (single container). Add a `docker-compose.yml` that:

- Mounts a persistent vault data directory (`TDAI_DATA_DIR`)
- Exposes the Gateway health endpoint for monitoring
- Shows the memory data as a mounted volume (our vault pattern)
- Example: `docker compose up -d` → Hermes starts with memory_tencentdb backed by local vault data

**Why us:** We run 32 cron jobs on our vault. We know persistent Hermes deployment. Our vault-integration pattern is something Tencent doesn't show.

**Source files:** `docker/opensource/Dockerfile.hermes`, `SKILL.md`

---

## Architecture Summary

```
┌─────────────────────────────────────────────────┐
│                   Hermes Agent                    │
│  ┌──────────────────────────────────────────┐    │
│  │       memory_tencentdb Provider           │    │
│  │  (__init__.py — 1,130 lines of Python)   │    │
│  │                                           │    │
│  │  on_memory_write() → POST /capture        │    │
│  │  on_session_end()   → POST /end-session   │    │
│  │  query()            → POST /search         │    │
│  └────────────────────┬─────────────────────┘    │
└───────────────────────┼──────────────────────────┘
                        │ HTTP :8420
┌───────────────────────┴──────────────────────────┐
│           TDAI Memory Gateway (Node.js)           │
│                                                   │
│  src/gateway/server.ts                            │
│                                                   │
│  L0 ─ Raw conversation logs                       │
│  L1 ─ Atomic fact extraction                     │
│  L2 ─ Scenario blocks                            │
│  L3 ─ Persona synthesis                          │
│                                                   │
│  Backends: LiteDB / TiKV / TCVDB                  │
└───────────────────────────────────────────────────┘
```

---

## Next Steps

| Step | What | Who |
|------|------|-----|
| 1 | Open PR #1 (security hardening) | Gentech |
| 2 | Open PR #2 (Python examples) | Gentech |
| 3 | Prepare PR #3 (Docker Compose) | Forge (desktop test needed) |
| 4 | After PRs merged → integration eval | Forge |
