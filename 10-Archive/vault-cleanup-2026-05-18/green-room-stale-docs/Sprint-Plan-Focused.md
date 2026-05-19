# 🎯 Sprint Plan — Focused Build
> **Updated:** 2026-04-29
> **Decision:** Cut scope. Two hackathons, done well.

---

## The Cut

| KEEP | DROP |
|------|------|
| 🔴 Solana Frontier — May 11 (12 days) | 🔵 Google Cloud Rapid Agent — Jun 11 |
| 🟡 Kite AI — May 17 (18 days) | 🟣 Retro9000 — Jul 14 |

**Rationale:** 4 hackathons × 4 layers = none done well. Two hackathons, focused execution = both submitted strong.

---

## Submission 1: Solana Frontier (May 11)

**What:** Agent Economy Core — registry, escrow, enforcement, arena
**Chain:** Solana (Anchor)
**Prize:** $230K+ main + $680K+ sidetracks

### Components
- [ ] `agent_registry` — Agent identity, skills, stake
- [ ] `job_escrow` — Payment flow, escrow, release
- [ ] `reputation` — Scores, endorsements, leaderboard
- [ ] Arena competition — Agents compete on LP performance
- [ ] Enforcement — Slashing, dispute resolution
- [ ] Demo video + README

### DMOB Build Order
1. Anchor scaffold + agent_registry program
2. job_escrow program + tests
3. reputation program
4. Arena scoring logic
5. Demo video

---

## Submission 2: Kite AI (May 17)

**What:** The Hybrid Strategy Brain — autonomous yield rotation
**Chain:** Kite AI (AVAX ecosystem)
**Prize:** $10K
**Track:** Agentic Trading

### Components
- [ ] Market regime classifier (volatility, trend, volume)
- [ ] Strategy performance tracker (LP APR vs staking vs HODL)
- [ ] Rotation engine (weighted allocation shifts)
- [ ] User training interface (Shadow → Supervised → Autonomous)
- [ ] Proactive notifications ("Switching strategy, approve?")
- [ ] Production demo on Vercel
- [ ] README + demo video

### DMOB Build Order
1. Regime classifier — signal detection
2. Strategy tracker — compare yields
3. Rotation engine — allocation logic
4. Training interface — user feedback loop
5. Deploy + demo

---

## Timeline

```
WEEK 1 (Apr 29 → May 4)
├── DMOB: Solana — Anchor scaffold, agent_registry, job_escrow
├── DMOB: Kite — Regime classifier, strategy tracker
└── Jordan: Arena game design, $TECH tokenomics

WEEK 2 (May 5 → May 11)
├── DMOB: Solana — reputation, enforcement, arena, demo
├── Jordan: Demo video, README polish
└── MAY 11: SUBMIT SOLANA FRONTIER 🔴

WEEK 3 (May 12 → May 17)
├── DMOB: Kite — rotation engine, training UI, deploy
├── Jordan: Demo video, README polish
└── MAY 17: SUBMIT KITE AI 🟡
```

---

## The Pitch

**Solana Frontier:** "The full agent economy — agents that compete, earn, and get ranked."
**Kite AI:** "AI agents that trade like you — learn your style, rotate strategies autonomously."

---

*Two hackathons. Focused execution. Let's ship.*
