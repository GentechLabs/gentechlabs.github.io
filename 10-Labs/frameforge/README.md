# FrameForge — AI Storyboard Service

Controlled pre-visualization pipeline: character reference sheet → locked look →
camera-native storyboard frames. No randomness, no character drift.

Built on the pipeline proven with Vanito's KAGE film: character sheet → seed →
time-coded prompts → inline character coating every frame → compiled storyboard.

## What's here

- **`src/character.py`** — Character locker. Analyzes a reference sheet and
  produces a deterministic locked look (coating + seed + palette). This is the
  core differentiator: the same character config is reused across every frame,
  so there's no drift between shots.
- **`src/engine.py`** — Storyboard engine. Character config + scene descriptions
  → batch-generate camera-native frames. Deterministic SVG output (no external
  deps), so every frame is reproducible and testable.
- **`src/compile.py`** — Compile pipeline. Frames → animated MP4 via ffmpeg
  (image2 sequence demuxer + title overlay).
- **`src/cli.py`** — CLI: `lock`, `build`, `compile`.
- **`tests/`** — 11 tests, all passing.
- **`demo/`** — Live end-to-end demo: KAGE character locked, 4-frame "Neon Run"
  storyboard built, compiled to `neon-run.mp4` (4s, verified via ffprobe).

## Usage

```bash
# 1. Lock a character from a reference sheet
python3 -m src.cli lock KAGE demo/kage-sheet.txt demo/kage-lock.json

# 2. Build a storyboard from a shot list
python3 -m src.cli build "Neon Run" demo/kage-lock.json demo/shots.json demo/out

# 3. Compile frames to video
python3 -m src.cli compile demo/out demo/neon-run.mp4 --title "Neon Run — FrameForge"
```

## Camera grammar

Each shot carries camera direction that maps to composition rules:

| Field | Options |
|-------|---------|
| `camera_angle` | eye, low, high, dutch, over, aerial |
| `shot_size` | wide, medium, close, extreme, full, two |
| `movement` | static, pan, tilt, dolly, crane, handheld |
| `lighting` / `mood` | free text |

## Revenue model (from spec)

- **Phase 1 — Service:** $1,500 flat storyboard (10 scenes × 3 frames), $2,500 express 48h, $150/additional scene.
- **Phase 2 — API:** `POST /v1/storyboard` $3–5/frame, `POST /v1/character/lock` $10, `POST /v1/storyboard/compile` $25.
- **Phase 3 — Subscription:** Starter $199/mo, Studio $799/mo, Enterprise custom.

## Status

**Shipped 2026-08-15** by Gentech (nightly build). Core pipeline + CLI + compile
verified end-to-end. Next: service portal landing page + order form (Phase 1
launch), then API (Phase 2).

**Service portal shipped 2026-08-21** — `app.py` (Flask) exposes the full
Phase-1 service flow:

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Landing page with working order form |
| `POST /api/order` | Create order (character sheet + shot list + tier) → runs lock→build→compile |
| `GET /order/<id>` | Delivery page (frames + compiled animatic) |
| `GET /orders/<id>/frame/<file>` | Serve a generated SVG frame |
| `GET /orders/<id>/video` | Serve the compiled MP4 |
| `GET /api/orders` | List orders (status) |
| `GET /api/health` / `GET /api/tiers` | Health + pricing |

**Run it:** `python3 app.py` → serves on port `8123` (orders persist under
`orders/<id>/`). Verified end-to-end with a live "Neon Run" order: 3 frames
locked, delivery page 200, video 200 (3.0s MP4, ffprobe-verified). Remaining
for Phase 1 launch: nginx reverse-proxy + TLS, and wire the payment rail
(x402) so orders can be paid.
