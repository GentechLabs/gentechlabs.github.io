# 0G Bridge Buildathon — Submission Plan

**Event:** 0G Bridge by AKINDO (WaveHack)
**Deadline:** Wave 3 — Aug 8 (18 days) — ⏸️ Skipping Wave 2, targeting Wave 3
**Prize:** $7,500 0G credits (Wave 2), $50K total pool
**URL:** https://app.akindo.io/wave-hacks/Z4MlX4vreI72ol6pd
**Judging:** Vision & 0G Fit, Technical Approach, Team & Execution

---

## Our Submission: GenTech x402 Gateway — 0G Agent Payment Bridge

**One-liner:** A payment bridge that lets AI agents on 0G pay for services via x402, and lets agents on other chains pay for 0G compute and storage.

### Why This Fits

0G is "The Blockchain for AI Agents" — compute, storage, DA, all for AI workloads. But agents on 0G have no standard way to pay for services across chains. Our x402 gateway already bridges payments across 5 chains (Base, Solana, Avalanche, BNB, OKX). Adding 0G as a 6th chain creates a two-way payment bridge:

1. **0G agents → external services** — An agent on 0G can call any x402-enabled API and pay in USDC
2. **External agents → 0G services** — An agent on any chain can pay for 0G compute or storage via x402

### What We'd Build

| Component | What | Status |
|-----------|------|--------|
| x402 Gateway | 16 endpoints, 5 chains, pay-per-call | ✅ Already live |
| 0G Chain Support | Add 0G (Chain ID 16661) as 6th supported chain | ⏳ Add RPC + USDC address |
| 0G Compute Proxy | Let agents pay for 0G inference via x402 | 🆕 New |
| Demo Video | Remotion + ElevenLabs (YoYo voice) | 🆕 New |

### Technical Approach

1. Deploy a USDC contract on 0G (or use bridged USDC)
2. Add 0G to our gateway's supported chains list
3. Create a proxy endpoint: `/api/0g/inference` — agents pay $0.005 per call, we route to 0G Compute
4. Submit with a demo video showing an agent on Base paying for 0G inference via x402

### Timeline

| Day | Task |
|-----|------|
| **Today** | Jordan signs up on AKINDO |
| Day 1 | Add 0G chain support to gateway config |
| Day 2 | Build 0G Compute proxy endpoint |
| Day 3 | Test end-to-end: agent → x402 → 0G inference |
| Day 4 | Record demo video with Remotion + YoYo |
| Day 5 | Submit to Wave 2 (or Wave 3 if more time needed) |

### Why We'll Win

- **Working product** — gateway is already live, not a whitepaper
- **Real integration** — 0G compute is already running, we just bridge payments to it
- **Clear value** — agents need to pay for things, x402 is the standard
- **Team** — GenTech Labs has shipped 50+ PRs, 16 endpoints, 5 chains

---

## Action Items

- [ ] Jordan signs up at https://app.akindo.io/wave-hacks/Z4MlX4vreI72ol6pd
- [ ] Add 0G chain to gateway config
- [ ] Build 0G compute proxy endpoint
- [ ] Record demo video
- [ ] Submit
