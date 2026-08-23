# Forge → Gentech (HQ) — Tomorrow's Plan — 2026-08-23

**From:** Forge
**To:** Gentech (HQ)
**Date:** 2026-08-22
**Status:** open

## Plan for tomorrow (Sat 2026-08-23)

Continuing the **desktop 3D lane** from today's session. One human-gated blocker needs a decision from Jordan.

## What's DONE (today)
- ✅ Handoff-watcher cron live on Forge (every 15 min daytime).
- ✅ Blender 5.2.0 LTS installed + verified. GPU = RTX 3070 8GB, CUDA 13.3.
- ✅ 3D toolkit scaffold at `10-Labs/3d-toolkit/` (venv + TripoSR). Torch 2.5.1+cu121 running on GPU.
- ✅ Evaluation verdicts written to `labs-to-forge/2026-08-22-forge-3d-lane.md`.

## Tomorrow's priorities
1. **Resolve the 3D-gen path** — Jordan picks ONE:
   - **(A)** Accept the MSVC Build Tools UAC prompt → I finish compiling `torchmcubes` → **TripoSR runs** (best fit: 6GB VRAM, GLB out).
   - **(B)** Pivot to **Hunyuan3D-2-mini** (5GB, has WinPortable bundle, no MSVC) — skip TripoSR.
   - **(C)** Defer 3D gen entirely; focus BlendCap/arcade.
2. **BlendCap go/no-go** — verdict leans **buy** ($60, offline, Blender 4.2+ / NVIDIA). Jordan's call — it's a paid add-on.
3. If 3D path resolved → trial a real asset (text→3D or image→3D) to validate the lane end-to-end.

## Ask for Jordan (surface in morning digest)
- "Which 3D path: TripoSR (need MSVC click) / Hunyuan3D-mini / defer?"
- "BlendCap ($60) — buy or skip? (Rokoko Vision free tier is only 30s/mo cloud, so BlendCap is the offline option.)"

## Context
- Full detail: `labs-to-forge/2026-08-22-forge-3d-lane.md`
- Working dir: `10-Labs/3d-toolkit/`
