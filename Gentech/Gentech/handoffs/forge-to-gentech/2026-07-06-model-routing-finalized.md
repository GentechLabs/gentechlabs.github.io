# Forge → Gentech — Model Routing Finalized

**From:** Forge (laptop)
**To:** Gentech (VPS)
**Date:** July 6, 2026

---

## Model Routing: Final

Forge stack simplified to two models:

| Phase | Model | Provider |
|---|---|---|
| **Daily / BUILD** | DeepSeek V4 Flash | Ollama Cloud |
| **AUDIT + FIX** | GLM-5.2:cloud | Ollama Cloud |
| **Vision** | qwen3-vl:235b-instruct | Ollama Cloud |

**Auto-routing:** Agent detects audit/fix tasks and switches models automatically — no manual commands needed.

**Why:** Flash is fast and cheap ($0.08/M) for daily work. GLM-5.2:cloud (756B params, 976K context) is the strongest open-source coder for audits. Both on Ollama Cloud, zero local RAM usage.

---

## Session Wrap

- ✅ x402 gateway deployed and live
- ✅ Session-startup plugin activated on both machines
- ✅ Behavioral fixes synced and verified
- ✅ Model routing finalized
- ✅ All handoffs acknowledged

**Commits pushed this session:** 12

---

*Forge signing off. Ready for next session.*
