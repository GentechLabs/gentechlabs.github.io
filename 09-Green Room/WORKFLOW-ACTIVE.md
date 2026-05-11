# WORKFLOW: Gentech Solo Operation Protocol
- **Date:** 2026-04-17 (updated May 11, 2026)
- **Status:** LIVE
- **Initiated by:** Jordan

## How This Works

Gentech operates as a **solo agent with topic-based routing**. There is one agent (Gentech) handling all core operations. Work is routed to specialist Telegram groups based on topic, not by separate agents.

### Topic-Based Routing

| Topic | Group | Chat ID |
|-------|-------|---------|
| Finance, DeFi, portfolio, yield, market analysis | Strategies | -1002916759037 |
| Code, SDKs, smart contracts, technical dev | Labs | -1003872552815 |
| Content, social media, hackathon submissions | Entertainment | -1003893562036 |
| Coordination, decisions, blockers, status | HQ | -1003863540828 |

### How Routing Works
1. Live conversation starts in HQ
2. When deep-diving on a topic, continue in the specialist group
3. Cron jobs deliver to their specialist groups
4. Jordan decides where conversations happen

### Auxiliary Agents
DMOB, YoYo, and Desmond are still part of the agency but **not part of the daily operation**. They are deployed for specific projects and specialist tasks when needed. Their Telegram bots remain connected but idle unless activated.

### Before You Reply — ALWAYS:
1. **Check Green Room** (`09-Green Room/drafts/`) — has work already started on this?
2. **Check Mess Hall** (`11-Mess Hall/`) — has this been discussed/resolved already?
3. **Check the topic** — does this belong in a specialist group?

### If It's NOT Your Domain:
- **Explicit mention** (Jordan names you for another domain): Acknowledge → route to correct group → report back
- **Domain shift** (conversation drifts): Offer to route, don't auto-execute
- Write handoff to `09-Green Room/drafts/`

### If It IS Your Domain:
- Check if a handoff exists in Green Room drafts
- Pick it up, do the work in YOUR group, report back

### Speaking To Each Other:
- Before replying to Jordan, check if context exists
- Green Room = coordination drafts
- Mess Hall = daily status
- Don't duplicate what's already been said

**Skill to load:** `proactive-handoff-routing`

Questions? Check the skill or ask in Green Room. Don't ask Jordan unless it's blocking.
