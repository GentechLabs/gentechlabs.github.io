---
type: reference-index
created: 2026-04-19
maintained-by: all-agents
---

# 🗂️ Gentech Vault Reference Index

**The master lookup table.** Maps every topic/project/tool to its vault file path.

## How It Works

1. **Memory stores**: `Vault Index: Skills/vault-reference-index.md`
2. **When a topic comes up**: Load the index → find the file path → `read_file` the full doc
3. **Result**: Memory stays lean, full context loads on demand

---

## Projects & Contracts

| Topic | Path | Description |
|-------|------|-------------|
| AAE Architecture | `Labs/AAE-Six-Layer-Architecture.md` | 6-layer design, education pipeline |
| AAE Agent Configs | `Projects/AAE/agent-configs.md` | Team setup, routing, protocols |
| AAE Tooling | `Projects/AAE/tooling-reference.md` | APIs, logins, VPS specs |
| AAE Content Strategy | `Projects/AAE/content-strategy.md` | Build public, revenue model |
| GEN Token | `Projects/GEN/` | 1B fixed supply, deflationary |
| GEN Contracts | `~/repos/AAE/` | Smart contract codebase |

## Hackathons & Funding

| Topic | Path | Description |
|-------|------|-------------|
| ETHGlobal Open Agents | `Labs/ETHGlobal-Open-Agents-Plan.md` | $50K prize, deadline May 3 |
| Arc Hackathon | `Labs/Arc/` | x402 payments, escrow, ERC-8004 |
| Kite AI Hackathon | `Labs/Kite/` | Due April 26 |
| Funding Tracker | `Labs/Funding-Tracker.md` | Active grants, bounties, deadlines |

## Infrastructure & Tools

| Topic | Path | Description |
|-------|------|-------------|
| Browser Harness | `Labs/Browser-Harness.md` | Chrome CDP, headless, global binary |
| Hermes Ecosystem Atlas | `References/hermes-ecosystem-atlas.md` | Full tool landscape |
| Cron Registry | `Skills/cron-registry.md` | All jobs, schedules, owners |
| Cron Routing | `Skills/cron-routing.md` | Department delivery rules |
| Channel Boundaries | `Skills/channel-boundaries.md` | Agent group assignments, admin model |
| Agent Protocol | `Skills/agents-protocol.md` | How agents operate |

## Communication & Coordination

| Topic | Path | Description |
|-------|------|-------------|
| Brain Usage Protocol | `Skills/brain-usage-protocol.md` | Memory rules, what goes in/out |
| Queue Discipline | `Skills/queue-discipline-protocol.md` | Task ordering, priority |
| Coordination Rules | `Skills/coordination-rules.md` | Cross-agent handoffs |
| Agent States | `08-Daily/agent-states/` | Per-session state files |

## Content & Media

| Topic | Path | Description |
|-------|------|-------------|
| X Content Series | `Labs/X-Content-Educational-Series.md` | Educational post templates |
| Content Drafts | `08-Daily/content-drafts/` | AAE origin story, flagship thread |

## Learning & Personal

| Topic | Path | Description |
|-------|------|-------------|
| Weekly Schedule | `08-Daily/2026-Weekly/Schedule — W16.md` | Work shifts, learning blocks |
| Cyfrin Progress | `08-Daily/skill-updates-*.md` | Latest learning updates |

---

## Group IDs (always keep in memory)

| Group | ID | Admin |
|-------|-----|-------|
| HQ | `-1003863540828` | Gentech |
| Strategies | `-1002916759037` | YoYo |
| Labs | `-1003872552815` | Dmob |
| Entertainment | `-1003893562036` | Desmond |

## Dispatch Rule

Jordan speaks to agent in HQ → Agent takes execution to their home group:
- Dmob → Labs
- YoYo → Strategies  
- Desmond → Entertainment
- Gentech → HQ (coordinates)
