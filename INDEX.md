---
date: 2026-06-07
purpose: Master vault navigation hub — links to every section and key file
updated: 2026-06-07
---

# 🧠 GenTech Vault — Master Index

> **Welcome.** This is the single source of truth for navigating the GenTech vault. Every section, every key file, every workflow — linked here.
>
> **Cross-reference:** [[HQ/INDEX]] | [[Labs/INDEX]] | [[Projects/INDEX]] | [[Strategies/INDEX]] | [[Entertainment/INDEX]] | [[Content/INDEX]] | [[Green-Room/INDEX]]

---

## 🗺️ Vault Map

| Zone | Purpose | Owner | Index |
|------|---------|-------|-------|
| **[[HQ/INDEX]]** | Operations — approvals, travel, grants, status board | Jordan | [[HQ/STATUS-BOARD]] |
| **[[System]]** | Agent configs, channel maps, cron jobs, secrets | Gentech | — |
| **Agents** | Bot configs, voice profiles | Gentech | — |
| **Agent-Arena** | Agent Arena formal spec | DMOB | [[Agent-Arena/AAE-FORMAL-SPEC]] |
| **[[Labs/INDEX]]** | Smart contracts, hackathons, bounties, research | DMOB | [[Labs/_INDEX]] |
| **[[Projects/INDEX]]** | Active builds with repos (Foundry, Anchor) | DMOB/YoYo | — |
| **[[Strategies/INDEX]]** | DeFi research, market analysis, LP tracking | YoYo | [[Strategies/_INDEX]] |
| **[[Entertainment/INDEX]]** | Content strategy, branding, episode drafts | Desmond | [[Entertainment/_INDEX]] |
| **Learning** | Course notes, academy material | Jordan | [[Learning/README]] |
| **Audits** | Code audits (Kite AI, C4) | DMOB | — |
| **[[Content/INDEX]]** | X drafts, blog posts, podcast concepts, social | Desmond | [[Content/Shared-References/INDEX]] |
| **Daily-Digest** | Daily digest summaries | Auto | — |
| **[[Green-Room/INDEX]]** | Active workspace — build logs, ideas, designs, travel | All | [[Green-Room/WORKFLOW-ACTIVE]] |
| **Archive** | Stale folders, swept history, merge artifacts | Auto | — |
| **Mess-Hall** | Decisions, sweep reports, banter | All | — |
| **Skills** | Agent skill exports, skill wikis | Auto | — |
| **Gaming** | POE2 builds, Vanito companion | Jordan | — |
| **Daily/** | Daily notes (date-stamped) | Jordan | — |
| **pals/** | GenTech Pals data (gaming companion) | Gentech | — |
| **scripts/** | Utility scripts (hackathon scanner, etc.) | Auto | — |
| **data/** | Structured data (projects.json) | Auto | — |

---

## 🔑 Quick Links

### Active Work (Jun 7, 2026)
- [[HQ/STATUS-BOARD]] — **Source of truth for what's live**
- [[00-Working-Memory]] — Current sprint state
- [[Green-Room/WORKFLOW-ACTIVE]] — Routing & workflow rules

### Hackathons & Grants
- [[HQ/hackathon-tracker]] — All hackathon statuses
- [[Strategies/Grant-Applications-Queue]] — Grant pipeline
- [[Labs/Hackathons/HACKATHON-ROSTER-2026]] — Full 2026 roster
- [[HQ/grants/pipeline]] — Active grant applications

### Infrastructure
- [[HQ/smart-routing-rules]] — Agent routing protocol
- [[Skills/agents-protocol]] — Agent communication rules
- [[Skills/channel-boundaries]] — Channel scope rules
- [[HQ/vault-health]] — Vault health metrics

### DeFi & Strategy
- [[Strategies/aae-core-philosophy]] — AAE core vision
- [[Strategies/agentic-finance-landscape]] — Market landscape
- [[Strategies/GenTech-Full-Strategy-Overview]] — Full strategy
- [[Strategies/Defi-Monitor]] — DeFi position monitoring

### Content & Brand
- [[Entertainment/Content-Strategy]] — Content framework
- [[Entertainment/content-pipeline]] — Publishing pipeline
- [[Content/Gentech-Brand-Narrative]] — Brand narrative
- [[HQ/Marketing]] — Marketing materials

### Travel
- [[HQ/HQ/01-Travel/trip-plan-2026-updated]] — Philippines trip plan
- [[Green-Room/philippines-trip-research]] — Trip research
- [[Green-Room/flight-price-log]] — Flight price tracking

### Learning
- [[Learning/GenTech-Academy/README]] — Academy modules
- [[Learning/Solana-for-EVM-Devs-CheatSheet]] — Solana cheat sheet
- [[Learning/x402-Research]] — x402 protocol research

---

## 🏷️ Tag Reference

- `#agent:yoyo` `#agent:dmob` `#agent:desmond` `#agent:gentech`
- `#status:active` `#status:todo` `#status:done`
- `#type:research` `#type:code` `#type:content`

---

## 🤖 Agent Routing

| Agent | Domain | Writes To |
|-------|--------|-----------|
| **Gentech** | Coordinator — routes everything | `HQ/`, `Daily/` |
| **YoYo** | DeFi, market research, LP tracking | `Strategies/` |
| **DMOB** | Smart contracts, security, hackathons | `Labs/` |
| **Desmond** | Content, branding, social media | `Entertainment/`, `Content/` |

**Routing rules:** [[Skills/agents-protocol]] | [[HQ/smart-routing-rules]]

---

## 📋 Maintenance Rules

1. **Single-file folders** → Move file to parent MOC; delete empty shell
2. **Merge artifacts** (`_*`) → Archive to `Archive/` with provenance
3. **Cross-domain duplicates** → Route to canonical agent owner
4. **Real repos** → Stay in `Projects/` or code root
5. **This file** → Updated on every consolidation pass

---

*Last consolidated: 2026-06-07. Next sweep: nightly auto-sweep.*
