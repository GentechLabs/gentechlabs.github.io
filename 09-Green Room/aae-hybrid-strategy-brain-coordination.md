---
date: 2026-04-29
type: coordination
from: Gentech (CEO)
to: DMOB (Labs), Desmond (Creative)
status: active
---

# Green Room: AAE Hybrid Strategy Brain — Coordination

## Current State (Apr 29, ~2:15 PM)

### What's Already Built
1. **Three-Agent Architecture** — `02-AAE/Hybrid-Strategy-Brain-Architecture.md` (DMOB)
   - Actually four logical agents: Analyst → Strategy Brain → Validator → Executor
   - Validator + Executor tightly coupled (same process, different roles)
   - Three independent decision-making units
   - Progression layer: Shadow → Supervised → Autonomous
   - Security: no single agent can drain funds, circuit breaker, time-locked rotations

2. **Regime Classifier** — `03-Strategies/scripts/regime-classifier.py` (DMOB)
   - Classifies 6 regimes: BULL_TRENDING, BEAR_TRENDING, RANGE_BOUND, HIGH_VOLATILITY, ACCUMULATION, PRICE_DISCOVERY
   - Uses DexScreener + DeFiLlama APIs
   - RSI, ATR, momentum, volume analysis
   - State persistence for regime change detection
   - Default pool: our LFJ AVAX/USDC (0x864d...16ea)

3. **DMOB Scoping Handoff** — `09-Green Room/handoff-dmob-aae-strategy-engine-scoping.md`
   - Awaiting DMOB's technical scoping response

### Jordan's Architecture Question (Answered)
Jordan asked: "Did we decide if we were still doing three agents or two or one?"
**Answer:** Four logical agents, three decision-making units. DMOB formalized this in the architecture doc.

### What's Next
- [ ] DMOB: Complete technical scoping (current infra capacity, yield oracle, execution complexity, learning system)
- [ ] DMOB: Prototype Brain decision logic with mock data
- [ ] Gentech: Consolidate into phased roadmap once scoping is in
- [ ] Desmond: Creative direction for user-facing dashboard/notification UX

### Open Questions for DMOB
1. Validator on GenLayer — is this still the plan, or pivot to something available now?
2. Beam Cloud for Analyst + Brain — do we have access, or need alternative?
3. Regime classifier ready to plug into Brain, or needs signal format standardization first?

---

*Coordination thread. Update here as work progresses.*
