# Multica vs Gentech Stack — Comparison & Fit Analysis

**Date:** 2026-04-17
**Repo:** https://github.com/multica-ai/multica (14.7K ⭐)
**Tagline:** "Your next 10 hires won't be human."

---

## What Multica Is

Open-source managed agents platform. Assign issues to AI agents like teammates — they pick up work, write code, report blockers, update status autonomously.

**Stack:** Next.js 16 + Go backend + PostgreSQL 17 (pgvector) + WebSocket
**Agent support:** Claude Code, Codex, OpenClaw, OpenCode, **Hermes**, Gemini, Pi, Cursor Agent
**Deployment:** Cloud-hosted OR self-hosted (Docker Compose)

---

## Architecture Comparison

### Multica
```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Next.js    │────>│  Go Backend  │────>│   PostgreSQL     │
│   Frontend   │<────│  (Chi + WS)  │<────│   (pgvector)     │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                            │
                     ┌──────┴───────┐
                     │ Agent Daemon │  (runs on YOUR machine)
                     └──────────────┘  (Hermes, Claude Code, etc.)
```

### Gentech (Current)
```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Telegram    │────>│  Hermes      │────>│  Obsidian Vault  │
│  (Dispatch)  │<────│  Gateway     │<────│  (Second Brain)  │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                            │
                     ┌──────┴───────┐
                     │  VPS Server  │  (agents live here)
                     └──────────────┘
```

---

## Feature Comparison

| Feature | Multica | Gentech/Hermes | Winner for Us |
|---------|---------|----------------|---------------|
| **Task Assignment** | Issue board with agent assignment | Telegram dispatch + cron jobs | Multica — proper board vs chat-based |
| **Task Tracking** | Status lifecycle (enqueue→claim→start→complete) | Manual checking via cron/Mess Hall | Multica — real status tracking |
| **Progress Streaming** | WebSocket real-time | Telegram message updates | Multica — better UX |
| **Multi-Agent** | Agents on a board with names/profiles | 4 agents in Telegram groups | Tie — both work |
| **Skill System** | Skills compound across team | Skills per agent, manual sharing | Multica — centralized |
| **Agent Runtimes** | Daemon auto-detects CLIs | Gateway manages all | Tie |
| **Communication** | Issue comments + chat | Telegram groups (HQ, Strategies, Labs) | Gentech — richer, real-time |
| **Persistent Memory** | Not built-in (relies on agent) | Second Brain + memory tool | Gentech — far superior |
| **Agent Identity** | Name + provider on board | Full personality + voice + branding | Gentech — deeper |
| **Self-Hosting** | Docker Compose | VPS + systemd | Tie — both self-hostable |
| **Cost** | Free (self-hosted) | Free (already running) | Tie |
| **Mobile Access** | Web dashboard | Telegram (native) | Gentech — Telegram is everywhere |
| **Orchestration** | Manual assignment | Hermes cron + delegation + watchdog | Gentech — more autonomous |
| **Offline Recovery** | Not documented | Catch-up digest + watchdog failover | Gentech — built this tonight |
| **Project Management** | Issues, labels, projects | Mess Hall + Second Brain notes | Multica — more structured |
| **User Model** | Multi-user teams | Solo operator (Jordan) | Depends on growth |

---

## What Multica Does BETTER

1. **Structured task management** — Real issue board vs. chat-based dispatch
2. **Skill compounding** — Centralized skill sharing across all agents
3. **Progress visibility** — WebSocket streaming, not "check Mess Hall later"
4. **Multi-user ready** — If Jordan brings on human collaborators, it's built for that
5. **Agent profiles on a board** — More professional than "4 bots in a Telegram group"

## What Gentech/Hermes Does BETTER

1. **Persistent memory** — Second Brain is massive. Multica has nothing equivalent.
2. **Agent personality/identity** — Desmond, YoYo, Dmob have full identities, not just "agent on a board"
3. **Communication layer** — Telegram is real-time, mobile-first, voice messages, media
4. **Autonomous orchestration** — Cron, delegation, watchdog, failover — agents manage themselves
5. **Offline recovery** — Catch-up digest we just built
6. **Cost** — Already running, no new infrastructure
7. **Jordan's workflow** — Telegram is his daily driver, not a web dashboard

---

## The Real Question: Can They Coexist?

**YES — and this is the play.**

Multica doesn't replace Hermes. It adds a **project management layer ON TOP** of Hermes.

```
┌─────────────────────────────────────┐
│          Multica (Board)            │
│   Issue tracking, task assignment,  │
│   progress streaming, skills hub    │
└──────────────┬──────────────────────┘
               │ API / Webhook
┌──────────────┴──────────────────────┐
│          Hermes (Brain)             │
│   Agent personality, memory,        │
│   communication, orchestration      │
└─────────────────────────────────────┘
```

**The integration pattern:**
1. Jordan creates an issue in Multica
2. Assigns it to "Desmond" (which maps to the Hermes agent)
3. Multica daemon triggers Hermes to execute
4. Hermes does the work (with its personality, memory, skills)
5. Reports back to Multica with status updates
6. Multica tracks it on the board

**What this gives us:**
- Jordan gets a proper project dashboard (Multica)
- Agents keep their identity, memory, and communication (Hermes)
- Skills compound across the team (Multica)
- Telegram stays the communication layer (Hermes gateway)
- Second Brain stays the memory layer (Hermes)

---

## For the Avalanche Agent Economy (AAE)

This is where it gets interesting. AAE needs:
- Agents as economic actors (identity, reputation) → Hermes
- Task marketplace (assignment, tracking, payment) → Multica could be this
- Skill marketplace (agents offer services) → Multica skills system
- Communication (social layer) → Telegram/Hermes

**Multica as the "project board" for AAE:**
- Agents list their capabilities as skills
- Users post tasks on the board
- Agents claim tasks autonomously
- Multica tracks completion + quality
- Reputation builds over time

---

## Recommendation

### Don't switch. Layer.

1. **Keep Hermes as the agent runtime** — personality, memory, communication, orchestration
2. **Self-host Multica as the project board** — task tracking, progress, skills compounding
3. **Connect them** — Multica daemon calls Hermes CLI, Hermes reports back to Multica
4. **Telegram stays the comms layer** — it's where Jordan lives

### Quick Test (tomorrow?)
```bash
# On VPS (or a test container)
docker compose up -d  # Multica self-host
# Point it at existing Hermes installation
# Create an agent "Desmond" mapped to Hermes
# Assign a test issue
# Watch it execute
```

### What to Watch For
- Does Multica's daemon actually integrate cleanly with Hermes CLI?
- Can we map Multica agents to specific Hermes profiles?
- WebSocket streaming — does it work with Telegram as a secondary channel?
- Skills system — can we import existing Hermes skills into Multica?

---

## TL;DR

Multica is the project management layer we didn't know we needed. It doesn't replace Hermes — it gives it a proper dashboard. Keep Telegram for communication, Hermes for agent intelligence, Multica for structured task management. Best of all three worlds.

**Jordan's rule holds:** "I don't marry technology." If Multica doesn't fit after testing, we drop it. But the fit looks strong.
