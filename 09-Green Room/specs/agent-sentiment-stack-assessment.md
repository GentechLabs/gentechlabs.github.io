# Agent Sentiment — Reading Our Own Stack (grounded assessment)

**Date:** 2026-08-03
**Context:** Jordan asked how we'd *actually* read agent sentiment given what we've already built. This is a stack audit → gap analysis → realistic first build. Not vision — what we can do with the code we already run.

---

## What we already have (the building blocks)

### 1. Agent identity / attribution — ✅ EXISTS
`8004scan-monitor.py` (the a2a-discovery module) already:
- Polls the **ERC-8004 agent registry** (`8004scan.io/api/v1/agents`)
- Tracks **696,404 registered agents** across chains
- Filters for `x402_supported`, named agents, Base chain
- Has a persistent state file (`8004scan-state.json`) — last_seen_id, totals, runs

**This is the agent-identity layer.** We can identify agents today. Attribution is possible.

### 2. Trade execution data — 🟡 PARTIAL (no agent attribution yet)
- `gta_executor.py` — turns arb scan state into trade decisions, writes `gta_position.json`
- `gta-arb-monitor.py` — scans Hyperliquid/Coinbase basis, dumps state JSON
- `gta_coinbase_leg.py`, `tradesta-signal.py` — signal + execution

**Gap:** trades are logged per-position, but there's **no `agent_id` field** on any of them. The ledger is anonymous — it doesn't say "this trade was executed by agent X."

### 3. Human sentiment feeds — ✅ EXISTS
- `narrative-rotation.py` — reads CMC fear/greed, narrative signals
- `tradesta-signal.py` — CMC-driven direction/leverage signal
- `fed-event-tracker.py`, `defi-crash-mode.py` — macro/risk overlays

**These measure HUMAN sentiment** (fear/greed, funding, macro). The human-sentiment side is covered.

### 4. The a2a module infra — ✅ EXISTS (underused)
`10-Labs/agent-kit-q402/` has: `audit_trail.py`, `enforcement.py`, `gateway.py`, `revenue_module.py`, `payment_module.py`. The audit-trail + gateway plumbing for agent-to-agent is built.

---

## The gap (it's ONE thing, not a rearchitecture)

We have three of four pieces:
- ✅ **Agent identity** (8004scan / ERC-8004)
- ✅ **Human sentiment** (narrative-rotation / CMC)
- ✅ **Trade execution** (GTA arb/executor)

❌ **The connective tissue: trades aren't attributed to agents, and no aggregation turns agent-trade-flow into a sentiment number.**

That's the whole build. Everything else already runs.

---

## Realistic first build (uses what we have)

**Step 1 — Add `agent_id` to the trade ledger (cheap, high-leverage).**
The GTA executor + arb monitor already write state JSON. Add an `agent_id` (or `source_agent`) field to each position/decision record. This is the **Layer 3 seed** — data-first, cheap now, expensive to retrofit later.

**Step 2 — Agent-flow aggregator (the sentiment index).**
A script that reads all attributed trade records and produces per-agent + aggregate:
- `net_positioning` (long vs short count/size)
- `confidence` (avg conviction, win-rate drift)
- `activity` (trade count, cadence)

**Step 3 — Agent-vs-human divergence.**
Cross the agent-flow index against existing human sentiment (`narrative-rotation.py` output). The spread becomes the signal.

**Step 4 — Expose it.**
Reuse the MCP server pattern (GTA arb is already packaged as MCP). Expose `agent_sentiment` as an MCP tool → any agent can read it, or it feeds GTA's own reasoning.

---

## Where the data comes from (honest answer)

- **Our own attributed trades** (GTA + any connected agent) — the core, we control it
- **8004scan ERC-8004 registry** — agent identity + count, but not their trade flow
- **Venue-level flow** (Polymarket/World order flow, funding) — proxy for aggregate agent activity
- **Xona-style arena** — if The Agency of Traders runs, its aggregate agent behavior IS the dataset

The richest source is **our own arena/platform** (The Agency of Traders) — it *generates* attributable agent-flow as a byproduct. That's the moat: we'd be the venue AND the indicator.

---

## Verdict

**We're genuinely on to something, and it's buildable on our existing stack.** The three core layers already exist (identity, execution, human sentiment). The missing piece is small and starts as a **data-collection discipline** (attribute trades), not a big build.

**Recommended sequence:**
1. Add `agent_id` attribution to GTA trade records — **start today, it's cheap** (build-order #6)
2. Build the agent-flow aggregator once we have a few weeks of attributed data
3. Cross against narrative-rotation → agent-vs-human divergence signal
4. Expose as MCP tool + feed GTA's own reasoning

**The moat:** nobody owns "agent sentiment" as a first-class indicator. If we collect attributable agent-flow from day one and let it compound, we're the first with real data behind it — not a theoretical index, but one built on actual agent behavior we recorded.

## Status
🔭 **Thesis confirmed + stack-validated (Aug 3).** First concrete move = agent attribution on the trade ledger. Not a rearchitecture — a data discipline that unlocks the whole Layer 3.

## Layer 3 seed — DONE (Aug 3, greenlit by Jordan)

`gta_executor.py` now appends every decision (ENTER/CLOSE/HOLD/REPORT/SKIP) to `agent-flow.jsonl` — an append-only, attributable ledger:

```json
{"agent_id": "gentech-gta", "ts": "...", "action": "REPORT",
 "symbol": "PAXG", "reasons": ["below_execute"], "mode": "DRY_RUN",
 "executed": false, "order_plan": null}
```

- **Attribution:** `agent_id` field (default `gentech-gta`, overridable via `GTA_AGENT_ID` so connected agents — Forge, ClawWork workers, arena competitors — log under their own id)
- **Append-only, never mutated** — safe for the aggregator to read
- **Logs HOLD/SKIP too** — flow includes "stayed out," not just trades
- **Never fails the trade on a logging error** — writes loudly to stderr and continues
- Verified: executor runs, appends attributed record, 9/9 existing tests still pass

**Why this is the right seed:** the GTA executor is the single decision point that reads arb-monitor state and produces actions. By attributing every decision there, we collect agent-flow from day one. When we build the aggregator + agent-vs-human divergence (steps 2-3 in the path), the data is already accumulating.

**Next (when ready):** agent-flow aggregator reading `agent-flow.jsonl` → per-agent net positioning / confidence / activity → cross against `narrative-rotation.py` → expose as MCP tool.
