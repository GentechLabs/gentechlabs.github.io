# Model Routing Configuration
**Last updated:** 2026-07-18

## Principle
All models through **same provider** (OpenCode Go) — no provider mixing.

## Tiered Routing

| Layer | Model | When |
|-------|-------|------|
| **Base** | DeepSeek V4 Flash | Default for everything. Day-to-day work, quick responses, simple reasoning. |
| **Coding** | Kimi K3 (or K2.7) | Code generation, debugging, refactoring, prototype work. K2.7 fallback until K3 releases (expected Jul 27+). |
| **Complex** | GLM 5.2 | Complex reasoning, architecture decisions, multi-step analysis, research, strategic planning. |

## Who This Applies To
- **Gentech** (Hermes Agent) — configured via provider/model settings
- **Forge** (Olima Cloud) — same models, same routing logic, Olima Cloud platform

## Decision Logic
1. Default: DeepSeek V4 Flash
2. If task involves writing/modifying code → Kimi K3/K2.7
3. If task requires deep reasoning, architecture, or complex strategy → GLM 5.2
4. If unsure → DeepSeek V4 Flash (safe default)

## Notes
- "Same-provider rule" = all model calls go through the same provider endpoint, no switching between providers mid-task
- This replaces the old Game Studio-specific routing which was only for canvas mobile game development
- Kimi K3 release date: ~Jul 27, 2026 (per Jordan)
