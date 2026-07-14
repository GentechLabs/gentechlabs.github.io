"""
RomM AI Companion — Windows Screen Capture Module
Captures RetroArch game window using Win32 API.
No Docker needed — works directly on Windows.
"""

import os, time, struct, ctypes, ctypes.wintypes
from dataclasses import dataclass
from typing import Optional, Callable
from PIL import Image
import io

# ──────────────────────────────────────────────
#  Win32 Constants
# ──────────────────────────────────────────────

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

SW_RESTORE = 9
SW_MINIMIZE = 6
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

@dataclass
class WindowInfo:
    hwnd: int
    title: str
    class_name: str
    pid: int
    rect: tuple[int, int, int, int]  # left, top, right, bottom
    is_visible: bool


# ──────────────────────────────────────────────
#  Window Finder
# ──────────────────────────────────────────────

class WindowFinder:
    """Find RetroArch or any game window by title/class."""

    def __init__(self):
        self._hwnds: list[int] = []

    def find_all(self, title_contains: str = "") -> list[WindowInfo]:
        """Find all windows matching a title substring."""
        self._hwnds = []

        def enum_callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd) + 1
                buf = ctypes.create_unicode_buffer(length)
                user32.GetWindowTextW(hwnd, buf, length)
                title = buf.value
                if title_contains.lower() in title.lower():
                    self._hwnds.append(hwnd)
            return True

        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        user32.EnumWindows(enum_proc(enum_callback), 0)

        results = []
        for hwnd in self._hwnds:
            info = self._get_window_info(hwnd)
            if info:
                results.append(info)
        return results

    def find_retroarch(self) -> Optional[WindowInfo]:
        """Find the RetroArch game window."""
        windows = self.find_all("RetroArch")
        if windows:
            return windows[0]
        # Also try common game window titles
        windows = self.find_all(" - ")
        for w in windows:
            if any(core in w.title.lower() for core in ["nes", "snes", "gba", "n64", "psx"]):
                return w
        return None

    def _get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """Get window info from handle."""
        length = user32.GetWindowTextLengthW(hwnd) + 1
        buf = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buf, length)

        class_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buf, 256)

        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        return WindowInfo(
            hwnd=hwnd,
            title=buf.value,
            class_name=class_buf.value,
            pid=pid.value,
            rect=(rect.left, rect.top, rect.right, rect.bottom),
            is_visible=bool(user32.IsWindowVisible(hwnd)),
        )


# ──────────────────────────────────────────────
#  Screen Capturer
# ──────────────────────────────────────────────

class WindowsScreenCapturer:
    """Captures game window screenshots using Win32 API."""

    def __init__(self, window_title: str = "RetroArch"):
        self.finder = WindowFinder()
        self.window_title = window_title
        self._target_hwnd: Optional[int] = None

    def find_window(self) -> bool:
        """Find and store the target window handle."""
        windows = self.finder.find_all(self.window_title)
        if windows:
            self._target_hwnd = windows[0].hwnd
            return True
        # Fallback: find any visible game window
        windows = self.finder.find_all("")
        for w in windows:
            if w.hwnd and w.is_visible and w.rect[2] > w.rect[0]:
                self._target_hwnd = w.hwnd
                return True
        return False

    def capture(self) -> Optional[bytes]:
        """Capture the game window as PNG bytes."""
        if not self._target_hwnd:
            if not self.find_window():
                return None

        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(self._target_hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top

        if w <= 0 or h <= 0:
            return None

        # Capture the window
        hdc_window = user32.GetDC(self._target_hwnd)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
        gdi32.SelectObject(hdc_mem, hbitmap)
        gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_window, 0, 0, 0x00CC0020)  # SRCCOPY

        # Convert to PIL Image
        bmp_info = ctypes.create_string_buffer(64)
        gdi32.GetObjectW(hbitmap, 64, bmp_info)
        bits = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetBitmapBits(hbitmap, w * h * 4, bits)

        img = Image.frombuffer("RGBA", (w, h), bits, "raw", "BGRA", 0, 1)
        img = img.convert("RGB")

        # Cleanup
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(self._target_hwnd, hdc_window)

        # Return PNG bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def bring_to_front(self):
        """Bring the game window to the foreground."""
        if self._target_hwnd:
            user32.ShowWindow(self._target_hwnd, SW_RESTORE)
            user32.SetForegroundWindow(self._target_hwnd)

    def get_window_rect(self) -> Optional[tuple[int, int, int, int]]:
        """Get the window position and size."""
        if not self._target_hwnd:
            return None
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(self._target_hwnd, ctypes.byref(rect))
        return (rect.left, rect.top, rect.right, rect.bottom)


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Windows Screen Capture")
    parser.add_argument("action", choices=["find", "capture", "info"])
    parser.add_argument("--title", default="RetroArch", help="Window title to find")
    args = parser.parse_args()

    capturer = WindowsScreenCapturer(args.title)

    if args.action == "find":
        found = capturer.find_window()
        if found:
            rect = capturer.get_window_rect()
            print(f"✅ Found window: {args.title}")
            print(f"   Position: {rect}")
        else:
            print(f"❌ No window found matching '{args.title}'")
            print("   Make sure RetroArch is running with a game loaded")

    elif args.action == "capture":
        data = capturer.capture()
        if data:
            print(f"✅ Captured: {len(data)} bytes ({len(data)/1024:.1f} KB)")
            # Save to file
            path = f"capture_{int(time.time())}.png"
            with open(path, "wb") as f:
                f.write(data)
            print(f"   Saved: {path}")
        else:
            print("❌ Capture failed — window not found")

    elif args.action == "info":
        found = capturer.find_window()
        if found:
            rect = capturer.get_window_rect()
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            print(f"Window: {args.title}")
            print(f"Size: {w}x{h}")
            print(f"Position: ({rect[0]}, {rect[1]})")
        else:
            print(f"❌ Window not found")
