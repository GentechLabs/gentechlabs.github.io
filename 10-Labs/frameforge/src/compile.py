"""Compile pipeline: storyboard frames -> animated video via ffmpeg concat.

Turns the deterministic SVG frames into a playable MP4 with title overlay.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Optional


def _svg_to_png(svg_path: str, png_path: str) -> None:
    """Convert one SVG to PNG using ffmpeg (no external rasterizer needed)."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", svg_path, png_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def compile_video(
    frame_dir: str,
    out_path: str,
    title: str = "FrameForge Storyboard",
    fps: int = 1,
) -> str:
    """Concat all frame_*.svg in frame_dir into an MP4. Returns out_path."""
    frames = sorted(
        f for f in os.listdir(frame_dir)
        if f.startswith("frame_") and f.endswith(".svg")
    )
    if not frames:
        raise FileNotFoundError(f"No frame_*.svg files in {frame_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        pngs = []
        for i, f in enumerate(frames):
            png = os.path.join(tmp, f"f{i:03d}.png")
            _svg_to_png(os.path.join(frame_dir, f), png)
            pngs.append(png)

        # Use the image2 sequence demuxer with a glob pattern. The concat
        # demuxer produces broken DTS/PTS for ffmpeg-generated PNGs, so we
        # feed the numbered sequence directly with an explicit framerate.
        pattern = os.path.join(tmp, "f%03d.png")
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(fps), "-i", pattern,
            "-vf", f"drawtext=text='{title}':fontsize=28:fontcolor=white:"
                   f"x=(w-text_w)/2:y=h-60:box=1:boxcolor=black@0.6:boxborderw=8",
            "-pix_fmt", "yuv420p", out_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    return out_path
