# 🚀 SG CUBE — Phase 3: Vision AI Capabilities

## Context
You are working on the SG CUBE project (`d:\sg\`). The backend is modular:
- `ai/llm.py` — Hybrid AI Engine (Ollama offline + online fallback + context memory)
- `utils/tasks.py` — OS command handler
- `routers/tools.py` — AI tool endpoints (codegen, summarizer, resume, notes)
- `server.py` — Main FastAPI app that imports all modules

Phase 1 (refactoring) and Phase 2 (AI tools) are complete. Now we add Vision AI — the ability to upload an image and receive a text description/analysis.

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\server.py` — The main FastAPI app. You will add a new endpoint here.
- `d:\sg\backend\ai\llm.py` — The hybrid AI engine. You will reference the `ask_ollama` / `ask_online` pattern.
- `d:\sg\backend\routers\tools.py` — Example of how tool endpoints are structured.
- `d:\sg\frontend\index.html` — The frontend UI (827 lines). Look for the existing "Vision AI" or camera-related sections.
- `d:\sg\frontend\app.js` — Frontend JS (1046 lines). Look for any vision/camera related functions.

## Goal
Add image analysis capabilities. A user can upload an image file via the frontend, and the backend processes it and returns a text description.

```
backend/
├── ai/
│   ├── llm.py         ← UNCHANGED
│   └── vision.py      ← NEW — Image analysis logic
├── server.py          ← MODIFY — Add /api/vision endpoint
```

## What to do

### 1. Create `backend/ai/vision.py`
Build image analysis using one of these approaches (pick whichever works best given installed dependencies):

**Option A: Using Gemini Vision API (Recommended — lightweight, no heavy ML deps)**
```
- Use GEMINI_API_KEY from .env
- Send image bytes to Gemini's vision endpoint
- Return the text description
```

**Option B: Using Ollama multimodal model (if available)**
```
- POST to http://127.0.0.1:11434/api/generate with model "llava" or "llama3.2-vision"
- Send base64-encoded image in the "images" field
- Return the response text
```

**Option C: Placeholder (if no vision model is available)**
```
- Accept image bytes
- Return basic metadata: file size, dimensions (using Pillow), format
- Return a message saying "Full vision analysis requires a vision model"
```

The function signature must be:
```python
def analyze_image(image_bytes: bytes, prompt: str = "Describe this image in detail") -> str:
```

Implement a hybrid approach: Try Ollama vision first → fall back to Gemini Vision → fall back to placeholder metadata.

### 2. Modify `backend/server.py`
Add a new endpoint:

```python
from ai.vision import analyze_image
from fastapi import UploadFile, File

@app.post("/api/vision")
async def process_vision(file: UploadFile = File(...)):
    image_bytes = await file.read()
    description = analyze_image(image_bytes)
    return {"success": True, "description": description}
```

Place this endpoint BEFORE the `app.include_router(tool_router)` line and BEFORE the static file mount.

### 3. (Optional) Add a simple vision prompt parameter
Allow an optional query parameter so the user can ask specific questions about the image:
```
POST /api/vision?prompt=What objects are in this image?
```

## API Contract
**Endpoint:** `POST /api/vision`
**Content-Type:** `multipart/form-data`
**Body:** Form field named `file` containing the image
**Optional Query Param:** `prompt` (string, default: "Describe this image in detail")
**Response:** `{"success": true, "description": "..."}`

## Dependencies
You may need to install:
```bash
pip install Pillow    # For image metadata fallback
```

## Critical Rules
- DO NOT modify `ai/llm.py` or `routers/tools.py`
- DO NOT break existing `/api/command` or `/api/tools/*` endpoints
- Server must remain on port 5000
- The vision endpoint must gracefully handle errors (bad image format, model unavailable) and return a meaningful error message instead of crashing

## Verify
1. `python server.py` starts without errors
2. `http://localhost:5000/docs` shows the new `/api/vision` endpoint
3. Upload a test image via Swagger UI → should return a description string (or metadata if no vision model is available)
4. Existing endpoints (`/api/command`, `/api/tools/codegen`, etc.) still work
