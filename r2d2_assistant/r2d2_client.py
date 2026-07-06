"""
R2D2 LLM Client — communicates with the R2D2 LLM API server.

Sends user messages and returns the droid's beep response.
Can also integrate with external LLM APIs for advanced tasks.
"""

import json
import urllib.request
import urllib.error


# Default API endpoints (try local first, then production)
DEFAULT_API_URL = "http://localhost:6969/v1/chat/completions"
PRODUCTION_API_URL = "https://ilukha.com/v1/chat/completions"


class R2D2Client:
    """Client for the R2D2 LLM API (OpenAI-compatible)."""

    def __init__(self, api_url=None):
        self.api_url = api_url or DEFAULT_API_URL

    def chat(self, message: str, stream: bool = False) -> str:
        """Send a message to R2D2 and get a beep response.

        Args:
            message: User's text message
            stream: Whether to use streaming mode

        Returns:
            R2D2's beep response as string
        """
        payload = json.dumps({
            "model": "r2d2-1b",
            "messages": [{"role": "user", "content": message}],
            "stream": stream,
        }).encode("utf-8")

        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError,
                json.JSONDecodeError, KeyError, ConnectionRefusedError) as e:
            # Fallback: local model not running, use built-in
            return self._fallback_beep(message, str(e))

    def _fallback_beep(self, message: str, error: str = "") -> str:
        """Fallback when API is not available — returns a default beep."""
        # Simple language detection for fallback
        import re
        if re.search(r"[а-яёА-ЯЁ]", message):
            return "Пиу-пиу!"
        elif re.search(r"[\u4e00-\u9fff]", message):
            return "哔哔!"
        elif re.search(r"[\u3040-\u30ff]", message):
            return "ピュピュ!"
        else:
            return "Beep boop!"


def quick_query(message: str) -> str:
    """Quick one-shot query to R2D2."""
    client = R2D2Client()
    return client.chat(message)


if __name__ == "__main__":
    import sys
    msg = " ".join(sys.argv[1:]) or "Hello R2D2!"
    response = quick_query(msg)
    print(f"User: {msg}")
    print(f"R2D2: {response}")
