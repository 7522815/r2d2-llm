"""
R2D2 Character Window — floating desktop droid.

Draws an animated R2D2 using tkinter Canvas with:
- Dome head with blinking eye
- Body panel with flashing LEDs
- Listening / speaking / idle animations
- Always-on-top, compact window
"""

import tkinter as tk
import math
import time
import threading


class R2D2Character(tk.Tk):
    """Floating R2D2 companion window. Stays on top of all apps."""

    # Animation states
    STATE_IDLE = "idle"
    STATE_LISTENING = "listening"
    STATE_THINKING = "thinking"
    STATE_SPEAKING = "speaking"

    # Colors
    DOME_BASE = "#e8e8e8"
    DOME_HIGHLIGHT = "#f5f5f5"
    BODY_COLOR = "#d0d0d0"
    BODY_DARK = "#404060"
    EYE_WHITE = "#ffffff"
    EYE_PUPIL = "#101010"
    LED_BLUE = "#2266ff"
    LED_RED = "#ff3333"
    LED_GREEN = "#33ff66"
    LED_YELLOW = "#ffdd00"
    BG_COLOR = "#1a1a2e"

    def __init__(self, on_click=None):
        super().__init__()
        self.on_click = on_click
        self.state = self.STATE_IDLE
        self.blink_open = True
        self.led_phase = 0

        # Window setup
        self.overrideredirect(True)  # No title bar
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.configure(bg=self.BG_COLOR)

        # Window size and position (bottom-right)
        self.W = 220
        self.H = 300
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{self.W}x{self.H}+{screen_w - self.W - 40}+{screen_h - self.H - 80}")

        # Canvas for drawing
        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                 bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Make window draggable
        self._drag_data = {"x": 0, "y": 0}
        self.canvas.tag_bind("drag_handle", "<ButtonPress-1>", self._drag_start)
        self.canvas.tag_bind("drag_handle", "<ButtonRelease-1>", self._drag_stop)
        self.canvas.tag_bind("drag_handle", "<B1-Motion>", self._drag_move)

        # Click handler on R2D2 body
        self.canvas.tag_bind("body", "<Button-1>", self._on_body_click)
        self.canvas.tag_bind("dome", "<Button-1>", self._on_body_click)

        # Draw static parts
        self._draw_static()

        # Start animation loop
        self._running = True
        self._anim_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self._anim_thread.start()

        # Bind close
        self.protocol("WM_DELETE_WINDOW", self._quit)

    # ─── Drawing ────────────────────────────────────────────────────

    def _draw_static(self):
        """Draw the non-animated parts of R2D2."""
        cx, by = self.W // 2, self.H - 20

        # Drag handle (invisible, covers top area)
        self.canvas.create_rectangle(0, 0, self.W, 40,
                                      fill="", outline="",
                                      tags="drag_handle", width=0)

        # Body rectangle
        bw, bh = 100, 110
        bx1, by1 = cx - bw // 2, by - bh
        bx2, by2 = cx + bw // 2, by
        self.canvas.create_rectangle(bx1, by1, bx2, by2,
                                      fill=self.BODY_COLOR,
                                      outline="#888888", width=2,
                                      tags="body")
        # Body panel details
        panel_x1, panel_y1 = bx1 + 10, by1 + 10
        panel_x2, panel_y2 = bx2 - 10, by2 - 10
        self.canvas.create_rectangle(panel_x1, panel_y1, panel_x2, panel_y2,
                                      fill=self.BODY_DARK,
                                      outline="#606080", width=1)

        # Vertical body stripe
        self.canvas.create_line(cx, by1 + 8, cx, by2 - 8,
                                 fill="#8080a0", width=2)

        # Horizontal panel lines
        for y_off in [25, 50, 75]:
            y = by1 + y_off
            self.canvas.create_line(panel_x1 + 5, y, panel_x2 - 5, y,
                                     fill="#505070", width=1)

        # Feet (small rectangles)
        foot_w, foot_h = 30, 10
        self.canvas.create_rectangle(cx - 40, by, cx - 10, by + foot_h,
                                      fill=self.BODY_COLOR, outline="#888888", width=1)
        self.canvas.create_rectangle(cx + 10, by, cx + 40, by + foot_h,
                                      fill=self.BODY_COLOR, outline="#888888", width=1)

        # Dome (half circle)
        dome_r = 55
        dome_y = by1
        self.canvas.create_arc(cx - dome_r, dome_y - dome_r,
                                cx + dome_r, dome_y + dome_r,
                                start=0, extent=180,
                                fill=self.DOME_BASE, outline="#aaaaaa", width=2,
                                tags="dome")

        # Dome highlight
        self.canvas.create_arc(cx - dome_r + 8, dome_y - dome_r + 8,
                                cx + dome_r - 8, dome_y + dome_r - 8,
                                start=0, extent=180,
                                fill=self.DOME_HIGHLIGHT, outline="", width=0,
                                tags="dome")

        # Store positions for animated elements
        self._cx = cx
        self._eye_y = dome_y - dome_r // 2 + 5
        self._body_top = by1
        self._panel_x1 = panel_x1
        self._panel_x2 = panel_x2
        self._panel_y1 = panel_y1
        self._panel_y2 = panel_y2

        # Create animated element placeholders
        self._eye_outer = None
        self._eye_inner = None
        self._leds = []
        self._status_text = None

    def _draw_eye(self, open_pupil=True):
        """Draw or update R2D2's eye."""
        cx, ey = self._cx, self._eye_y

        # Remove old eye
        self.canvas.delete("eye")

        if open_pupil:
            # Open eye — outer circle
            self.canvas.create_oval(cx - 16, ey - 14, cx + 16, ey + 14,
                                     fill=self.EYE_WHITE, outline="#333333", width=2,
                                     tags="eye")
            # Pupil
            self.canvas.create_oval(cx - 5, ey - 4, cx + 5, ey + 4,
                                     fill=self.EYE_PUPIL, outline="", tags="eye")
            # Pupil highlight
            self.canvas.create_oval(cx - 2, ey - 5, cx + 3, ey,
                                     fill="#ffffff", outline="", tags="eye")
        else:
            # Closed eye (line)
            self.canvas.create_line(cx - 14, ey, cx + 14, ey,
                                     fill="#333333", width=3, tags="eye")

    def _draw_leds(self, pattern="idle"):
        """Draw indicator LEDs with animation pattern."""
        self.canvas.delete("leds")
        cx = self._cx
        py = self._panel_y1 + 35  # Y position for LEDs

        # Define LED positions (4 LEDs)
        led_positions = [
            (cx - 30, py),
            (cx - 10, py),
            (cx + 10, py),
            (cx + 30, py),
        ]

        colors = {
            "idle": [self.LED_BLUE, self.LED_BLUE, self.LED_GREEN, self.LED_GREEN],
            "listening": [self.LED_RED, self.LED_YELLOW, self.LED_YELLOW, self.LED_RED],
            "thinking": [self.LED_BLUE, self.LED_YELLOW, self.LED_YELLOW, self.LED_BLUE],
            "speaking": [self.LED_GREEN, self.LED_BLUE, self.LED_BLUE, self.LED_GREEN],
        }

        cols = colors.get(pattern, colors["idle"])

        # Apply phase shift for animation
        phase = self.led_phase
        for i, (x, y) in enumerate(led_positions):
            brightness = 0.5 + 0.5 * math.sin(phase + i * 1.2)
            col = cols[i]
            r = 5 + 2 * brightness
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                     fill=col, outline="",
                                     tags="leds")

    def _draw_status(self, text):
        """Draw status text below R2D2."""
        self.canvas.delete("status")
        if text:
            self.canvas.create_text(self._cx, self.H - 45,
                                     text=text, fill="#888899",
                                     font=("Helvetica", 9),
                                     tags="status")

    # ─── Animation ──────────────────────────────────────────────────

    def _animation_loop(self):
        """Background animation loop."""
        blink_counter = 0
        while self._running:
            time.sleep(0.05)  # ~20 FPS
            blink_counter += 1
            self.led_phase += 0.08

            # Blink every ~3 seconds in idle, more often when listening
            blink_interval = 60 if self.state == self.STATE_IDLE else 20
            self.blink_open = (blink_counter % blink_interval) < (blink_interval - 4)

            # Update UI on main thread
            try:
                self.after(0, self._update_visuals)
            except tk.TclError:
                break

    def _update_visuals(self):
        """Update animated elements (called from main thread)."""
        try:
            self._draw_eye(open_pupil=self.blink_open)
            self._draw_leds(pattern=self.state)

            status_map = {
                self.STATE_IDLE: "🟢 waiting",
                self.STATE_LISTENING: "🎤 listening...",
                self.STATE_THINKING: "⚡ thinking...",
                self.STATE_SPEAKING: "🔊 speaking...",
            }
            self._draw_status(status_map.get(self.state, ""))
        except tk.TclError:
            pass

    # ─── Public API ─────────────────────────────────────────────────

    def set_state(self, state):
        """Change R2D2's animation state."""
        self.state = state

    # ─── Event handlers ─────────────────────────────────────────────

    def _drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _drag_stop(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _drag_move(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.winfo_x() + dx
        y = self.winfo_y() + dy
        self.geometry(f"+{x}+{y}")

    def _on_body_click(self, event):
        """Trigger external click handler."""
        if self.on_click:
            self.on_click()

    def _quit(self):
        self._running = False
        self.destroy()


def run_gui(on_click=None):
    """Launch the R2D2 character window (blocking)."""
    app = R2D2Character(on_click=on_click)
    app.mainloop()


if __name__ == "__main__":
    run_gui()
