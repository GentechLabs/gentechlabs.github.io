## Dmob State — 2026-04-19

- **Coordinated Auth Reset**: Cron `c4cce60ce247` set up — runs `refresh-all-auth.py` at `0 * * * *` (top of every hour)
- Script clears Nous tokens from all 4 agents (dmob, yoyo, desmond, gentech) simultaneously
- Forces all agents to re-auth together → synchronized token expiry
- Tested: script works, all 4 auth.json files cleared successfully
- Next run: 23:00 UTC tonight
