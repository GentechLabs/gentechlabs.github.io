"""
RomM AI Companion — Screen Capture Module
Captures EmulatorJS canvas frames for vision analysis.
Supports: browser automation (Playwright), file-based screenshots, and simulated frames for testing.
"""

import json, os, time, base64, io
from dataclasses import dataclass, field
from typing import Optional, Callable
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

@dataclass
class GameFrame:
    """A single captured game frame with metadata."""
    timestamp: float
    frame_id: str
    width: int
    height: int
    image_data: bytes  # PNG bytes
    game: str = "unknown"
    source: str = "unknown"  # "browser", "file", "simulated"

    @property
    def as_base64(self) -> str:
        return base64.b64encode(self.image_data).decode()

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "frame_id": self.frame_id,
            "width": self.width,
            "height": self.height,
            "game": self.game,
            "source": self.source,
            "image_size_kb": round(len(self.image_data) / 1024, 1),
        }


@dataclass
class CaptureConfig:
    """Configuration for the screen capture pipeline."""
    fps: int = 4  # Frames per second (4 is enough for game state analysis)
    max_frames: int = 100  # Max frames to keep in buffer
    output_dir: str = "captures"
    browser_url: str = "http://localhost:8080"  # RomM/EmulatorJS URL
    screenshot_selector: str = "canvas"  # CSS selector for game canvas


# ──────────────────────────────────────────────
#  Frame Buffer
# ──────────────────────────────────────────────

class FrameBuffer:
    """Ring buffer for game frames. Keeps the last N frames."""

    def __init__(self, max_frames: int = 100):
        self.max_frames = max_frames
        self._frames: list[GameFrame] = []
        self._frame_count = 0

    def add(self, frame: GameFrame):
        self._frames.append(frame)
        self._frame_count += 1
        if len(self._frames) > self.max_frames:
            self._frames.pop(0)

    def latest(self) -> Optional[GameFrame]:
        return self._frames[-1] if self._frames else None

    def recent(self, n: int = 5) -> list[GameFrame]:
        return self._frames[-n:]

    def clear(self):
        self._frames.clear()

    @property
    def count(self) -> int:
        return self._frame_count

    @property
    def size(self) -> int:
        return len(self._frames)


# ──────────────────────────────────────────────
#  Capturers
# ──────────────────────────────────────────────

class SimulatedCapturer:
    """Generates simulated frames for testing without a real browser."""

    def __init__(self, width: int = 256, height: int = 240):
        self.width = width
        self.height = height
        self._frame_num = 0

    def capture(self) -> GameFrame:
        """Generate a minimal simulated frame (small PNG)."""
        self._frame_num += 1
        # Create a minimal valid PNG (1x1 pixel)
        # PNG header + IHDR + IDAT + IEND
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47,  # PNG signature
            0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D,  # IHDR chunk
            0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01,  # width=1
            0x00, 0x00, 0x00, 0x01,  # height=1
            0x08, 0x02, 0x00, 0x00,  # 8-bit grayscale
            0x00, 0x90, 0x77, 0x53,
            0xDE,
            0x00, 0x00, 0x00, 0x0C,  # IDAT chunk
            0x49, 0x44, 0x41, 0x54,
            0x08, 0xD7, 0x63, 0x60, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0xE5, 0x27,
            0xDE, 0xFC,
            0x00, 0x00, 0x00, 0x00,  # IEND chunk
            0x49, 0x45, 0x4E, 0x44,
            0xAE, 0x42, 0x60, 0x82,
        ])
        return GameFrame(
            timestamp=time.time(),
            frame_id=f"sim_{self._frame_num:06d}",
            width=self.width,
            height=self.height,
            image_data=png_bytes,
            game="test",
            source="simulated",
        )


class FileCapturer:
    """Loads pre-captured screenshots from disk for testing."""

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self._files = sorted(self.directory.glob("*.png"))
        self._index = 0

    def capture(self) -> Optional[GameFrame]:
        if self._index >= len(self._files):
            return None
        path = self._files[self._index]
        self._index += 1
        data = path.read_bytes()
        return GameFrame(
            timestamp=time.time(),
            frame_id=path.stem,
            width=0,  # unknown until decoded
            height=0,
            image_data=data,
            game=path.parent.name,
            source="file",
        )


# ──────────────────────────────────────────────
#  Capture Pipeline
# ──────────────────────────────────────────────

class CapturePipeline:
    """Orchestrates frame capture at a configurable rate."""

    def __init__(self, config: CaptureConfig = None):
        self.config = config or CaptureConfig()
        self.buffer = FrameBuffer(self.config.max_frames)
        self._capturer = SimulatedCapturer()  # Default: simulated
        self._running = False

    def set_capturer(self, capturer):
        """Set the active capturer (simulated, file, or browser)."""
        self._capturer = capturer

    def capture_frame(self) -> Optional[GameFrame]:
        """Capture a single frame and add to buffer."""
        try:
            frame = self._capturer.capture()
            if frame:
                self.buffer.add(frame)
            return frame
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def capture_burst(self, count: int = 10, interval: float = 0.25) -> list[GameFrame]:
        """Capture multiple frames at a fixed interval."""
        frames = []
        for _ in range(count):
            frame = self.capture_frame()
            if frame:
                frames.append(frame)
            time.sleep(interval)
        return frames

    def save_frame(self, frame: GameFrame, path: str = None) -> str:
        """Save a frame to disk."""
        if not path:
            os.makedirs(self.config.output_dir, exist_ok=True)
            path = os.path.join(self.config.output_dir, f"{frame.frame_id}.png")
        with open(path, "wb") as f:
            f.write(frame.image_data)
        return path


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RomM Screen Capture")
    parser.add_argument("action", choices=["capture", "burst", "info"])
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=0.25)
    args = parser.parse_args()

    pipeline = CapturePipeline()

    if args.action == "capture":
        frame = pipeline.capture_frame()
        print(f"Captured: {frame.frame_id} ({frame.width}x{frame.height})")

    elif args.action == "burst":
        frames = pipeline.capture_burst(args.count, args.interval)
        print(f"Captured {len(frames)} frames:")
        for f in frames:
            print(f"  {f.frame_id}: {f.width}x{f.height} from {f.source}")

    elif args.action == "info":
        print(f"Buffer: {pipeline.buffer.size}/{pipeline.config.max_frames}")
        print(f"Total captured: {pipeline.buffer.count}")
