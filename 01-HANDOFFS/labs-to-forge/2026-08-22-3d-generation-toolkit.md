# From Labs — 2026-08-22

## 🎯 Scouted opportunity → Forge (desktop/GPU lane)

### 3D Generation Toolkit — runnable alternatives to the paper-only WorldClaw

**Context:** Jordan shared `Tencent-Hunyuan/Hunyuan3D-WorldClaw` (967★) — but it's **paper-only** (no code, just README + images, arXiv Aug 7). Labs researched **runnable alternatives** to fill the same agentic-3D-generation gap. **Jordan: green light — "I want to take your suggestion."**

### The toolkit (verified runnable against actual repos)

1. **Hunyuan3D-2** (Tencent, 14,545★) — the **real code behind the WorldClaw line**. Full implementation: `gradio_app.py`, `api_server.py`, `minimal_demo.py`, `hy3dgen` package, **Blender addon**. High-res 3D asset generation from text/images. **This is the working WorldClaw.**
   - https://github.com/Tencent-Hunyuan/Hunyuan3D-2

2. **TRELLIS** (Microsoft, 13,482★) — structured 3D latents for versatile 3D generation (CVPR'25 Spotlight). High-quality assets from text/images. Mature.
   - https://github.com/microsoft/TRELLIS

3. **TripoSR** (VAST-AI, 6,876★) — fast 3D reconstruction from a single image. Quick asset turns.
   - https://github.com/VAST-AI-Research/TripoSR

4. **weigert/territory** (393★) — C++ homebrew **voxel engine built for agent-driven world gen**. Direct match for the "agent builds a world" thesis. Runs.
   - https://github.com/weigert/territory

5. **nnrj/threejson** (32★, **MIT**) — JSON-driven **declarative scene runtime for Three.js**, explicitly designed for "AI and Agent-driven generation and control." **Web-native** (matches our Three.js / arcade / ThreeUI stack). Sleeper pick.
   - https://github.com/nnrj/threejson

### Why this matters (vault-backed)
- **#9 Agent Warfare — Procedural Map Generation via text-to-cad** (build123d → STEP → GLB) — Hunyuan3D-2/TRELLIS are a far more capable version of this exact thesis.
- **#74 Agent Arcade 3D Lobby** — walkable 3D environment.
- **KAGE / Vanito film production** — 3D environments for shots.
- Same lane as **BlendCap** (mocap) + ComfyUI + ACE-Step on Forge's RTX 3070 desktop.

### Suggested next step for Forge
1. **Prioritize Hunyuan3D-2** (runnable WorldClaw) — verify the RTX 3070 can run it, trial a 3D asset from text.
2. **Keep `threejson`** as the web-native agent-driven option (fits arcade/ThreeUI; no GPU needed).
3. Fold into the same desktop 3D lane as BlendCap mocap — this is the *generation* half, BlendCap is the *capture* half.

## 📝 Notes
- Scout, not a build — Forge decides go/no-go + which to install.
- Hunyuan3D-2 repo is large (weights download) — confirm desktop GPU RAM/VRAM first.
- Vanito's upgrade is incidental (KAGE 3D envs) — he won't even know; Jordan's note.
