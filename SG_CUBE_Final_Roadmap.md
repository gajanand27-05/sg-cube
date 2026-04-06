# SG CUBE — Final Combined Roadmap

## What's Already Done (Phases 1–4) ✅

| Phase | What was built | Files |
|-------|---------------|-------|
| 1 | Backend refactoring (monolith → modules) | `ai/llm.py`, `utils/tasks.py`, `server.py` |
| 2 | AI Tools router (codegen, summarizer, resume, notes) | `routers/tools.py` |
| 3 | Vision AI endpoint (Ollama → Gemini → Pillow fallback) | `ai/vision.py`, `server.py` |
| 4 | Frontend modal wiring (tool cards → backend) | `index.html`, `style.css`, `app.js` |

---

## What's Left (Phases 5–9)

### Phase 5: Real Gemini SDK Integration 🔴 CRITICAL
**Why first:** Right now `ask_online()` in `llm.py` returns `"(Online AI): your prompt"` — a useless placeholder. Every tool, every chat message, every vision analysis FAILS when Ollama isn't running. This phase makes the entire app actually functional.

**What to do:**
- Install `google-generativeai` SDK
- Replace placeholder `ask_online()` in `ai/llm.py` with real Gemini API call using `GEMINI_API_KEY`
- Replace placeholder in `ai/vision.py` Gemini fallback with real Gemini Vision API (send image + prompt)
- Add model config (temperature, max_tokens) as constants

---

### Phase 6: Ollama Local Model Setup 🟠 HIGH
**Why second:** Offline AI is the core promise of "Hybrid AI". Right now Ollama calls exist in code but there's no setup or model management.

**What to do:**
- Document Ollama installation steps for Windows
- Add `/api/ollama/status` endpoint to check if Ollama is running and which models are pulled
- Add `/api/ollama/models` endpoint to list available models
- Add model selector in Settings screen (frontend dropdown)
- Handle model switching in `ai/llm.py` (not hardcoded to `"llama3"`)

---

### Phase 7: Chat History & Persistence 🟡 MEDIUM
**Why third:** Currently `CONTEXT_MEMORY` is a Python dictionary — server restart = all conversations lost.

**What to do:**
- Create `chat_history` table in SQLite (`users.db`)
- Save every user/assistant message pair with timestamp and user_id
- Load history on login (populate `CONTEXT_MEMORY` from DB)
- Add conversation history UI in Chat screen (scrollable past sessions)
- Add "Clear History" button

---

### Phase 8: Voice TTS Improvements 🟢 POLISH
**Why fourth:** Current browser Web Speech API works. These are enhancements.

**What to do:**
- Add voice selection dropdown in Settings (use `speechSynthesis.getVoices()`)
- Add speech rate/pitch sliders
- Add streaming TTS (speak response as it arrives, not after full load)
- Optional: Backend Whisper STT endpoint for higher accuracy

---

### Phase 9: System Task Automation Expansion 🟢 POLISH
**Why last:** Current `tasks.py` has basic commands. These are additions for power users.

**What to do:**
- Make "Coding Setup" actually execute: open VS Code, open terminal, run dev server
- Make "Study Mode" actually block distracting sites (edit hosts file or use focus script)
- Add real shutdown/restart with confirmation flow
- Wire Automation screen workflow buttons (Launch Dev Server, Start Database, etc.) to real `subprocess.Popen()` calls
- Add custom command builder in frontend

---

## Summary Comparison

| Feature | My Original Plan | Coder's Plan | ✅ Final Combined |
|---------|-----------------|-------------|-------------------|
| Backend refactoring | ✅ | ✅ | ✅ Phase 1 |
| Context memory | ✅ | ✅ (in Phase 1) | ✅ Phase 1 |
| AI Tools endpoints | ✅ | ✅ | ✅ Phase 2 |
| Vision AI | ✅ | ✅ | ✅ Phase 3 |
| Frontend wiring | ❌ Missing | ✅ | ✅ Phase 4 |
| Real Gemini SDK | ❌ Missing | ✅ | ✅ Phase 5 |
| Ollama model management | ❌ Missing | ✅ | ✅ Phase 6 |
| Chat persistence (SQLite) | ❌ Missing | ✅ | ✅ Phase 7 |
| Voice TTS upgrades | ✅ | ✅ | ✅ Phase 8 |
| System task automation | ✅ | ❌ Missing | ✅ Phase 9 |

**The final combined plan takes the best of both: 9 phases, nothing missing.**
