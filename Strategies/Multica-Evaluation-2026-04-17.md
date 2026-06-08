# Multica vs Paperclip — Gentech Evaluation

**Date:** 2026-04-17
**Status:** Prototype planned — Jordan handles sign-up in morning

## TL;DR

Multica is NOT a Hermes replacement — it's a Hermes integration layer. It spawns `hermes acp` as a subprocess and talks to it via ACP JSON-RPC. Same agents, better dashboard.

## Architecture

```
Multica Board (Next.js) → Go Backend (Chi) → Daemon → `hermes acp` → our agent
```

- Frontend: Next.js 16, App Router
- Backend: Go (Chi router, sqlc, gorilla/websocket)
- Database: PostgreSQL 17 with pgvector
- Agent Runtime: Local daemon, auto-detects `hermes` on PATH
- Protocol: ACP JSON-RPC 2.0 over stdin/stdout

## Multica vs Paperclip

| Feature | Paperclip | Multica |
|---|---|---|
| Agent management | Local-first, single operator | Multi-user teams |
| UI | Dashboard port 3102 (goes down) | Next.js board, issue-based |
| Hermes integration | Direct spawning | `hermes acp` subprocess (ACP protocol) |
| Task workflow | Heartbeat + approvals | Issue → assign → auto-execute |
| Skills system | Yes | Yes (compounds over time) |
| Self-hosted | Yes | Yes (Docker, one command) |
| Backend | Node.js | Go |
| Reliability | ...you know | Production-grade |
| Multi-workspace | No | Yes |
| Governance | Heavy (org chart, budgets) | Light (issues, labels) |

## What We'd Gain
- Actually working dashboard
- Issue-based task assignment (like Jira for agents)
- Multi-user for team growth
- Skills that compound across agents
- Go backend (more reliable than Node)
- Free API access (no paid X developer plan needed for social features)

## What We'd Lose
- Paperclip's approval/budget governance
- "Zero-human company" philosophy (Multica is team-focused)
- Any custom Paperclip integrations

## Prototype Plan
1. Spin up Multica self-hosted on test port (Docker)
2. Run alongside Paperclip for a week
3. Test: create agents, assign issues, monitor execution
4. Compare reliability, UX, workflow
5. Decide: migrate, complement, or pass

## Jordan's Morning Tasks
- Sign up / configure X API keys if needed
- Approve prototype spin-up
- Review findings

## Notes
- "Lol I see free api key and that's worth it alone"
- Paperclip dashboard was literally down during this conversation
- Hermes ACP integration already exists in Multica codebase
