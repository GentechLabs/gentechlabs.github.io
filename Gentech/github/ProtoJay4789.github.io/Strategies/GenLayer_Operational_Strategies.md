# GenLayer Ecosystem Strategies

## Passive Income Paths
     1|# GenLayer Passive Income Research
     2|**Date:** Apr 21, 2026
     3|**Status:** Initial Research — Needs Token Price Data for ROI Calculations
     4|
     5|---
     6|
     7|## 🎯 Summary: 3 Passive Income Paths
     8|
     9|| Path | Min Capital | Complexity | Risk | Passive? |
    10||------|-------------|------------|------|----------|
    11|| **Delegator** | 42 GEN | Low | Low-Med | ✅ Fully passive |
    12|| **Validator** | 42,000 GEN | High | Medium | ⚠️ Requires node ops |
    13|| **Builder Points → Airdrop** | Free (time) | Low | Speculative | ✅ Passive after setup |
    14|
    15|---
    16|
    17|## 1️⃣ Delegation (Best Passive Play)
    18|
    19|**Minimum:** 42 GEN tokens
    20|**Infrastructure:** None required
    21|**Rewards:** Proportional stake rewards minus validator's 10% operational fee
    22|
    23|### How It Works
    24|- Delegate GEN to a trusted validator
    25|- Earn passive rewards proportional to your stake
    26|- Validator takes 10% operational fee, you keep 90% of your share
    27|- Rewards auto-compound via the share system (stake-per-share increases)
    28|
    29|### Key Details
    30|- **Shares system:** You receive shares when depositing. Shares are fixed, but the GEN-per-share ratio increases as rewards accumulate. Your stake grows automatically.
    31|- **No active management** — set and forget
    32|- **7-epoch unbonding period** to withdraw (~7 days, epochs are 1 day)
    33|- **Slashing risk:** If your chosen validator gets slashed, delegators share the penalty
    34|
    35|### Reward Sources
    36|- Transaction fees from network usage
    37|- Inflation rewards: **starting at 15% APR**, decreasing to 4% APR over time
    38|
    39|### Epoch 0 Opportunity
    40|- **Currently in bootstrapping (Epoch 0)** — no minimum stake required to register
    41|- Stakes activate in Epoch 2 if minimums are met (42 GEN for delegators)
    42|- Shares calculated 1:1 in Epoch 0 (advantageous — later shares are ratio-based)
    43|- ⚠️ Must meet 42 GEN minimum by Epoch 2 or stake stays inactive
    44|
    45|### 📊 ROI Estimate (Needs GEN Token Price)
    46|```
    47|Inflation APR: ~15% (early, decreasing over time)
    48|After validator 10% fee: ~13.5% effective APR
    49|Break-even example: If GEN = $1 → 42 GEN = $42 → ~$5.67/year at 13.5%
    50|```
    51|
    52|---
    53|
    54|## 2️⃣ Validator (Higher Yield, Higher Effort)
    55|
    56|**Minimum:** 42,000 GEN tokens
    57|**Infrastructure:** Must run a node with LLM provider config
    58|**Rewards:** 10% operational fee + proportional stake rewards
    59|
    60|### Requirements
    61|- Run a node with appropriate LLM providers and models
    62|- Must call `validatorPrime()` every epoch (permissionless, but critical)
    63|- If `validatorPrime()` isn't called, excluded from next epoch's selection
    64|- Max 1,000 active validators (top by stake)
    65|
    66|### Validator Selection Formula
    67|```
    68|Weight = (0.6 × Self_Stake + 0.4 × Delegated_Stake)^0.5
    69|```
    70|- Self-stake counts 50% more than delegated
    71|- Square-root damping prevents whale dominance
    72|- Smaller validators often get better returns per GEN staked
    73|
    74|### Reward Distribution (Total Pool)
    75|- **10%** → Validator owners (operational fee)
    76|- **75%** → Total validator stake (validators + delegators split)
    77|- **10%** → Developers
    78|- **5%** → DeepThought AI-DAO (future allocation)
    79|
    80|### Risks
    81|- Slashing for malicious/incompetent behavior
    82|- Must stay in top 1,000 by stake
    83|- Node maintenance overhead
    84|- 7-epoch unbonding if you want to exit
    85|
    86|### 📊 Validator vs Delegator Comparison
    87|```
    88|At 15% APR on 42,000 GEN:
    89|- Validator: 10% op fee (630 GEN) + stake rewards (~5,670 GEN) = ~6,300 GEN/year
    90|- Delegator to same validator: ~13.5% = ~5,670 GEN/year on same stake
    91|- Validator earns ~11% more but has infra costs + slashing risk
    92|```
    93|
    94|---
    95|
    96|## 3️⃣ Builder Points → Airdrop (Free Play)
    97|
    98|**Cost:** Time only
    99|**Action:** Deploy Intelligent Contracts, earn Builder Points, get on leaderboard
   100|
   101|### Steps
   102|1. Go to studio.genlayer.com → create account + connect wallet
   103|2. Grab testnet GEN from testnet-faucet.genlayer.foundation
   104|3. Deploy a minimal Intelligent Contract (LLM Hello World)
   105|4. Register on dev portal → earn Builder Points → get on leaderboard
   106|5. Join GenLayer Discord + intro in builder channels
   107|
   108|### Why This Matters
   109|- Early testnet participants often get retroactive airdrops
   110|- Builder Points = trackable contribution metric
   111|- GenLayer has no mainnet token yet (testnet only) = earliest possible entry
   112|- BuildersClaw hackathon running on Bradbury = extra visibility
   113|
   114|### Risk/Reward
   115|- **Risk:** Airdrop is speculative, no guarantee
   116|- **Cost:** Just time and gas on testnet (free)
   117|- **Upside:** Could be significant if GEN launches at meaningful valuation
   118|
   119|---
   120|
   121|## 🔗 Network Details
   122|- **Network:** Bradbury Testnet
   123|- **RPC:** https://rpc-bradbury.genlayer.com
   124|- **Chain ID:** 4221 (note: older docs say 17180 — verify current)
   125|- **Faucet:** testnet-faucet.genlayer.foundation
   126|
   127|---
   128|
   129|## ⚠️ Open Questions
   130|1. **GEN token price** — testnet only, no price yet. Need to estimate post-mainnet valuation.
   131|2. **Mainnet timeline** — when does testnet end and real staking begin?
   132|3. **Builder Points conversion** — any official word on points → tokens?
   133|4. **Delegation availability** — can we delegate on testnet now, or mainnet only?
   134|5. **Inflation schedule** — "15% APR decreasing to 4%" — over what timeframe?
   135|6. **LLM costs for validators** — what does the LLM provider integration cost?
   136|
   137|---
   138|
   139|## 🎬 Recommended Action Plan
   140|1. **Immediate (free):** Deploy on testnet, farm Builder Points, climb leaderboard
   141|2. **Pre-mainnet:** Accumulate GEN if possible (faucet, early allocation)
   142|3. **Mainnet launch:** Delegate minimum (42 GEN) to a strong validator
   143|4. **Scale up:** If GEN appreciates, consider running a validator node
   144|5. **Synergy:** Use AgentEscrow project as showcase for Builder Points
   145|
   146|---
   147|
   148|## 💡 Strategic Note
   149|GenLayer's value prop is "AI oracle for smart contracts." Our AgentEscrow already integrates GenLayer for dispute resolution. We're building ON GenLayer while also potentially staking IN GenLayer — dual exposure to the ecosystem.
   150|
   151|If GenLayer becomes the standard for AI-based smart contract adjudication:
   152|- Our contracts gain utility (demand for GEN as gas)
   153|- Our staked GEN appreciates
   154|- Our Builder Points convert to tokens
   155|- Triple win from a single ecosystem bet.
   156|

---
*Added via HQ Orchestrator on 2026-04-23*
