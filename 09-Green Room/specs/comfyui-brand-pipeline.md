# ComfyUI — Self-Hosted Brand Asset Pipeline

**Build queue #46** · Desktop tool (VPS has no GPU) · Assigned: Jordan

## Why we're using this

We generate the **Consigliere Fed Chair family** (one per chain) and the **treasury
hex "G" emblems**. Right now each render is a fresh FAL call that *reinterprets*
the face — so the Solana Chair and the Arc Chair would drift apart. ComfyUI solves
the real problem: **character consistency**.

- **IPAdapter + InstantID** — lock the Powell face from a reference so every chain's
  Fed Chair keeps the *same* face, just recolored.
- **LoRA training** — train a "Consigliere" LoRA once, then every render is the same
  character in a different suit/chain palette.
- **Reusable node graph** — one workflow recolors the hex "G" emblem per chain,
  no re-prompting.

## Hardware requirement

ComfyUI needs a **GPU**. Our VPS has none (4-core / 15GB RAM / 22GB free disk).

| Tier | Spec | What it runs |
|------|------|--------------|
| Minimum | 4GB VRAM / 16GB RAM | SDXL, slow |
| **Sweet spot** | **12GB VRAM (RTX 3060)** | FLUX, decent speed |
| Comfortable | 32GB+ RAM, high-VRAM NVIDIA | FLUX + video (Wan/LTX) |

## Install (on the GPU machine)

**Option A — pip (simplest):**
```bash
pip install comfyui
comfyui
# opens http://127.0.0.1:8188
```

**Option B — portable build (recommended for Windows):**
1. Download the portable build from `github.com/Comfy-Org/ComfyUI` (Releases).
2. Unzip, run `run_nvidia_gpu.bat`.
3. Opens `http://127.0.0.1:8188`.

**Option C — from source:**
```bash
git clone https://github.com/Comfy-Org/ComfyUI
cd ComfyUI
pip install -r requirements.txt
python main.py
```

Docs: `docs.comfy.org/installation/system_requirements`

## The Consigliere workflow (once installed)

1. **Load the reference** — use the Powell likeness (`img_835707901bff.jpg`) as the
   IPAdapter/InstantID anchor so the face stays fixed.
2. **Build the base graph** — FLUX checkpoint → IPAdapter (face) → prompt with the
   fixed Consigliere description (silver side-part, dark charcoal suit, navy tie,
   arms crossed, robotic jaw/cheek panels).
3. **Recolor per chain** — swap the accent color in the prompt + a color-tint node:
   - Solana: teal→purple (`#00FFA3` → `#DC1FFF`)
   - Arc: teal/gold
   - Base: Coinbase blue
   - Ethereum: platinum/silver
4. **Train the LoRA (optional, for full consistency)** — generate a character sheet,
   train a "Consigliere" LoRA, then every render uses it.

## Deliverable

- Consigliere LoRA + reusable per-chain workflow
- Full Fed Chair cabinet (Solana/Arc/Base/ETH) + treasury hex emblems in one
  consistent pass
- Finished assets return to the VPS for the site/avatars

## Status

- [ ] Jordan installs ComfyUI on a GPU machine (12GB+ VRAM ideal)
- [ ] Gentech writes the base Consigliere workflow JSON
- [ ] Generate the full cabinet
- [ ] Ship assets to VPS
