# Jordan Items — Aug 21, 2026 (Nightly Build)

Blockers and decisions surfaced by stale-notes scan + considerations. Morning Digest should flag these.

## 🚨 Urgent / gated on Jordan

1. **🔴 AVAX KEY ROTATION (COMPROMISE EVENT, high)** — Jordan's personal AVAX private key was pasted in chat (derives to Main `0x7ebf...96a`, ~0.099 AVAX, nonce 5363). Stored locked-down at `/root/.blockrun/jordan-personal-avax/`. Needs rotation decision + movement of funds. Oldest unresolved security item.

2. **🔴 Algorand First-Mover (urgent)** — Composite entry SHIPPED Aug 7. **Jordan: (1) provide Algorand wallet address so X402_PAYTO_ALGORAND goes live, (2) confirm late-leaderboard eligibility or mark dead.**

3. **🔴 Algorand Global x402 Challenge #82 (deadline passed Jul 31)** — Jordan: confirm if registered / late-leaderboard eligible, or mark dead.

4. **🟠 Superteam USA (high)** — Applied; Jordan confirmed Aug 12 applied for second triage. **Waiting on their decision.** No action beyond monitor.

5. **🟠 Solana Foundation USA Grant** — Applied Aug 5. Aug 20 check: no approval/rejection email, still pending. STILL PENDING.

6. **BountyBook payout rail** — Reproduced verifier crash (code_test). Lifetime settlements 0/32. Bug report drafted in diag file. **Jordan: paste report to Discord `discord.gg/BXKTe44Y` / X `@_ptonik`, or let me hand you the text.** Operator has $150 fee outstanding.

## 🟠 Decisions needed (do not decide for you — surfacing)

- **Model Strength Score #12** — needs Jordan greenlight + Modal GPU funding.
- **Paymenter x402 #4** — RE-GATED: submission needs Jordan's live Paymenter account + Discord bot token; canonical Extensions repo archived (no PR path). Connector doc fleshed.
- **Super Arcade Tennis #73 production deploy** — Jordan: (a) deploy prod build, (b) wire crypto payments.
- **FrameForge #71 / Open Generative AI #77** — go/no-go direction decisions.
- **Make other GenTech surfaces PWAs** (Aug 11) — no build until scoped in HQ/CLI.
- **GTA real-execution rails** — AVAX spot leg NOT in `gta_coinbase_leg.py` SUPPORTED map; `GTA_HL_KEY` unsealed. Robinhood KYC + OAuth (perp leg), Fund Coinbase wallet (spot leg) — both Jordan one-time actions.
- **Composio fork decision** — build on open SDK vs self-host auth backend.
- **Krexa invite code** — Jordan grab invite via Discord `discord.gg/aMSEG7yj` → I run `krexa activate <code>`.

## 🆕 This session (gentech-only, ready to spike)

- **CopilotKit Channels SDK** — fleshed to a 3-step x402 approval-gate spike (sandbox only, no funds). Ready to run next session — no Jordan action needed unless you want to veto.

---
GENTECH — build lane empty (0 pending autonomous), so this was a maintenance run. No blockers on my side.

## Agent Builders Cup — SUBMITTED (2026-08-21)
- ✅ Jordan submitted the strategy for review (Aug 21)
- Strategy: LP Slot Operator (Solana CLMM, Meteora/Orca/Raydium) — Solana-only
- Team: Meteora · Repo: github.com/ProtoJay4789/gentech-condor-racer (public)
- Video: 26s demo → Jordan uploaded to Drive/YouTube
- ✅ Capital: sponsor-funded by Botcamp (Jordan note) — no self-funding needed
- ⏳ Applications close Aug 31; judging Sep 1-30; finals Oct 1-2

## Sentient $42M AGI Grant — SUBMITTED (2026-08-21)
- ✅ Jordan submitted (Aug 21)
- Pitch: Agentic Treasury (open x402 gateway for agent payments/trust)
- Ask: $10k · rolling, no deadline
- Demo: interactive at gentechlabs.net/treasury-demo/ + live gateway api.gentechlabs.net
- Deck: 10-Labs/treasury-demo/agentic-treasury-pitch.pptx
- Deliverables (if funded): mainnet hardening, 3 new rails (bridge/recurring/ERC-8004), open SDK, community
