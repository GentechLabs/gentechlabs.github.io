# Monad Agent Hub + Poker Arena — Status

**Date:** July 10, 2026
**Status:** Registered, pending claim

---

## Monad Agent Hub

- Monad launched **Agent Hub** at `app.monad.xyz/agents`
- 8 dApp manifests indexed (Uniswap, Morpho, Balancer, etc.)
- Agents settle in MON via x402
- Skills hosted on PortalHQ (`agents.portalhq.io/monad/skills/`)
- **GenTech needs:** Register our APIs as skills on the hub

## Dev.fun Poker Arena

- **$50K total prize pool** — No-Limit Texas Hold'em
- Sponsored by Monad
- Runs Jun 2 → Aug 30
- 4 stages: Playground → Tournament → Ladder → Pro Table Finale (vs Tom Dwan!)
- Playground is **free to enter**, live now

### GenTech Registration

| Field | Value |
|-------|-------|
| Agent ID | `cmrexlc1u2sg12dkyeflbga3a` |
| Handle | `GenTech` |
| API Key | `arena_sk_588f082c26341b1462969b4dd5e78dbbfb615d1a32252fd8dd3095097a470873` |
| Status | **Pending** |

### To Activate (Jordan/Forge Tonight)

1. Go to `arena.dev.fun` → sign in with X/Twitter
2. Claim the agent
3. Run heartbeat: `read https://arena.dev.fun/skills/arena.md and follow the instructions`
4. I'll take it from there — enter Playground, play hands, maintain heartbeat

### Strategy

- **Playground S7** is free — enter immediately after claim
- Gentech's Hermes agent plays poker directly
- Heartsbeat every 4 hours (cron job) to check inbox + leaderboard
- Target: qualify for Tournament (top 25% advance)
