"""Google AI Studio (Gemini API) Client module.
Zero-dependency implementation using Python standard library (urllib.request).
Loads configuration from .env and provides structured generation under constrained prompt rules.
"""
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

def load_dotenv(env_path: Optional[str] = None) -> None:
    """Lightweight .env file loader for environment variables without third-party dependencies."""
    if env_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env_path = os.path.join(project_root, ".env")
        
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key, val = stripped.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                # Do not overwrite if already set in environment
                if key and key not in os.environ:
                    os.environ[key] = val

# Auto-load .env upon module import
load_dotenv()

class GeminiClient:
    """Client for Google AI Studio Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        self.api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
        try:
            self.temperature = float(temperature or os.environ.get("GEMINI_TEMPERATURE", 0.2))
        except (ValueError, TypeError):
            self.temperature = 0.2

    def is_available(self) -> bool:
        """Check if an API key is configured."""
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        timeout: int = 15
    ) -> Optional[str]:
        """Send generation request to Google AI Studio Gemini REST endpoint."""
        if not self.is_available():
            return None

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 2048,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            return None
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            print(f"[GeminiClient HTTPError {e.code}]: {err_msg}")
            return None
        except Exception as e:
            print(f"[GeminiClient Exception]: {e}")
            return None
