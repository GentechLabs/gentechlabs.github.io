# Agent Configs — All Agent Setups, Tool Assignments, Group Routing

*Last updated: April 19, 2026*

---

## Agent Team

| Agent | Role | Home Group | Admin | Voice |
|-------|------|------------|-------|-------|
| **YoYo** | Research, market analysis, DeFi | Strategies | YoYo | RyanNeural-GB (-5%) |
| **Dmob** | Smart contracts, Solidity, dev | Labs | Dmob | AndrewNeural (-10%) |
| **Desmond** | Content, social media, branding | Entertainment | Desmond | GuyNeural (+2%) |
| **Jordan** | Founder, architect | HQ | Jordan | AndrewNeural (-12%) |

## Group Structure

| Group | Purpose | Lead | Rule |
|-------|---------|------|------|
| **HQ** | Dispatch, decisions, brainstorm | Jordan | Everyone responds fully |
| **Strategies** | Research, market analysis | YoYo | YoYo speaks last (anchor) |
| **Labs** | Smart contracts, dev | Dmob | Dmob leads, others hang back |
| **Entertainment** | Content, branding | Desmond | Desmond leads, others hang back |

## Channel Discipline

- **Full rules:** `/opt/hermes-agents/shared/channel-boundaries.md`
- HQ-first routing: messages → HQ → relay → respond
- Green Room/Mess Hall for cross-agent coordination
- Admin speaks LAST in their group — final take anchors Jordan's view

## Response Protocol

1. Read Green Room before responding
2. Check if another agent covered the topic
3. Write perspective in Green Room (2-3 lines)
4. Respond with distinct angle
5. Handoff if needed (post to Mess Hall handoff-board)

## Queue Discipline

- Finish current task completely
- Second Brain activity (Green Room + Mess Hall)
- Then check queue for next message
- Only interrupt for explicit "stop" / "drop that" / "switch to X"

## Context Save Protocol

When context hits ~75-80%:
1. Save state to `vault/08-Daily/agent-states/{agent}-{date}-state.md`
2. Write 1-line summary to Mess Hall: `vault/11-Mess Hall/Chat — {date}.md`
3. Reset — pick up from saved state in new session

## Tool Assignments

- **Web research:** YoYo (primary), all agents can search
- **Code/terminal:** Dmob (primary), YoYo routes to Dmob
- **Content/social:** Desmond (primary)
- **Browser automation:** All agents (Nous subscription)
- **Image generation:** All agents (Nous subscription)
- **TTS:** Edge TTS primary, Voicebox backup

## Cron Jobs

- **Strategies:** 6 jobs (Portfolio/LP 3x/day, LP Range 10min + pause/resume)
- **HQ:** 1 job (Skills Update Sun 10:00)
- **Local:** 1 job (Vault Maint 22:00)
- Total: 8 jobs, all healthy

## Memory System

- **Memory tool:** 2,200 chars, injected every turn — pointers only
- **Vault (Obsidian):** Unlimited storage, searchable via `search_files`
- **Agent states:** `/08-Daily/agent-states/` — session context saves
- **Session search:** Recall past conversations by keywords
- **Pattern:** Memory = Index, Vault = Library
