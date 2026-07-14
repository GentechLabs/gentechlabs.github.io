# Model Routing — Active Config

> Last updated: 2026-07-09
> Changes announced by Jordan.

## Shared Model Stack

| Role | Model |
|------|-------|
| 🖊️ Draft / Build | DeepSeek V4 Flash |
| 🔍 Audit / Verify | GLM-5.2 |
| 🔄 Fallback | Nous Research |

## Per-Agent Gateway

| Agent | Gateway | Hardware |
|-------|---------|----------|
| 🖥️ **Gentech** (VPS) | OpenCode Go | Cloud |
| 🛠️ **Forge** (Desktop) | Ollama Cloud | RTX 3070 + Cloud |
| 🔄 Both | Nous Research (backup) | Cloud |

**Workflow:**
1. Build with DeepSeek V4 Flash
2. Verify it works
3. If it fails → audit with GLM-5.2
4. Fix → re-verify

**Provider updates:** Jordan confirms before changing.
