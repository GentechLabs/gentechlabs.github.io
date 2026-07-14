"""
RomM AI Companion — Decision Engine
Maps game state to input actions. Simple rule-based system.
"""

import json, time, random
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum

from vision_analysis import GameState, StateTracker, GameGenre
from input_emulation import InputController, InputSequence, GameButton, Macros


# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

class PlayStyle(Enum):
    """AI companion play styles."""
    AGGRESSIVE = "aggressive"     # Attack first, ask later
    DEFENSIVE = "defensive"       # Stay back, support player
    BALANCED = "balanced"         # Mix of both
    FOLLOWER = "follower"         # Follow the player
    EXPLORER = "explorer"         # Explore independently


@dataclass
class Decision:
    """A decision made by the AI."""
    action: str  # "move", "jump", "attack", "wait", "dodge", "collect"
    direction: Optional[str] = None  # "left", "right", "up", "down"
    priority: int = 5  # 1-10 (higher = more urgent)
    reason: str = ""
    duration: float = 0.3
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


# ──────────────────────────────────────────────
#  Decision Engine
# ──────────────────────────────────────────────

class DecisionEngine:
    """Maps game state to input decisions."""

    def __init__(self, style: PlayStyle = PlayStyle.BALANCED):
        self.style = style
        self._last_decision: Optional[Decision] = None
        self._decision_count = 0

    def decide(self, state: GameState, tracker: StateTracker) -> Decision:
        """Make a decision based on current game state."""
        self._decision_count += 1

        # Priority 10: Danger — dodge or heal
        if tracker.is_in_danger():
            d = Decision(
                action="dodge",
                direction=random.choice(["left", "right"]),
                priority=10,
                reason="Low health, retreating",
            )
            self._last_decision = d
            return d

        # Priority 9: Game over — wait for restart
        if state.is_game_over:
            d = Decision(action="wait", priority=9, reason="Game over")
            self._last_decision = d
            return d

        # Priority 8: Paused — wait
        if state.is_paused:
            d = Decision(action="wait", priority=8, reason="Game paused")
            self._last_decision = d
            return d

        # Priority 7: Enemies nearby — attack or dodge
        if state.enemies_visible > 0:
            if self.style == PlayStyle.AGGRESSIVE:
                d = Decision(
                    action="attack",
                    direction="right",
                    priority=7,
                    reason=f"Attacking {state.enemies_visible} enemies",
                )
            elif self.style == PlayStyle.DEFENSIVE:
                d = Decision(
                    action="dodge",
                    direction="left",
                    priority=7,
                    reason="Enemies nearby, backing off",
                )
            else:
                d = Decision(
                    action="jump",
                    direction="right",
                    priority=7,
                    reason=f"Jumping over {state.enemies_visible} enemies",
                )
            self._last_decision = d
            return d

        # Priority 5: Items visible — collect
        if state.items_visible > 0:
            d = Decision(
                action="collect",
                direction="right",
                priority=5,
                reason=f"Collecting {state.items_visible} items",
            )
            self._last_decision = d
            return d

        # Priority 3: Default — move right (progress)
        if self.style == PlayStyle.FOLLOWER:
            d = Decision(action="wait", priority=3, reason="Following player")
        elif self.style == PlayStyle.EXPLORER:
            d = Decision(
                action="move",
                direction=random.choice(["left", "right", "up", "down"]),
                priority=3,
                reason="Exploring",
            )
        else:
            d = Decision(
                action="move",
                direction="right",
                priority=3,
                reason="Moving forward",
            )
        self._last_decision = d
        return d

    def execute_decision(self, decision: Decision, controller: InputController):
        """Execute a decision using the input controller."""
        if decision.action == "move" and decision.direction:
            controller.move(decision.direction, decision.duration)
        elif decision.action == "jump":
            controller.jump()
        elif decision.action == "attack":
            controller.attack()
        elif decision.action == "jump_attack":
            controller.jump_attack()
        elif decision.action == "dodge":
            controller.move(decision.direction or "left", 0.4)
        elif decision.action == "collect":
            controller.move("right", 0.3)
            controller.jump()
        elif decision.action == "wait":
            time.sleep(decision.duration)


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RomM Decision Engine")
    parser.add_argument("action", choices=["decide", "loop"])
    parser.add_argument("--style", default="balanced", choices=["aggressive", "defensive", "balanced", "follower", "explorer"])
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    style = PlayStyle(args.style)
    engine = DecisionEngine(style)
    tracker = StateTracker()
    from vision_analysis import VisionAnalyzer
    analyzer = VisionAnalyzer()

    if args.action == "decide":
        state = analyzer._simulate_analysis("frame_0000")
        tracker.update(state)
        decision = engine.decide(state, tracker)
        print(f"Decision: {decision.action} → {decision.direction or '-'} "
              f"(priority {decision.priority})")
        print(f"Reason: {decision.reason}")

    elif args.action == "loop":
        print(f"Running {args.count} decision cycles ({args.style} style):")
        for i in range(args.count):
            state = analyzer._simulate_analysis(f"frame_{i:04d}")
            tracker.update(state)
            decision = engine.decide(state, tracker)
            print(f"  [{i+1}] {decision.action:8s} → {str(decision.direction or '-'):6s} "
                  f"pri={decision.priority} | {decision.reason}")
            time.sleep(0.1)
