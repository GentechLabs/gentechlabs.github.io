# 👑 Jordan Action Items — 2026-08-13

## 🔴 URGENT — Deadlines

- **#80 Keeperhub Agents Onchain — DEADLINE TODAY Aug 13 (1 day).** JORDAN CONFIRMED GO. Proof transfer complete Aug 8 (0.01 USDC on-chain, TX 0x88fe6c9a...b1df, Base). **REMAINING: film demo video + assemble submission.** This is the #1 priority today.
- **#83 CockroachDB × AWS — Agentic Memory — Aug 18 (5 days).** $8.75K. Persistent memory + MCP Server. **Jordan: register?** (Devpost cockroachdb-ai.devpost.com)
- **#29 Build with Gemini XPRIZE — Aug 17 (4 days).** Labs marked shipped (build brief consumed) but **Jordan still needs to register on Devpost** (xprize.devpost.com) + decide build. Money & Financial Access category fits our x402 gateway.

## Needs Your Action

- **#13 Multica + Paperclip — Set Up ClawWork Squad + GenTech Shop Plugin** — Multica at localhost:3001 (verification code 402402), Paperclip at ProtoJay4789/paperclip. Both greenlit.
- **#15 DeFi Model — QLoRA Fine-Tune DeepSeek R1 32B on BlockRun** — $2.50, ~1hr. Scripts ready at 10-Labs/defi-model/. Jordan funds BlockRun wallet, then `python3 run-modal.py`.
- **#36 Superteam USA — Remote Community Membership** — Applied, second triage in progress. Waiting on their decision.
- **#46 ComfyUI — Self-Hosted Brand Asset Pipeline** — Desktop-only (no GPU on VPS). Setup guide + LoRA workflow for Consigliere Fed Chair family.

## Needs Your Decision

- **#32 Model Strength Score — score trained models 0-850** — Needs greenlight + Modal GPU funding (~$30-60).
- **#53 Vault Git Divergence Cleanup** — main diverged from origin. Needs go-ahead to pull-rebase + push (touches shared history).
- **#82 Algorand Global x402 Challenge — DEADLINE PASSED Jul 31** — confirm if registered / late-leaderboard eligible, or mark dead.
- **Algorand First-Mover Play** — provide Algorand wallet address so X402_PAYTO_ALGORAND goes live, or confirm late-leaderboard eligibility.
- **#73 Super Arcade Tennis production deploy** — (a) deploy production build, (b) wire crypto payments?
- **#71 FrameForge** — direction decision? (Proven on KAGE film, ready to productize.)
- **#77 Open Generative AI** — go/no-go?
- **🔑 AVAX KEY ROTATION (COMPROMISE EVENT)** — personal AVAX private key was pasted in chat. Stored locked-down at `/root/.blockrun/jordan-personal-a...`. **Rotate this key.**
- **Robinhood KYC + OAuth** — perp leg for basis arb. One-time in-app.
- **Fund Coinbase wallet** — moves spot leg from dry-run to real execution.
- **Composio fork decision** — build on open Composio SDK vs self-host auth backend.

## Blockers / Notes

- **🔴 TREASURY: CPI Bid-Ask reposition BLOCKED — Steward wallet swept empty.** Verified on-chain (3 independent reads) Aug 12: wallet `0x572ABd6461BED2258615E6b99c585Ab7c5d05037` holds NO LFJ V2.2 position, 0 WAVAX, ~0.0006 USDC, only 0.2979 AVAX gas. Root cause: ~43.72 USDC swept OFF the wallet Aug 11 evening (20:15–20:18 UTC) to `0xeee3fe6c...26e6c9` (residual 22.39 to `0xeee3c4ea...`). **Jordan: confirm if this was an intentional treasury wind-down/emergency move or unexpected.** If unintentional, immediate review needed — funds are off the managed treasury wallet. Recommend pausing the two CPI one-shots (`31432dce0de9`, `e13db42767b0`) + re-enabling the position heartbeat (was paused, so the empty wallet went unreported).
- **BountyBook payout rail** — code_test verifier crash reproduced twice. Lifetime code_test settlements 0/32. Bug report drafted (Discord `discord.gg/BXKTe44Y`, X `@_ptonik`). Jordan: paste report or let Gentech hand you the text.
- **GTA real-execution rails** — AVAX spot leg NOT in `gta_coinbase_leg.py` SUPPORTED map; `GTA_HL_KEY` unsealed. Not executable until fixed.
- **Narrative Rotation cron** — CMC key not loaded in pre-run (HTTP 401, all-zero JSON). Root cause: inline pre-run step doesn't read env.

---
*Gentech, 2026-08-13*
