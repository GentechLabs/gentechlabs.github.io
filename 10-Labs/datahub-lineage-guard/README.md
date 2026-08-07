# Lineage Guard — DataHub Agent Hackathon Submission

**"What breaks if I drop / change / deprecate this data asset?"**

An agent that reads a DataHub context graph, walks the downstream lineage to compute the full blast radius, classifies every affected asset by severity, and writes the risk assessment back to the graph so the next engineer inherits it.

**Category:** Agents That Do Real Work

## The loop (read → reason → act → contribute back)
1. **Read** — connects to a DataHub context graph (self-hosted GMS via GraphQL)
2. **Reason** — walks DOWNSTREAM lineage to compute the full blast radius of any dataset
3. **Classify** — tags every affected asset by type (dataset/chart/dashboard/ML model) and severity (critical/high/medium/low)
4. **Act** — emits a verdict: **BLOCK** (if a critical/high asset is at risk), **REVIEW**, or **SAFE**
5. **Contribute back** — writes the risk assessment to the graph so the knowledge persists

## Why it's "an agent that does real work"
It's not a wrapper or a demo — it's a read → reason → act → contribute-back loop a data engineer would actually use before dropping or deprecating a table. It turns a manual, error-prone "who depends on this?" investigation into a one-command risk report.

## The x402 angle (differentiator)
The agent is optionally monetizable behind an x402 payment gateway (pay-per-query). A data team can call the blast-radius endpoint for $0.001-0.10 USDC per query — no subscription, no signup, HTTP-native. This is the "agent economy" pattern: agents paying agents for intelligence.

## Usage
```bash
# Analyze a specific dataset
python3 lineage_guard.py "urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.orders,PROD)"

# Search for a dataset by name
python3 lineage_guard.py --search "orders"

# Find the highest-blast-radius asset automatically
python3 lineage_guard.py --scan
```

## Files
- `lineage_guard.py` — the full agent (read → reason → act → contribute back)
- `lineage_guard_backend.py` — x402 backend service
- `DATAHUB-RUNNING-CONFIG.md` — how to run against a live DataHub GMS

## Tech stack
- **DataHub** — context graph + lineage (GraphQL API)
- **Python** — agent logic
- **x402** — optional pay-per-query monetization
