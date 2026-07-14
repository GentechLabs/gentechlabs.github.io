"""
RomM AI Companion — Unified Agent
Ties together screen capture, vision analysis, decision engine, and input emulation.
"""

import json, os, sys, time, threading
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from screen_capture import CapturePipeline, CaptureConfig, SimulatedCapturer, FrameBuffer
from vision_analysis import VisionAnalyzer, VisionConfig, StateTracker, GameState
from decision_engine import DecisionEngine, Decision, PlayStyle
from input_emulation import InputController, SimulatedEmitter, InputSequence, GameButton


# ──────────────────────────────────────────────
#  Agent
# ──────────────────────────────────────────────

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class AgentConfig:
    fps: int = 4
    style: PlayStyle = PlayStyle.BALANCED
    max_loops: int = 0  # 0 = unlimited
    verbose: bool = True


class AICompanion:
    """The main AI Companion agent that plays games alongside humans."""

    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.status = AgentStatus.IDLE

        # Subsystems
        self.capture = CapturePipeline(CaptureConfig(fps=self.config.fps))
        self.vision = VisionAnalyzer()
        self.tracker = StateTracker()
        self.decision = DecisionEngine(style=self.config.style)
        self.input = InputController(SimulatedEmitter())

        # Stats
        self.loops = 0
        self.decisions_made = 0
        self.frames_processed = 0
        self._start_time = 0.0

    def start(self):
        """Start the game loop."""
        self.status = AgentStatus.RUNNING
        self._start_time = time.time()
        self.loops = 0

        if self.config.verbose:
            print(f"🤖 AI Companion started ({self.config.style.value} style)")
            print(f"   FPS: {self.config.fps}, Max loops: {self.config.max_loops or 'unlimited'}")

        try:
            while self.status == AgentStatus.RUNNING:
                if self.config.max_loops and self.loops >= self.config.max_loops:
                    self.stop()
                    break

                self._tick()
                self.loops += 1
                time.sleep(1.0 / self.config.fps)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the game loop."""
        self.status = AgentStatus.STOPPED
        elapsed = time.time() - self._start_time
        if self.config.verbose:
            print(f"\n⏹ AI Companion stopped")
            print(f"   Loops: {self.loops}, Frames: {self.frames_processed}")
            print(f"   Decisions: {self.decisions_made}")
            print(f"   Runtime: {elapsed:.1f}s")

    def pause(self):
        self.status = AgentStatus.PAUSED

    def resume(self):
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.RUNNING

    def _tick(self):
        """One game loop tick: capture → analyze → decide → act."""
        # 1. Capture frame
        frame = self.capture.capture_frame()
        if not frame:
            return
        self.frames_processed += 1

        # 2. Analyze with vision
        state = self.vision.analyze_from_bytes(frame.image_data, frame.frame_id)
        self.tracker.update(state)

        # 3. Decide
        decision = self.decision.decide(state, self.tracker)
        self.decisions_made += 1

        # 4. Act
        self.decision.execute_decision(decision, self.input)

        if self.config.verbose and self.loops % 10 == 0:
            s = self.tracker.summary()
            print(f"  [{self.loops}] {decision.action:8s} → {str(decision.direction or '-'):6s} "
                  f"| health={s.get('health', '?'):<5} score={s.get('score', '?')}")

    def summary(self) -> dict:
        return {
            "status": self.status.value,
            "style": self.config.style.value,
            "loops": self.loops,
            "frames": self.frames_processed,
            "decisions": self.decisions_made,
            "runtime": time.time() - self._start_time if self._start_time else 0,
            "game_state": self.tracker.summary(),
        }


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RomM AI Companion")
    parser.add_argument("action", choices=["run", "test", "status"])
    parser.add_argument("--style", default="balanced", choices=["aggressive", "defensive", "balanced", "follower", "explorer"])
    parser.add_argument("--loops", type=int, default=20)
    parser.add_argument("--fps", type=int, default=4)
    args = parser.parse_args()

    config = AgentConfig(
        fps=args.fps,
        style=PlayStyle(args.style),
        max_loops=args.loops,
        verbose=True,
    )

    agent = AICompanion(config)

    if args.action == "run":
        agent.start()
        print(f"\nFinal: {json.dumps(agent.summary(), indent=2)}")

    elif args.action == "test":
        print("Testing all subsystems...")
        # Capture
        frame = agent.capture.capture_frame()
        print(f"  Capture: {frame.frame_id} ({frame.width}x{frame.height}) ✅")
        # Vision
        state = agent.vision.analyze_from_bytes(frame.image_data, frame.frame_id)
        print(f"  Vision: health={state.health:.2f}, score={state.score} ✅")
        # Decision
        decision = agent.decision.decide(state, agent.tracker)
        print(f"  Decision: {decision.action} → {decision.direction} (pri={decision.priority}) ✅")
        # Input
        agent.decision.execute_decision(decision, agent.input)
        print(f"  Input: executed ✅")
        print(f"\nAll subsystems OK")

    elif args.action == "status":
        print(json.dumps(agent.summary(), indent=2))
