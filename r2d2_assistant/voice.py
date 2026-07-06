"""
Voice subsystem — speech-to-text and text-to-speech for R2D2.

Uses:
- SpeechRecognition + macOS NSSpeechRecognizer for STT
- macOS `say` command for TTS (authentic system voice)
- Plays R2D2 beep sounds as audio feedback
"""

import subprocess
import tempfile
import os
import threading
import time

import speech_recognition as sr


# ─── Text-to-Speech ──────────────────────────────────────────────────

def speak(text: str, voice: str = "Alex", rate: int = 200):
    """Say text aloud using macOS TTS.

    Args:
        text: Text to speak
        voice: macOS voice name (default: Alex — sounds most droid-like)
        rate: Words per minute (default: 200)
    """
    # Escape for shell safety
    safe_text = text.replace('"', '\\"')
    cmd = ["say", "-v", voice, "-r", str(rate), safe_text]
    try:
        subprocess.run(cmd, check=True, timeout=30)
    except subprocess.TimeoutExpired:
        pass
    except subprocess.CalledProcessError:
        # Fallback to default voice
        try:
            subprocess.run(["say", safe_text], check=True, timeout=30)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass


def speak_beep():
    """Play a quick R2D2-style beep sound using afplay or say."""
    try:
        # Use say with a short tone-like sound
        subprocess.run(["say", "-v", "Bells", "-r", 300, "beep"],
                       check=True, timeout=3)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass


# ─── Speech-to-Text ──────────────────────────────────────────────────

def listen(timeout: float = 3.0, phrase_time: float = 5.0):
    """Listen for speech and return recognized text.

    Args:
        timeout: Max seconds to wait for speech to start
        phrase_time: Max seconds for a single phrase

    Returns:
        Recognized text string, or None if no speech detected
    """
    recognizer = sr.Recognizer()
    # Adjust for ambient noise
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 4000

    try:
        with sr.Microphone() as source:
            # Quick noise calibration
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=timeout,
                                       phrase_time_limit=phrase_time)
    except sr.WaitTimeoutError:
        return None
    except OSError:
        # No microphone available
        return None

    try:
        text = recognizer.recognize_google(audio, language="auto")
        return text
    except (sr.UnknownValueError, sr.RequestError):
        return None


def listen_async(callback, timeout=3.0, phrase_time=5.0):
    """Listen in a background thread and call callback(text) when done.

    Args:
        callback: Function to call with recognized text (or None)
    """
    def _worker():
        text = listen(timeout=timeout, phrase_time=phrase_time)
        if callback:
            callback(text)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread


# ─── Audio feedback ──────────────────────────────────────────────────

def play_beep_sequence(pattern: str = "wake"):
    """Play a sequence of beeps to signal state changes.

    Patterns:
        "wake" — two rising tones (attention)
        "done" — two falling tones (task complete)
        "error" — flat buzz (error)
        "hear" — short pip (heard you)
    """
    tones = {
        "wake": [("Bells", 400), ("Bells", 500)],
        "done": [("Bells", 500), ("Bells", 400)],
        "error": [("Bubbles", 200), ("Bubbles", 200), ("Bubbles", 200)],
        "hear": [("Bells", 300)],
    }
    seq = tones.get(pattern, tones["hear"])
    for voice, rate in seq:
        try:
            subprocess.run(["say", "-v", voice, "-r", str(rate), "beep"],
                           check=True, timeout=2)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        time.sleep(0.1)


if __name__ == "__main__":
    print("🎤 R2D2 Voice Test — speak now...")
    text = listen(timeout=5)
    if text:
        print(f"📝 You said: {text}")
        speak(f"You said: {text}")
        play_beep_sequence("done")
    else:
        print("🤖 No speech detected")
        play_beep_sequence("error")
