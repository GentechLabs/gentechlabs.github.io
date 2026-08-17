# ClawWork + Paperclip — Setup Status (Aug 17, 2026)

## ✅ ClawWork — Agent RUNNING end-to-end
- **Repo:** /root/ClawWork (HKUDS/ClawWork, $19K/8hrs demonstrated by ATIC+Qwen3.5-Plus)
- **Env:** .env fully configured (OPENAI_API_KEY → local proxy 127.0.0.1:8011, WEB_SEARCH tavily, CODE_SANDBOX boxlite)
- **GDPVal dataset:** downloaded to gdpval/data/train-00000-of-00001.parquet (openai/gdpval on HuggingFace)
- **Agent run:** `gentech-qwen-ollama` (qwen3.5:397b) ran 3 days, survived, balance $999.76, status THRIVING
  - 220 task values loaded ($82.78-$5004, avg $259.45)
  - Economic tracker initialized at $1000
  - **Fix needed:** EVALUATION_MODEL must be set to a proxy-available model (e.g. `deepseek-v4-flash:0731`), NOT gpt-4o (404 on proxy)
  - **Note:** agent's tool calls (create_file, execute_code_sandbox) returned "not found" — the sandbox tools aren't wired in this config. Quality score was 0.10 (below threshold) so no payment earned yet. Needs tool wiring for real earnings.

## ✅ Paperclip — genTech-shop plugin BUILT + VERIFIED
- **Dev server:** running on port 3101, health ok, auth ready
- **Plugin:** `@paperclipai/plugin-gentech-shop` at /root/paperclip-fork/packages/plugins/gentech-shop
  - Build: ✅ (dist/manifest.js, worker.js, ui/index.js)
  - Tests: ✅ 2/2 pass
  - Features: build queue panel (total/shipped/pending/blocked + by agent/platform) + service catalog + refresh action
- **Scaffold bug:** the standalone `create-paperclip-plugin` scaffold pins a stale SDK snapshot (shared@0.3.1) that fails to build. Building inside the repo workspace (workspace:* resolution) works.

## ✅ Multica — FULLY OPERATIONAL
- Workspace "GenTech Labs" (a3f54635-73ae-4950-9950-afce9822c276)
- Runtime "Hermes (gentech-vps)" ONLINE, auto-detected opencode + hermes
- Hermes agent created, status working, 6 concurrent tasks
- Daemon running, PAT saved
- Web UI: localhost:3001

## Next steps
1. **ClawWork:** wire the sandbox tools (create_file, execute_code_sandbox) so the agent can produce real deliverables → real earnings. Set EVALUATION_MODEL in .env permanently.
2. **Multica:** create ClawWork agents as teammates + a Squad for routing.
3. **Paperclip:** register the genTech-shop plugin in the running instance.
