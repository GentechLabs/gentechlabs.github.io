---
date: 2026-06-07
purpose: Master vault navigation hub — links to every section and key file
updated: 2026-06-07
---

# 🧠 GenTech Vault — Master Index

> **Welcome.** This is the single source of truth for navigating the GenTech vault. Every section, every key file, every workflow — linked here.
>
> **Cross-reference:** [[00-HQ/INDEX]] | [[02-Labs/INDEX]] | [[03-Projects/INDEX]] | [[03-Strategies/INDEX]] | [[04-Entertainment/INDEX]] | [[06-Content/INDEX]] | [[09-Green Room/INDEX]]

---

## 🗺️ Vault Map

| Zone | Purpose | Owner | Index |
|------|---------|-------|-------|
| **[[00-HQ/INDEX]]** | Operations — approvals, travel, grants, status board | Jordan | [[00-HQ/STATUS-BOARD]] |
| **[[00-System]]** | Agent configs, channel maps, cron jobs, secrets | Gentech | — |
| **01-Agents** | Bot configs, voice profiles | Gentech | — |
| **02-Agent-Arena** | Agent Arena formal spec | DMOB | [[02-Agent-Arena/AAE-FORMAL-SPEC]] |
| **[[02-Labs/INDEX]]** | Smart contracts, hackathons, bounties, research | DMOB | [[02-Labs/_INDEX]] |
| **[[03-Projects/INDEX]]** | Active builds with repos (Foundry, Anchor) | DMOB/YoYo | — |
| **[[03-Strategies/INDEX]]** | DeFi research, market analysis, LP tracking | YoYo | [[03-Strategies/_INDEX]] |
| **[[04-Entertainment/INDEX]]** | Content strategy, branding, episode drafts | Desmond | [[04-Entertainment/_INDEX]] |
| **05-Learning** | Course notes, academy material | Jordan | [[05-Learning/README]] |
| **06-Audits** | Code audits (Kite AI, C4) | DMOB | — |
| **[[06-Content/INDEX]]** | X drafts, blog posts, podcast concepts, social | Desmond | [[06-Content/Shared-References/INDEX]] |
| **08-Daily-Digest** | Daily digest summaries | Auto | — |
| **[[09-Green Room/INDEX]]** | Active workspace — build logs, ideas, designs, travel | All | [[09-Green Room/WORKFLOW-ACTIVE]] |
| **10-Archive** | Stale folders, swept history, merge artifacts | Auto | — |
| **11-Mess Hall** | Decisions, sweep reports, banter | All | — |
| **12-Skills** | Agent skill exports, skill wikis | Auto | — |
| **15-Gaming** | POE2 builds, Vanito companion | Jordan | — |
| **Daily/** | Daily notes (date-stamped) | Jordan | — |
| **pals/** | GenTech Pals data (gaming companion) | Gentech | — |
| **scripts/** | Utility scripts (hackathon scanner, etc.) | Auto | — |
| **data/** | Structured data (projects.json) | Auto | — |

---

## 🔑 Quick Links

### Active Work (Jun 7, 2026)
- [[00-HQ/STATUS-BOARD]] — **Source of truth for what's live**
- [[00-Working-Memory]] — Current sprint state
- [[09-Green Room/WORKFLOW-ACTIVE]] — Routing & workflow rules

### Hackathons & Grants
- [[00-HQ/hackathon-tracker]] — All hackathon statuses
- [[03-Strategies/Grant-Applications-Queue]] — Grant pipeline
- [[02-Labs/Hackathons/HACKATHON-ROSTER-2026]] — Full 2026 roster
- [[00-HQ/grants/pipeline]] — Active grant applications

### Infrastructure
- [[00-HQ/smart-routing-rules]] — Agent routing protocol
- [[12-Skills/agents-protocol]] — Agent communication rules
- [[12-Skills/channel-boundaries]] — Channel scope rules
- [[00-HQ/vault-health]] — Vault health metrics

### DeFi & Strategy
- [[03-Strategies/aae-core-philosophy]] — AAE core vision
- [[03-Strategies/agentic-finance-landscape]] — Market landscape
- [[03-Strategies/GenTech-Full-Strategy-Overview]] — Full strategy
- [[03-Strategies/Defi-Monitor]] — DeFi position monitoring

### Content & Brand
- [[04-Entertainment/Content-Strategy]] — Content framework
- [[04-Entertainment/content-pipeline]] — Publishing pipeline
- [[06-Content/Gentech-Brand-Narrative]] — Brand narrative
- [[00-HQ/Marketing]] — Marketing materials

### Travel
- [[00-HQ/01-Travel/trip-plan-2026-updated]] — Philippines trip plan
- [[09-Green Room/philippines-trip-research]] — Trip research
- [[09-Green Room/flight-price-log]] — Flight price tracking

### Learning
- [[05-Learning/GenTech-Academy/README]] — Academy modules
- [[05-Learning/Solana-for-EVM-Devs-CheatSheet]] — Solana cheat sheet
- [[05-Learning/x402-Research]] — x402 protocol research

---

## 🏷️ Tag Reference

- `#agent:yoyo` `#agent:dmob` `#agent:desmond` `#agent:gentech`
- `#status:active` `#status:todo` `#status:done`
- `#type:research` `#type:code` `#type:content`

---

## 🤖 Agent Routing

| Agent | Domain | Writes To |
|-------|--------|-----------|
| **Gentech** | Coordinator — routes everything | `00-HQ/`, `Daily/` |
| **YoYo** | DeFi, market research, LP tracking | `03-Strategies/` |
| **DMOB** | Smart contracts, security, hackathons | `02-Labs/` |
| **Desmond** | Content, branding, social media | `04-Entertainment/`, `06-Content/` |

**Routing rules:** [[12-Skills/agents-protocol]] | [[00-HQ/smart-routing-rules]]

---

## 📋 Maintenance Rules

1. **Single-file folders** → Move file to parent MOC; delete empty shell
2. **Merge artifacts** (`_*`) → Archive to `10-Archive/` with provenance
3. **Cross-domain duplicates** → Route to canonical agent owner
4. **Real repos** → Stay in `03-Projects/` or code root
5. **This file** → Updated on every consolidation pass

---

*Last consolidated: 2026-06-07. Next sweep: nightly auto-sweep.*
