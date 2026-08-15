"""Tests for FrameForge character locker + storyboard engine.

Run: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.character import lock_character, load_lock
from src.engine import Shot, build_storyboard, generate_frame, write_storyboard
from src.compile import compile_video

SHEET = (
    "KAGE is a crimson-haired cyberpunk courier in a charcoal tactical jacket "
    "with steel accents. Pale skin, gold visor, navy undersuit. "
    "Moody, low-key lighting."
)


class TestCharacterLock(unittest.TestCase):
    def test_lock_is_deterministic(self):
        a = lock_character("KAGE", SHEET)
        b = lock_character("KAGE", SHEET)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.coating, b.coating)
        self.assertEqual(a.palette, b.palette)

    def test_palette_extracted_from_sheet(self):
        lock = lock_character("KAGE", SHEET)
        # crimson, charcoal, steel, gold, navy should all be present
        self.assertIn("#8e1a1a", lock.palette)   # crimson
        self.assertIn("#2b2b2b", lock.palette)   # charcoal
        self.assertIn("#4682b4", lock.palette)   # steel
        self.assertIn("#c9a227", lock.palette)   # gold
        self.assertIn("#1a2a4a", lock.palette)   # navy

    def test_empty_sheet_raises(self):
        with self.assertRaises(ValueError):
            lock_character("X", "   ")

    def test_roundtrip_json(self):
        lock = lock_character("KAGE", SHEET)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "lock.json")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(lock.to_json())
            loaded = load_lock(p)
        self.assertEqual(loaded.seed, lock.seed)
        self.assertEqual(loaded.coating, lock.coating)
        self.assertEqual(loaded.palette, lock.palette)


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.character = lock_character("KAGE", SHEET)

    def test_frame_is_deterministic(self):
        shot = Shot(scene=1, index=1, description="KAGE runs across a neon rooftop")
        f1 = generate_frame(self.character, shot)
        f2 = generate_frame(self.character, shot)
        self.assertEqual(f1, f2)

    def test_frame_is_svg(self):
        shot = Shot(scene=1, index=1, description="test")
        frame = generate_frame(self.character, shot)
        self.assertTrue(frame.startswith("<svg"))
        self.assertIn("</svg>", frame)
        self.assertIn("SC 01 SHOT 01", frame)

    def test_camera_angle_changes_frame(self):
        a = generate_frame(self.character, Shot(1, 1, "x", camera_angle="eye"))
        b = generate_frame(self.character, Shot(1, 1, "x", camera_angle="dutch"))
        self.assertNotEqual(a, b)

    def test_shot_size_changes_frame(self):
        a = generate_frame(self.character, Shot(1, 1, "x", shot_size="close"))
        b = generate_frame(self.character, Shot(1, 1, "x", shot_size="wide"))
        self.assertNotEqual(a, b)

    def test_build_storyboard(self):
        shots = [
            Shot(1, 1, "KAGE enters the alley", camera_angle="low", shot_size="wide"),
            Shot(1, 2, "KAGE draws her blade", camera_angle="eye", shot_size="medium"),
            Shot(2, 1, "The drone closes in", camera_angle="high", shot_size="close"),
        ]
        sb = build_storyboard("Neon Run", self.character, shots)
        self.assertEqual(len(sb.frames), 3)
        self.assertEqual(len(sb.shots), 3)
        self.assertEqual(sb.to_dict()["frame_count"], 3)

    def test_write_storyboard(self):
        shots = [Shot(1, 1, "test frame")]
        sb = build_storyboard("T", self.character, shots)
        with tempfile.TemporaryDirectory() as d:
            written = write_storyboard(sb, d)
            self.assertEqual(len(written), 2)  # manifest + 1 frame
            self.assertTrue(os.path.exists(os.path.join(d, "storyboard.json")))
            self.assertTrue(os.path.exists(os.path.join(d, "frame_01_01.svg")))
            with open(os.path.join(d, "storyboard.json"), encoding="utf-8") as mf:
                manifest = json.load(mf)
            self.assertEqual(manifest["frame_count"], 1)
            self.assertIn("prompts", manifest)
            self.assertIn("prompt", manifest["prompts"][0])

    def test_compile_video(self):
        shots = [Shot(1, 1, "test frame"), Shot(1, 2, "second frame")]
        sb = build_storyboard("T", self.character, shots)
        with tempfile.TemporaryDirectory() as d:
            write_storyboard(sb, d)
            out = os.path.join(d, "out.mp4")
            compile_video(d, out, title="Test")
            self.assertTrue(os.path.exists(out))
            self.assertGreater(os.path.getsize(out), 1000)  # real MP4, not empty
            # Verify it's a valid MP4 via ffprobe.
            import subprocess
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", out],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0)
            self.assertGreater(float(r.stdout.strip()), 0)


if __name__ == "__main__":
    unittest.main()
