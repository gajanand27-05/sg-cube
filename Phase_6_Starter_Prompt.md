# 🚀 SG CUBE — Phase 6: Ollama Local Model Setup

## Context
You are working on the SG CUBE project (`d:\sg\`). Phases 1–5 are complete. The backend has a working Hybrid AI Engine:
- `ai/llm.py` — Tries Ollama offline first, falls back to Gemini SDK online
- Ollama calls are hardcoded to model `"llama3"` on `http://127.0.0.1:11434`

**The problem:** There's no way to check if Ollama is running, what models are available, or switch models. The model name `"llama3"` is hardcoded. If the user has `mistral` or `phi3` installed instead, they can't use it.

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\ai\llm.py` — Read full file. Note `OLLAMA_MODEL = "llama3"` on line 12 is hardcoded.
- `d:\sg\backend\ai\vision.py` — Note `OLLAMA_VISION_MODELS = ["llama3.2-vision", "llava"]` on line 12.
- `d:\sg\backend\server.py` — Read to see where to add new endpoints (before static file mount).
- `d:\sg\frontend\index.html` — Read lines 422-525 for the Settings screen structure. Look for the "VOICE ASSISTANT" settings group as a reference for how settings are structured.
- `d:\sg\frontend\app.js` — Read to understand how settings inputs work (e.g. `server-ip`, `server-port`).

## Goal
1. Add backend endpoints to check Ollama status and list available models
2. Make the text model configurable (not hardcoded)
3. Add a model selector in the frontend Settings screen

## What to do

### 1. Modify `d:\sg\backend\ai\llm.py`
- Change `OLLAMA_MODEL = "llama3"` to a mutable variable that can be updated at runtime:
```python
_current_model = "llama3"

def get_ollama_model():
    return _current_model

def set_ollama_model(model_name: str):
    global _current_model
    _current_model = model_name
```
- Update `ask_ollama()` to use `get_ollama_model()` instead of the constant

### 2. Modify `d:\sg\backend\server.py`
Add three new endpoints BEFORE the static file mount:

**A. Check Ollama status:**
```python
@app.get("/api/ollama/status")
async def ollama_status():
    """Check if Ollama is running and return current model."""
    try:
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"online": True, "models": models, "current_model": get_ollama_model()}
        return {"online": False, "models": [], "current_model": get_ollama_model()}
    except:
        return {"online": False, "models": [], "current_model": get_ollama_model()}
```

**B. List pulled models:**
```python
@app.get("/api/ollama/models")
async def ollama_models():
    """List all models pulled in Ollama."""
    try:
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        resp.raise_for_status()
        models = resp.json().get("models", [])
        return {"success": True, "models": [{"name": m["name"], "size": m.get("size", 0)} for m in models]}
    except:
        return {"success": False, "models": [], "message": "Ollama is not running"}
```

**C. Switch active model:**
```python
@app.post("/api/ollama/model")
async def set_model(body: dict):
    """Change the active Ollama model."""
    model_name = body.get("model", "").strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="Model name required")
    set_ollama_model(model_name)
    return {"success": True, "current_model": model_name}
```

**D. Add imports to server.py:**
```python
from ai.llm import generate_smart_response, get_ollama_model, set_ollama_model
import requests  # if not already imported
```

### 3. Modify `d:\sg\frontend\index.html`
Add a new settings group **inside the Settings screen** (after the "VOICE ASSISTANT" group, before the "APPEARANCE" group). Follow the exact same HTML pattern used by the existing settings groups:

```html
<div class="settings-group">
    <div class="settings-group-label">AI ENGINE</div>
    <div class="setting-item row">
        <div>
            <span class="setting-label">Ollama Status</span>
            <span class="setting-desc" id="ollama-status-text">Checking...</span>
        </div>
        <span class="setting-status" id="ollama-status-dot">
            <i class="fas fa-circle"></i> Offline
        </span>
    </div>
    <div class="setting-item">
        <label class="setting-label" for="ollama-model-select">Active Model</label>
        <select class="setting-select" id="ollama-model-select">
            <option value="">No models found</option>
        </select>
    </div>
    <div class="setting-item row">
        <div>
            <span class="setting-label">Fallback</span>
            <span class="setting-desc">Gemini API (Online)</span>
        </div>
        <span class="setting-status connected"><i class="fas fa-circle"></i> Ready</span>
    </div>
</div>
```

### 4. Modify `d:\sg\frontend\app.js`
Add JavaScript at the END of the file:

**A. Fetch Ollama status on Settings screen load:**
```javascript
async function checkOllamaStatus() {
    const serverIp = document.getElementById('server-ip').value;
    const serverPort = document.getElementById('server-port').value;
    const url = `http://${serverIp}:${serverPort}/api/ollama/status`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        const statusDot = document.getElementById('ollama-status-dot');
        const statusText = document.getElementById('ollama-status-text');
        const modelSelect = document.getElementById('ollama-model-select');
        
        if (data.online) {
            statusDot.innerHTML = '<i class="fas fa-circle"></i> Online';
            statusDot.className = 'setting-status connected';
            statusText.textContent = `${data.models.length} model(s) available`;
            
            // Populate model dropdown
            modelSelect.innerHTML = '';
            data.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                if (m === data.current_model) opt.selected = true;
                modelSelect.appendChild(opt);
            });
        } else {
            statusDot.innerHTML = '<i class="fas fa-circle"></i> Offline';
            statusDot.className = 'setting-status';
            statusText.textContent = 'Ollama not running — using Gemini online';
            modelSelect.innerHTML = '<option value="">Ollama offline</option>';
        }
    } catch(e) {
        console.error('Ollama status check failed:', e);
    }
}
```

**B. Handle model switch:**
```javascript
document.getElementById('ollama-model-select')?.addEventListener('change', async (e) => {
    const model = e.target.value;
    if (!model) return;
    const serverIp = document.getElementById('server-ip').value;
    const serverPort = document.getElementById('server-port').value;
    const url = `http://${serverIp}:${serverPort}/api/ollama/model`;
    await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: model})
    });
});
```

**C. Call `checkOllamaStatus()` when navigating to Settings screen:**
Find the existing navigation logic where screens are switched and add `checkOllamaStatus()` when `screen-settings` becomes active. Or simply call it on page load:
```javascript
checkOllamaStatus();
```

## Critical Rules
- DO NOT break existing `/api/command`, `/api/tools/*`, or `/api/vision` endpoints
- DO NOT change the Gemini SDK integration in `llm.py` (Phase 5 work)
- DO NOT change anything in `vision.py`
- The model selector should be a `<select>` dropdown that auto-populates from the Ollama API, not a text input
- Handle Ollama being offline gracefully everywhere — no crashes, just show "Offline" status

## Verify
1. `python server.py` starts without errors
2. `GET /api/ollama/status` returns `{"online": false, ...}` when Ollama isn't running
3. If Ollama IS running: status returns `{"online": true, "models": ["llama3", ...], "current_model": "llama3"}`
4. Settings screen shows "AI ENGINE" section with status dot and model dropdown
5. If Ollama is online, dropdown populates with available models
6. Switching model via dropdown actually changes what `ask_ollama()` uses
7. All existing endpoints still work
