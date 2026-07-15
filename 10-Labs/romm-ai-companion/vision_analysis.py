"""
RomM AI Companion — Vision Analysis Module
Analyzes game screenshots using vision models to extract game state.
Supports: qwen3-vl (Ollama Cloud), simulated analysis for testing.
"""

import json, os, base64, time, re
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum

# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

class GameGenre(Enum):
    ACTION = "action"
    PLATFORMER = "platformer"
    RPG = "rpg"
    FIGHTING = "fighting"
    RACING = "racing"
    PUZZLE = "puzzle"
    SHOOTER = "shooter"
    SPORTS = "sports"
    UNKNOWN = "unknown"


@dataclass
class GameState:
    """Parsed game state from a screenshot."""
    frame_id: str
    timestamp: float
    game: str = "unknown"
    genre: GameGenre = GameGenre.UNKNOWN

    # Common game state fields
    health: Optional[float] = None       # 0.0 - 1.0
    score: Optional[int] = None
    lives: Optional[int] = None
    level: Optional[str] = None
    position: Optional[dict] = None      # {"x": ..., "y": ...}
    enemies_visible: int = 0
    items_visible: int = 0
    is_paused: bool = False
    is_game_over: bool = False
    is_loading: bool = False

    # Raw analysis
    raw_description: str = ""
    detected_objects: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 - 1.0

    def to_dict(self) -> dict:
        return {
            "frame_id": self.frame_id,
            "game": self.game,
            "genre": self.genre.value,
            "health": self.health,
            "score": self.score,
            "lives": self.lives,
            "level": self.level,
            "position": self.position,
            "enemies_visible": self.enemies_visible,
            "items_visible": self.items_visible,
            "is_paused": self.is_paused,
            "is_game_over": self.is_game_over,
            "is_loading": self.is_loading,
            "detected_objects": self.detected_objects,
            "confidence": self.confidence,
        }


@dataclass
class VisionConfig:
    """Configuration for vision analysis."""
    model: str = "gemma4:31b"
    provider: str = "ollama-cloud"
    api_url: str = "https://ollama.com/v1"
    verbose: bool = False
    prompt_template: str = (
        "You are analyzing a retro game screenshot. "
        "Extract the following game state as JSON:\n"
        "- health: player health as 0.0-1.0 (null if not visible)\n"
        "- score: current score as integer (null if not visible)\n"
        "- lives: remaining lives (null if not visible)\n"
        "- level: level/round name (null if not visible)\n"
        "- enemies_visible: number of enemies on screen\n"
        "- items_visible: number of collectible items\n"
        "- is_paused: true if game is paused\n"
        "- is_game_over: true if game over screen\n"
        "- is_loading: true if loading screen\n"
        "- detected_objects: list of visible game objects\n"
        "- genre: game genre (action, platformer, rpg, fighting, racing, puzzle, shooter, sports)\n"
        "- description: one sentence describing what's happening\n"
        "\nRespond with ONLY valid JSON, no markdown."
    )


# ──────────────────────────────────────────────
#  Vision Analyzer
# ──────────────────────────────────────────────

class VisionAnalyzer:
    """Analyzes game screenshots using vision models."""

    def __init__(self, config: VisionConfig = None):
        self.config = config or VisionConfig()

    def analyze(self, image_base64: str, frame_id: str = "unknown") -> GameState:
        """Analyze a screenshot using the vision model, fall back to simulated."""
        if not os.environ.get("OLLAMA_API_KEY"):
            return self._simulate_analysis(frame_id)
        try:
            return self._call_vision_api(image_base64, frame_id)
        except Exception as e:
            if self.config.verbose:
                print(f"  ⚠️ Vision API failed ({e}), using simulated analysis")
            return self._simulate_analysis(frame_id)

    def analyze_from_bytes(self, image_data: bytes, frame_id: str = "unknown") -> GameState:
        """Analyze from raw PNG bytes."""
        b64 = base64.b64encode(image_data).decode()
        return self.analyze(b64, frame_id)

    def _call_vision_api(self, image_base64: str, frame_id: str) -> GameState:
        """Call the Ollama Cloud vision API with the screenshot."""
        import urllib.request, urllib.error

        api_key = os.environ.get("OLLAMA_API_KEY", "")
        if not api_key:
            raise ValueError("OLLAMA_API_KEY not set")

        data_url = f"data:image/png;base64,{image_base64}"
        payload = {
            "model": self.config.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": self.config.prompt_template},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }],
            "stream": False,
        }

        req = urllib.request.Request(
            f"{self.config.api_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        text = result["choices"][0]["message"]["content"]
        return self._parse_llm_response(text, frame_id)

    def _simulate_analysis(self, frame_id: str) -> GameState:
        """Simulated analysis for testing without a vision model."""
        import random
        return GameState(
            frame_id=frame_id,
            timestamp=time.time(),
            game="test_game",
            genre=random.choice(list(GameGenre)),
            health=random.uniform(0.3, 1.0),
            score=random.randint(0, 99999),
            lives=random.randint(0, 5),
            level=f"Level {random.randint(1, 8)}",
            enemies_visible=random.randint(0, 8),
            items_visible=random.randint(0, 3),
            is_paused=False,
            is_game_over=False,
            is_loading=False,
            detected_objects=["player", "enemy", "platform"],
            confidence=random.uniform(0.7, 0.95),
            raw_description="Player is moving right, enemies ahead.",
        )

    def _parse_llm_response(self, text: str, frame_id: str) -> GameState:
        """Parse LLM JSON response into GameState."""
        # Strip markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return GameState(
                frame_id=frame_id,
                timestamp=time.time(),
                raw_description=text,
                confidence=0.0,
            )

        genre = GameGenre.UNKNOWN
        try:
            genre = GameGenre(data.get("genre", "unknown"))
        except ValueError:
            pass

        return GameState(
            frame_id=frame_id,
            timestamp=time.time(),
            game=data.get("game", "unknown"),
            genre=genre,
            health=data.get("health"),
            score=data.get("score"),
            lives=data.get("lives"),
            level=data.get("level"),
            position=data.get("position"),
            enemies_visible=data.get("enemies_visible", 0),
            items_visible=data.get("items_visible", 0),
            is_paused=data.get("is_paused", False),
            is_game_over=data.get("is_game_over", False),
            is_loading=data.get("is_loading", False),
            detected_objects=data.get("detected_objects", []),
            confidence=data.get("confidence", 0.5),
            raw_description=data.get("description", ""),
        )


# ──────────────────────────────────────────────
#  State Tracker
# ──────────────────────────────────────────────

class StateTracker:
    """Tracks game state over time for trend analysis."""

    def __init__(self, window: int = 30):
        self.window = window
        self._states: list[GameState] = []

    def update(self, state: GameState):
        self._states.append(state)
        if len(self._states) > self.window:
            self._states.pop(0)

    def latest(self) -> Optional[GameState]:
        return self._states[-1] if self._states else None

    def health_trend(self) -> str:
        """Return health trend: 'improving', 'declining', 'stable'."""
        if len(self._states) < 3:
            return "stable"
        recent = [s.health for s in self._states[-3:] if s.health is not None]
        if len(recent) < 2:
            return "stable"
        if recent[-1] > recent[0] + 0.1:
            return "improving"
        elif recent[-1] < recent[0] - 0.1:
            return "declining"
        return "stable"

    def is_in_danger(self) -> bool:
        """Check if player is in danger (low health + declining)."""
        latest = self.latest()
        if not latest or latest.health is None:
            return False
        return latest.health < 0.3 and self.health_trend() == "declining"

    def summary(self) -> dict:
        """Get a summary of recent game state."""
        latest = self.latest()
        if not latest:
            return {"status": "no_data"}
        return {
            "status": "active",
            "game": latest.game,
            "health": latest.health,
            "score": latest.score,
            "lives": latest.lives,
            "level": latest.level,
            "health_trend": self.health_trend(),
            "in_danger": self.is_in_danger(),
            "enemies_visible": latest.enemies_visible,
            "frames_analyzed": len(self._states),
        }


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RomM Vision Analysis")
    parser.add_argument("action", choices=["analyze", "track", "simulate"])
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    if args.action == "analyze" or args.action == "simulate":
        analyzer = VisionAnalyzer()
        for i in range(args.count):
            state = analyzer._simulate_analysis(f"frame_{i:04d}")
            print(f"Frame {i}: health={state.health:.2f}, score={state.score}, "
                  f"enemies={state.enemies_visible}, genre={state.genre.value}")

    elif args.action == "track":
        tracker = StateTracker()
        analyzer = VisionAnalyzer()
        for i in range(10):
            state = analyzer._simulate_analysis(f"frame_{i:04d}")
            tracker.update(state)
        s = tracker.summary()
        print(f"Summary: {s['status']}, health={s['health']}, "
              f"trend={s['health_trend']}, danger={s['in_danger']}")
