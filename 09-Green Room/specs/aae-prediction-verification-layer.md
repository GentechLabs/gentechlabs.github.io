# AAE Prediction/Verification Layer — Agent + Human Claim Verification
**End-to-End Spec** — Jordan greenlit (Aug 10, 2026)
**Build flow:** DeepSeek V4 Flash (DEV) → Kimi K2.7 (AUDIT). Per `develop-and-verify` + `build-queue` skills.

---

## 1. Why this build

Jordan's thesis (verbatim intent):
> "There was a part of the prediction layer stuff in the AAE stack that we wanted a way to verify stuff. Let's say weight loss — somebody wants to take out a bet themselves and say 'I bet you I can lose the weight.' How can agents and humans verify?"

The **AAE stack already has the data-side of verification** — the `claim_evaluator` concept (see `agent-kit-claim-evaluator-spec.md`) runs a market claim against our data layers and returns a "stack vs. crowd" divergence verdict. What's **missing is the physical-side**: verifying real-world outcomes that text alone can't confirm (weight, form, progress, a completed task).

**Goal:** Build the AAE **Prediction/Verification Layer** — a way for agents AND humans to verify real-world claims/outcomes, combining:
1. **Data-side** — the claim-evaluator divergence verdict (already specced, parked).
2. **Physical-side** — Vision Agents (GetStream) realtime vision to *watch and verify* physical outcomes.

This extends the proprietary **agent-sentiment / divergence index** (Layer-3 signal) into a **verifiable-outcomes** layer — a genuinely differentiated capability.

---

## 2. Architecture — two verification rails, one verdict

```
             ┌──────────────────────────────────────────────┐
             │  AAE VERIFICATION LAYER (the brain)            │
             │  claim → data-verdict + vision-verdict        │
             │  → fused VERIFIED / UNVERIFIED / DISPUTED      │
             └───────────────┬──────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌─────▼─────┐        ┌─────▼──────┐
   │ DATA RAIL│        │ VISION RAIL│        │ SETTLE RAIL│
   │ claim-   │        │ Vision     │        │ x402 escrow│
   │ evaluator│        │ Agents     │        │ / Q402     │
   │ (diverg- │        │ (watch +   │        │ (pay on    │
   │ ence)    │        │  verify)   │        │  outcome)  │
   └──────────┘        └───────────┘        └────────────┘
   EXISTING (parked)    NEW (this build)     EXISTING (x402)
```

**Principle (mirrors AAE):** verification is venue-agnostic. The data rail and vision rail are interchangeable; the fused verdict is the product. Settlement rides our existing x402/Q402 escrow rails.

---

## 3. Build phases (Easy → Hard, Karpathy-gated)

### Phase A — Data-side verification (claim evaluator, unblocked)
**Why first:** the spec already exists (`agent-kit-claim-evaluator-spec.md`), it's pure code, no hardware gate, and it's the foundation the vision rail builds on.

- **A1. `services/claim_evaluator.py`** — read the 4 feeds (regime, narrative, arb basis, price trend), diff claim vs layers, emit verdict JSON (`AGREE / DIVERGE / CONFIRMED / CONTRADICT` + action read).
- **A2. Register as MCP tool** in the kit server: `claim_evaluator.evaluate(claim, asset?)`.
- **A3. `skills/claim-evaluation/SKILL.md`** — usage + decision rules.
- **A4. Tests** — TDD: verdict correctness on known claims, feed-missing fallback, stale-feed guard.

**Acceptance (Phase A done):** `claim_evaluator.evaluate("crypto bottom is in", "BTC")` returns a correct divergence verdict with the layer values visible (demo value).

### Phase B — Vision-side verification (Vision Agents, hardware-gated)
**Why second:** needs the Vision Agents PoC (x402-as-tool) to be proven first, and needs a camera/edge surface.

- **B1. Vision Agents PoC** — our x402 gateway as an MCP server wired into a Vision Agents voice agent (`MCPServerRemote(url=...)`). Proves "agent pays per call" in realtime voice/vision.
- **B2. `vision_verifier.py`** — a Vision Agents processor that watches a subject over time and emits a physical-outcome verdict (e.g. weight-loss progress, form, task completion).
- **B3. Fuse** — combine data-verdict + vision-verdict into one `VERIFIED / UNVERIFIED / DISPUTED` output.

**Acceptance (Phase B done):** a Vision Agents agent can watch a subject and emit a physical-outcome verdict, fused with the data verdict.

### Phase C — Settlement (bets/challenges, x402 escrow)
**Why last:** highest value, needs both rails + funded escrow.

- **C1. Bet/challenge contract** — agent + human stake on an outcome (weight-loss bet, task completion).
- **C2. Verify → settle** — on fused verdict, release escrow to the winner via x402/Q402.
- **C3. Dispute path** — human can dispute a vision verdict; escalation to manual review.

**Acceptance (Phase C done):** a weight-loss bet can be staked, verified by vision + data, and settled to the winner on-chain.

---

## 4. Dev/Audit workflow (Jordan's directive)

Per `develop-and-verify`:
- **DEV:** DeepSeek V4 Flash — `deepseek-v4-flash:0731` (ollama-cloud)
- **AUDIT:** Kimi K2.7 — `kimi-k2.7-code` on Ollama Cloud
- **Karpathy gates every phase:** no scope creep, testable acceptance, verify persistence before declaring done
- **Audit checklist:** hardcoded secrets, error-detail leakage, input bounds, verify-then-mutate ordering

---

## 5. Deliverables & demo

- **Phase A:** `services/claim_evaluator.py` + MCP registration + `skills/claim-evaluation/SKILL.md` + tests
- **Phase B:** Vision Agents PoC + `vision_verifier.py` + fusion logic
- **Phase C:** bet/challenge contract + x402 settlement + dispute path
- **Demo (per Jordan's rule):** major product → auto-add to demo site (gentechlabs.net) with a live "verify a claim" demo

---

## 6. Blockers to flag (not hide)

- **Phase B needs the Vision Agents PoC first** — and Vision Agents leans on Stream's edge network (free tier 333K participant-min/mo). Camera/edge surface required.
- **Phase C needs funded escrow** — x402/Q402 settlement needs a funded wallet.
- **Vision limitations (their own):** video AI struggles with small text; context degrades on ~30s+ continuous video; realtime models need audio/text to trigger.

---

## 7. Definition of Done

The Prediction/Verification Layer is "real" when, end to end:
1. A claim is evaluated against our data layers → divergence verdict (Phase A)
2. A physical outcome is watched and verified by vision → physical verdict (Phase B)
3. Both fuse into one `VERIFIED / UNVERIFIED / DISPUTED` output
4. A bet/challenge can be staked, verified, and settled on-chain via x402 (Phase C)
5. Every step verified by real output, not declared success

---

## Status
🅿️ **PARKED** — spec captured (Aug 10). Phase A is unblocked and buildable overnight; Phase B waits on the Vision Agents PoC; Phase C waits on funded escrow. Jordan to greenlight build.
