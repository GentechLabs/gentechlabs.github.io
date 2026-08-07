# DataHub Agent Hackathon — Devpost Submission Draft

**Project:** Lineage Guard — "What breaks if I drop this data asset?"
**Category:** Agents That Do Real Work
**Repo:** https://github.com/ProtoJay4789/lineage-guard
**Deadline:** Aug 10, 2026

---

## Elevator pitch (one line)
An agent that answers "what breaks if I drop / change / deprecate this data asset?" — it walks the DataHub lineage graph, computes the full blast radius, classifies every affected asset by severity, and writes the risk assessment back to the graph so the next engineer inherits it.

## What it does (the loop)
1. **Read** — connects to a DataHub context graph (self-hosted GMS via GraphQL)
2. **Reason** — walks DOWNSTREAM lineage to compute the full blast radius of any dataset
3. **Classify** — tags every affected asset by type (dataset/chart/dashboard/ML model) and severity (critical/high/medium/low)
4. **Act** — emits a verdict: **BLOCK** (if a critical/high asset is at risk), **REVIEW**, or **SAFE**
5. **Contribute back** — writes the risk assessment to the graph so the knowledge persists

## Why it's "an agent that does real work"
It's not a wrapper or a demo — it's a read → reason → act → contribute-back loop that a data engineer would actually use before dropping or deprecating a table. It turns a manual, error-prone "who depends on this?" investigation into a one-command risk report.

## The x402 angle (differentiator)
The agent is optionally monetizable behind an x402 payment gateway (pay-per-query). A data team can call the blast-radius endpoint for $0.001-0.10 USDC per query — no subscription, no signup, HTTP-native. This is the "agent economy" pattern: agents paying agents for intelligence.

## How to run
```bash
# Analyze a specific dataset
python3 lineage_guard.py "urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.orders,PROD)"

# Search for a dataset by name
python3 lineage_guard.py --search "orders"

# Find the highest-blast-radius asset automatically
python3 lineage_guard.py --scan
```

## Tech stack
- **DataHub** — context graph + lineage (GraphQL API)
- **Python** — agent logic
- **x402** — optional pay-per-query monetization

## What's in the repo
- `lineage_guard.py` — the full agent (255 lines, self-contained)
- Blast-radius walker, severity classifier, verdict engine, write-back
- x402 endpoint integration

## Category fit
**Agents That Do Real Work** — this is exactly that: an agent that reads a real data catalog, reasons about impact, and produces a decision a human acts on. It's the kind of "boring but valuable" automation that saves data teams hours and prevents costly breakage.
