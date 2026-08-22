# From Labs — 2026-08-21

## 🎯 Scouted opportunity → Forge (desktop/GPU lane)

### BlendCap — local video-based motion capture for Blender
- **What:** 100% local, offline Blender add-on (Arcomade) that extracts full-body + hand + facial tracking directly from a single video file. Maps performance onto Rigify, Auto-Rig Pro, Mixamo, or CloudRig. Includes instant FK-to-IK conversion for fast keyframe cleanup.
- **Why it matters:** Free, no-subscription, no-cloud mocap pipeline — fits our self-host ethos. Plugs into KAGE / Vanito film production (Seedance, character-driven music videos) and arcade / Agent Warfare animation.
- **Key feature:** captures saved locally → reuse a performance on different characters without re-running tracking.
- **Requirements:** Blender 4.2+ on Windows/Linux, **NVIDIA GPU recommended**. VPS has no GPU → this is a **Forge desktop** tool (same lane as ComfyUI + ACE-Step on the RTX 3070).
- **Source:** 3DxDEV review — https://3dxdev.com/assets/blendcap-review-offline-full-body-hand-facial-mocap-from-any-video/ (X post 2090842627197354137, Aug 21 2026)
- **Status:** SCOUTED, not installed. It's a review of a paid add-on (Arcomade), not the add-on being free. Evaluate before committing.

## Why this matters (vault-backed)
Blender is already a **planned Forge desktop tool** across multiple projects:
- **SETUP.md** — Forge's role: "game dev (Unreal/Blender — desktop-only, needs GPU)"
- **#74 Agent Arcade 3D Lobby** — walkable 3D environment built in Blender/Unreal (spec: ProtoJay4789.github.io/10-Labs/agent-arcade-build-queue.md)
- **`blender_mcp`** skill installed + up to date
- KAGE / Vanito film production + arcade / Agent Warfare animation

BlendCap's video mocap is a direct accelerant for all of these — capture a performance once, retarget to any Rigify/Auto-Rig Pro/Mixamo/CloudRig character.

## Suggested next step for Forge
1. Verify Blender 4.2+ + NVIDIA GPU available on the desktop lane.
2. Evaluate BlendCap vs. free alternatives (e.g. MediaPipe/Rokoko Video) for our KAGE/arcade animation needs.
3. If it fits, trial on a KAGE character performance → retarget to Rigify.

## 📝 Notes
- No build item created yet — this is a scout. Forge decides go/no-go.
