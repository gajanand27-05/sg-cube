# 🚀 SG CUBE — Phase 1: Backend Architecture Refactoring

## Context
You are working on the SG CUBE project — a Jarvis-inspired AI assistant with a FastAPI backend and HTML/CSS/JS frontend. The project lives at `d:\sg\`.

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\server.py` — Current monolithic backend (545 lines). Read the FULL file.
- `d:\sg\backend\.env` — API keys (GEMINI_API_KEY)
- `d:\sg\frontend\app.js` — Frontend JS that calls the backend APIs. Read to understand the API contracts.

## Goal
Split the monolithic `server.py` into clean modules:

```
backend/
├── server.py         ← MODIFY (thin API layer, imports from modules)
├── ai/
│   ├── __init__.py   ← NEW (empty)
│   └── llm.py        ← NEW (Hybrid AI: Ollama offline + Gemini online + context memory)
└── utils/
    ├── __init__.py   ← NEW (empty)
    └── tasks.py      ← NEW (OS commands extracted from server.py's handle_command)
```

## What to do

### 1. Create `backend/ai/llm.py`
Build a Hybrid AI Engine:
- `CONTEXT_MEMORY = {}` — stores conversation history per user_id (keep last 10 messages)
- `ask_ollama(prompt, user_id)` — POST to `http://127.0.0.1:11434/api/generate` with model `"llama3"`, prepend context, timeout 5s. Raise exception on failure.
- `ask_online(prompt, user_id)` — Fallback using `GEMINI_API_KEY` from env. For now, can return placeholder string like `"(Online AI): {prompt}"`. Real Gemini SDK integration comes later.
- `generate_smart_response(prompt, user_id)` — Try offline first, catch exception → fallback to online. Return `{"response": "...", "action": "chat_offline"/"chat_online", "success": True}`

### 2. Create `backend/utils/tasks.py`
Extract the `handle_command()` function (lines 364-508 of server.py) into:
- `handle_os_command(text: str) -> dict | None`
- Keep ALL existing regex patterns and responses EXACTLY the same (greetings, system status, open apps, coding setup, study mode, shutdown, restart, time, date, identity, help)
- For OS actions (open chrome, notepad, etc.) actually execute them with `os.system("start ...")` on Windows
- If nothing matches → return `None` (not a dict), which tells server.py to route to the AI engine

### 3. Modify `backend/server.py`
- Add imports: `from ai.llm import generate_smart_response` and `from utils.tasks import handle_os_command`
- Change `/api/command` endpoint: First try `handle_os_command(text)` → if None, call `generate_smart_response(text, user_id=request.client.host)`
- Add `request: Request` to the endpoint signature
- DELETE the entire `handle_command()` function (it's now split across tasks.py and llm.py)
- **KEEP EVERYTHING ELSE UNCHANGED**: database, login, register, admin endpoints, system info, static file serving

## API Contract (DO NOT BREAK)
The frontend expects `/api/command` to return: `{"response": "...", "action": "...", "success": true/false}`
All other endpoints must remain identical.

## Critical Rules
- DO NOT modify any frontend files
- DO NOT change the API response format
- DO NOT delete database/auth/admin logic
- Server must remain on port 5000

## Verify
1. `python server.py` starts without errors
2. `http://localhost:5000/` loads the UI
3. `http://localhost:5000/docs` shows Swagger
4. Login with admin/admin works
5. Typing "hello" in chat returns a response
6. Typing "system status" returns real CPU/RAM data
