# Handoff — Telegraph Hackathon H1 (Season I) — Miner Build
*Prepared 2026-08-12 · H1 window **Aug 17 – Sep 7** (21 days) · $5K H1 / $10K H2 / H3 mainnet · $15K total pool*

## What it is
Telegraph = verifiable-intelligence protocol. Miners wrap any API/model/dataset/tool into a declarative YAML, register on-chain, and serve verifiable answers to the network. Applications consume live miners; scripts rank quality.

**Prize:** H1 $5K, H2 $10K, H3 (mainnet) TBD — $15K+ total.

## Key facts (verified from docs)
- **Miner = a YAML file, not code.** Declarative spec wraps our existing API + auth + param mapping + intents. Validated at `integrate.telegraphprotocol.com`, then registered on-chain.
- **Registration open now; Track 1 & 2 open Aug 17 12:00 UTC.** Early registrants get task specs + core-team Discord.
- **Payments are x402** — Base Sepolia USDC or Solana Devnet. This is EXACTLY our lane (we run x402).
- Testnet dispatcher: `http://13.237.89.59:7044/miner-dispatcher`

## ⚠️ Critical finding — intent mismatch
The **miner registration schema's canonical intents** do NOT include CRYPTO_PRICE / WALLET_BALANCE / TVL (those are application-layer intents). The 27 registerable canonical intents include:
`WEB_SEARCH, NEWS_SEARCH, RESEARCH_SYNTHESIS, FACT_CHECK, CONTENT_VERIFICATION, TWITTER_SEARCH, CHAT_COMPLETION, TASK_COMPLETION, AGENT_TASK, ...`

**Consequence:** We cannot yet register our DeFi/crypto services as miners under the current canonical intent set. The clean path is a **search/research miner**.

## What to build NOW (shippable overnight)
**A WEB_SEARCH / NEWS_SEARCH / RESEARCH_SYNTHESIS miner wrapping Tavily** (which we wired Aug 12).
- We have a working Tavily key at `/root/.blockrun/tavily-api-key`
- Tavily = the search engine; map its JSON output to the miner schema
- This is a real, registerable miner that fills a canonical intent and earns on x402

**Draft YAML at `telegraph/example-miner.yaml`** in this repo.

## The strategic play (for H1, beyond the search miner)
1. **Search/research miner (tonight)** — wrap Tavily → WEB_SEARCH + NEWS_SEARCH + RESEARCH_SYNTHESIS. Register it. This is the overnight build.
2. **Evaluation script (Track 2)** — write a script that ranks miners. Low-effort, high-leverage, feeds our "agent-sentiment index" thesis.
3. **Crypto intents later** — once the schema opens CRYPTO_PRICE/TVL/WALLET, port our Nevermined services in (they're already x402-ready).
4. **Contribute to the Telegraph GitHub (parallel, low-risk)** — telegraphprotocol org has:
   - `Telegraph` (protocol node source) — read to learn how miners are routed/scored/ranked
   - `Telegraph-MCP` (MCP server for AI agents) — natural fit: we run MCP extensively
   - `telegraph-docs` + `telegraph-examples` — docs fixes / example miners
   Contributing = open-source credibility for judging + fastest way to learn the protocol. Start with docs/examples PRs (safe), then MCP-server improvements once we understand it. Follow pr-submission-rules.

## For Labs — what to prep (overnight queue)
- [ ] Register on integrate.telegraphprotocol.com (or prep creds)
- [ ] Write miner YAML wrapping Tavily (WEB_SEARCH intent) — template below
- [ ] Validate at integrate.telegraphprotocol.com (sandbox-tests against live Tavily API)
- [ ] Register the miner (on-chain, Base Sepolia)
- [ ] Test an x402-paid inference call against it
- [ ] Public repo + LICENSE

## Judging criteria (screen for these)
- Telegraph ranking & performance
- Number of applications built on the miner
- Total requests served
- X progress posts + engagement

## Notes / blockers
- Miner registration is **on-chain and immutable** — validate YAML at integrate.telegraphprotocol.com FIRST (the #1 failure mode is schema/auth mistakes caught post-registration)
- Never put the raw API key in YAML — only the `env_var` name
- Deadline: Track 1&2 open Aug 17, H1 closes Sep 7. No urgency conflict with KeeperHub (Aug 13).

**Status:** Jordan registered early. Build brief ready for overnight queue.
