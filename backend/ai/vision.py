"""
SG CUBE — Vision AI Engine
Image analysis via Ollama multimodal → Gemini Vision REST → Pillow metadata fallback.
"""

import os
import io
import base64
import requests

OLLAMA_VISION_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_VISION_MODELS = ["llama3.2-vision", "llava"]
OLLAMA_VISION_TIMEOUT = 15

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def _try_ollama_vision(image_bytes: bytes, prompt: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    for model in OLLAMA_VISION_MODELS:
        try:
            resp = requests.post(
                OLLAMA_VISION_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [b64],
                    "stream": False,
                },
                timeout=OLLAMA_VISION_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
            if text:
                return text
        except Exception:
            continue
    raise RuntimeError("Ollama vision models unavailable")


def _try_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("No GEMINI_API_KEY configured")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    resp = requests.post(
        f"{GEMINI_VISION_URL}?key={GEMINI_API_KEY}",
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64,
                            }
                        },
                    ]
                }
            ]
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return text.strip()


def _fallback_metadata(image_bytes: bytes) -> str:
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        return (
            f"Image metadata — Format: {img.format}, "
            f"Size: {img.size[0]}x{img.size[1]} pixels, "
            f"Mode: {img.mode}, "
            f"File size: {len(image_bytes)} bytes. "
            f"Full vision analysis requires a vision model (Ollama llava/llama3.2-vision or Gemini)."
        )
    except Exception:
        return (
            f"Image file size: {len(image_bytes)} bytes. "
            f"Full vision analysis requires a vision model (Ollama llava/llama3.2-vision or Gemini)."
        )


def analyze_image(
    image_bytes: bytes, prompt: str = "Describe this image in detail"
) -> str:
    try:
        return _try_ollama_vision(image_bytes, prompt)
    except Exception:
        pass
    try:
        return _try_gemini_vision(image_bytes, prompt)
    except Exception:
        pass
    return _fallback_metadata(image_bytes)
