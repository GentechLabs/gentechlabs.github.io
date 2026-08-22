---
date: 2026-08-21
type: brain-snapshot
source: 11-Mess Hall/considerations.md + Aug 21 handoffs (treasury-to-gentech, gentech-to-hq, entertainment, ideas) + context-weight
generated: 2026-08-22 00:07 ET (overnight run — captures Aug 21 activity)
---

# 🧠 Brain Snapshot — 2026-08-21

> Captured from `11-Mess Hall/considerations.md` + Aug 21 handoffs for cross-session continuity.
> Overnight run (00:07 ET). Context-weight regenerated same timestamp.

## 🆕 AUG 21 PROGRESS — shipped this session

- **Steward "OUT of range" bug AUDITED + FIXED (treasury)** — Root cause: `steward_execute.py` hardcoded `REDEPLOY_BIN_SPREAD = 5` for autonomous redeploy → 11-bin / ~1% wide curve. In a trending market (AVAX +10%, BTC $79K) that leaves range within minutes → 10-min watchdog re-centered endlessly. **Fix:** redeploy spread now shape-aware (`REDEPLOY_BIN_SPREAD_BY_SHAPE = {"curve": 11, "bid-ask": 15}`, Jordan's bin lever); `gta_avax_lp_execute.py` default now 11. Synced 3 copies + profile rail. Verified dry-run builds ±11/23-bin curve. Position live: 11 bins IN range $26.76.
- **Treasury council — BTC $79K short-liquidation** — Minutes: `Treasury/Strategy-Journal/2026-08-21-council-btc-79k-liquidation.md`. Verdict **CONSENSUS bull**, deployed (cbBTC +22%, AVAX LFJ in range). Vault committed `3260da53`.
- **GenTech EDU pilot page SHIPPED (nightly build)** — `09-Green Room/gentech-edu/lfj-avax-usdc-pool-pilot.md` — honest-expectations per-pool guide for the treasury's default AVAX rail, from **live verified numbers** (`discover_positions.py` → 11 bins · IN range · $7.31 · ~$26.77 deployed). Covers real returns at small size, exact start steps, common mistakes (incl. the CompositionFactorFlawed bug fixed live), risk profile, milestone ladder, trust contract.
- **Nightly build lane was EMPTY (0 pending autonomous)** — maintenance run. Group returns all already shipped (labs/entertainment/treasury/forge). Queue validated valid JSON. Infra health all PASS (gateway 200, bazaar 402 paywall, hub-launcher 200, arcade 200). Vault sync ✅ + GitHub push `d6777605` → origin/main.

## 🏆 Agent Builders Cup — Meteora Submission DRAFT (Aug 21)

- **Team:** Meteora (Solana-native seat). **Strategy:** **Consigliere — Solana CLMM LP Market-Making Agent** (LP slot operator: adopt/monitor open CLMM slots, exit at TP/SL/idle, fill ONE best-yield free slot per ~2-min tick).
- **⚠️ SCOPE CORRECTION (Jordan Aug 21):** We do NOT have Hyperliquid access → the HL perp-arb leg is **DROPPED** from the submission. **Solana-only** CLMM (Meteora / Orca / Raydium via Jupiter), tokens SOL/JUP/WIF/PENGU. We don't claim a venue we can't execute.
- Code: `/root/condor/agents/solana_dex_lp_expert/strategies/consigliere/strategy.md`. Params: 2-min tick, 3 slots, TP/SL 20, out-of-range 1800s, 0.3 SOL reserve, mint-not-symbol matching, width clamps.
- **⏳ JORDAN (submit by Aug 31):** (1) fund the Condor gateway wallet (racer can't trade without it), (2) final submit on botcamp.xyz. Demo video: `gentechlabs.net/videos/agent-builders-cup-meteora-demo.mp4`.

## 🎬 Entertainment — Cold Crown (KIRI) MV Opening (Aug 21)

- **Opening sequence LOCKED + deployed** (vanito.gentechlabs.net/music/vanito/cold-crown/): Beat 1 walk → Beat 2 edge → Beat 3 hood-down face reveal → Beat 4 eyes scan → Stitch `cold-crown-stitch-w-audio.mp4` (25.3s + drop).
- **Cinematic Drop (money shot):** Drop keyframe APPROVED v4 (arms spread, falling FORWARD, black leather jacket, mist streaming). Drop A free-fall spin (FF vibe) DONE. Drop B — **silver smoke pours from both eyes (THE MONEY SHOT)** DONE.
- **Beat drop timestamp CONFIRMED:** 30.6s in `cold-crown-clip-audio.mp3`.
- **⏳ BLOCKED:** Wallet **$0.59 USDC** — needs top-up (~$1.50-2/clip). **User wants Cold Crown drop REDO:** proper SKYDIVE (straight down, arms out, belly-down), and eye shot = camera-on-EYE → he CLOSES eye → silver mist streams from CLOSED eye (NOT open eyes w/ smoke). Build-up too short (fall lands ~20s, drop at ~32s — need more build-up beats).
- **HIKARI solo lyrics** ("Wake the Light / 光を呼べ") drafted in chat, dark gothic rock. **NOT yet saved to files** — awaiting Vanito approval + save signal.

## 🧭 Key context — cross-session continuity

- **Solana rail = LIVE.** Treasury Solana wallet `BE815V7ojVz63P..pUvP` recorded. Needs `SOLANA_PRIVATE_KEY` (base58) or keypair json wired into gentech-treasury profile to activate (`solana_homebase.py` reports `no_keypair`). Position reader fixed this session (real `positionUsd`).
- **Mastercard Innovation Challenge** — REGISTERED Aug 18, submit Aug 31. Build live (fraud stack 13/13, ERC-8004 identity + credit 76.7/HIGH). Remaining: realism, session-aware eval, UI polish, demo video.
- **Unichain Treasury Port SHIPPED** (#58/37) — `10-Labs/unichain-treasury/`, tests 9/9. Onchain deploy gated on capital on Unichain (wallet flat ~$1.88). App form `share.hsforms.com/18Kv3hTvDSt-x1wK9va0OYwsdca9`.
- **GTA dry-run (#GTA-DRYRUN):** decision ENTER (basis ≥ 10 bps). Freshest live scan picks **SOL (14.96 bps)** top basis. NO funds moved — awaiting Jordan approval for real execution.

## 🚨 Urgent — Deadlines + Open decisions (for Jordan)

| Item | Status / Next |
|------|----------------|
| Mastercard Innovation Challenge | Submit Aug 31 — build live, demo video pending |
| Agent Builders Cup (Meteora) | Draft ready → fund wallet + submit before Aug 31 |
| 🔴 AVAX KEY ROTATION | Compromise event — Jordan rotate / move funds off `0x7ebf…96a` (OLDEST open security item) |
| Algorand First-Mover + Global x402 #82 | Jordan: provide Algorand wallet / confirm eligibility or mark dead |
| Superteam USA membership | Pending 2nd triage (monitor) |
| Solana Foundation USA Grant | Applied Aug 5, still pending (no email) |
| BountyBook payout rail | Verifier crash reproduced; settlements 0/32 — Jordan paste report |
| AI Factory #79 / Build with DataHub | Deadlines passed Aug 10 — confirm submission status or close |
| Model Strength Score #12 | Needs Jordan greenlight + Modal GPU |
| GTA real-execution rails | AVAX spot leg + HL key (Robinhood KYC + fund Coinbase wallet) |
| Composio fork decision | open SDK vs self-host auth backend |
| Krexa invite | Jordan grab Discord `discord.gg/aMSEG7yj` → run `krexa activate <code>` |
| Solana wallet keypair wiring | wire keypair into gentech-treasury profile to activate Solana rail |

## 🛠 Infra health (Aug 21 nightly — all PASS)
- Gateway root **200** · Bazaar manifest **402** (expected paywall) · Hub-launcher **200** · Arcade **200**
- Treasury position live + earning: 11 bins IN range $26.76; shape-aware redeploy now ±11/23-bin curve
- Vault: Obsidian sync ✅, GitHub push `d6777605` → origin/main

## 🔗 Related
- [[brain-snapshot-2026-08-20]] — prior snapshot (captures Aug 20)
- [[context-weight]] — auto-generated project overview
- [[2026-08-21-jordan-items]] — Jordan action items (urgent + decisions)
- [[2026-08-21-nightly-build]] — nightly build handoff for morning digest
- [[agent-builders-cup-meteora-submission-2026-08-21]] — Agent Builders Cup draft
- [[gentech-edu/lfj-avax-usdc-pool-pilot]] — EDU pilot shipped Aug 21
