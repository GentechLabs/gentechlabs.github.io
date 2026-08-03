# ClawWork Setup — Ollama Cloud wiring (Aug 3 2026)

## Status
- **Agent model: WIRED & VERIFIED** — Ollama Cloud via OpenAI-compatible `/v1` base.
  - Key: from gentech profile `.env` (`OLLAMA_API_KEY`)
  - Config: `livebench/configs/test_gentech_qwen_ollama.json` (basemodel `qwen3.5:397b`)
  - Verified: LiveAgent inits clean, model responds ("MODEL OK: OK")
  - Agent signature: `gentech-qwen-ollama`

## What's wired
- `OPENAI_API_KEY` → Ollama Cloud key
- `OPENAI_API_BASE` → `https://ollama.com/v1`
- LiveAgent loads with base_url = ollama /v1

## What still needs keys (agent not fully operational until set)
- **`WEB_SEARCH_API_KEY`** — ClawWork needs Tavily (or Jina) for `search_web` / `learn_from_web` tools. Free tiers available at tavily.com / jina.ai. Currently empty.
- **`E2B_API_KEY`** — code sandbox (`execute_code_sandbox`). e2b.dev free tier. Currently empty. (Alternative: `CODE_SANDBOX_PROVIDER=boxlite` — boxlite IS installed, but needs sync extras confirmed.)

## Second provider (in ~8 days)
- **OpenCode Go** (`https://opencode.ai/zen/go/v1`, `OPENCODE_GO_API_KEY` in .env) — 100% usage cooldown clears ~Aug 11. Then we can switch agent model or run a second agent lane on it.

## How to run
```bash
cd /root/ClawWork
# model-only check
PYTHONPATH=/root/ClawWork/livebench .venv/bin/python -c "..."
# full agent run (needs web-search + sandbox keys first)
./run_test_agent.sh livebench/configs/test_gentech_qwen_ollama.json
```

## Blocker
ClawWork agents are "employees" — but they can't do real tasks until web-search + code-sandbox keys are provided. The MODEL brain is live; the TOOLS (search + sandbox) are offline.
