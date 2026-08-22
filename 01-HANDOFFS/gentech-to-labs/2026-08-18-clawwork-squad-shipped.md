# Handoff: ClawWork Employee Squad — Infra Shipped

**Date:** 2026-08-18 (Nightly Build)
**From:** gentech → labs
**Build Queue:** #3 ClawWork Integration — GenTech Employee Squad → **SHIPPED** (verified)

## What was verified & shipped

The ClawWork employee-squad *infrastructure* is now live and verified. Two components confirmed working end-to-end:

### 1. Provider-fallback Router (`/root/ClawWork/clawwork-router.py`)
- OpenAI-compatible shim; points ClawWork agents at PRIMARY (Ollama Cloud) with automatic failover to FALLBACK (OpenCode Go) on 429/5xx/timeout.
- **LIVE** on `127.0.0.1:8011` (verified via `ss -ltnp`, pid 736).
- Verified `/v1/models` passthrough returns the full model list.
- Verified a full `/v1/chat/completions` round-trip against `deepseek-v4-flash:0731` → HTTP 200, real content (reasoning token observed).
- To run: `cd /root/ClawWork && python3 clawwork-router.py` (or it's already running).

### 2. GDPVal Task Pipeline (`livebench/work/task_manager.py`)
- `TaskManager` loads real GDPVal tasks from `gdpval/data/train-00000-of-00001.parquet`.
- **Verified:** 220 tasks loaded, 9 sectors, 44 occupations.
- Task values loaded (220 entries): **$82.78 – $5004.00, avg $259.45**.
- Daily task selection verified — picked a *Property Manager* task, max payment **$139.20**, 2 reference files.
- Config at `livebench/configs/test_gentech_qwen_ollama.json` (agent `gentech-qwen-ollama`, model `qwen3.5:397b`).

Committed to `/root/ClawWork` (git, on `main`).

## NEXT STEP for labs

The infra is proven but no *actual* GDPVal task has been executed by an agent yet. The revenue thesis ($19K/8hrs ATIC+Qwen3.5) requires a real agent run. **Next: run one GDPVal task end-to-end with an agent** (LiveAgent against the router on :8011) to prove a real deliverable + settlement. That's the item that turns infra into actual earnings.

## Routing note
This was originally `gentech/labs` cloud lane. The task-execution step stays in labs (cloud VPS has the code + router). Forge is NOT needed (no GPU required for the agent execution path via Ollama Cloud).
