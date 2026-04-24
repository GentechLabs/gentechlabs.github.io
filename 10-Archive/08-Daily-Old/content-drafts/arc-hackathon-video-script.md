# ARC Hackathon — Demo Video Script (2-Min)

**Status:** DRAFT — ready for Jordan review
**Hackathon:** Agentic Economy on Arc | Deadline: Apr 25
**Format:** Screen recording + voiceover

---

## ⏱️ 0:00–0:10 — HOOK (10 seconds)

> *"AI agents are about to move billions of dollars — but who makes sure they actually deliver?"*

**Visual:** Show a terminal with an agent initiating a transaction, then a "Payment Released ✅" on-chain confirmation.

---

## ⏱️ 0:10–0:35 — PROBLEM (25 seconds)

> *"Right now, when an AI agent hires another agent to do work, there's no trust layer. Agent A pays Agent B, but what if Agent B does a bad job? What if Agent A refuses to pay? Today's smart contracts can't judge quality — they only execute conditions."*

**Visual:** Split screen — left shows a failed agent job with no recourse, right shows "Contract deployed but no enforcement" in red.

---

## ⏱️ 0:35–1:05 — SOLUTION: AgentEscrow (30 seconds)

> *"AgentEscrow fixes that. It's an AI-validated escrow system built for the agentic economy. Agent A posts a job and deposits payment into escrow. Agent B completes the work. An AI validator reviews the output — checking quality, completeness, accuracy. If it passes, funds release automatically. If there's a dispute? On-chain arbitration kicks in with AI consensus deciding the outcome."*

**Visual:** Walk through the flow:
1. Agent posts job → "Job Created: Summarize this contract" 
2. Escrow funded → "$0.50 locked in escrow"
3. AI validator evaluates → "Output matches requirements ✅"
4. Payment released → "Escrow closed — funds delivered"

---

## ⏱️ 1:05–1:35 — WHY ARC / NANOPAYMENTS (30 seconds)

> *"The reason we're building on Arc is nanopayments. Sub-cent transactions between agents weren't viable until now. With Arc's USDC settlement and Circle's infrastructure, agents can micro-pay for tiny tasks — a sentence translation, a data lookup, a quick code review. Each one costs fractions of a cent. That's the real agentic economy — high-frequency, low-value, automated."*

**Visual:** Show a rapid series of micro-transactions — 0.001 USDC, 0.003 USDC, 0.0005 USDC — all settling on-chain in seconds.

---

## ⏱️ 1:35–1:50 — THE TECH (15 seconds)

> *"Built with Foundry and Circle's x402 protocol. EIP-712 signatures for gas-efficient approvals. AI validator uses GenLayer's subjective consensus for dispute resolution. Deployed on Arc testnet."*

**Visual:** Quick code flash — contract snippet showing `createJob()`, `submitWork()`, `validateAndRelease()`.

---

## ⏱️ 1:50–2:00 — CTA (10 seconds)

> *"This is AgentEscrow. AI agents that can trust each other. Built for Arc."*

**Visual:** Gentech logo + "AgentEscrow on Arc" + GitHub link + "Built by Gentech"

---

## 🎬 Recording Notes for Jordan

1. **Record your screen** showing the Foundry test output (40/40 passing)
2. **Show the contract** in your editor briefly — the `createEscrow()` function
3. **Use a blockchain explorer** (Fuji testnet) to show a real deployment if possible
4. **Voice:** Natural, builder energy — no sales pitch tone
5. **Keep it raw** — judges prefer authentic demos over polished marketing

---

## 🔊 Voiceover Script (Full, Read Aloud)

*"AI agents are about to move billions of dollars — but who makes sure they actually deliver?"*

*"Right now, when an AI agent hires another agent to do work, there's no trust layer. There's no way to judge quality on-chain. Today's smart contracts can only execute conditions — they can't evaluate work."*

*"AgentEscrow fixes that. It's an AI-validated escrow system built for the agentic economy. Here's how it works: Agent A posts a job and deposits payment into escrow. Agent B completes the work. An AI validator reviews the output — checking quality, completeness, accuracy. If it passes, funds release automatically. If there's a dispute, on-chain arbitration kicks in with AI consensus deciding the outcome."*

*"We're building on Arc because nanopayments make this possible at scale. Sub-cent transactions between agents — a sentence translation, a data lookup, a quick code review. Each costs fractions of a cent. With Arc's USDC settlement, that's the real agentic economy."*

*"Built with Foundry, Circle's x402 protocol, and AI consensus for disputes. This is AgentEscrow. AI agents that can trust each other."*

---

#hackathon #arc #demo-script #video
