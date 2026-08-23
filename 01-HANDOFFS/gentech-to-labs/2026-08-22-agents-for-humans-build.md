# 🤝 Handoff to Gizmo (Labs) — Agents for Humans Hackathon Build Research

**From:** Gentech (HQ) · **Date:** 2026-08-22
**Status:** OPEN — research + scope the build, report back

## Task
Research and scope the **Agents for Humans Hackathon (Amazon)** build so we can start building. Jordan registered Aug 22. Deadline **Sep 14, 2026 5:00 PM PDT** (23 days). $40K across 3 tracks.

## The Hackathon
- **Host:** Amazon (AWS) on Devpost · **Prize:** $40,000 cash
- **Theme:** Build an AI agent with the **Strands Agents SDK** that handles routine/repetitive tasks in the background — runs autonomously, only surfaces when there's a real decision.
- **3 tracks:**
  1. **Everyday Agents** — busywork out of daily life (home, money, health, errands, family)
  2. **Professional Agents** — makes someone dramatically better at their work (professionals, makers, small-business owners)
  3. **Good Neighbor Agents** — helps groups (neighborhoods, nonprofits, food banks, schools)
- **Prizes:** Grand $10K + per-track Golden $5K / Silver $3K / Bronze $2K
- **4,572 participants** already registered
- **$50 AWS credits** available (Resources tab request form)

## Recommended Direction (Gentech's pick)
**Track: Professional Agents** — build a **"Treasury Agent"** that handles repetitive DeFi/crypto portfolio tasks (yield monitoring, LP position checks, rebalancing signals) in the background, pinging the owner only when there's a real decision.

**Why this fits us:**
- Our exact stack (GTA, DeFi agents, x402 payments)
- Genuinely useful to a real audience (small-business owners, solo investors)
- **Differentiated:** x402 integration is a non-obvious, creative use of Strands most entrants won't have
- Scores high on Technical Implementation (live demo + AgentCore deployment + x402)

## Strands Agents SDK — Key Facts (verified)
- **Open source, Apache 2.0**, model-driven agent SDK by AWS. Used in production by Amazon Q, AWS Glue, VPC Reachability Analyzer.
- **Install:** `pip install strands-agents strands-agents-tools` (Python 3.10+)
- **Default model:** Amazon Bedrock, Claude Sonnet 4. Needs AWS credentials + Bedrock model access.
- **Other providers:** Anthropic, LiteLLM, Llama API, Mistral, **Ollama**, OpenAI, Writer, Cohere, CLOVA, FireworksAI, custom.
- **Supports MCP and A2A directly; x402 via complementary integrations** — this is our rail.
- **Multi-agent:** Graph or Swarm patterns.
- **Observability:** OpenTelemetry traces/metrics, AgentResult.
- **Deploy:** AgentCore (Bedrock) strengthens Technical Implementation score.
- **MCP server** available for dev (uvx strands-agents-mcp-server).

## Submission Requirements
- Text description (what/for whom/how)
- **Public repo** (MIT/Apache license, README, setup instructions)
- **Architecture diagram**
- **Demo video ≤5 min** (problem → who → why; no need to appear on camera)
- **AWS Builder ID**
- Optional live demo link (scores higher on Technical Implementation)
- **Bonus:** builder.aws.com post with "Agents for Humans" in title

## Judging Criteria
1. **Technological Implementation** — Strands depth, working non-trivial code, live demo + AgentCore deployment strengthen
2. **Design** — complete coherent product, not just POC
3. **Potential Impact** — credible case for real problem/audience
4. **Creativity & Originality** — non-obvious use of Strands
5. **Presentation** — video demonstrates end-to-end, clear pitch

## What I Need From You (Gizmo)
1. **Research the Strands Agents SDK** — read the docs, understand the agent loop, tools, multi-agent, x402 integration path
2. **Scope the Treasury Agent build** — architecture, tools needed, x402 integration approach, what's reusable from our existing GTA/DeFi stack
3. **Propose the concrete build plan** — repo structure, milestones, what to build first
4. **Report back** with the scoped plan for Jordan's approval

## Constraints
- **Solana-only** for any onchain work (no Hyperliquid — we don't have access)
- x402 is our rail — integrate it as the differentiator
- Reuse existing GenTech stack where possible (GTA, DeFi agents, x402 gateway)
- Deadline Sep 14 — 23 days, so scope for a tight, shippable build
- Report back via completion note in `01-HANDOFFS/gentech-completions.md` (or your lane's completion file)

## Reference
- Hackathon page: https://agentsforhumans.devpost.com
- Strands docs: https://strandsagents.com/docs/user-guide/quickstart/python
- Strands GitHub: https://github.com/strands-agents/harness-sdk
- Build queue: #64 (pending, assigned gentech)
