#!/usr/bin/env python3
"""
R2D2 Visual Assistant — main launch point.

Brings together:
- Floating R2D2 character window
- Voice input (speech-to-text)
- Voice output (text-to-speech)
- Desktop vision & interaction
- R2D2 LLM brain

Modes:
    python3 app.py          — GUI mode (floating R2D2 + voice)
    python3 app.py --voice  — Voice-only mode (no GUI)
    python3 app.py --cli    — Command-line mode
    python3 app.py --help   — All options
"""

import sys
import os
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from r2d2_assistant.r2d2_gui import R2D2Character
from r2d2_assistant import voice
from r2d2_assistant import desktop_agent
from r2d2_assistant import r2d2_client


class R2D2Assistant:
    """Main assistant controller — connects GUI, voice, desktop, and brain."""

    def __init__(self, use_gui=True, use_voice=True):
        self.use_gui = use_gui
        self.use_voice = use_voice
        self.gui = None
        self.brain = r2d2_client.R2D2Client()

    def start(self):
        """Launch the assistant."""
        if self.use_gui:
            self._start_gui()
        elif self.use_voice:
            self._voice_loop()
        else:
            self._cli_loop()

    def _start_gui(self):
        """Start the GUI with R2D2 character."""
        self.gui = R2D2Character(on_click=self._on_r2d2_click)
        self.gui.set_state(R2D2Character.STATE_IDLE)

        if self.use_voice:
            # Start voice trigger in background
            self._start_voice_trigger()

        self.gui.mainloop()

    def _start_voice_trigger(self):
        """Background thread that listens for wake word."""
        def watcher():
            time.sleep(2)  # Wait for GUI to initialize
            voice.play_beep_sequence("wake")
            while True:
                try:
                    text = voice.listen(timeout=0.5, phrase_time=2.0)
                    if text and self.gui:
                        self.gui.set_state(R2D2Character.STATE_LISTENING)
                        self._handle_voice_input(text)
                        time.sleep(0.5)
                        self.gui.set_state(R2D2Character.STATE_IDLE)
                except (AttributeError, RuntimeError):
                    break
                time.sleep(0.1)

        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()

    def _on_r2d2_click(self):
        """Called when user clicks on R2D2 character — quick chat mode."""
        if self.gui:
            self.gui.set_state(R2D2Character.STATE_LISTENING)

        voice.play_beep_sequence("hear")
        text = voice.listen(timeout=4, phrase_time=6)

        if text:
            self._handle_voice_input(text)
        else:
            if self.gui:
                self.gui.set_state(R2D2Character.STATE_IDLE)

    def _handle_voice_input(self, text: str):
        """Process voice input: detect intent, respond."""
        text = text.strip().lower()
        if not text:
            return

        # Detect special commands
        if self._is_desktop_command(text):
            self._handle_desktop_command(text)
            return

        if self._is_screenshot_command(text):
            self._handle_screenshot()
            return

        # Default: send to R2D2 LLM
        self._query_r2d2(text)

    def _is_desktop_command(self, text: str) -> bool:
        """Check if this is a desktop interaction command."""
        desktop_keywords = [
            "click", "scroll", "type", "press", "open",
            "move mouse", "drag", "double click",
        ]
        return any(kw in text for kw in desktop_keywords)

    def _is_screenshot_command(self, text: str) -> bool:
        """Check if user wants a screenshot."""
        keywords = ["screenshot", "capture screen", "what's on", "show desktop",
                     "capture", "snapshot"]
        return any(kw in text for kw in keywords)

    def _handle_desktop_command(self, text: str):
        """Parse and execute a desktop command."""
        if self.gui:
            self.gui.set_state(R2D2Character.STATE_THINKING)
        voice.play_beep_sequence("hear")

        # Simple command parsing
        if "screenshot" in text or "capture" in text:
            self._handle_screenshot()
            return

        if "click" in text:
            x, y = desktop_agent.get_mouse_position()
            desktop_agent.click(x, y)
        elif "scroll" in text:
            desktop_agent.scroll(-3)
        elif "type" in text:
            # Extract text after "type"
            parts = text.split("type", 1)
            if len(parts) > 1:
                desktop_agent.type_text(parts[1].strip())
        elif "enter" in text or "press enter" in text:
            desktop_agent.press_key("enter")
        elif "escape" in text:
            desktop_agent.press_key("escape")

        voice.speak("Done")
        voice.play_beep_sequence("done")

        if self.gui:
            self.gui.set_state(R2D2Character.STATE_IDLE)

    def _handle_screenshot(self):
        """Take a screenshot and describe it."""
        if self.gui:
            self.gui.set_state(R2D2Character.STATE_THINKING)

        info = desktop_agent.screenshot_and_analyze()
        summary = (
            f"Screen captured. "
            f"Size: {info['screen_size'][0]}x{info['screen_size'][1]}. "
            f"Active window: {info['active_window']}. "
        )

        voice.play_beep_sequence("done")
        voice.speak(summary)

        if self.gui:
            self.gui.set_state(R2D2Character.STATE_IDLE)

    def _query_r2d2(self, text: str):
        """Send text to R2D2 LLM and speak the response."""
        if self.gui:
            self.gui.set_state(R2D2Character.STATE_THINKING)

        response = self.brain.chat(text)

        if self.gui:
            self.gui.set_state(R2D2Character.STATE_SPEAKING)

        voice.play_beep_sequence("hear")
        voice.speak(response, rate=180)
        voice.play_beep_sequence("done")

        if self.gui:
            self.gui.set_state(R2D2Character.STATE_IDLE)

    def _voice_loop(self):
        """Voice-only mode — no GUI."""
        print("🤖 R2D2 Voice Assistant (voice-only mode)")
        print("   Speak or press Ctrl+C to exit\n")
        voice.play_beep_sequence("wake")

        while True:
            try:
                text = voice.listen(timeout=10, phrase_time=8)
                if text:
                    print(f"🎤 You: {text}")
                    self._handle_voice_input(text)
                else:
                    print("⏳ Waiting...")
            except KeyboardInterrupt:
                break

    def _cli_loop(self):
        """Simple CLI mode."""
        print("🤖 R2D2 CLI — type 'exit' to quit\n")
        while True:
            try:
                text = input(">>> ")
                if text.lower() in ("exit", "quit"):
                    break
                response = self.brain.chat(text)
                print(f"R2D2: {response}")
            except (EOFError, KeyboardInterrupt):
                break


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="R2D2 Visual Assistant — The droid you're looking for"
    )
    parser.add_argument("--no-gui", action="store_true",
                        help="Run without GUI (voice or CLI mode)")
    parser.add_argument("--voice", action="store_true",
                        help="Voice-only mode (no GUI)")
    parser.add_argument("--cli", action="store_true",
                        help="CLI-only mode (no voice, no GUI)")
    parser.add_argument("--query", type=str, nargs="+",
                        help="One-shot query (returns response, no GUI)")

    args = parser.parse_args()

    if args.query:
        text = " ".join(args.query)
        response = r2d2_client.quick_query(text)
        print(f"R2D2: {response}")
        return

    if args.cli:
        assistant = R2D2Assistant(use_gui=False, use_voice=False)
    elif args.voice or args.no_gui:
        assistant = R2D2Assistant(use_gui=False, use_voice=True)
    else:
        assistant = R2D2Assistant(use_gui=True, use_voice=True)

    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n🤖 R2D2 signing off. Beep boop!")
        sys.exit(0)


if __name__ == "__main__":
    main()
