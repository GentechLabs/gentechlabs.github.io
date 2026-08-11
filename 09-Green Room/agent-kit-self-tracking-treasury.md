# Agent Kit — Auto-Provisioning "Self-Tracking Treasury" (Product Idea, Aug 11 2026)

**Jordan's idea:** when a user sets up their Agentic Treasury / Agent Kit, the
cron jobs should AUTOMATICALLY pick up whatever LP/position/rail they deploy —
no manual wiring, no "start from the beginning." The kit should make it trivial
to connect deployed positions to the reporting crons. "We're cooking."

## Why this is buildable (we already did the hard part)
The `agentic-treasury.py` fused report was JUST upgraded (Aug 11) to read the
LIVE on-chain V2.2 LP position on the Steward wallet directly — via RPC reads
(`getActiveId`, `balanceOf(addr,binId)` over a ±20 bin window), not a stale feed.
That pattern (read live on-chain → render a report line) is the reusable core.
It's chain-agnostic and wallet-driven: change the WALLET + PAIR constants and it
tracks any position.

## The product: Auto-provisioning self-tracking treasury
Users set up their Agentic Treasury with a wallet + config. The kit's cron
layer then AUTO-DISCOVERS deployed positions and reports them — no manual
wiring of "which pool," "which wallet," "which range."

### Design — config-driven auto-discovery
```
Agent Kit install
  ├─ treasury_config.json      ← user sets: wallet(s), chains, [optional] pools
  ├─ agentic-treasury.py       ← reads config, auto-discovers + reports
  ├─ provision.sh              ← one-command cron setup (registers crons)
  └─ skills/treasury/*         ← self-onboarding skills the agent loads
```

### How auto-discovery works (reuse the Aug 11 pattern)
1. Read the wallet + chain from config.
2. For each configured chain, probe for LP positions:
   - **LFJ V2.2** (Avalanche): `getActiveId` + `balanceOf(addr, binId)` window
     → bins, range, IN/OUT, live price.
   - **Meteora DLMM** (Solana): same shape system → bin balance query via RPC.
   - **Base/Ethereum**: ERC-20 balances (cbBTC, USDC, LINK, PAXG...).
3. Emit a report line per discovered position (the `layer_lp()` we just built).
4. The cron (same `agentic-treasury.sh` wrapper) picks it up automatically.

### Why this is a moat, not just convenience
- **Zero-friction onboarding** — "deploy a position, the kit tracks it."
  No config plumbing, no "where do I tell it about my pool."
- **Proves the trust loop** at small scale — the same thing we just validated
  with Jordan's $45: the kit watches its own deployed capital, reports honestly,
  and rebalances only when gas-justified.
- **Chain-agnostic = more connector/supplier surface** — LFJ, Meteora, Base,
  Ethereum, Monad (same LB pattern extends) all auto-tracked from one config.

### Deliverables (if greenlit)
1. `provision.sh` — one-command cron provisioning (registers the report crons
   against the user's config).
2. `treasury_config.json` template + docs.
3. Generalize `agentic-treasury.py`'s `layer_lp_live()` into a reusable
   `discover_positions(chain, wallet)` in the kit.
4. Skills: `skills/treasury/self-tracking/SKILL.md` (self-onboarding).

## Status
🔵 IDEA — logged, not built. Jordan to greenlight scope/priority.
