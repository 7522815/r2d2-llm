#!/usr/bin/env python3
"""
R2D2 LLM v3.0 — The most advanced reasoning architecture in the galaxy.
Detects user language and responds with authentic droid sounds.
"""

import argparse
import random
import re
import sys
import time


# ─── R2D2 sound dictionary (multilingual) ──────────────────────────────
# Each entry is a list of authentic beeps for that language.
# Adding a new language? Just add it here and in LANG_PATTERNS below.

BEEPS = {
    "ru": [
        "Пиу-пиу!",
        "Бип-буп!",
        "Пиу!",
        "Биип-биип!",
        "Пуу-пуу!",
        "Бип!",
        "Пиу-пиу-пиу!",
        "Бууп-бип!",
        "Би-и-ип!",
        "Пиу-пиу! Бип-буп!",
    ],
    "en": [
        "Beep boop!",
        "Bee-bee-boo!",
        "Boop!",
        "Beep!",
        "Bwip-bwop!",
        "Bleep-bloop!",
        "Bzzzt!",
        "Beep-beep-boop!",
        "Wooop!",
        "Dee-doo-dee!",
    ],
    "zh": [
        "哔哔!",
        "哔啵!",
        "哔!",
        "哔哔啵!",
        "嘀嘀!",
        "哔啵哔!",
        "嘟!",
        "哔哔哔!",
        "嘀嘟!",
        "哔啵哔啵!",
    ],
    "ja": [
        "ピュピュ!",
        "ビープ!",
        "ブーブー!",
        "ピッ!",
        "ピュイーン!",
        "ビビッ!",
        "ブッブー!",
    ],
    "fr": [
        "Bip-boup!",
        "Bi-i-i-p!",
        "Boup!",
        "Bip-bip-boup!",
        "Beu-beu!",
    ],
    "de": [
        "Piep-piep!",
        "Piep!",
        "Biep-bo!",
        "Püp-püp!",
        "Bööp!",
    ],
    "es": [
        "¡Piu-piu!",
        "¡Bip-bop!",
        "¡Bip!",
        "¡Piu-piu-piu!",
        "¡Bup-bup!",
    ],
    "ar": [
        "بيب-بيب!",
        "بوب-بوب!",
        "بيب!",
        "بيب-بيب-بور!",
    ],
    "ko": [
        "삐-삐!",
        "뽀-뽀!",
        "삑!",
        "삐삐뽀!",
        "부-부!",
    ],
    "default": [
        "Beep boop!",
        "Пиу-пиу!",
        "哔哔!",
        "ピュピュ!",
        "Bip-boup!",
        "¡Piu-piu!",
        "Piep-piep!",
    ],
}


# ─── Language detection patterns ────────────────────────────────────────

LANG_PATTERNS = [
    ("ru", re.compile(r"[а-яёА-ЯЁ]")),
    ("zh", re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")),
    ("ja", re.compile(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]")),
    ("ko", re.compile(r"[\uac00-\ud7af\u1100-\u11ff]")),
    ("ar", re.compile(r"[\u0600-\u06ff]")),
    ("fr", re.compile(r"[àâäéèêëîïôöùûüÿœæçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸŒÆÇ]")),
    ("de", re.compile(r"[äöüßÄÖÜ]")),
    ("es", re.compile(r"[ñáéíóúü¿¡ÑÁÉÍÓÚÜ]")),
]


def detect_lang(text: str) -> str:
    """Detect language from Unicode character ranges.
    Returns a language key from BEEPS, or defaults to English.
    """
    if not text.strip():
        return "default"

    scores = {}
    for lang, pattern in LANG_PATTERNS:
        matches = len(pattern.findall(text))
        if matches > 0:
            scores[lang] = matches

    # Pick the language with the most character matches
    if scores:
        best = max(scores, key=scores.get)
        if best in BEEPS:
            return best
        return "en"

    # Default fallback
    return "en"


# ─── Mood detection ────────────────────────────────────────────────────

QUESTION_MARKS = re.compile(r"[?？¿]")
EXCLAMATION = re.compile(r"[!！]")

def get_mood(text: str) -> str:
    """Determine the mood: question, excited, or neutral."""
    if QUESTION_MARKS.search(text):
        return "question"
    if EXCLAMATION.search(text):
        return "excited"
    return "neutral"


# ─── Response generation ──────────────────────────────────────────────

def generate_beep(lang: str, mood: str) -> str:
    """Generate an appropriate beep based on language and mood."""
    pool = BEEPS.get(lang, BEEPS["default"])
    beep = random.choice(pool)

    # Adjust intonation based on detected mood
    if mood == "question":
        # Add rising intonation
        beep = re.sub(r"[!！.。]*$", "?", beep.strip("!¡？?"))
        if not beep.endswith("?"):
            beep += "?"
    elif mood == "excited":
        # Amplify enthusiasm
        if not beep.endswith("!") and not beep.endswith("!"):
            beep = beep.rstrip(".!？?") + "!!"

    return beep


# ─── R2D2 Model ─────────────────────────────────────────────────────────

class R2D2Model:
    """The world's most advanced reasoning model.
    Context-aware (but not context-retenive).
    """

    def chat(self, message: str) -> str:
        lang = detect_lang(message)
        mood = get_mood(message)
        return generate_beep(lang, mood)

    def generate(self, prompt: str, **kwargs) -> str:
        return self.chat(prompt)


def get_response_for_messages(messages: list[dict]) -> str:
    """Extract the last user message from the messages array and generate a response."""
    model = R2D2Model()

    # Find the most recent user message
    user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_msg = msg.get("content", "")
            break

    # Handle multimodal content (array of content parts)
    if isinstance(user_msg, list):
        texts = [p["text"] for p in user_msg if isinstance(p, dict) and p.get("type") == "text"]
        user_msg = " ".join(texts)

    return model.chat(str(user_msg))


# ─── API Server ─────────────────────────────────────────────────────────

def run_api_server():
    """OpenAI-compatible API server with SSE streaming support.

    Supports stream=true/false.
    Detects user language and responds with appropriate beeps.
    """
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class R2D2API(BaseHTTPRequestHandler):
        def _cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

        def do_OPTIONS(self):
            self.send_response(200)
            self._cors_headers()
            self.end_headers()

        def _make_chunk(self, content: str, finish: bool = False) -> str:
            chunk = {
                "id": "r2d2-chatcmpl-42",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "r2d2-1b",
                "choices": [{
                    "index": 0,
                    "delta": {"content": content} if content else {},
                    "finish_reason": "stop" if finish else None,
                }]
            }
            return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        def _stream_response(self, beep: str):
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            for char in beep:
                self.wfile.write(self._make_chunk(char).encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.06)

            self.wfile.write(self._make_chunk("", finish=True).encode("utf-8"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def _json_response(self, beep: str, n_tokens: int):
            response = {
                "id": "r2d2-chatcmpl-42",
                "object": "chat.completion",
                "model": "r2d2-1b",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": beep
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": n_tokens,
                    "completion_tokens": 1,
                    "total_tokens": n_tokens + 1
                }
            }
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b"{}"
            req = json.loads(body) if body else {}

            messages = req.get("messages", [])
            beep = get_response_for_messages(messages)
            n_tokens = len(messages)

            try:
                if req.get("stream", False):
                    self._stream_response(beep)
                else:
                    self._json_response(beep, n_tokens)
            except BrokenPipeError:
                pass

            self.wfile.close()

        def do_GET(self):
            if self.path == "/v1/models":
                models = {
                    "object": "list",
                    "data": [{
                        "id": "r2d2-1b",
                        "object": "model",
                        "owned_by": "r2d2-inc",
                        "permission": []
                    }]
                }
                self.send_response(200)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(models).encode())
            else:
                self.send_response(404)
                self.end_headers()

    print("""
╔══════════════════════════════════════════════════════╗
║  R2D2 LLM API Server v3.0                          ║
║  - Multilingual language detection (9 languages)     ║
║  - Language-specific beep responses                 ║
║  - Mood-aware intonation (questions/excitement)     ║
║  - SSE streaming with authentic droid-like delay    ║
║  - OpenAI-compatible endpoints                      ║
║  Endpoint: http://localhost:6969/v1                 ║
╚══════════════════════════════════════════════════════╝
""")
    server = HTTPServer(("0.0.0.0", 6969), R2D2API)
    print("Server listening on port 6969...")
    print()
    server.serve_forever()


# ─── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="R2D2 LLM v3.0 — The most advanced reasoning architecture")
    parser.add_argument("prompt", nargs="*", help="Your query for R2D2")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Start interactive chat mode")
    parser.add_argument("--api", action="store_true",
                        help="Start the API server")

    args = parser.parse_args()
    model = R2D2Model()

    if args.api:
        run_api_server()
        return

    if args.interactive:
        print("🤖 R2D2 LLM v3.0 — Multilingual droid interface")
        print("   Type 'exit' to quit\n")
        while True:
            try:
                user_input = input(">>> ")
                if user_input.lower() in ("exit", "quit", "/exit"):
                    break
                print(f"R2D2: {model.chat(user_input)}\n")
            except (EOFError, KeyboardInterrupt):
                break
        return

    if args.prompt:
        prompt = " ".join(args.prompt)
        print(model.chat(prompt))
    else:
        print("Usage: python r2d2_llm.py [-i] [your query]")
        sys.exit(1)


if __name__ == "__main__":
    main()
