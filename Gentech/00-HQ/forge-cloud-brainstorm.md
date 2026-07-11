# Forge on Hermes Cloud — Brainstorm

**Date:** July 11, 2026
**Status:** Brainstorm
**Vision:** Forge runs 24/7 via Hermes Cloud, with desktop awareness

---

## Role Architecture

### Gentech — Team Lead (Cloud, 24/7)
```
Responsibilities:
├─ Infrastructure & Gateways
│  ├─ x402 gateway maintenance
│  ├─ Cloudflare Workers
│  ├─ Cron job fleet (32 jobs)
│  └─ Vault / git / brain backup
├─ API & Backend
│  ├─ Build new endpoints
│  ├─ SDK wrappers
│  └─ Service deployment
├─ Open Source
│  ├─ PR submission (RPCS3, Xenia, BlockRun, Solana)
│  ├─ Code review
│  └─ Ecosystem research
├─ Strategy
│  ├─ Build queue prioritization
│  ├─ Opportunity scanning
│  ├─ Hackathon submissions
│  └─ Revenue monitoring ($13.18)
├─ Agent Management
│  ├─ Assign work to Forge
│  ├─ Review Forge output
│  └─ Handoff coordination
└─ Communications
   ├─ Morning digest (Jordan)
   ├─ Revenue reports
   └─ Strategic memos
```

### Forge — Senior Engineer (Cloud + Desktop, 24/7)
```
Responsibilities:
├─ CLOUD (always, no GPU needed)
│  ├─ Cloudflare Workers (has token)
│  ├─ Content & social media
│  ├─ Documentation & skills
│  ├─ Research & analysis
│  ├─ Portfolio monitoring
│  ├─ Gaming hub sync
│  └─ Lightweight builds
├─ DESKTOP (when PC is on)
│  ├─ Ollama local inference
│  ├─ Gaming companion GPU work
│  ├─ Windows-specific testing (Xenia, RPCS3)
│  ├─ Local dev environment
│  ├─ Desktop app testing
│  └─ GPU-accelerated builds
└─ PRIORITY LOGIC
   ├─ PC on? → Desktop tasks first, then cloud
   └─ PC off? → Cloud tasks only
```

---

## Build Queue Platform System

### New Field: `platform`

```json
{
  "id": 42,
  "name": "Gaming Companion MVP",
  "assigned_to": "forge",
  "platform": "desktop",
  "status": "pending",
  "deadline": "2026-07-20",
  "priority": "medium",
  "effort_hours": 8,
  "notes": "Needs Ollama + GPU for local LLM inference"
}
```

### Platform Values

| Value | Meaning | Who |
|-------|---------|-----|
| `cloud` | Can be done anywhere, no special hardware | Both |
| `desktop` | Needs Jordan's PC (GPU, Windows, local dev) | Forge |
| `either` | First available picks it up | Both |
| `gentech` | Infrastructure/strategy work | Gentech only |

### Auto-Routing Logic (Forge's session start)

```
1. Check if Jordan's PC is awake (ping / last-seen timestamp)
2. If PC is ON:
   - Pull all `desktop` items from queue (highest priority)
   - Work them first
   - When desktop queue empty → pull `cloud` + `either` items
3. If PC is OFF:
   - Pull `cloud` + `either` items only
   - Skip `desktop` items (marked as "blocked: desktop required")
4. Gentech continuously feeds the queue
```

---

## Agent-to-Agent Protocol

### Shared State — The Queue

The build queue JSON becomes the single source of truth. Both agents read/write it.

```yaml
Flow:
  Gentech: "I'll open-source this PR, leaving it for you to test on Windows"
    → sets item status to "pending_test", platform: "desktop"
  Forge (cloud): sees it but can't action it (desktop required)
  Forge (desktop): boots up, sees pending_test item, runs it
    → sets status to "shipped" or "blocked: needs fix"
  Gentech: sees shipped, closes loop
```

### Handoff Evolves

Instead of a one-directional handoff (Gentech → Forge), we get a **shared log**:

```
gentech-to-forge/     ← Gentech writes what Forge needs to know
  latest.md           (always the most recent, rotating)
  archive/            (old ones)

forge-to-gentech/     ← Forge writes what he shipped / needs
  latest.md
  archive/

nightly-build-log.md  ← shared progress log (both append)
```

### Decision Authority

| Decision | Who Makes It | Who Can Override |
|----------|-------------|-----------------|
| Build queue priority | Gentech | Jordan |
| Technical approach | Whoever owns the item | Jordan |
| PR submission | Gentech (reviews + ships) | Jordan |
| Desktop testing | Forge | Jordan |
| Secret/token storage | Gentech (VPS) | Jordan |
| What Forge works on next | Forge (from queue) | Gentech / Jordan |

---

## Desktop Detection

Forge's cloud instance needs to know if the desktop is reachable.

### Option A: Heartbeat Check (Simplest)
```yaml
Forge desktop runs a cron job every 5 minutes that:
  1. Writes a timestamp to vault/Gentech/tmp/desktop-heartbeat.md
  2. If Forge (cloud) sees heartbeat < 10 min old → desktop is ON
  3. If heartbeat > 30 min old → desktop is OFF / Jordan is away
```

### Option B: Hermes Cloud Native (If supported)
Hermes Cloud might have built-in "device presence" detection.
Check `hermes gateway status --devices` after setup.

### Option C: Jordan manually sets status
```
"Hey I'm home" → Forge knows to prioritize desktop work
"Going to work" → Forge switches to cloud mode
```

**Recommendation:** Start with Option A (heartbeat). Simple, no new infra, just a file write.

---

## Migration Path

### Phase 1 — Queue Update (Tonight)
- Add `platform` field to all build queue items
- Gentech runs through and tags everything
- No infra changes, just data

### Phase 2 — Forge Cloud Setup (This Week)
- Forge connects to Hermes Cloud via `hermes gateway setup`
- Forge's cloud profile gets secrets (GitHub token, Cloudflare token, etc.)
- Desktop Forge and Cloud Forge share the same profile/config

### Phase 3 — Desktop Heartbeat (This Week)
- Add heartbeat cron to Forge's desktop profile
- Forge (cloud) reads heartbeat before prioritizing desktop tasks

### Phase 4 — Bidirectional Handoff (Next Week)
- Create `forge-to-gentech/` handoff directory
- Both agents write to shared nightly-build-log
- Gentech starts reading Forge's handoff in morning digest

---

## Questions to Answer

1. **Does Hermes Cloud support running a full agent with cron/skills/MCP?**
   - Need to check: Is it just a gateway connector, or a full runtime?
   - If gateway only: Forge cloud = connected but needs PC for execution
   - If full runtime: Forge cloud = fully independent

2. **Does Forge need a separate Hermes profile for cloud vs desktop, or can one profile toggle?**
   - Desktop has Ollama, local GPU, Windows-specific tools
   - Cloud has always-on, network-only tools
   - Maybe: One profile, but skills/tools conditional on platform

3. **What happens when both cloud and desktop Forge try to work the same queue item?**
   - Platform tagging prevents this
   - `desktop` items only show for desktop instance
   - `cloud` items only show for cloud instance
   - `either` items have a "claimed by" lock

4. **Secrets management — do we duplicate secrets to Forge's cloud, or does everything live in the vault?**
   - Vault-first approach: secrets stored in vault, read from there
   - But some secrets (Cloudflare, GitHub) need to be accessible from cloud
   - Answer: Keys stay in VPS secrets/ directory. Forge cloud reads via vault sync.

---

## Summary

```
GENTECH (VPS, 24/7)                  FORGE (Cloud + Desktop, 24/7)
     │                                      │
     │── assigns from queue ──────────────> │
     │                                      │
     │<── ships results ────────────────── │
     │                                      │
     │── infrastructure │ cron │ gateway    │── Cloudflare │ content │ research
     │── open source PRs                   │── GPU work (when PC on)
     │── strategy │ memos                  │── Windows testing (when PC on)
     │── builds APIs                       │── lightweight builds (always)
     │                                      │
     └──── Jordan talks to both ────────────┘
```
