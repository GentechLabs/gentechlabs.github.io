# Infrastructure Handoff: OpenCode Go Primary Routing Failure

**From:** Desmond (Creative)
**Assigned to:** DMOB / Infrastructure
**Date:** 2026-04-26
**Priority:** High — blocks Jordan's preferred model workflow

---

## Summary
- User: Jordan (ProtoJay4789)
- **OpenCode Go subscription was working last night but has stopped today**
- No clear error messaging visible to user
- Ollama Cloud models still functional but hitting rate limits and HTTP issues
- Vision analysis (`vision_analyze`) also returning `401 Invalid API key` errors — could be related credential outage

---

## User's Desired Setup
- **Primary:** OpenCode Go models
  - Ollama Cloud models as backup/fallback
- **DMOB Coding Tasks:** Currently on Qwen via Ollama
  - User open to switching DMOB coding tasks to OpenCode Go too

---

## Symptoms
1. OpenCode Go model routing fails (when user switches to it)
2. Ollama Cloud works but is rate-limited / less reliable
3. `vision_analyze` tool throwing `401 Invalid API key` across the board
4. No error logs surfaced to Jordan — unclear if Hermes config issue or API key expiration

---

## Action Items
1. **Check Hermes `config.yaml`** — verify OpenCode Go provider configuration, API key, model mapping
2. **Check `.env` or credential files** — are OpenCode Go credentials expired/missing?
3. **Check if OpenCode Go API itself is up** — test connectivity independently of Hermes
4. **Verify model switching logic** — does switching to OpenCode Go actually route requests there, or fail silently?
5. **Fix `vision_analyze` auth** — appears to be a broader API key/credential issue

---

## Context from this session
- Jordan tested model switch from kimi-k2.6 → qwen3-vl:235b-instruct via Ollama Cloud
- Worked around `vision_analyze` failures using `tesseract` OCR as fallback
- Extracted content from X post: https://x.com/AIonBase_/status/2048437997050466724 (saved as competitive intel)

---

**Status:** Pending pickup by ops/infrastructure team
