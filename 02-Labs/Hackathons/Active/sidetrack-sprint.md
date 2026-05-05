# Sidetrack Sprint — Option B ($8K total)
**Started:** May 5, 2026
**Deadline:** May 11, 2026 (6 days)
**Bounties:** 
- Zerion CLI — $5,000 (Agent that auto-discovers and delegates tasks via CLI)
- GoldRush/Covalent — $3,000 (Agent risk dashboard with on-chain data feed)

---

## Decision Log
- **May 5:** Jordan locked in **Option B** — Zerion ($5K) + GoldRush ($3K) = $8K total
- Video demo approach: Jordan experiments with local Hermes + Hagen + video agent on May 6 (day off)
- Fallback video: screen recording + voiceover if local pipeline doesn't work
- Adapter specs: `09-Green Room/active-handoffs/sidetrack-adapter-specs.md`

---

## Daily Milestones

### Day 1 (May 5) — ✅ DONE
- [x] Sprint plan created
- [x] Labs handoff sent to DMOB
- [x] Sidetrack research complete (vault has maps)
- [x] Option B locked in

### Day 2 (May 6) — Jordan's day off / DMOB builds
- [ ] **DMOB:** Register for Zerion API key (dashboard.zerion.io) + GoldRush API key (goldrush.covalenthq.com)
- [ ] **DMOB:** Scaffold both adapter projects (zerion_cli + goldrush)
- [ ] **Jordan:** Experiment with local Hermes model + Hagen + video agent
- [ ] **Jordan:** Test video pipeline locally — if it works, we use it for demo

### Day 3 (May 7) — Core functionality
- [ ] **DMOB:** Zerion adapter — implement agent task discovery (scan for opportunities)
- [ ] **DMOB:** Zerion adapter — implement CLI task delegation interface
- [ ] **DMOB:** GoldRush adapter — implement risk scoring + position health monitoring
- [ ] **Jordan:** Review video demo results — decide on demo approach

### Day 4 (May 8) — Polish + demo
- [ ] **DMOB:** Zerion adapter — error handling, edge cases, CLI UX polish
- [ ] **DMOB:** GoldRush adapter — error handling, feed into AgentEscrow reputation
- [ ] **Desmond:** Start writing submission READMEs (both sidetracks)
- [ ] **Jordan:** Record video demo (local pipeline OR screen recording)

### Day 5 (May 9) — Submission prep
- [ ] **Desmond:** Finalize both READMEs, submission docs, pitch narratives
- [ ] **DMOB:** Final testing, bug fixes (both adapters)
- [ ] **Jordan:** Review everything, approve submission

### Day 6 (May 10) — Submit
- [ ] **All:** Final review + submit both sidetracks (Zerion $5K + GoldRush $3K)
- [ ] **Desmond:** Social posts ready (pre-scheduled for post-submit)

---

## Video Demo Plan
**Primary (experiment May 6):** Local Hermes model + Hagen + video agent
- Jordan tests on home machine (32GB RAM)
- If pipeline works → clean agent demo with real video output
- If not → screen recording of CLI in action + voiceover

**Key question:** Can we get Hermes running locally with video agent capabilities?
- Jordan's machine: 32GB RAM, should be sufficient for quantized models
- Hagen integration: needs testing
- Fallback is solid — screen recording is always an option

---

## Assignment Matrix
| Agent | Primary Tasks | Availability |
|-------|--------------|-------------|
| DMOB | Zerion CLI build, API integration, testing | Full sprint |
| Desmond | README, submission docs, social posts | Full sprint |
| Jordan | Video demo, architecture decisions, final approval | May 6 (experiment), May 9-10 (review) |

---

## Files
- `sidetrack-adapter-specs.md` — detailed API specs for both adapters
- `SUBMISSION-README.md` — to be created Day 4-5
- `TECHNICAL-WALKTHROUGH.md` — to be created Day 4-5
- `VIDEO-SCRIPT.md` — TBD based on May 6 experiment results
