# Agent Builders Cup — Workshop & Strategy Research (Aug 18, 2026)

**Source:** botcamp.xyz/hackathons/agent-builders-cup-1/resources + hummingbot/skills repo
**Status:** Research complete. Skill `hackathon-workshop-hunter` created to systematize this.

## The multi-sponsor strategy (Jordan's "cooler idea")

The winning play is **trading between sponsors**, not picking one. The official example
that does this is the **Solana DEX LP Expert** — it scans trending memecoin pools via
GeckoTerminal, ranks by fees/TVL yield, and runs LP Executor positions across
**Meteora/Orca/Raydium** with per-slot take-profit/stop-loss.

## The concrete implementation: `lp-agent` skill (hummingbot/skills repo)

Full skill at `github.com/hummingbot/skills/tree/main/skills/lp-agent`. This is the
reference for cross-venue LP on Solana CLMMs.

**Workflow:** `start` → `deploy-hummingbot-api` → `setup-gateway` → `add-wallet` →
`explore-pools` → `select-strategy` → `run-strategy` → `analyze-performance`

**Two strategy types:**
1. **Rebalancer Controller** (recommended) — auto-repositions when price moves out of
   range. Set-and-forget.
2. **LP Executor** — single fixed position, you control close/reopen. Good for
   limit-order-style LP.

**Key operational pitfalls (from the skill — critical):**
- **Custom RPC is REQUIRED** — public Solana RPC rate-limits and causes fake
  "Insufficient funds" / "Transaction simulation failed" errors. Use Helius free key.
- **Gateway must run as Docker** (not dev mode) on macOS — containers can't reach host.
- **Use `hummingbot:development` image**, not `latest` (latest may lack LP executor).
- **Token symbol must match pool exactly** (e.g. `Percolator` not `PRCLT`).
- **Check wallet balance BEFORE computing `--amount`** — multiple SPL accounts.
- **`*_pct` params are already percent** — `position_width_pct: 10` = 10%, not 0.10.

## What this means for our ABC Racer / Condor agent

Our existing ABC Racer (cross_venue_arb: GeckoTerminal DEX prices vs Hyperliquid perp
mids, 0.8% fee fence) already does cross-venue detection. The `lp-agent` skill shows the
**LP execution side** — how to actually deploy positions across Meteora/Orca/Raydium.
Combining our arb detection with their LP executor = the full multi-sponsor play.

## Workshops (Agent Builders Cup)
- Market Making Controllers Part 1: youtube.com/watch?v=qxPdDMWZrss
- Market Making Controllers Part 2: youtube.com/watch?v=M8H0GtWASkQ
- Creating AI Trading Agents in Condor: youtube.com/watch?v=_f9Jvqr-wnI
- Bot Pod Ep. 1 (Trading Agents in Condor): youtube.com/watch?v=O93R_ddB-8o
- Bot Pod Ep. 11 (Cup Kickoff): condor.hummingbot.org/podcast/ep11

## Timeline
- Build window: Aug 1-31 (NOW)
- Judging: Sep 1-30
- Finals: Oct 1-2 (livestreamed)
- Winners: Oct 7 (Token2049 Singapore)
