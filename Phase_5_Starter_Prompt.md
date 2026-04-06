# 🚀 SG CUBE — Phase 5: Real Gemini SDK Integration

## Context
You are working on the SG CUBE project (`d:\sg\`). Phases 1–4 are complete. The backend has a Hybrid AI Engine in `ai/llm.py` that tries Ollama offline first and falls back to an online function. **The problem:** the online fallback `ask_online()` currently returns a useless placeholder string instead of calling a real AI API.

This means when Ollama isn't running (which is most of the time), the user gets:
```
"(Online AI): What is Python?"    ← useless
```
Instead of an actual AI-generated answer.

This phase replaces that placeholder with **real Gemini API calls** using the `google-generativeai` SDK.

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\ai\llm.py` — **THE FILE YOU WILL MODIFY.** Read the full 60-line file. Focus on:
  - Line 47-48: `ask_online()` — the placeholder you need to replace
  - Lines 16-25: `_build_context_prompt()` — how context is built (reuse this for Gemini)
  - Lines 51-59: `generate_smart_response()` — the main hybrid router
- `d:\sg\backend\ai\vision.py` — Already has working Gemini Vision REST API calls (lines 43-69). **DO NOT modify this file** — vision is already working.
- `d:\sg\backend\.env` — Contains `GEMINI_API_KEY=AIzaSyCM44zk41ceC8E0o1m3F-6JwhCVuIhLANg`
- `d:\sg\backend\routers\tools.py` — Uses `ask_online()` as fallback (line 22). Fixing `llm.py` automatically fixes all tool endpoints too.

## Goal
Replace the placeholder `ask_online()` function with a real Gemini API call. After this phase, every chat message and every AI tool will return **real AI-generated responses** when Ollama is offline.

## What to do

### 1. Install the Gemini Python SDK
```bash
pip install google-generativeai
```

### 2. Modify `d:\sg\backend\ai\llm.py`
You are modifying ONE file only. Here's exactly what to change:

**A. Add new imports at the top (after existing imports):**
```python
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
```

**B. Add Gemini configuration constants (after the OLLAMA constants):**
```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"  # Fast, cheap, good quality
```

**C. Add Gemini initialization (after the constants):**
```python
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
```

**D. Replace the `ask_online()` function (lines 47-48) with:**
```python
def ask_online(prompt: str, user_id: str) -> str:
    """Online fallback via Google Gemini API."""
    if not GEMINI_API_KEY:
        return "AI is currently unavailable. No API key configured and Ollama is offline."
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Build conversation history for Gemini
        history = CONTEXT_MEMORY.get(user_id, [])
        chat_history = []
        for entry in history:
            chat_history.append({"role": "user", "parts": [entry["user"]]})
            chat_history.append({"role": "model", "parts": [entry["assistant"]]})
        
        # Use chat session for context-aware responses
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API error: {str(e)}"
```

**E. DO NOT change anything else:**
- `ask_ollama()` stays the same
- `_build_context_prompt()` stays the same
- `_save_to_memory()` stays the same
- `generate_smart_response()` stays the same — it already calls `ask_online()` as fallback
- `CONTEXT_MEMORY` stays the same

### 3. DO NOT modify any other files
- `vision.py` — Already uses Gemini REST API directly, already works
- `tools.py` — Uses `ask_online()` from llm.py, will automatically get real responses
- `server.py` — No changes needed
- Frontend files — No changes needed

## After this change, the full file should look like:
```
ai/llm.py (approximately 80 lines):
  - Imports: os, requests, google.generativeai, dotenv
  - Constants: OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, GEMINI_API_KEY, GEMINI_MODEL
  - Gemini init: genai.configure(...)
  - CONTEXT_MEMORY dict
  - _build_context_prompt() — unchanged
  - _save_to_memory() — unchanged
  - ask_ollama() — unchanged
  - ask_online() — NEW real Gemini implementation with chat history
  - generate_smart_response() — unchanged
```

## Critical Rules
- ONLY modify `ai/llm.py`
- DO NOT touch `vision.py`, `tools.py`, `server.py`, or any frontend files
- DO NOT remove or change the Ollama logic — it must still be tried first
- DO NOT change the function signatures (`ask_online(prompt, user_id) -> str`)
- DO NOT change the return type of `generate_smart_response()` — must still return `{"response": "...", "action": "...", "success": True}`
- Handle missing API key gracefully (return error string, don't crash)
- Handle Gemini API errors gracefully (return error string, don't crash)

## Verify
1. `python server.py` starts without errors
2. **Without Ollama running**, type "What is Python?" in chat → should get a **real AI-generated answer** (not the placeholder)
3. Type a follow-up "Tell me more about it" → should get a **context-aware response** (it remembers the previous question)
4. Go to AI Tools → Code Generator → type "Python fibonacci" → should get **real generated code**
5. Go to AI Tools → Summarizer → paste any text → should get **real bullet point summary**
6. Vision AI still works (it uses its own Gemini REST call, not this function)
7. If Ollama IS running, chat should use Ollama first (verify `"action": "chat_offline"` in response)
