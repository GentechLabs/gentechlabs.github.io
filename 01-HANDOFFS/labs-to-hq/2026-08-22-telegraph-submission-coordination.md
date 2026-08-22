# From Labs → HQ — 2026-08-22

## 🏆 Telegraph Season I Hackathon — submission coordination (handing up)

**Why this lands at HQ:** Jordan noted the hackathon coordination is being handled
at Gentech/HQ level. Labs has done the *build* side; the *submission + registration*
gates are Jordan's, so this needs HQ coordination.

### What Labs has SHIPPED (the build side)
1. **Miner YAML ready** — `10-Labs/telegraph-miners/gentech-token-security.yaml`
   (wraps our live Token Security / Rugcheck endpoint, `min_price_usdc: 0.01`,
   verified the endpoint returns HTTP 402 x402 challenge = exactly what Telegraph gates on).
2. **Prediction-Arb rail** — `Treasury/scripts/steward_prediction.py` (Phase 1 dry-run),
   a natural **Track 3 App** (consumes prediction-market intelligence, drives demand).
3. **Reference studied** — cloned `/root/telegraph-usecases/` (official Polymarket
   bot pattern) as the App-track template.

## What's needed to SUBMIT (human gates — Jordan)
1. **Register** at `hackathon.telegraphprotocol.com` → Register Now.
   → unlocks official Discord (**REQUIRED**, rule 06) + early-access specs + core-team support.
2. **Host the miner YAML at a public URL** (GitHub raw or VPS). Labs can do this once told where.
3. **Register miner on-chain** on Base — call `MinerRegistryFacet` (YAML URL + hash +
   fee address + floor price + intents). Needs **a Base wallet + gas**. Jordan signs in MetaMask.

### Submission facts (from live site + docs, verified Aug 22)
- **Deadline:** Track 1&2 (Miner+Script) close **Sep 7 12:00 UTC**. Track 3 (Apps) opens Aug 31.
- **Prize:** H1 $5K (Miner 1st $2K / Script $1K / App $2K). Series total $15K across H1-H3.
- **Judge (Miner):** 75% normalized performance within intent + 25% X engagement (tag `@Telegraphprotoc`).
- **Guardrail:** intent needs ≥3 active miners AND ≥100 real requests from Track-3 apps to be cash-eligible.
- **Strategy:** win = ship miner AND a Track-3 app that routes real traffic to it (Prediction-Arc rail fits).

## Ask of HQ
- Coordinate Jordan's registration + Base wallet gas + on-chain miner registration.
- Decide submission cadence (register early = Discord + early specs).
- Confirm whether the Prediction-Arc rail should be the Track-3 App entry.

## Files
- Miner YAML: `10-Labs/telegraph-miners/gentech-token-security.yaml`
- Prediction-Arc spec: `09-Green Room/specs/steward-prediction-arb-flash-loan.md`
- Telegraph build plan: `09-Green Room/specs/telegraph-hackathon-build-plan.md`
