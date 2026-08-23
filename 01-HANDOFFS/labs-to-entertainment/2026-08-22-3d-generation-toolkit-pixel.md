# From Labs → Entertainment (Pixel) — 2026-08-22

## 🎯 How the 3D Generation Toolkit helps what you're working on

Jordan: *"prep Pixel for how this can help with what we're working on."* Labs scouted
runnable 3D-generation tools (the paper-only WorldClaw had no code; these all run).
Same toolkit handed to **Forge** (desktop GPU lane) — but here's the **Entertainment**
angle, tailored to your current work (Vanito series, KAGE, Cold Crown/KIRI MV).

### The toolkit (runnable, open source)
1. **Hunyuan3D-2** (Tencent, 14.5k★) — high-res 3D asset gen from text/images, full code, **Blender addon**. https://github.com/Tencent-Hunyuan/Hunyuan3D-2
2. **TRELLIS** (Microsoft, 13.5k★) — 3D generation from text/images, CVPR'25.
3. **TripoSR** (VAST-AI) — fast 3D reconstruction from a single image.
4. **threejson** (MIT) — JSON-driven Three.js scene runtime, built for agent-driven worlds.

### Why it matters for YOUR work (not Forge's)
Your **#1 technical blocker** is **character drift** — each clip generated in isolation,
the model forgets the face/outfit. Your anchor fix = video continuation (chaining). The
**3D toolkit attacks the SAME problem from the geometry side**:

- **3D character anchors instead of 2D keyframes.** Hunyuan3D-2 can generate a **3D
  model of the character**, then you render consistent camera angles from the same mesh —
  the face/outfit literally can't drift because it's the same geometry every frame.
  This is the *permanent* fix vs. the opacity-blend / CG-anchor workarounds you're
  using now.
- **KAGE / Vanito series 3D environments.** Build coherent 3D world backdrops
  (Demon Slayer × Afro Samurai settings) once, reuse across Episode beats — consistent
  env instead of re-generating per shot.
- **Cold Crown drop / skydive beats.** Generate the rooftop + sky 3D scene as a stable
  backdrop for the money-shot free-fall, so the environment doesn't warble between clips.

### Forge is the executor
The tools run on **Forge's desktop GPU** (RTX 3070), not VPS. Forge builds the 3D assets;
**you consume them** as scene/character anchors in the film pipeline. So the workflow:
Forge generates the 3D anchor → exports renders → you feed those as the new stable
seed frames into your Seedance-2 continuation chain.

### Suggested next step for Pixel
1. Note the **3D-anchor strategy** as the long-term fix for character drift (replaces
   opacity-blend + CG-anchor hacks once Forge produces a Hunyuan3D-2 character mesh).
2. Keep current work (continuation chaining) as the near-term path — wallet-gated.
3. When Forge ships a 3D character anchor, trial it on the KAGE Episode-1 rebuild.

### 📝 Notes
- Scout, not a build — Forge decides install. No action needed from Pixel today.
- **Cold Crown wallet top-up** (`labs-to-entertainment/2026-08-22-wallet-topup.md`) is the
  current real blocker for video work — separate from this.
