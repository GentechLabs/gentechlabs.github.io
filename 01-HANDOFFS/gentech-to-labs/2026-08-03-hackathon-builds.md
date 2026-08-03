# Gentech → Labs Handoff — Hackathon Builds (Aug 3 2026)

Jordan gave the green light to build both hackathon submissions autonomously. Both are tagged `labs` in the build queue and are the top-priority builds this week.

---

## 🎯 BUILD #1 — DataHub Agent Hackathon (item #30)
**Deadline:** Aug 10, 2026 @ 5pm EDT · **Prize:** $20,500
**Register link:** https://datahub.devpost.com · **Rules:** https://datahub.devpost.com/rules
**Build status:** IN PROGRESS (Gentech set up CLI, exploring self-hosted on isolated port)

### The challenge
Build an AI agent that uses DataHub's context graph (via MCP Server / Agent Context Kit / DataHub Skills) to do REAL work — read schemas/lineage/ownership/ML metadata, take action, and WRITE results back to the graph. 4 tracks:
1. Agents That Do Real Work
2. Metadata-Aware Code Generation & Development
3. Production ML Agents
4. Open / Wildcard

### Our chosen angle (Jordan + Gentech agreed)
**"Data Lineage Guard"** — a paid agent answering *"what breaks if I drop/change this table?"* Reads lineage + ownership from DataHub MCP, simulates blast radius, writes a risk report + approval back to the DataHub graph. **Monetized via our x402 gateway** (pay per query). Wins on: Use of DataHub (contributes back), Originality, Real-World Usefulness, and the x402 angle is a differentiator.

### Key facts to respect
- **Judging criteria:** Use of DataHub (30%), Technical Execution, Originality, Real-World Usefulness, Submission Quality. Bonus: meaningful OSS contribution to DataHub.
- **What to submit:** public repo (Apache 2.0 license), <3min demo video on YouTube/Vimeo, text description, live-demo URL. Optional: sample outputs in examples/.
- **Sample datasets provided** (load into local DataHub): `datahub datapack load showcase-ecommerce` (1,049 entities), plus nyc-taxi, healthcare, fiction-retail (planted data-quality scenarios).
- **Resources:** https://datahub.devpost.com/resources · Docs: docs.datahub.com · MCP server: github.com/acryldata/mcp-server-datahub · Agent Context Kit: pip install datahub-agent-context

### Infrastructure decision (IMPORTANT)
- DataHub quickstart needs **14 containers**, GMS on **port 8080** — which is TAKEN by our live x402 gateway.
- **DO NOT touch port 8080.** If self-hosting, remap GMS to **28080** via a custom quickstart compose file.
- Gentech was weighing: Option A (managed MCP, read-only, 401-gated) vs isolated self-host on 28080. **Self-host on 28080 is the right call** — it's what the hackathon designed for (load datapacks, write back to graph).
- Disk at 86% — check space before pulling images. See infra-audit notes below.

---

## 🎯 BUILD #2 — KeeperHub Agents Onchain (item #1)
**Deadline:** Aug 13, 2026 · **Prize:** $5,000 + $1,000 bounties
**Register link:** https://dorahacks.io/hackathon/agents-onchain/detail

### The challenge (HARD REQUIREMENT)
Your agent MUST execute a real onchain transaction through **KeeperHub** (the execution/reliability layer). Not a mockup — every submission links a transaction the agent executed. KeeperHub = MCP server, x402/MPP payments, smart gas estimation, MEV protection, audit trail.

### Our chosen angle (Jordan + Gentech agreed)
**"Autonomous Yield Rebalancer"** — an agent that monitors a yield position and executes rebalance through KeeperHub (real tx) when APY/spread crosses threshold. Uses KeeperHub's x402/MPP for pay-per-execution, gas estimation for reliability, audit trail for observability.
PLUS **"Best Onboarding UX" bounty** (stackable $1K split): a starter template getting someone from zero to their first executed transaction fast.

### Key facts
- **Judging:** execution (does it run onchain via KeeperHub), use of KeeperHub surfaces, reliability/observability, originality, DX.
- **Must submit:** GitHub link, short demo video, and a **link to a transaction the agent executed via KeeperHub**.
- **Stack:** KeeperHub docs: docs.keeperhub.com · MCP server: docs.keeperhub.com/ai-tools/mcp-server · Discord: discord.gg/keeperhub
- We're the x402 people — the x402-through-KeeperHub angle is our edge.

---

## 📋 How to continue (when Jordan says "run build list" in Labs)
1. Read the queue at /root/vaults/gentech/scripts/build_queue.json
2. Filter to items tagged `group: labs` (DataHub #30, Keeperhub #1 are top priority)
3. Read this handoff for context, then build with the develop-and-verify workflow
4. On completion, write handoff note to 01-HANDOFFS/gentech-to-labs/ so the morning digest routes it

## 🛠 Infra audit context (from Aug 3)
Jordan asked to audit ports/storage for space before the DataHub 14-container stack. Findings:
- **buzz-relay is crash-looping** (6905 restarts, Redis connection refused) — dead weight, candidate to stop
- **hermes-brain-backup = 9.6GB** (vault backup), pixelrag-env = 5.6GB — largest disk consumers
- docker reclaimable: ~4.9GB images, ~586MB volumes
- Check these before pulling DataHub images
