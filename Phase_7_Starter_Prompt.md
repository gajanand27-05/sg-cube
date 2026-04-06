# 🚀 SG CUBE — Phase 7: Chat History & Persistence

## Context
You are working on the SG CUBE project (`d:\sg\`). Phases 1–6 are complete. The backend has a working Hybrid AI Engine with Gemini SDK and Ollama model switching.

**The problem:** Chat history lives in a Python dictionary (`CONTEXT_MEMORY` in `ai/llm.py`). When the server restarts, ALL conversations are lost. There is no way to view past conversations.

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\ai\llm.py` — Read full file. Focus on `CONTEXT_MEMORY`, `_save_to_memory()`, and `_build_context_prompt()`.
- `d:\sg\backend\server.py` — Read full file. Focus on:
  - Lines 65-108: Database setup (`get_db()`, `init_db()`, SQLite tables)
  - Lines 171-180: `/api/command` endpoint (uses `generate_smart_response()` with `user_id=request.client.host`)
  - The `DB_PATH` variable pointing to `users.db`
- `d:\sg\frontend\app.js` — Read full file. Focus on:
  - Lines 269-311: `sendToBackend()` — sends voice commands to `/api/command`
  - Lines 479-526: `setupChat()` — sends chat messages to `/api/command`
  - Lines 528-550: `addChatBubble()` — creates chat bubble DOM elements
- `d:\sg\frontend\index.html` — Read lines 148-237 for the Chat screen structure. Note the hardcoded demo bubbles and the clear chat button (line 153).

## Goal
1. Save every chat message (user + AI response) to SQLite
2. Load chat history when the user opens the chat screen
3. Add a "Clear History" button that clears both the DB and the UI
4. Remove the hardcoded demo chat bubbles from the HTML

## What to do

### 1. Modify `d:\sg\backend\server.py` — Add chat_history table

**A. Add a new table in `init_db()` (inside the existing function, after the `app_settings` table creation):**
```python
c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)''')
```

**B. Add a save chat endpoint:**
```python
@app.post("/api/chat/save")
async def save_chat(body: dict):
    """Save a chat message pair to the database."""
    user_id = body.get("user_id", "default")
    user_msg = body.get("user_message", "")
    ai_msg = body.get("ai_message", "")
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO chat_history (user_id, role, message) VALUES (?, 'user', ?)", (user_id, user_msg))
            c.execute("INSERT INTO chat_history (user_id, role, message) VALUES (?, 'assistant', ?)", (user_id, ai_msg))
            conn.commit()
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
```

**C. Add a load chat history endpoint:**
```python
@app.get("/api/chat/history")
async def get_chat_history(user_id: str = "default", limit: int = 50):
    """Load recent chat history for a user."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT role, message, timestamp FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
            rows = c.fetchall()
        # Reverse so oldest first
        messages = [{"role": r["role"], "message": r["message"], "timestamp": r["timestamp"]} for r in reversed(rows)]
        return {"success": True, "messages": messages}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
```

**D. Add a clear chat history endpoint:**
```python
@app.delete("/api/chat/history")
async def clear_chat_history(user_id: str = "default"):
    """Clear all chat history for a user."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
            conn.commit()
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
```

Place all these endpoints BEFORE the static file mount.

### 2. Modify `d:\sg\backend\ai\llm.py` — Load context from DB on startup

**A. Add a function to seed CONTEXT_MEMORY from the database:**
```python
def load_context_from_db(db_path: str, user_id: str):
    """Load recent chat history from SQLite into CONTEXT_MEMORY."""
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT role, message FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT 20",
            (user_id,)
        )
        rows = list(reversed(c.fetchall()))
        conn.close()
        
        # Build memory pairs
        history = []
        for i in range(0, len(rows) - 1, 2):
            if rows[i]["role"] == "user" and i + 1 < len(rows) and rows[i + 1]["role"] == "assistant":
                history.append({"user": rows[i]["message"], "assistant": rows[i + 1]["message"]})
        CONTEXT_MEMORY[user_id] = history[-10:]
    except Exception:
        pass
```

**B. Call it in `generate_smart_response()` if user has no memory yet:**
```python
def generate_smart_response(prompt: str, user_id: str = "default", db_path: str = None) -> dict:
    # Auto-load from DB if no context exists for this user
    if user_id not in CONTEXT_MEMORY and db_path:
        load_context_from_db(db_path, user_id)
    
    # ... rest of existing logic unchanged
```

**C. Update the call in `server.py`:**
Change line 179 from:
```python
result = generate_smart_response(text, user_id=request.client.host)
```
To:
```python
result = generate_smart_response(text, user_id=request.client.host, db_path=DB_PATH)
```

### 3. Modify `d:\sg\frontend\index.html`

**A. Remove hardcoded demo chat bubbles:**
Delete everything inside `<div class="chat-container" id="chat-container">` EXCEPT the date divider. It should become:
```html
<div class="chat-container" id="chat-container">
    <div class="chat-date-divider"><span>Today</span></div>
</div>
```

**B. Wire the clear chat button (already exists in the header as a trash icon):**
Give it an ID:
```html
<button class="header-action" aria-label="Clear chat" id="btn-clear-chat"><i class="fas fa-trash-alt"></i></button>
```

### 4. Modify `d:\sg\frontend\app.js`

**A. After a successful chat response, save to DB:**
In `setupChat()`, after `addChatBubble('ai', data.response ...)`, add:
```javascript
// Save to persistent history
fetch(`${url}/api/chat/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 'default',
        user_message: text,
        ai_message: data.response || 'Command processed.'
    })
});
```

Do the same in `sendToBackend()` (the voice command handler, lines 288-292).

**B. Load history when Chat screen becomes active:**
In the navigation logic (around line 106), after `if (target === 'screen-system')`, add:
```javascript
if (target === 'screen-chat') {
    loadChatHistory();
}
```

**C. Add `loadChatHistory()` function:**
```javascript
async function loadChatHistory() {
    const url = getServerUrl();
    try {
        const res = await fetch(`${url}/api/chat/history?user_id=default&limit=50`);
        const data = await res.json();
        if (data.success && data.messages.length > 0) {
            // Clear current bubbles (keep date divider)
            const container = document.getElementById('chat-container');
            const divider = container.querySelector('.chat-date-divider');
            container.innerHTML = '';
            if (divider) container.appendChild(divider);
            
            // Add bubbles from history
            data.messages.forEach(msg => {
                addChatBubble(msg.role === 'user' ? 'user' : 'ai', msg.message);
            });
        }
    } catch(e) {
        console.log('Could not load chat history:', e);
    }
}
```

**D. Add clear chat handler:**
```javascript
document.getElementById('btn-clear-chat')?.addEventListener('click', async () => {
    const url = getServerUrl();
    await fetch(`${url}/api/chat/history?user_id=default`, { method: 'DELETE' });
    
    // Clear UI
    const container = document.getElementById('chat-container');
    container.innerHTML = '<div class="chat-date-divider"><span>Today</span></div>';
    
    showToast('fa-trash-alt', 'Chat history cleared');
});
```

## API Contracts (new endpoints)
| Endpoint | Method | Params/Body | Response |
|----------|--------|-------------|----------|
| `/api/chat/save` | POST | `{"user_id": "...", "user_message": "...", "ai_message": "..."}` | `{"success": true}` |
| `/api/chat/history` | GET | `?user_id=default&limit=50` | `{"success": true, "messages": [...]}` |
| `/api/chat/history` | DELETE | `?user_id=default` | `{"success": true}` |

## Critical Rules
- DO NOT break existing `/api/command`, `/api/tools/*`, `/api/vision`, `/api/ollama/*` endpoints
- DO NOT change the Gemini SDK or Ollama logic
- Chat saving should be fire-and-forget (don't await it in the main chat flow, don't block the UI)
- Handle empty DB gracefully (first-time user sees empty chat, no errors)
- The `user_id` can be `"default"` for now (proper user session mapping comes later)

## Verify
1. `python server.py` starts without errors (new table auto-created)
2. Open chat, type "Hello" → AI responds → message saved to DB
3. Restart the server (`Ctrl+C` then `python server.py`)
4. Open chat screen → previous messages reload from DB automatically
5. Click the trash icon → chat clears in UI and DB
6. Type new messages → they save and persist through restarts
7. All other endpoints still work
