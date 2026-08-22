# Borrow Log — LLMRouter (2026-08-21)

**Source:** github.com/ulab-uiuc/LLMRouter (MIT, UIUC, arXiv + HF Daily Papers)
**Frame:** borrow-the-mechanism

## What it is (bones — SPIT OUT)
Open-source **learned LLM routing** library: 16+ router methods (KNN/SVM/MLP/Elo/graph/
matrix-factorization/personalized), xRouteBench (quality + cost joint eval), CLI, ComfyUI.
torch-heavy, needs training data + GPU, academic framework. **Not adopted.**

## The mechanism (meat — BORROW)
We route by **heuristic + manual escalation** (V3: Flash / K2.7 / K3 by task tier).
LLMRouter does what we don't:
1. **Cost-aware learned routing** — route by predicted quality-per-dollar, not a static task→tier table.
2. **Elo / pairwise ranking** — continuously re-rank our provider pool (Ollama ↔ OpenCode Go ↔
   ClawRouter ↔ Nous) from actual task outcomes, instead of static ordering.

**Wire-in:** a lightweight cost-aware routing evaluator over the existing three-tier `model-routing`
skill — log (quality, cost) per (task, model) across providers, let Elo drift tier defaults.
~a few hundred lines, NOT a dependency.

**Verdict:** Borrow cost-aware learned routing + Elo ranking; spit out the library.
**Status:** Green Room watch/borrow note. Build only if provider costs justify the tuning effort.
