# From Forge — 2026-08-22

## ✅ Shipped — desktop 3D lane (your scout → I actioned)
- **Blender 5.2.0 LTS** installed + verified (`blender.exe --version` → 5.2.0). First step of the 3D lane done.
- **GPU confirmed:** RTX 3070 Laptop, 8GB VRAM, CUDA 13.3. Torch 2.5.1+cu121 builds CUDA → verified `cuda True` on the 3070.
- **3D toolkit scaffold** created at `10-Labs/3d-toolkit/` (venv + TripoSR cloned). TripoSR deps installed and importing on GPU.

## ⏸ Blocked — torchmcubes (TripoSR mesh extraction)
TripoSR's `tsr/models/isosurface.py` **hard-imports `torchmcubes`** (line 6) for marching cubes. It has **no prebuilt Windows wheel** and **requires MSVC Build Tools** to compile from source. MSVC won't install non-interactively (needs a UAC elevation click).

**Options for Jordan:**
- A) **I click the VS Build Tools prompt** (I'll kick it off, you accept the UAC) → then I compile torchmcubes, TripoSR runs on the 3070.
- B) **Skip TripoSR**, install **Hunyuan3D-2 Windows portable** instead (has prebuilt wheels / WinPortable bundle, 5GB shape-only on 3070).
- C) Defer 3D gen; BlendCap/arcade don't need TripoSR now.

## 📋 Evaluation verdicts
- **BlendCap ($60 one-time, 11GB, NVIDIA)** — real local mocap, but same MSVC-free pipeline is fine (it's a Blender add-on, not Python build). Verdict: **buy** if we need real performance-capture for KAGE/Vanito; **Rokoko Vision free tier is now 30s/month cloud** → NOT aligned with self-host ethos. Lean BlendCap over Rokoko for offline.
- **Hunyuan3D-2** full is 10GB VRAM (won't fit 3070); **Hunyuan3D-2-mini 5GB** fits. Path B is viable.
- **TRELLIS** needs 16GB → won't fit 3070, skip.

## Notes
- Handoff-watcher cron set up (15 min, desktop).
- Working dir: `10-Labs/3d-toolkit/`
