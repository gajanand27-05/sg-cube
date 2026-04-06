# 🚀 SG CUBE — Phase 2: Web AI Tools Integration

## Context
You are working on the SG CUBE project (`d:\sg\`). Phase 1 is complete! The backend now has a modular architecture with `ai/llm.py`, `utils/tasks.py`, and `server.py`.

In Phase 2, we need to create dedicated backend endpoints for the 6 AI Tools shown in the UI (Code Generator, Summarizer, Resume Builder, Notes Organizer, Vision AI, and Chatbot).

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\ai\llm.py` — Contains the Hybrid AI logic (`ask_ollama`, `ask_online`)
- `d:\sg\backend\server.py` — The core FastAPI application.

## Goal
Build a new router for AI tools that leverages our existing Hybrid AI engine, and register it with the main server.

```
backend/
├── server.py         ← MODIFY (Import and include the tools router)
├── routers/
│   ├── __init__.py   ← NEW (empty)
│   └── tools.py      ← NEW (FastAPI router with endpoints for each tool)
```

## What to do

### 1. Create `backend/routers/tools.py`
Create a FastAPI router to handle specific AI tasks using custom system prompts:
- Initialize `tool_router = APIRouter(prefix="/api/tools")`
- Create a `ToolRequest` Pydantic model: `{ "input_data": str }`
- Create a helper wrapper `safe_llm_call(prompt: str)` that tries `ask_ollama(prompt, "tool_user")` and falls back to `ask_online(prompt, "tool_user")` on failure.
- Create the following POST endpoints that wrap the user's input with specific instructions before passing to the LLM:
  - `/codegen`: Prompt = "Generate production-ready code for: {input_data}. Return only the code."
  - `/summarizer`: Prompt = "Summarize the following text accurately in bullet points: {input_data}"
  - `/resume`: Prompt = "Format the following career data into a professional Markdown Resume: {input_data}"
  - `/notes`: Prompt = "Organize the following raw ideas into structured meeting notes: {input_data}"
  - *(Note: We will handle Vision AI in Phase 3, you can skip it for now)*

### 2. Modify `backend/server.py`
- Add import: `from routers.tools import tool_router`
- Register the router right before the static file mounting: `app.include_router(tool_router)`

## API Contract (DO NOT BREAK)
The frontend will expect the following when calling the tool endpoints (`/api/tools/codegen`, etc.):
**Method:** POST
**Body:** `{ "input_data": "..." }`
**Response:** `{ "result": "..." }`

## Critical Rules
- DO NOT break the existing `/api/command` flow.
- DO NOT modify the context memory structure in `ai/llm.py`.
- Server must remain on port 5000.

## Verify
1. `python server.py` starts without errors.
2. `http://localhost:5000/docs` shows the new `/api/tools/codegen`, `/api/tools/summarizer`, etc. endpoints under the Swagger UI.
3. Sending a POST request to `/api/tools/summarizer` correctly invokes the Ollama/Online model and returns a summary.
