#!/usr/bin/env python3
"""FrameForge service portal backend.

Phase 1 service: takes a character reference sheet + shot list, runs the
proven FrameForge pipeline (lock -> build -> compile), and serves a delivery
page with the storyboard frames + compiled animatic.

Endpoints
---------
GET  /                     landing page (web/index.html)
POST /api/order            create an order {project, tier, character_sheet, shots[]}
GET  /order/<order_id>     delivery page
GET  /orders/<order_id>/frame/<file>   serve a generated SVG frame
GET  /orders/<order_id>/video          serve the compiled animatic MP4
GET  /api/orders           list orders (status only)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory, abort

from src.character import lock_character
from src.engine import Shot, build_storyboard, write_storyboard
from src.compile import compile_video

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
ORDERS_DIR = BASE_DIR / "orders"

app = Flask(__name__)

# --- Pricing (Phase 1, from spec) ------------------------------------------
TIERS = {
    "storyboard": {"label": "Storyboard", "price": 1500, "scenes": 10, "frames_per_scene": 3},
    "express": {"label": "Express 48h", "price": 2500, "scenes": 10, "frames_per_scene": 3},
    "per_scene": {"label": "Per scene", "price": 150, "scenes": 1, "frames_per_scene": 3},
}


def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return text or "project"


@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "frameforge", "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


@app.get("/api/tiers")
def tiers():
    return jsonify(TIERS)


@app.post("/api/order")
def create_order():
    data = request.get_json(silent=True) or {}
    project = (data.get("project") or "Untitled").strip()[:80]
    tier = data.get("tier", "storyboard")
    character_sheet = (data.get("character_sheet") or "").strip()
    shots_raw = data.get("shots") or []

    if not character_sheet:
        return jsonify({"error": "character_sheet is required"}), 400
    if not shots_raw:
        return jsonify({"error": "shots is required (at least one scene)"}), 400
    if tier not in TIERS:
        return jsonify({"error": f"tier must be one of {list(TIERS)}"}), 400

    # Build Shot objects from the shot list.
    shots = []
    for s in shots_raw:
        shots.append(
            Shot(
                scene=int(s.get("scene", 1)),
                index=int(s.get("index", 1)),
                description=str(s.get("description", "")).strip(),
                camera_angle=s.get("camera_angle", "eye"),
                shot_size=s.get("shot_size", "medium"),
                movement=s.get("movement", "static"),
                lighting=s.get("lighting", "natural"),
                mood=s.get("mood", "neutral"),
            )
        )

    order_id = uuid.uuid4().hex[:12]
    order_dir = ORDERS_DIR / order_id
    frame_dir = order_dir / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    # 1. Lock the character (the FrameForge differentiator).
    lock = lock_character(project, character_sheet)

    # 2. Build the storyboard (deterministic SVG frames + manifest).
    sb = build_storyboard(project, lock, shots)
    write_storyboard(sb, str(frame_dir))

    # 3. Compile to an animatic MP4.
    video_path = order_dir / f"{_slugify(project)}.mp4"
    try:
        compile_video(str(frame_dir), str(video_path), title=f"{project} — FrameForge")
    except Exception as exc:  # video is nice-to-have; frames are the product
        video_path = None
        video_error = str(exc)
    else:
        video_error = None

    order_meta = {
        "id": order_id,
        "project": project,
        "tier": tier,
        "tier_label": TIERS[tier]["label"],
        "price": TIERS[tier]["price"],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "character": lock.to_dict(),
        "frame_count": len(sb.frames),
        "shots": [s.to_dict() for s in sb.shots],
        "video": video_path.name if video_path else None,
        "video_error": video_error,
        "status": "ready",
    }
    (order_dir / "order.json").write_text(json.dumps(order_meta, indent=2), encoding="utf-8")

    return jsonify({"order_id": order_id, "delivery_url": f"/order/{order_id}", "meta": order_meta}), 201


def _load_order(order_id: str) -> dict:
    order_dir = ORDERS_DIR / order_id
    meta_path = order_dir / "order.json"
    if not meta_path.exists():
        abort(404, description="Order not found")
    return json.loads(meta_path.read_text(encoding="utf-8"))


@app.get("/order/<order_id>")
def delivery_page(order_id: str):
    meta = _load_order(order_id)
    html = _render_delivery(meta)
    return html


@app.get("/orders/<order_id>/frame/<path:filename>")
def order_frame(order_id: str, filename: str):
    _load_order(order_id)  # 404 if missing
    return send_from_directory(ORDERS_DIR / order_id / "frames", filename)


@app.get("/orders/<order_id>/video")
def order_video(order_id: str):
    meta = _load_order(order_id)
    if not meta.get("video"):
        abort(404, description="No video for this order")
    return send_file(ORDERS_DIR / order_id / meta["video"], mimetype="video/mp4")


@app.get("/api/orders")
def list_orders():
    out = []
    if ORDERS_DIR.exists():
        for d in sorted(ORDERS_DIR.iterdir()):
            meta_path = d / "order.json"
            if meta_path.exists():
                m = json.loads(meta_path.read_text(encoding="utf-8"))
                out.append({"id": m["id"], "project": m["project"], "tier": m["tier_label"],
                            "status": m["status"], "created_at": m["created_at"], "frame_count": m["frame_count"]})
    return jsonify({"orders": out})


def _render_delivery(meta: dict) -> str:
    frames = ""
    for i, s in enumerate(meta["shots"], start=1):
        fname = f"frame_{s['scene']:02d}_{s['index']:02d}.svg"
        frames += (
            f'<div class="shot"><h3>Shot {i} — SC {s["scene"]:02d} {s["shot_size"].upper()} {s["camera_angle"].upper()}</h3>'
            f'<p class="desc">{s["description"]}</p>'
            f'<img src="/orders/{meta["id"]}/frame/{fname}" alt="Shot {i}"/></div>'
        )
    video_block = ""
    if meta.get("video"):
        video_block = f'<video controls src="/orders/{meta["id"]}/video" style="width:100%;border-radius:8px;margin:1rem 0"></video>'
    c = meta["character"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta['project']} — FrameForge Storyboard</title>
<style>
:root{{--ink:#111;--paper:#faf7f2;--accent:#c9a227;--muted:#666}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Georgia,serif;background:var(--paper);color:var(--ink);line-height:1.6}}
header{{background:var(--ink);color:var(--paper);padding:2.5rem 2rem;text-align:center}}
header h1{{font-size:2.2rem}} header p{{color:#ccc;margin-top:.4rem}}
.wrap{{max-width:1000px;margin:0 auto;padding:2rem}}
.badge{{display:inline-block;background:var(--accent);color:var(--ink);font-weight:bold;padding:.3rem .8rem;border-radius:20px;font-size:.85rem}}
.meta{{background:#fff;border:1px solid #e5e0d6;border-radius:8px;padding:1.2rem;margin:1.5rem 0}}
.meta .row{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}}
.shot{{background:#fff;border:1px solid #e5e0d6;border-radius:8px;padding:1.2rem;margin:1.2rem 0}}
.shot h3{{color:var(--accent);margin-bottom:.3rem}}
.shot .desc{{color:var(--muted);margin-bottom:.8rem;font-style:italic}}
.shot img{{width:100%;border-radius:6px;border:1px solid #eee;display:block}}
footer{{text-align:center;color:var(--muted);padding:2rem;font-size:.9rem}}
</style></head><body>
<header><h1>{meta['project']}</h1><p>FrameForge storyboard · <span class="badge">{meta['tier_label']}</span> · {meta['frame_count']} frames</p></header>
<div class="wrap">
  <div class="meta">
    <div class="row"><strong>Order</strong><span>{meta['id']}</span></div>
    <div class="row"><strong>Character locked</strong><span>{c['name']}</span></div>
    <div class="row"><strong>Seed</strong><span>{c['seed']}</span></div>
    <div class="row"><strong>Palette</strong><span>{', '.join(c['palette'])}</span></div>
  </div>
  {video_block}
  <h2>Storyboard</h2>
  {frames}
</div>
<footer>FrameForge — a GenTech Labs service. Built on the KAGE previs pipeline.</footer>
</body></html>"""


if __name__ == "__main__":
    ORDERS_DIR.mkdir(parents=True, exist_ok=True)
    # Production-ish: listen on all interfaces so it can sit behind nginx.
    app.run(host="0.0.0.0", port=8123, debug=False)
