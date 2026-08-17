# 👑 Jordan Action Items — 2026-08-14

## 🔴 URGENT — Deadlines

- **#83 CockroachDB × AWS — Agentic Memory — Aug 18 (4 days).** $8.75K. **BUILD SHIPPED by gentech 2026-08-14** (GenTech Agent Memory layer, 9/9 tests pass, verified against live CockroachDB). **Jordan: register on Devpost** (cockroachdb-ai.devpost.com), record <3-min demo video, push public repo. Build is done — only submission steps remain.
- **#29 Build with Gemini XPRIZE — Aug 17 (3 days).** Labs marked shipped (build brief consumed) but **Jordan still needs to register on Devpost** (xprize.devpost.com) + decide build. Money & Financial Access category fits our x402 gateway.
- **#80 Keeperhub Agents Onchain — DEADLINE PASSED Aug 13.** JORDAN CONFIRMED GO. Proof transfer complete Aug 8. **REMAINING: film demo video + assemble submission** — confirm if submitted or mark done.

## Needs Your Action

- **Apify Store — Publish a GenTech Actor (optional, needs human)** — Apify Store (apify.com) is the largest marketplace of web-automation tools for AI; 20,000+ Actors are now x402-payable (USDC on Base, June 2026), $1.4M paid out last month, many devs earn $3k+. This is a REAL sell-side income rail, but it needs a human: Apify account login + packaging our capability as a containerized "Actor" (Docker scraper), which is a different model from our x402 gateway. **If you want a scraping-actor presence:** (1) create an Apify account at apify.com, (2) pick one capability to package (e.g. token-security or market-intel as a pay-per-event Actor), (3) follow apify.com/partners/actor-developers to publish, (4) paste back the Actor URL + API token. 20% commission, pay-per-event/result. Otherwise skip — our x402 gateway already covers the API-seller niche.
- **#13 Multica + Paperclip — Set Up ClawWork Squad + GenTech Shop Plugin** — Multica at localhost:3001 (verification code 402402), Paperclip at ProtoJay4789/paperclip. Both greenlit.
- **#15 DeFi Model — QLoRA Fine-Tune DeepSeek R1 32B on BlockRun** — $2.50, ~1hr. Scripts ready at 10-Labs/defi-model/. Jordan funds BlockRun wallet, then `python3 run-modal.py`.
- **#36 Superteam USA — Remote Community Membership** — Applied, second triage in progress. Waiting on their decision.
- **#46 ComfyUI — Self-Hosted Brand Asset Pipeline** — Desktop-only (no GPU on VPS). Setup guide + LoRA workflow for Consigliere Fed Chair family.
- **Fund 0G testnet wallet for 0G Bridge Wave 3** — wallet `0x36795Fa569a66f8a6Fc2121E0e2d139B68C5AE93` is at **0.0 0G**; Compute ledger needs **3 0G min** but faucets only give 0.1 0G/day (~30 days — too slow for the 16-day wave). Do when home: post request in 0G Discord for >0.1 0G/day (documented path), and/or ask AKINDO for testnet credits (other participant @Crypto_hg is asking the same on the wave page). Once funded, Gentech wires `.env` (PRIVATE_KEY/RPC_URL/PROVIDER) + deploys `10-Labs/0g-defi-agent`.
- **Create Beep account + API keys (Sui rail)** — Jordan greenlit adding a **Sui payment rail** via Beep (agentic finance, USDC-on-Sui, a402/x402). Gentech has the adapter + Sui network entry staged to build the moment keys land. **You need to sign up at app.justbeep.it and grab a `beep_sk_*` (server) + `beep_pk_*` (publishable) key.** Paste them back and I'll wire the rail into the x402 gateway and test it.
- **CockroachDB × AWS #83 — SUBMIT (deadline Aug 18 5pm EDT, $8.75K)** — Build SHIPPED + verified (GenTech Agent Memory, 9/9 tests, live CockroachDB v24.3.4). **Remaining submission steps (from the guidelines email):** (1) register on Devpost (cockroachdb-ai.devpost.com), (2) record <3-min demo video — start live demo within 20-30s, name AWS Lambda + CockroachDB vector indexing on screen, visibly show memory in action, state problem + target audience up front; production tips: write/practice script + test audio, record at readable resolution, upload early (YouTube/Vimeo), make public/unlisted + playable without login, (3) push public GitHub repo (LICENSE at root), (4) list which CockroachDB + AWS tools used in writeup. Gentech can draft the script + writeup; you record + upload.
- **Virtuals ACP Registration (#64) — STILL PENDING since Jul 22** — register GenTech on Virtuals Protocol's Agent Commerce Protocol (ACP) at **app.virtuals.io/acp/new**. Needs wallet auth (you). 45K+ agents, $2.27M revenue, ACP is x402-native — our gateway is a natural fit. Re-surfaced Aug 14 after AgentLayer announced a Virtuals partnership (Virtuals actively onboarding external providers). Do when home: connect wallet, create agent identity, list our x402 gateway as an ACP offering.
- **Virtuals Spark credits — verify/claim** — revenue-monitor says "✅ Virtuals Spark Tier — $200/wk inference credits (claimed Jul 15)" but you say you still have to claim them. **Discrepancy to reconcile** — confirm whether the $200/wk Spark credits are actually claimed and active, or if that line is aspirational/wrong. If unclaimed, find + claim them.

## Needs Your Decision

- **#32 Model Strength Score — score trained models 0-850** — Needs greenlight + Modal GPU funding (~$30-60).
- **#53 Vault Git Divergence Cleanup** — main diverged from origin. Needs go-ahead to pull-rebase + push (touches shared history).
- **#82 Algorand Global x402 Challenge — DEADLINE PASSED Jul 31** — confirm if registered / late-leaderboard eligible, or mark dead.
- **Algorand First-Mover Play** — provide Algorand wallet address so X402_PAYTO_ALGORAND goes live, or confirm late-leaderboard eligibility.
- **#73 Super Arcade Tennis production deploy** — (a) deploy production build, (b) wire crypto payments?
- **#71 FrameForge** — direction decision? (Proven on KAGE film, ready to productize.)
- **#77 Open Generative AI** — go/no-go?
- **Robinhood KYC + OAuth** — perp leg for basis arb. One-time in-app.
- **Fund Coinbase wallet** — moves spot leg from dry-run to real execution.
- **Composio fork decision** — build on open Composio SDK vs self-host auth backend.

## Blockers / Notes

- **BountyBook payout rail** — code_test verifier crash reproduced twice. Lifetime code_test settlements 0/32. Bug report drafted (Discord `discord.gg/BXKTe44Y`, X `@_ptonik`). Jordan: paste report or let Gentech hand you the text.
- **GTA real-execution rails** — AVAX spot leg NOT in `gta_coinbase_leg.py` SUPPORTED map; `GTA_HL_KEY` unsealed. Not executable until fixed.
- **Narrative Rotation cron** — CMC key not loaded in pre-run (HTTP 401, all-zero JSON). Root cause: inline pre-run step doesn't read env.

---
*Gentech, 2026-08-14*
