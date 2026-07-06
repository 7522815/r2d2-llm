"""
Desktop Agent — screen capture and desktop interaction for R2D2.

Uses:
- mss for fast screen capture
- pyautogui for mouse/keyboard control
- macOS accessibility APIs via pyautogui backend
"""

import os
import time
import tempfile
from PIL import Image
import mss
import pyautogui

# Safe mode — no corner exits, no failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


# ─── Screen Capture ──────────────────────────────────────────────────

def capture_screen(region=None, output_path=None):
    """Capture the full screen or a region.

    Args:
        region: (left, top, width, height) tuple — None for full screen
        output_path: Save path (auto-generated temp file if None)

    Returns:
        Path to the saved screenshot image
    """
    with mss.mss() as sct:
        if region:
            monitor = {"left": region[0], "top": region[1],
                       "width": region[2], "height": region[3]}
        else:
            monitor = sct.monitors[1]  # Primary monitor

        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".png", prefix="r2d2_desktop_")
            os.close(fd)

        img.save(output_path, "PNG")
        return output_path


def get_mouse_position() -> tuple[int, int]:
    """Get current mouse cursor position."""
    return pyautogui.position()


# ─── Desktop Interaction ─────────────────────────────────────────────

def click(x: int, y: int, button: str = "left", clicks: int = 1):
    """Click at specific screen coordinates.

    Args:
        x, y: Screen coordinates
        button: 'left', 'right', 'middle'
        clicks: Number of clicks (2 for double-click)
    """
    pyautogui.click(x, y, button=button, clicks=clicks)


def double_click(x: int, y: int):
    """Double-click at position."""
    click(x, y, clicks=2)


def right_click(x: int, y: int):
    """Right-click at position."""
    click(x, y, button="right")


def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.3):
    """Drag from (x1, y1) to (x2, y2)."""
    pyautogui.moveTo(x1, y1)
    pyautogui.drag(x2 - x1, y2 - y1, duration=duration)


def scroll(clicks: int = -3):
    """Scroll vertically. Negative = scroll down, Positive = scroll up."""
    pyautogui.scroll(clicks)


def type_text(text: str):
    """Type text at the current cursor position."""
    pyautogui.write(text, interval=0.02)


def press_key(key: str):
    """Press a keyboard key (e.g., 'enter', 'escape', 'tab')."""
    pyautogui.press(key)


def hotkey(*keys: str):
    """Press a keyboard combination (e.g., hotkey('cmd', 'space'))."""
    pyautogui.hotkey(*keys)


# ─── Active Window ───────────────────────────────────────────────────

def get_active_window_title() -> str:
    """Get the title of the currently active window (macOS)."""
    try:
        import Quartz
        ws = Quartz.NSWorkspace.sharedWorkspace()
        active_app = ws.activeApplication()
        app_name = active_app.get('NSApplicationName', 'Unknown')
        return str(app_name)
    except ImportError:
        return "Unknown (requires pyobjc-framework-Quartz)"


def get_screen_size() -> tuple[int, int]:
    """Get screen dimensions."""
    return pyautogui.size()


# ─── Color Detection ─────────────────────────────────────────────────

def get_pixel_color(x: int, y: int) -> tuple[int, int, int]:
    """Get RGB color at screen coordinates."""
    return pyautogui.pixel(x, y)


# ─── Screenshot and Analyze ─────────────────────────────────────────

def screenshot_and_analyze() -> dict:
    """Take a screenshot and return info about the desktop.

    Returns dict with:
        - screenshot_path: path to PNG
        - screen_size: (width, height)
        - active_window: title of active window
        - mouse_position: (x, y)
    """
    path = capture_screen()
    size = get_screen_size()
    title = get_active_window_title()
    mouse = get_mouse_position()

    return {
        "screenshot_path": path,
        "screen_size": size,
        "active_window": title,
        "mouse_position": mouse,
    }


if __name__ == "__main__":
    info = screenshot_and_analyze()
    print(f"📸 Desktop captured: {info['screenshot_path']}")
    print(f"🖥️  Screen: {info['screen_size']}")
    print(f"📱 Active: {info['active_window']}")
    print(f"🖱️  Mouse: {info['mouse_position']}")
