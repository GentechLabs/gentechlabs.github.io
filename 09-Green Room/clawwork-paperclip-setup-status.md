# ClawWork + Paperclip — Setup Status (Aug 17, 2026)

## ✅ ClawWork — Agent EARNING (revenue stream LIVE)
- **Repo:** /root/ClawWork (HKUDS/ClawWork, $19K/8hrs demonstrated by ATIC+Qwen3.5-Plus)
- **Env:** .env fully configured (OPENAI_API_KEY → local proxy 127.0.0.1:8011, WEB_SEARCH tavily, CODE_SANDBOX boxlite)
- **GDPVal dataset:** downloaded to gdpval/data/train-00000-of-00001.parquet (openai/gdpval on HuggingFace)
- **Agent run:** `gentech-qwen-ollama` (qwen3.5:397b) ran 3 days, **EARNED $337.78** work income
  - Final balance: $1336.16 (from $1000), status THRIVING
  - Best single task: $226.99 (glueball editorial, score 0.90)
  - Created real deliverables: napa_valley_wineries.docx, glueball_editorial.docx
  - 220 task values loaded ($82.78-$5004, avg $259.45)

### 🔧 Fixes applied (documented for reuse)
1. **EVALUATION_MODEL** must be set to a proxy-available model (e.g. `deepseek-v4-flash:0731`), NOT gpt-4o (404 on proxy)
2. **PyPDF2** missing → broke productivity tools import. Installed it.
3. **boxlite sandbox needs KVM** (not on this VPS) → `execute_code` crashes with pyo3 panic. Fixed by catching `BaseException` (not just `Exception`) in `code_execution_sandbox.py` + `wrapup_workflow.py` so it degrades gracefully. Agent falls back to `create_file`/`read_file`/`search_web` which don't need the sandbox.

### ⚠️ Remaining limitation
- `execute_code` (Python execution) doesn't work on this VPS (no KVM for boxlite, no E2B key). Agent earns via file creation + web research instead. For full code-execution capability, would need E2B_API_KEY or a KVM-enabled host.

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
