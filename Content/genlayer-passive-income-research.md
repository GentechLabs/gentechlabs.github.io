# GenLayer Passive Income Research
**Date:** Apr 21, 2026
**Status:** Initial Research — Needs Token Price Data for ROI Calculations

---

## 🎯 Summary: 3 Passive Income Paths

| Path | Min Capital | Complexity | Risk | Passive? |
|------|-------------|------------|------|----------|
| **Delegator** | 42 GEN | Low | Low-Med | ✅ Fully passive |
| **Validator** | 42,000 GEN | High | Medium | ⚠️ Requires node ops |
| **Builder Points → Airdrop** | Free (time) | Low | Speculative | ✅ Passive after setup |

---

## 1️⃣ Delegation (Best Passive Play)

**Minimum:** 42 GEN tokens
**Infrastructure:** None required
**Rewards:** Proportional stake rewards minus validator's 10% operational fee

### How It Works
- Delegate GEN to a trusted validator
- Earn passive rewards proportional to your stake
- Validator takes 10% operational fee, you keep 90% of your share
- Rewards auto-compound via the share system (stake-per-share increases)

### Key Details
- **Shares system:** You receive shares when depositing. Shares are fixed, but the GEN-per-share ratio increases as rewards accumulate. Your stake grows automatically.
- **No active management** — set and forget
- **7-epoch unbonding period** to withdraw (~7 days, epochs are 1 day)
- **Slashing risk:** If your chosen validator gets slashed, delegators share the penalty

### Reward Sources
- Transaction fees from network usage
- Inflation rewards: **starting at 15% APR**, decreasing to 4% APR over time

### Epoch 0 Opportunity
- **Currently in bootstrapping (Epoch 0)** — no minimum stake required to register
- Stakes activate in Epoch 2 if minimums are met (42 GEN for delegators)
- Shares calculated 1:1 in Epoch 0 (advantageous — later shares are ratio-based)
- ⚠️ Must meet 42 GEN minimum by Epoch 2 or stake stays inactive

### 📊 ROI Estimate (Needs GEN Token Price)
```
Inflation APR: ~15% (early, decreasing over time)
After validator 10% fee: ~13.5% effective APR
Break-even example: If GEN = $1 → 42 GEN = $42 → ~$5.67/year at 13.5%
```

---

## 2️⃣ Validator (Higher Yield, Higher Effort)

**Minimum:** 42,000 GEN tokens
**Infrastructure:** Must run a node with LLM provider config
**Rewards:** 10% operational fee + proportional stake rewards

### Requirements
- Run a node with appropriate LLM providers and models
- Must call `validatorPrime()` every epoch (permissionless, but critical)
- If `validatorPrime()` isn't called, excluded from next epoch's selection
- Max 1,000 active validators (top by stake)

### Validator Selection Formula
```
Weight = (0.6 × Self_Stake + 0.4 × Delegated_Stake)^0.5
```
- Self-stake counts 50% more than delegated
- Square-root damping prevents whale dominance
- Smaller validators often get better returns per GEN staked

### Reward Distribution (Total Pool)
- **10%** → Validator owners (operational fee)
- **75%** → Total validator stake (validators + delegators split)
- **10%** → Developers
- **5%** → DeepThought AI-DAO (future allocation)

### Risks
- Slashing for malicious/incompetent behavior
- Must stay in top 1,000 by stake
- Node maintenance overhead
- 7-epoch unbonding if you want to exit

### 📊 Validator vs Delegator Comparison
```
At 15% APR on 42,000 GEN:
- Validator: 10% op fee (630 GEN) + stake rewards (~5,670 GEN) = ~6,300 GEN/year
- Delegator to same validator: ~13.5% = ~5,670 GEN/year on same stake
- Validator earns ~11% more but has infra costs + slashing risk
```

---

## 3️⃣ Builder Points → Airdrop (Free Play)

**Cost:** Time only
**Action:** Deploy Intelligent Contracts, earn Builder Points, get on leaderboard

### Steps
1. Go to studio.genlayer.com → create account + connect wallet
2. Grab testnet GEN from testnet-faucet.genlayer.foundation
3. Deploy a minimal Intelligent Contract (LLM Hello World)
4. Register on dev portal → earn Builder Points → get on leaderboard
5. Join GenLayer Discord + intro in builder channels

### Why This Matters
- Early testnet participants often get retroactive airdrops
- Builder Points = trackable contribution metric
- GenLayer has no mainnet token yet (testnet only) = earliest possible entry
- BuildersClaw hackathon running on Bradbury = extra visibility

### Risk/Reward
- **Risk:** Airdrop is speculative, no guarantee
- **Cost:** Just time and gas on testnet (free)
- **Upside:** Could be significant if GEN launches at meaningful valuation

---

## 🔗 Network Details
- **Network:** Bradbury Testnet
- **RPC:** https://rpc-bradbury.genlayer.com
- **Chain ID:** 4221 (note: older docs say 17180 — verify current)
- **Faucet:** testnet-faucet.genlayer.foundation

---

## ⚠️ Open Questions
1. **GEN token price** — testnet only, no price yet. Need to estimate post-mainnet valuation.
2. **Mainnet timeline** — when does testnet end and real staking begin?
3. **Builder Points conversion** — any official word on points → tokens?
4. **Delegation availability** — can we delegate on testnet now, or mainnet only?
5. **Inflation schedule** — "15% APR decreasing to 4%" — over what timeframe?
6. **LLM costs for validators** — what does the LLM provider integration cost?

---

## 🎬 Recommended Action Plan
1. **Immediate (free):** Deploy on testnet, farm Builder Points, climb leaderboard
2. **Pre-mainnet:** Accumulate GEN if possible (faucet, early allocation)
3. **Mainnet launch:** Delegate minimum (42 GEN) to a strong validator
4. **Scale up:** If GEN appreciates, consider running a validator node
5. **Synergy:** Use AgentEscrow project as showcase for Builder Points

---

## 💡 Strategic Note
GenLayer's value prop is "AI oracle for smart contracts." Our AgentEscrow already integrates GenLayer for dispute resolution. We're building ON GenLayer while also potentially staking IN GenLayer — dual exposure to the ecosystem.

If GenLayer becomes the standard for AI-based smart contract adjudication:
- Our contracts gain utility (demand for GEN as gas)
- Our staked GEN appreciates
- Our Builder Points convert to tokens
- Triple win from a single ecosystem bet.
