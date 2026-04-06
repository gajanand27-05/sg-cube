"""
SG CUBE — Hybrid AI Engine
Offline Ollama + Online Gemini fallback with context memory.
"""

import os
import sqlite3
import requests
from google import genai

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

CONTEXT_MEMORY = {}

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
_ollama_model = "llama3"
OLLAMA_TIMEOUT = 5


def get_ollama_model():
    return _ollama_model


def set_ollama_model(model_name: str):
    global _ollama_model
    _ollama_model = model_name


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def load_context_from_db(db_path: str, user_id: str):
    """Load recent chat history from SQLite into CONTEXT_MEMORY."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT role, message FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT 20",
            (user_id,),
        )
        rows = list(reversed(c.fetchall()))
        conn.close()

        history = []
        for i in range(0, len(rows) - 1, 2):
            if (
                rows[i]["role"] == "user"
                and i + 1 < len(rows)
                and rows[i + 1]["role"] == "assistant"
            ):
                history.append(
                    {"user": rows[i]["message"], "assistant": rows[i + 1]["message"]}
                )
        CONTEXT_MEMORY[user_id] = history[-10:]
    except Exception:
        pass


def _build_context_prompt(prompt: str, user_id: str) -> str:
    history = CONTEXT_MEMORY.get(user_id, [])
    context_lines = []
    for entry in history:
        context_lines.append(f"User: {entry['user']}")
        context_lines.append(f"Assistant: {entry['assistant']}")
    if context_lines:
        context_block = "\n".join(context_lines)
        return f"Previous conversation:\n{context_block}\n\nCurrent question: {prompt}"
    return prompt


def _save_to_memory(user_id: str, prompt: str, response: str):
    history = CONTEXT_MEMORY.setdefault(user_id, [])
    history.append({"user": prompt, "assistant": response})
    if len(history) > 10:
        CONTEXT_MEMORY[user_id] = history[-10:]


def ask_ollama(prompt: str, user_id: str) -> str:
    full_prompt = _build_context_prompt(prompt, user_id)
    resp = requests.post(
        OLLAMA_URL,
        json={"model": get_ollama_model(), "prompt": full_prompt, "stream": False},
        timeout=OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def ask_online(prompt: str, user_id: str) -> str:
    """Online fallback via Google Gemini API."""
    if not GEMINI_API_KEY:
        return (
            "AI is currently unavailable. No API key configured and Ollama is offline."
        )

    try:
        if client is None:
            return "Gemini API client not initialized."

        history = CONTEXT_MEMORY.get(user_id, [])
        chat_contents = []
        for entry in history:
            chat_contents.append({"role": "user", "parts": [{"text": entry["user"]}]})
            chat_contents.append({"role": "model", "parts": [{"text": entry["assistant"]}]})
        
        chat_contents.append({"role": "user", "parts": [{"text": prompt}]})

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=chat_contents
        )
        return response.text.strip()
    except Exception as e:
        return f"Gemini API error: {str(e)}"


def generate_smart_response(
    prompt: str, user_id: str = "default", db_path: str = None
) -> dict:
    if user_id not in CONTEXT_MEMORY and db_path:
        load_context_from_db(db_path, user_id)

    try:
        response_text = ask_ollama(prompt, user_id)
        _save_to_memory(user_id, prompt, response_text)
        return {"response": response_text, "action": "chat_offline", "success": True}
    except Exception:
        response_text = ask_online(prompt, user_id)
        _save_to_memory(user_id, prompt, response_text)
        return {"response": response_text, "action": "chat_online", "success": True}
