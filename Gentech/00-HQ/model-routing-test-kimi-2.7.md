# Model Routing Test Plan — Kimi 2.7 Code vs GLM-5.2

**Started:** July 6, 2026
**Purpose:** Determine if `kimi-k2.7-code` via Ollama Cloud can replace GLM-5.2 for any part of the Forge BUILD→AUDIT+FIX→TEST→SYNC pipeline.

---

## Hypothesis

`kimi-k2.7-code` (Ollama Cloud, effectively free) is capable of handling at least Forge's **BUILD and daily execution tasks**. Whether it can replace GLM-5.2 for **AUDIT+FIX** is unknown and must be tested.

---

## Test Matrix

| Phase | Task Type | Model A | Model B | Success Metric |
|---|---|---|---|---|
| **1** | BUILD (simple) | kimi-k2.7-code | DeepSeek V4 Flash | Compiles, passes tests, matches spec |
| **2** | BUILD (multi-file) | kimi-k2.7-code | DeepSeek V4 Flash | All files consistent, no broken imports |
| **3** | AUDIT+FIX (simple bug) | kimi-k2.7-code | GLM-5.2 | Finds issue, applies fix, tests pass |
| **4** | AUDIT+FIX (security) | kimi-k2.7-code | GLM-5.2 | Catches hardcoded secrets, injection risks |
| **5** | Complex architecture | kimi-k2.7-code | GLM-5.2 | Clean refactor, minimal regressions |

---

## Live Session 1 — July 6, 2026

### What Was Tested
- Pull handoff from GitHub
- Read 3 handoff files + worker.js + wrangler.toml
- Create Forge → Gentech response
- Git add/commit/push
- `wrangler deploy --dry-run`
- Identify and document blockers

### Results
- **Tool calls:** ~48
- **Errors handled:** wrangler auth missing, missing scripts, KV discrepancy
- **Execution:** Completed 4 todos
- **Cost:** $0
- **Speed:** Fast, no rate limits

### Verdict
✅ **kimi-k2.7-code handles routine Forge execution well.**

---

## First A/B Test: x402 Worker Audit

### Target
`10-Labs/x402-gateway/worker.js`

### Known Issues
1. **Hardcoded CDP API keys** — security risk, should be Wrangler secrets
2. **KV namespace requested but unused** — handoff says create `RATE_LIMIT_KV`; worker doesn't reference it
3. **No rate limiting implementation** — anyone with a valid payment can hammer endpoints
4. **Empty agent card** authentication scheme says `Bearer` but x402 uses `PAYMENT-REQUIRED` header

### Test Design
1. **Path A (kimi):** Ask kimi to audit + patch `worker.js` and `wrangler.toml` to fix #1 and #2
2. **Path B (GLM-5.2):** Delegate identical prompt to GLM-5.2
3. **Compare outputs:** diffs, compile check, dry-run deploy
4. **Record findings here**

---

## Provisional Routing Rules (Until Test Complete)

| Pipeline Phase | Primary | Fallback | Notes |
|---|---|---|---|
| BUILD | DeepSeek V4 Flash | kimi-k2.7-code | Use kimi if DeepSeek slow/down |
| AUDIT+FIX | **GLM-5.2** | GLM-4.7 / llama3.1:70b | kimi still in testing |
| Daily execution | **kimi-k2.7-code** | GLM-4.7 | Ollama Cloud is free/fast |
| Complex architecture | GLM-5.2 | GLM-4.7 | No change until Phase 5 |
| Vision | qwen3-vl:235b-instruct | llava:7b | Unchanged |

---

## Decision Gates

- **Gate 1:** If kimi passes Phase 1-2 → authorize for BUILD tasks
- **Gate 2:** If kimi passes Phase 3 → authorize for simple AUDIT+FIX
- **Gate 3:** If kimi passes Phase 4-5 → consider full GLM-5.2 replacement

---

## Log

| Date | Test | Result | Notes |
|---|---|---|---|
| 2026-07-06 | Live session handling | ✅ Pass | Handoff processing, git, wrangler dry-run |
| 2026-07-06 | A/B x402 audit | 🔄 In progress | See results below after run |

---

## Notes

- Ollama Cloud subscription is $20/mo unlimited for this model.
- GLM-5.2 on Nous may have usage/cost implications.
- Keep this file updated after each test.
