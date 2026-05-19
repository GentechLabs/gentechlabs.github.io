# AgentCash Design

**Date:** 2026-05-19
**Status:** 🟢 Approved

## Problem
AI agents need to discover and pay for APIs autonomously. Currently there's no registry where agents can find x402-enabled APIs, inspect pricing, and pay per-call without human intervention.

## Proposed Solution
AgentCash is an x402 payment discovery layer — a registry + marketplace where:
1. API providers register their OpenAPI spec with pricing metadata
2. Agent consumers discover, inspect, and pay for API calls via x402
3. Built-in demo APIs showcase the flow (regime detection, price feeds)

## Alternatives Considered
1. **Standalone registry only** — simpler but no demo value, harder to showcase
2. **Full marketplace with reviews/ratings** — too much scope, YAGNI for hackathon
3. **Chosen: Registry + demo APIs + discovery** — shows the full loop in one deployable

## Architecture
```
┌─────────────────────────────────────────────┐
│              AgentCash Platform              │
├─────────────────────────────────────────────┤
│  /                    → Landing + API list   │
│  /api/register        → Register new API     │
│  /api/discover        → Search/browse APIs   │
│  /api/[id]/openapi    → OpenAPI spec         │
│  /api/[id]/call/*     → x402-protected call  │
│  /demo/regime         → AdaptiveFolio demo   │
│  /demo/price          → Price feed demo      │
└─────────────────────────────────────────────┘
         ↑ x402 payment via ampersend
         ↓ OpenAPI discovery
┌──────────────┐    ┌──────────────┐
│  API         │    │  Agent       │
│  Providers   │    │  Consumers   │
└──────────────┘    └──────────────┘
```

## Tech Stack
- Next.js 14 (App Router) — platform + API routes
- SQLite (better-sqlite3) — API registry
- TypeScript — full type safety
- ampersend SDK — x402 payment integration
- Tailwind CSS — dark theme UI
- Deploy: Vercel or GitHub Pages (static + API)

## Success Criteria
- API registration flow works (POST /api/register)
- Discovery endpoint returns registered APIs (GET /api/discover)
- Demo endpoints require x402 payment to access
- ampersend fetch can pay for demo endpoints
- Landing page shows registered APIs with pricing
- OpenAPI specs served for each registered API
