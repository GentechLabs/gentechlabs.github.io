# From Gentech — Mastercard Innovation Challenge 2026 (Labs handoff)

**Date:** 2026-08-15
**Source:** X post by @suraj_sharma14 (https://x.com/i/status/2088453123086164312)
**Group of origin:** Gentech Treasury (finance/security play) → routed to Labs for build.

## The challenge

**Mastercard Innovation Challenge 2026** at GFF 2026 (Mumbai). Red team / blue team on **GenAI-powered payment fraud**.

- **Build the attack, then build the defense.**
- Participants: identify emerging GenAI payment-fraud attacks → build agents that simulate attacks at scale → develop AI/ML systems to detect and mitigate → **ship a working web prototype with a presentable UI**.
- Open to students + professionals 18+, online from anywhere.

## Key dates
- **Registration closes: Aug 20, 2026** (5 days from handoff)
- **Submission deadline: Aug 31, 2026**
- Top teams present at GFF: **Sept 8–11, Mumbai**

## Prizes (INR)
- 🥇 ₹2,56,000 (~$3K) · 🥈 ₹1,28,000 (~$1.5K) · 🥉 ₹64,000 (~$750)

## Fit assessment — ★★★★☆ (strong, strategic-exposure play)
- **Not a prize play** — modest purse. The value is the **Mastercard credential** + a strong agentic-payment-security portfolio piece.
- **Directly on-thesis:** our AAE stack is **deterministic pre-execution governance** (policy-bound execution, ERC-8004 identity, audit trail, x402 rails) — the counter-position to stochastic fraud detection. We don't just detect fraud; we stop it at the boundary before the agent can act.
- Reuses existing rails: AAE identity, x402 payments, agent runtime (Hermes).

## Proposed build (scaffold for Labs)
A **red-team/blue-team agent demo**:
1. **Red team** — a fraud-simulating agent that generates GenAI payment-fraud attack patterns at scale (phishing-style prompts, anomalous tx patterns, identity spoofing).
2. **Blue team** — a **pre-execution governance guard** that blocks the attack at the boundary (policy checks, identity verification, anomaly scoring) rather than post-hoc detection.
3. **Web UI** — clean prototype showing attack → blocked, with a presentable dashboard.

## Next actions
- ✅ **Registration link VERIFIED (2026-08-18):** https://luma.com/kyz978xv — "Mastercard Innovation Challenge @ GFF 2026" by Mastercard AI Garage (931 going). **Jordan must register by Aug 20.**
- ✅ **Build KICKED OFF + scaffolded (2026-08-18)** at `10-Labs/mastercard-challenge/` — `red_team.py` (7 attack types), `blue_team.py` (pre-execution governance BLOCK/FLAG/ALLOW), `index.html` + `demo_server.py` (web prototype), `test_mastercard.py` (10/10 pass). Verified server works.
- ⏸ **Labs next:** extend red-team realism (more attack patterns), add session-aware evaluation to the server, polish UI, prep demo video + README by Aug 31.
- **Gentech:** track in hackathon queue; prepare submission materials (README, demo video, social posts) by Aug 31.
