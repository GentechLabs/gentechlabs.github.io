# Meta Ray-Ban + LingBot-Map: Wearable 3D Reconstruction Pipeline

**Status:** Concept / Reference
**Filed:** 2026-07-18
**Source:** github.com/Robbyant/lingbot-map (12.6k⭐, Apache-2.0)

## The Vision

Wear Meta Ray-Ban glasses, walk through a city, and return with a distortion-free 3D reconstruction of the entire experience. Virtual path, privacy filtering, and crowdsourced contribution layer.

## Hardware

| Spec | Meta Ray-Ban Gen 2 |
|------|-------------------|
| Video | 3K Ultra HD at **60fps** |
| Capture | 3-minute clips (Gen 2 improved battery) |
| Live stream | Via phone tether |
| Camera | Ultra-wide 12MP |
| AI features | Built-in Meta AI (limited on-device) |

## Pipeline

```
Ray-Ban → Phone → Cloud API → LingBot-Map → Post-process → Output
```

### 1. Capture (60fps → 20fps sample)
- LingBot-Map's target resolution: 518×378
- Downscale 3K frames → match resolution
- Sample every 3rd frame → ~20fps input to model
- Paged KV cache preserves temporal continuity

### 2. Reconstruction (LingBot-Map Core)
- **Anchor context** — coordinate grounding
- **Pose-reference window** — camera trajectory tracking
- **Trajectory memory** — long-range drift correction
- Output: 3D point cloud + camera poses + RGB texture

### 3. Virtual Path (Built-in)
- Camera pose is tracked by default
- Reconstruct walking path in 3D space
- Overlay on map or view as 3D flythrough

### 4. Privacy Toggle
- **On:** Detect humans → replace with generic mannequins
- **Off:** Raw reconstruction with people intact
- Similar UX to Google Maps layer toggles (satellite / traffic / terrain)

### 5. GenTech x402 Layer
- Wrap LingBot-Map inference as pay-per-scene API
- $X per minute of reconstructed footage
- Settlement in USDC on Base via x402

## Contribution Protocol (Future)

- Users opt-in to share reconstructions
- Token-incentivized 3D map building
- Privacy-filtered by default
- Competitive moat: data network effect (more walks → better coverage → more users)

## Technical Constraints

| Constraint | Detail |
|------------|--------|
| GPU required | RTX 3070+ recommended |
| Model size | ~1GB (HuggingFace) |
| Inference speed | ~20fps on 518×378 |
| Latency | Glasses → phone → cloud → reconstruction adds ~2-5s |
| Offline mode | Possible with Forge desktop RTX 3070, not on glasses |

## Next Steps (TODO)

1. [ ] Clone and test LingBot-Map locally (Forge desktop)
2. [ ] Verify 60fps → 20fps downsampling pipeline
3. [ ] Build x402 inference wrapper API
4. [ ] Prototype privacy mannequin swap filter
5. [ ] Acquire Meta Ray-Ban Gen 2 for testing

## Connections

- **scroll-world** — 3D promo scene pipeline (overlapping 3D reconstruction tech)
- **KAGEKŌ scroll world** — Band promo 3D space (adjacent 3D rendering pipeline)
- **x402 gateway** — Payment spine for inference API
- **GenTech Academy** — Could become a course module: real-time 3D from wearables
