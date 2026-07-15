"""
RomM AI Companion — Input Emulation Module
Emulates gamepad/keyboard inputs for EmulatorJS.
Supports: simulated inputs (testing), browser automation (Playwright), direct gamepad API.
"""

import json, time, threading
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum

# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

class GameButton(Enum):
    """Standard retro gamepad buttons."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    START = "start"
    SELECT = "select"
    L = "l"  # Left shoulder
    R = "r"  # Right shoulder


@dataclass
class InputAction:
    """A single input action."""
    button: GameButton
    pressed: bool  # True = press, False = release
    duration: float = 0.1  # seconds to hold
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class InputSequence:
    """A sequence of input actions (a macro)."""
    actions: list[InputAction] = field(default_factory=list)
    name: str = "unnamed"

    def add(self, button: GameButton, duration: float = 0.1):
        self.actions.append(InputAction(button=button, pressed=True, duration=duration))
        self.actions.append(InputAction(button=button, pressed=False, duration=0.05))

    def add_hold(self, button: GameButton, duration: float = 0.5):
        self.actions.append(InputAction(button=button, pressed=True, duration=duration))
        self.actions.append(InputAction(button=button, pressed=False, duration=0.05))

    def add_wait(self, seconds: float = 0.5):
        self.actions.append(InputAction(button=GameButton.START, pressed=False, duration=seconds))

    @property
    def total_duration(self) -> float:
        return sum(a.duration for a in self.actions)


# ──────────────────────────────────────────────
#  Common Input Sequences (Macros)
# ──────────────────────────────────────────────

class Macros:
    """Pre-built input sequences for common game actions."""

    @staticmethod
    def jump() -> InputSequence:
        s = InputSequence(name="jump")
        s.add(GameButton.A, 0.15)
        return s

    @staticmethod
    def attack() -> InputSequence:
        s = InputSequence(name="attack")
        s.add(GameButton.B, 0.1)
        return s

    @staticmethod
    def move_right(duration: float = 0.5) -> InputSequence:
        s = InputSequence(name="move_right")
        s.add_hold(GameButton.RIGHT, duration)
        return s

    @staticmethod
    def move_left(duration: float = 0.5) -> InputSequence:
        s = InputSequence(name="move_left")
        s.add_hold(GameButton.LEFT, duration)
        return s

    @staticmethod
    def move_up(duration: float = 0.3) -> InputSequence:
        s = InputSequence(name="move_up")
        s.add_hold(GameButton.UP, duration)
        return s

    @staticmethod
    def move_down(duration: float = 0.3) -> InputSequence:
        s = InputSequence(name="move_down")
        s.add_hold(GameButton.DOWN, duration)
        return s

    @staticmethod
    def jump_and_attack() -> InputSequence:
        s = InputSequence(name="jump_attack")
        s.add(GameButton.A, 0.1)
        s.add(GameButton.B, 0.1)
        return s

    @staticmethod
    def dash_right() -> InputSequence:
        s = InputSequence(name="dash_right")
        s.add_hold(GameButton.RIGHT, 0.3)
        s.add(GameButton.B, 0.1)
        s.add_hold(GameButton.RIGHT, 0.3)
        return s

    @staticmethod
    def pause() -> InputSequence:
        s = InputSequence(name="pause")
        s.add(GameButton.START, 0.1)
        return s

    @staticmethod
    def confirm() -> InputSequence:
        s = InputSequence(name="confirm")
        s.add(GameButton.A, 0.15)
        return s

    @staticmethod
    def cancel() -> InputSequence:
        s = InputSequence(name="cancel")
        s.add(GameButton.B, 0.1)
        return s


# ──────────────────────────────────────────────
#  Input Emitters
# ──────────────────────────────────────────────

class InputEmitter:
    """Base class for input emitters."""

    def press(self, button: GameButton):
        raise NotImplementedError

    def release(self, button: GameButton):
        raise NotImplementedError

    def tap(self, button: GameButton, duration: float = 0.1):
        self.press(button)
        time.sleep(duration)
        self.release(button)

    def execute(self, sequence: InputSequence):
        """Execute a full input sequence."""
        for action in sequence.actions:
            if action.pressed:
                self.press(action.button)
            else:
                self.release(action.button)
            time.sleep(action.duration)


class SimulatedEmitter(InputEmitter):
    """Simulated input emitter for testing — just logs."""

    def __init__(self):
        self.history: list[InputAction] = []

    def press(self, button: GameButton):
        self.history.append(InputAction(button=button, pressed=True))
        print(f"  [SIM] Press {button.value}")

    def release(self, button: GameButton):
        self.history.append(InputAction(button=button, pressed=False))
        print(f"  [SIM] Release {button.value}")

    def last_n_actions(self, n: int = 10) -> list[InputAction]:
        return self.history[-n:]


class KeyboardEmitter(InputEmitter):
    """Emits keyboard inputs for EmulatorJS via browser automation."""

    KEY_MAP = {
        GameButton.UP: "ArrowUp",
        GameButton.DOWN: "ArrowDown",
        GameButton.LEFT: "ArrowLeft",
        GameButton.RIGHT: "ArrowRight",
        GameButton.A: "KeyZ",       # Z = A button (common mapping)
        GameButton.B: "KeyX",       # X = B button
        GameButton.X: "KeyA",       # A = X button
        GameButton.Y: "KeyS",       # S = Y button
        GameButton.START: "Enter",
        GameButton.SELECT: "ShiftRight",
        GameButton.L: "KeyQ",
        GameButton.R: "KeyW",
    }

    def __init__(self, page=None):
        self.page = page  # Playwright page object
        self._pressed_keys: set[str] = set()

    def press(self, button: GameButton):
        key = self.KEY_MAP.get(button)
        if not key:
            return
        if self.page:
            # Would use: self.page.keyboard.down(key)
            pass
        self._pressed_keys.add(key)

    def release(self, button: GameButton):
        key = self.KEY_MAP.get(button)
        if not key:
            return
        if self.page:
            # Would use: self.page.keyboard.up(key)
            pass
        self._pressed_keys.discard(key)


# ──────────────────────────────────────────────
#  Input Controller
# ──────────────────────────────────────────────

class InputController:
    """High-level input controller that combines emitters and macros."""

    def __init__(self, emitter: InputEmitter = None):
        self.emitter = emitter or SimulatedEmitter()
        self.macros = Macros()

    def jump(self):
        self.emitter.execute(self.macros.jump())

    def attack(self):
        self.emitter.execute(self.macros.attack())

    def move(self, direction: str, duration: float = 0.5):
        if direction == "right":
            self.emitter.execute(self.macros.move_right(duration))
        elif direction == "left":
            self.emitter.execute(self.macros.move_left(duration))
        elif direction == "up":
            self.emitter.execute(self.macros.move_up(duration))
        elif direction == "down":
            self.emitter.execute(self.macros.move_down(duration))

    def jump_attack(self):
        self.emitter.execute(self.macros.jump_and_attack())

    def dash_right(self):
        self.emitter.execute(self.macros.dash_right())

    def pause(self):
        self.emitter.execute(self.macros.pause())

    def confirm(self):
        self.emitter.execute(self.macros.confirm())

    def execute(self, sequence: InputSequence):
        self.emitter.execute(sequence)


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RomM Input Emulation")
    parser.add_argument("action", choices=["test", "macro", "sequence"])
    parser.add_argument("--macro", default="jump", help="Macro name")
    args = parser.parse_args()

    controller = InputController(SimulatedEmitter())

    if args.action == "test":
        print("Testing basic inputs:")
        controller.jump()
        controller.attack()
        controller.move("right", 0.3)
        controller.jump_attack()

    elif args.action == "macro":
        print(f"Executing macro: {args.macro}")
        macro_fn = getattr(controller.macros, args.macro, None)
        if macro_fn:
            controller.execute(macro_fn())
        else:
            print(f"Unknown macro: {args.macro}")
            print(f"Available: jump, attack, jump_attack, dash_right, pause, confirm, cancel")

    elif args.action == "sequence":
        seq = InputSequence(name="custom")
        seq.add(GameButton.RIGHT, 0.3)
        seq.add(GameButton.A, 0.1)
        seq.add(GameButton.RIGHT, 0.2)
        seq.add(GameButton.B, 0.1)
        print(f"Executing custom sequence ({seq.total_duration:.1f}s):")
        controller.execute(seq)
