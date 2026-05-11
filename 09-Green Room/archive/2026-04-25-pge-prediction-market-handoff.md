# PGE Prediction Market Layer — Cross-Team Handoff

**Status**: ACTIVE  
**Initiated**: 2026-04-25  
**Requested by**: Jordan (HQ)  
**Scope**: Layer 10/11 of Personal Goal Engine — Prediction Market Module

---

## Jordan's Vision (Voice Memo Paraphrase)

> "Add a prediction market as Layer 10 or 11. Focus it on market-making predictions: where do you think TOWEL will be? Where do you think the coins you're yield farming will be? Leaderboards for accuracy. Keep it separate from education tiers — this is social/game layer. Tie it into bots and social game mechanics."

---

## Open Questions by Specialist

### YoYo (Strategy/Research)
- [ ] Is this a true prediction market (binary outcomes, AMM-based) or social betting (fixed odds, leaderboard)?
- [ ] Oracle requirements: price feeds, resolution sources
- [ ] Game theory: how to prevent whale manipulation / Sybil attacks on leaderboards
- [ ] Regulatory exposure: is this gambling or skill-based forecasting?

### DMOB (Contracts/Dev)
- [ ] Contract architecture for binary prediction markets
- [ ] Staking/escrow mechanism for predictions
- [ ] Leaderboard scoring: accuracy % vs profit-weighted?
- [ ] Can GenLayer oracle be used for market resolution?
- [ ] Gas cost estimates for on-chain scoring

### Desmond (Content/UX)
- [ ] How to frame predictions within social game without confusing edu flow
- [ ] Copy for "prediction markets" vs "learning simulations" — branding gap?
- [ ] Leaderboard UX: what metrics matter most to users?

---

## Constraints
- Must remain SEPARATE from core education tiers (1-9)
- Must integrate with existing bot/social game layer
- Must not create regulatory/regulatory risk for AAE brand

---

## Next Action
Each specialist to drop initial assessment in this thread by EOD. HQ will consolidate into a single recommendation for Jordan.
