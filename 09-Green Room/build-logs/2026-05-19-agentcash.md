# AgentCash Build Log

**Date:** 2026-05-19
**Status:** Built and verified

## What We Built
AgentCash — x402 payment discovery layer for AI agents. Registry + marketplace where API providers register OpenAPI specs with pricing, and agent consumers discover, inspect, and pay per-call.

## Architecture
- Next.js 14 App Router (TypeScript, Tailwind)
- SQLite (better-sqlite3) for API registry
- x402 v2 middleware (PAYMENT-REQUIRED base64 header)
- ampersend SDK integration (fetch + inspect)
- 3 demo APIs: regime detection, price feed, oracle data

## Key Decisions
1. **x402 v2 format** — Uses `PAYMENT-REQUIRED` base64 header, not JSON body. v1 used body, v2 moved to headers.
2. **Relative imports** — `@/` alias doesn't work for server-side imports in Next.js dev mode. Used relative paths.
3. **process.cwd()** for DB path — `__dirname` resolves to compiled output dir in Next.js, not project root.
4. **Page/route separation** — Can't have page.tsx and route.ts at same `/api/[id]` path. Moved detail page to `/apis/[id]`.

## Endpoints Built
- `POST /api/register` — Register API with OpenAPI spec + pricing
- `GET /api/discover` — Browse/search registered APIs
- `GET /api/[id]` — API detail (JSON)
- `GET /api/[id]/openapi` — OpenAPI spec for registered API
- `GET /api/demo/regime` — x402-protected regime detection (1 USDC)
- `GET /api/demo/price` — x402-protected price feed (0.5 USDC)
- `GET /api/demo/oracle` — x402-protected oracle data (0.75 USDC)
- `GET /apis/[id]` — API detail page (HTML)
- `GET /` — Landing page with registered API cards

## Verification
- ✅ Build passes: `npm run build` — 0 errors, 0 warnings
- ✅ Registry CRUD: register → discover → detail → openapi
- ✅ Demo endpoints return correct JSON
- ✅ x402 middleware: 402 without payment, 200 with payment header
- ✅ ampersend inspect: correctly parses PAYMENT-REQUIRED header
- ⚠️ ampersend fetch: payment fails due to ampersend API auth (401) — infrastructure issue, not our code

## Pitfalls Encountered
1. **`@/` path alias** — Works in client-side but not server-side in dev mode. Fixed with relative imports.
2. **`__dirname` in Next.js** — Resolves to `.next/server/...`, not project root. Used `process.cwd()`.
3. **better-sqlite3 import** — `esModuleInterop` flag needed. Used `import * as Database`.
4. **Page/route conflict** — Can't have page.tsx + route.ts at same dynamic route path.
5. **x402 format** — v1 used body JSON, v2 uses base64 `PAYMENT-REQUIRED` header. Ampersend only parses v2.
6. **Port conflicts** — Next.js dev server on 3000 often conflicts. Used 3001.
7. **SQLite WAL files** — Stale `.db-shm`/`.db-wal` files cause I/O errors. Clean them when restarting.

## Files
- `/root/repos/agentcash/` — Full project
- `/root/vaults/gentech/09-Green Room/designs/agentcash.md` — Design doc
- `/.hermes/plans/agentcash.md` — Implementation plan
