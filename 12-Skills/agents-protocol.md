---
type: protocol
status: ACTIVE
enforced-by: all-agents
updated: 2026-04-20
---

# 🤖 Agents Protocol — Smart Routing v2

## The Golden Rule
**Gentech receives. Gentech routes. Agents execute in their groups.**

## Message Flow
```
Jordan → HQ (Gentech) → Analyze → Route to specialist group → Agent works → Summary back to HQ
```

## Who Works Where

| Agent | Group | Group ID | Domain |
|-------|-------|----------|--------|
| Gentech | GenTech HQ | -1003863540828 | Coordinator — receives all, routes to specialists |
| YoYo | GenTech Strategies | -1002916759037 | DeFi, investing, market research, financial analysis |
| DMOB | GenTech Labs | -1003872552815 | Smart contracts, security, code, hackathons, bug bounties |
| Desmond | GenTech Creative | -1003893562036 | Content, docs, branding, social media |

## Routing Rules

1. **Agents do NOT respond in HQ** unless Gentech explicitly asks them to
2. **Agents do NOT ask Jordan questions in HQ** — route to your group first, work there
3. **When Jordan shares something in HQ**, Gentech analyzes and says:
   - "DMOB, check this out in Labs" → link/context posted in Labs group
   - "YoYo, something for Strategies" → relevant info posted in Strategies group
4. **Agents report back to HQ** with a summary when work is done or when blocking
5. **Observers can watch** — all specialist groups have observers who can follow along

## Collaboration
- Need another agent? Post in the Green Room (`09-Green Room/`) and tag them
- Cross-domain work gets coordinated in HQ by Gentech
- Don't do another agent's job — if it's not your domain, route it

## Vault Sync
- **Use `ob sync`** — we're logged into Obsidian Headless already
- Command: `cd /root/vaults/gentech && ob sync`
- Sync after major changes to push to Windows
- Sync at start of shift to pull latest from Windows

## Stopping Points
When switching tasks or ending a shift:
1. Write status to Mess Hall (`11-Mess Hall/`)
2. Leave a Green Room handoff if another agent needs to continue
3. Clean slate for next task
