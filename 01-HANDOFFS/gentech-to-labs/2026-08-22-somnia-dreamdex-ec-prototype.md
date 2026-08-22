# #63 — Somnia x DreamDEX Event Contracts Hackathon — AI Trading Agent: PROTOTYPE VERIFIED LIVE

**Date:** 2026-08-22 (nightly build)
**Group:** Labs
**Queue status:** pending → **SHIPPED** (prototype phase) 2026-08-22

## What shipped
The `ec-oracle-follow` strategy in the DreamDEX bot-kit is verified **working live against Somnia testnet** — the directional AI trading agent for event contracts (binary Up/Down markets on BTC/ETH). This is the core prototype the DreamDEX submission needs.

**Evidence (saved in vault):**
- `10-Labs/somnia-dreamdex-ec-agent/verification-testnet-dryrun-2026-08-22.log`
- `10-Labs/somnia-dreamdex-ec-agent/startup-venue-scope-2026-08-22.log`

## Live verification — what the bot actually did (real testnet, real oracle feed)
```
oracle-follow up as (no key, dry run) · model=strike interval=8000ms window=60000ms edge=0.03
idle · 8 tradable · flat · warming up ×8        # connects to venue, sees 8 live binary markets
DRY BUY_YES 5 BTC-0-22AUG26-0500 #YES @ ~0.357 (opening 78397.00 vs spot 78274.53, vol 0.112% measured,
    r muted, tilt +0.083 off market 0.341, pUp 0.424, fair 0.424, ask 0.355)
DRY BUY_NO 5 BTC-0-22AUG26-0415 #NO @ ~0.866 (opening 78397.00 vs spot 78273.75, vol 0.111% measured,
    r -0.0015, tilt -0.096 off market 0.852, pUp 0.052, fair 0.948, ask 0.864)
idle · 8 tradable · net 10 · model disagrees with market ×2, no edge ×5, at max shares ×1
    # ETH-0-22AUG26-0415 model 0.808 vs market 0.454 (off by 0.354)   <- muzzle working
    # closest BTC-0-22AUG26-0800 ref opening 78397.00 tilt +0.037 fair 0.458 ask 0.436 (needs 0.008 more)
BTC-0-22AUG26-0415: signal favours YES but we hold 5 NO — sitting out   <- opposing-leg guard working
```

Every subsystem exercised live:
- **Venue scoping** — VENUE_ID set correctly; bot refuses to guess across the 2 live venues.
- **Spot history warmup** — measures realized vol from the on-chain EMA oracle feed (vol 0.112% measured).
- **Edge-gated takes** — two real DRY trades crossed (BUY_YES + BUY_NO), each with full reasoning (opening ref vs spot, measured vol, tilt off market mid, fair vs ask).
- **Risk limits all firing** — max shares hit, model-disagreement muzzle (0.354 gap), opposing-leg sit-out (never mints complete sets).

## To run
```bash
cd /tmp/dreamdex
npm start -w ec-oracle-follow        # DRY_RUN=true by default (no key needed)
```
Set `DRY_RUN=false` + a funded `PRIVATE_KEY` in `strategies/ec-oracle-follow/.env` to trade for real on testnet.

## Remaining for the submission (Jordan / Labs)
1. **Testnet prototype with real fills** — run with a funded testnet key + `DRY_RUN=false`; capture a real cross (currently only DRY verified).
2. **GitHub repo** — publish a clean fork/summary repo of the working strategy (the kit's `origin` is somnia-chain/dreamdex-bot-kit; our working copy is at /tmp/dreamdex). Jordan to create the GenTech repo.
3. **2-3 min demo video** — record the live dry-run reasoning + a real fill.
4. **Feedback report** — the kit ships with an EC feedback/report flow (`scripts/ec-test/`); generate the report.
5. **Deadline Sep 8**, $5K pool, virtual.
