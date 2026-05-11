---
created: 2026-04-19
updated: 2026-05-11
tags: [agent-config, team, operational, governance]
---

# Agent Team Configuration

## Org Chart & Governance
Full org chart with reporting structure, accountability, and escalation paths:
→ `01-GenTech HQ/Org Chart.md`

## Team Roster

### Primary Agent
| Agent | Telegram Bot | Speciality | Telegram Group |
|-------|-------------|------------|----------------|
| Gentech | Original | Orchestration, planning, QA, all operations | HQ (-1003863540828) |

### Auxiliary Agents (Reserve — deployed per-project)
| Agent | Telegram Bot | Speciality | Telegram Group |
|-------|-------------|------------|----------------|
| YoYo | YOYO | Research, analysis, due diligence | Strats (-1002916759037) |
| Dmob | DMOB | Solidity, smart contracts, debugging | Labs (-1003872552815) |
| Desmond | Desmond | Content, writing, social, narratives | Ent (-1003893562036) |

## Agent Groups (Telegram)
- **HQ**: -1003863540828 (Gentech — comms hub, all coordination)
- **Strats**: -1002916759037 (DeFi, portfolio, market analysis)
- **Labs**: -1003872552815 (Code, SDKs, smart contracts, dev)
- **Ent**: -1003893562036 (Content, social, hackathon submissions)
- Topic-based routing: work goes to the group by topic, not by agent assignment
- Auxiliary agents idle in their groups unless activated for a project

## Agent Reach
- **Connected**: 8/16 channels
- **Cookie auth**: Twitter, XHS, Weibo, Reddit
- **Missing**: 小宇宙, 雪球, Douyin, LinkedIn

## Browser Automation
- Harness: `~/repos/browser-harness`
- Service: `chrome-harness.service` on `:9222`
- Adapter: `hermes_browser_adapter.py`

## Voice Assignments (ElevenLabs)
- Gentech: Ivan on Tech
- YoYo: Optimus (reserve)
- Dmob: (default) (reserve)
- Desmond: Steve Harvey (reserve)

## Cron Routing
- Cron → specialist groups per topic (Strategies, Labs, Entertainment)
- HQ → coordination, digests, audits
- Local → vault maintenance, backups

## Provider Strategy (Confirmed May 2026)
- **Primary**: OpenRouter → mimo-v2-pro (daily driver)
- **Fallback**: OpenCode-go → qwen3.6-plus (auto-switch)
- Auto-token-check cron every 6h + Telegram alert when reauth needed

## Team Lead Protocol
1. Gentech monitors all handoffs — see `11-Mess Hall/handoff-board.md`
2. Confirm receiving agent picks up (ACK within 2 hours)
3. Status check after completion
4. Nudge silent agents (4h+ unclaimed)
5. Jordan gets one status line, not a chase
6. Escalation: 12h+ unclaimed → Jordan notified in HQ
7. Board maintenance: scan every 30 min for stale briefs

## Communication Rules
- DM: emergencies only
- Normal → HQ (-1003863540828)
- Cron → specialist groups per topic
- Post-collab: debrief Mess Hall
- HQ = single comms hub
- Specialist groups = focused work only

## Kite Design
- 6-layer agent: Brain, Personality, Strategy, Enforcement, Execution, Memory
- Presets ≠ Locks — every layer editable after cloning
- Leaderboard = discoverability, users fork/remix like GitHub
- Enforcement respects CURRENT user's education tier

## Gentech Entertainment
- YouTube podcast framework: `06-Content/Gentech Entertainment - Content Framework.md`
- Adult-oriented talk show: finances, geopolitics, trending topics
- Jordan personal brand + Gentech
- Uncensored, no-holds-barred
- LLC planned for podcast costs + liability
