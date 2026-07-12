"""
RomM AI Companion — Windows Input Module
Sends keyboard/gamepad inputs to RetroArch using Win32 SendInput API.
No browser automation needed — direct keypresses to the emulator window.
"""

import ctypes, ctypes.wintypes, time
from dataclasses import dataclass
from typing import Optional

from input_emulation import GameButton, InputEmitter, InputSequence, Macros

# ──────────────────────────────────────────────
#  Win32 Constants
# ──────────────────────────────────────────────

user32 = ctypes.windll.user32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("union", _INPUT),
    ]


# ──────────────────────────────────────────────
#  RetroArch Key Mapping
# ──────────────────────────────────────────────

# RetroArch default keyboard mappings
RETROARCH_KEY_MAP = {
    GameButton.UP: 0x26,        # Up arrow
    GameButton.DOWN: 0x28,      # Down arrow
    GameButton.LEFT: 0x25,      # Left arrow
    GameButton.RIGHT: 0x27,     # Right arrow
    GameButton.A: 0x5A,         # Z
    GameButton.B: 0x58,         # X
    GameButton.X: 0x41,         # A
    GameButton.Y: 0x53,         # S
    GameButton.START: 0x0D,     # Enter
    GameButton.SELECT: 0x10,    # Shift
    GameButton.L: 0x51,         # Q
    GameButton.R: 0x57,         # W
}

# Virtual key codes
VK_MAP = {
    0x26: "VK_UP",
    0x28: "VK_DOWN",
    0x25: "VK_LEFT",
    0x27: "VK_RIGHT",
    0x5A: "VK_Z",
    0x58: "VK_X",
    0x41: "VK_A",
    0x53: "VK_S",
    0x0D: "VK_RETURN",
    0x10: "VK_SHIFT",
    0x51: "VK_Q",
    0x57: "VK_W",
}


# ──────────────────────────────────────────────
#  Windows Input Emitter
# ──────────────────────────────────────────────

class WindowsInputEmitter(InputEmitter):
    """Sends direct keyboard inputs to Windows using SendInput."""

    def __init__(self, target_hwnd: Optional[int] = None):
        self.target_hwnd = target_hwnd
        self._pressed_keys: set[int] = set()

    def press(self, button: GameButton):
        vk = RETROARCH_KEY_MAP.get(button)
        if not vk:
            return
        if vk in self._pressed_keys:
            return  # Already pressed

        self._send_key(vk, False)
        self._pressed_keys.add(vk)

    def release(self, button: GameButton):
        vk = RETROARCH_KEY_MAP.get(button)
        if not vk:
            return
        if vk not in self._pressed_keys:
            return  # Already released

        self._send_key(vk, True)
        self._pressed_keys.discard(vk)

    def release_all(self):
        """Release all currently pressed keys."""
        for vk in list(self._pressed_keys):
            self._send_key(vk, True)
        self._pressed_keys.clear()

    def _send_key(self, vk_code: int, key_up: bool):
        """Send a single key event using SendInput."""
        flags = KEYEVENTF_KEYUP if key_up else 0
        x = INPUT()
        x.type = INPUT_KEYBOARD
        x.union.ki = KEYBDINPUT(
            wVk=ctypes.wintypes.WORD(vk_code),
            wScan=0,
            dwFlags=ctypes.wintypes.DWORD(flags),
            time=0,
            dwExtraInfo=None,
        )
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    def tap_key(self, vk_code: int, duration: float = 0.05):
        """Press and release a key by virtual key code."""
        self._send_key(vk_code, False)
        time.sleep(duration)
        self._send_key(vk_code, True)

    def __del__(self):
        self.release_all()


# ──────────────────────────────────────────────
#  Windows Input Controller
# ──────────────────────────────────────────────

class WindowsInputController:
    """High-level controller combining Windows input with game macros."""

    def __init__(self, target_hwnd: Optional[int] = None):
        self.emitter = WindowsInputEmitter(target_hwnd)
        self.macros = Macros()

    def focus_window(self):
        """Bring the game window to focus before sending inputs."""
        if self.emitter.target_hwnd:
            user32.SetForegroundWindow(self.emitter.target_hwnd)
            time.sleep(0.05)

    def jump(self):
        self.focus_window()
        self.emitter.execute(self.macros.jump())

    def attack(self):
        self.focus_window()
        self.emitter.execute(self.macros.attack())

    def move(self, direction: str, duration: float = 0.5):
        self.focus_window()
        if direction == "right":
            self.emitter.execute(self.macros.move_right(duration))
        elif direction == "left":
            self.emitter.execute(self.macros.move_left(duration))
        elif direction == "up":
            self.emitter.execute(self.macros.move_up(duration))
        elif direction == "down":
            self.emitter.execute(self.macros.move_down(duration))

    def jump_attack(self):
        self.focus_window()
        self.emitter.execute(self.macros.jump_and_attack())

    def dash_right(self):
        self.focus_window()
        self.emitter.execute(self.macros.dash_right())

    def pause(self):
        self.focus_window()
        self.emitter.execute(self.macros.pause())

    def confirm(self):
        self.focus_window()
        self.emitter.execute(self.macros.confirm())

    def execute(self, sequence: InputSequence):
        self.focus_window()
        self.emitter.execute(sequence)


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Windows Input Emulation")
    parser.add_argument("action", choices=["test", "macro", "list"])
    parser.add_argument("--macro", default="jump", help="Macro to execute")
    args = parser.parse_args()

    controller = WindowsInputController()

    if args.action == "test":
        print("Testing Windows input (5 seconds)...")
        print("  Moving right...")
        controller.move("right", 0.3)
        time.sleep(0.2)
        print("  Jumping...")
        controller.jump()
        time.sleep(0.2)
        print("  Attacking...")
        controller.attack()
        print("✅ Test complete")

    elif args.action == "macro":
        print(f"Executing macro: {args.macro}")
        macro_fn = getattr(controller.macros, args.macro, None)
        if macro_fn:
            controller.execute(macro_fn())
        else:
            print(f"Unknown macro: {args.macro}")
            print(f"Available: jump, attack, jump_attack, dash_right, pause, confirm, cancel")

    elif args.action == "list":
        print("RetroArch Key Mappings:")
        for button, vk in sorted(RETROARCH_KEY_MAP.items(), key=lambda x: x[0].value):
            print(f"  {button.value:8s} → {VK_MAP.get(vk, hex(vk))}")
