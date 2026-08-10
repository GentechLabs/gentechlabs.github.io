# KAGE Church Combat Film — Director's Cut (Save Point)

**Date:** 2026-08-10
**Status:** IN PROGRESS — final cut v3 delivered, awaiting Vanito's look-check on the candlestick scene (S3)

---

## 🎬 The Film

**30-second cinematic director's cut** — KAGE vs shadow creatures in a worn-out gothic church, ending with him leaving after confirming the job is done.

- **Model:** Seedance 2.0 (`bytedance/seedance-2.0` via ClawRouter proxy, ~$1.136/call)
- **Image model:** GPT Image 2 ONLY (`openai/gpt-image-2`, ~$0.063/image)
- **Audio:** "Blood on the Strings" (30s, -1.3dB, 194kbps AAC)
- **Ratio:** 16:9 wide (keyframe 1536×1024 → 720p output)

## 📽️ The 7-Clip Sequence

| # | Scene | Status |
|---|-------|--------|
| S1 | Desert Eagle combat (opening) | ✅ KEPT (good) |
| S2 | Chair kick (Leon Kennedy RE4 style) | ✅ KEPT (good) |
| S3 | Candlestick swing | 🔄 REBUILT v3 — Vanito look-checking |
| S4 | Kill shot, creature dissolves | ✅ REBUILT v3 |
| S5 | Rises, surveys, confirms all shadows gone | ✅ REBUILT v3 |
| S6 | Walks to door, pauses, pushes open | ✅ REBUILT v3 |
| S7 | Steps into blood moon rain, looks back, walks away | ✅ REBUILT v3 |

## 🔑 CRITICAL — The Method That Keeps KAGE Consistent

After many failed attempts, this is what WORKED (from the Blood Moon Rising video — `generate_clips.sh`):

1. **Seed EVERY clip from a character reference image** — NOT the previous clip's last frame.
2. Last-frame chaining causes KAGE to degrade into the shadow creature over generations. **Never chain.**
3. Append a fixed **COATING block** to every prompt — full character description + style lock.
4. Each clip self-contained. No drift accumulation.

**The COATING block:**
```
KAGE: jet black spiky messy hair covering one eye, very pale skin, dark guyliner
and smoky eye makeup, amber-gold eyes, long black leather trench coat with dark
red phoenix emblem, silver razor blade pendant on chain, heavy silver industrial
chain across chest, black t-shirt with red winged cross, black combat boots, dense
black scribble tattoos on forearms and hands. Same look as the seed image. Same dark
gothic digital painting style as the sheet, NOT photorealistic, NOT 3D.
Palette: crimson #CC0000, deep black, cold rain blue.
```

## ⚠️ PITFALLS (learned the hard way)

- **Character sheet as seed = WRONG.** A multi-panel grid makes Seedance render the grid itself and misreads skin tone. Vanito hated this. Use a CLEAN SINGLE render as seed.
- **Panel grid from old original = WRONG.** Vanito said "I like the other one better what we have" — the existing action sheet (`/tmp/kage-action-sheet.png`) is the correct reference, NOT the new panel grid built from S1.
- **Last-frame chaining = KAGE drifts into shadow creature.** Always re-seed from the sheet/render.
- **Audio mux:** input seek (`-ss` before `-i`), explicit `-c:a aac -b:a 192k`. Output seek = silent sections.

## 📁 Working Files (local)

| File | Path |
|------|------|
| Final cut v3 | `/tmp/kage-fixed3/kage-final-v3.mp4` |
| Good S1 | `/tmp/kage-v2-s1.mp4` |
| Good S2 | `/tmp/kage-v2-s2.mp4` |
| Rebuilt S3-S7 | `/tmp/kage-fixed3/S3.mp4` ... `S7.mp4` |
| KAGE action sheet (Vanito's pick) | `/tmp/kage-action-sheet.png` |
| Clean S1 render (loved by Vanito) | `/tmp/kage-church-wide.png` |
| Audio | `/tmp/kage-combat-audio-v2.mp3` |
| Rebuild scripts | `/tmp/kage-fixed3/prep.sh` |
| CDN seed | `https://vanito.gentechlabs.net/kage-sheet-seed.png` |

## 💰 Budget

- Wallet: F8 `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` (Base USDC)
- Cost per Seedance clip: ~$1.14 (10s request → ~5s actual)
- v3 rebuild (5 clips): ~$5.70

## ⏭️ NEXT STEP

Vanito is look-checking S3 (candlestick scene) in the v3 final cut. If KAGE holds his look → DONE, save the final. If S3 drifted → regenerate S3 only with same action-sheet method.
