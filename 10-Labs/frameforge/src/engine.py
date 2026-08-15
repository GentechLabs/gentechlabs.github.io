"""Storyboard engine: character config + scene descriptions -> batch generate
camera-native storyboard frames. Deterministic SVG output (no external deps),
so every frame is reproducible and testable. The SVG frames are the product
artifact; a compile step can later turn them into an animated video via ffmpeg.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any

from .character import CharacterLock

# Camera grammar: angle + shot size + movement. These map to composition rules.
CAMERA_ANGLES = {
    "eye": "eye-level, neutral",
    "low": "low-angle, subject towering",
    "high": "high-angle, subject diminished",
    "dutch": "dutch tilt, unease",
    "over": "over-the-shoulder, depth",
    "aerial": "aerial, top-down geography",
}

SHOT_SIZES = {
    "wide": "wide establishing shot",
    "medium": "medium shot, waist up",
    "close": "close-up, face",
    "extreme": "extreme close-up, detail",
    "full": "full body",
    "two": "two-shot",
}

MOVEMENTS = {
    "static": "locked-off tripod",
    "pan": "panning",
    "tilt": "tilting",
    "dolly": "dolly in",
    "crane": "crane up",
    "handheld": "handheld, kinetic",
}


@dataclass
class Shot:
    """A single storyboard frame request."""

    scene: int
    index: int
    description: str
    camera_angle: str = "eye"
    shot_size: str = "medium"
    movement: str = "static"
    lighting: str = "natural"
    mood: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene": self.scene,
            "index": self.index,
            "description": self.description,
            "camera_angle": self.camera_angle,
            "shot_size": self.shot_size,
            "movement": self.movement,
            "lighting": self.lighting,
            "mood": self.mood,
        }


@dataclass
class Storyboard:
    """A compiled storyboard: locked character + ordered shots + frames."""

    title: str
    character: CharacterLock
    shots: list[Shot] = field(default_factory=list)
    frames: list[str] = field(default_factory=list)  # SVG strings

    def add_shot(self, shot: Shot) -> None:
        self.shots.append(shot)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "character": self.character.to_dict(),
            "shots": [s.to_dict() for s in self.shots],
            "frame_count": len(self.frames),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# --- deterministic pseudo-random from a seed (stable across runs) -----------

def _rand(seed: int, salt: str) -> float:
    h = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _frame_seed(character_seed: int, scene: int, index: int) -> int:
    return int(hashlib.sha256(f"{character_seed}:{scene}:{index}".encode()).hexdigest()[:8], 16)


def _camera_rule(shot: Shot) -> str:
    angle = CAMERA_ANGLES.get(shot.camera_angle, CAMERA_ANGLES["eye"])
    size = SHOT_SIZES.get(shot.shot_size, SHOT_SIZES["medium"])
    move = MOVEMENTS.get(shot.movement, MOVEMENTS["static"])
    return f"{angle}; {size}; {move}"


def _build_prompt(character: CharacterLock, shot: Shot) -> str:
    """The KAGE-proven time-coded, character-coated prompt structure."""
    return (
        f"[0-3s] {_camera_rule(shot)}. {shot.description}. "
        f"Character: {character.coating}. "
        f"Lighting: {shot.lighting}. Mood: {shot.mood}. "
        f"Palette: {', '.join(character.palette)}."
    )


def _render_svg(character: CharacterLock, shot: Shot, seed: int) -> str:
    """Render a deterministic SVG storyboard frame (16:9, 960x540)."""
    W, H = 960, 540
    r = _rand
    # Background gradient from palette.
    c0 = character.palette[0]
    c1 = character.palette[-1]
    # Subject silhouette position varies deterministically by shot size.
    if shot.shot_size == "close":
        cx, cy, rad = W * 0.5, H * 0.42, 150
    elif shot.shot_size == "extreme":
        cx, cy, rad = W * 0.5, H * 0.5, 90
    elif shot.shot_size == "wide":
        cx, cy, rad = W * 0.5, H * 0.55, 60
    elif shot.shot_size == "full":
        cx, cy, rad = W * 0.5, H * 0.6, 110
    elif shot.shot_size == "two":
        cx, cy, rad = W * 0.5, H * 0.55, 80
    else:  # medium
        cx, cy, rad = W * 0.5, H * 0.5, 100

    # Dutch tilt rotates the frame.
    tilt = 0.0
    if shot.camera_angle == "dutch":
        tilt = 8.0

    # Movement adds a subtle offset (dolly in = larger subject).
    scale = 1.0
    if shot.movement == "dolly":
        scale = 1.15
    elif shot.movement == "crane":
        cy -= 20

    # Deterministic "camera" grid + framing guides.
    guides = (
        f'<line x1="{W/3}" y1="0" x2="{W/3}" y2="{H}" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>'
        f'<line x1="{2*W/3}" y1="0" x2="{2*W/3}" y2="{H}" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>'
        f'<line x1="0" y1="{H/3}" x2="{W}" y2="{H/3}" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>'
        f'<line x1="0" y1="{2*H/3}" x2="{W}" y2="{2*H/3}" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>'
    )

    # Subject: layered silhouette using palette colors.
    body = (
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rad*0.55*scale:.0f}" ry="{rad*0.8*scale:.0f}" '
        f'fill="{c0}" opacity="0.9"/>'
        f'<circle cx="{cx:.0f}" cy="{cy-rad*0.7*scale:.0f}" r="{rad*0.32*scale:.0f}" fill="{c1}" opacity="0.9"/>'
    )

    # Ground line.
    ground = f'<line x1="0" y1="{H*0.85:.0f}" x2="{W}" y2="{H*0.85:.0f}" stroke="{c1}" stroke-opacity="0.4" stroke-width="2"/>'

    # Shot metadata overlay (bottom bar).
    meta = (
        f'<rect x="0" y="{H-46}" width="{W}" height="46" fill="#000000" opacity="0.75"/>'
        f'<text x="16" y="{H-20}" font-family="monospace" font-size="15" fill="#ffffff">'
        f'SC {shot.scene:02d} SHOT {shot.index:02d} | {shot.shot_size.upper()} | {shot.camera_angle.upper()} | {shot.movement.upper()}</text>'
        f'<text x="{W-16}" y="{H-20}" font-family="monospace" font-size="15" fill="#ffffff" text-anchor="end">'
        f'FrameForge v0.1 | seed {seed}</text>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{c0}"/><stop offset="100%" stop-color="{c1}"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
        f'{guides}{ground}{body}{meta}'
        f'</svg>'
    )
    return svg


def generate_frame(character: CharacterLock, shot: Shot) -> str:
    """Generate one deterministic SVG frame for a shot."""
    seed = _frame_seed(character.seed, shot.scene, shot.index)
    return _render_svg(character, shot, seed)


def build_storyboard(
    title: str,
    character: CharacterLock,
    shots: list[Shot],
) -> Storyboard:
    """Compile a full storyboard: lock character, generate every frame."""
    sb = Storyboard(title=title, character=character)
    for shot in shots:
        sb.add_shot(shot)
        sb.frames.append(generate_frame(character, shot))
    return sb


def write_storyboard(sb: Storyboard, out_dir: str) -> list[str]:
    """Write frames + manifest to disk. Returns written file paths."""
    os.makedirs(out_dir, exist_ok=True)
    written: list[str] = []
    manifest = sb.to_dict()
    manifest["prompts"] = [
        {"shot": s.to_dict(), "prompt": _build_prompt(sb.character, s)}
        for s in sb.shots
    ]
    manifest_path = os.path.join(out_dir, "storyboard.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    written.append(manifest_path)

    for i, (shot, frame) in enumerate(zip(sb.shots, sb.frames), start=1):
        fname = f"frame_{shot.scene:02d}_{shot.index:02d}.svg"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as fh:
            fh.write(frame)
        written.append(fpath)
    return written
