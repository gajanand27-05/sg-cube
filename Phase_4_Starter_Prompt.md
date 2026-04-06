# 🚀 SG CUBE — Phase 4: Frontend ↔ Backend Tool Wiring

## Context
You are working on the SG CUBE project (`d:\sg\`). The backend is fully modular:
- `ai/llm.py` — Hybrid AI (Ollama + online fallback + context memory)
- `ai/vision.py` — Image analysis (Ollama vision → Gemini Vision → Pillow fallback)
- `routers/tools.py` — AI tool endpoints: `/api/tools/codegen`, `/api/tools/summarizer`, `/api/tools/resume`, `/api/tools/notes`
- `server.py` — Main app with `/api/command`, `/api/vision`, tool router, auth, admin

The frontend already has an **AI Tools screen** (`id="screen-tools"`) with 6 clickable tool cards:
- `data-tool="chatbot"` — Chatbot (AI Conversations)
- `data-tool="codegen"` — Code Generator
- `data-tool="summarizer"` — Summarizer
- `data-tool="resume"` — Resume Builder
- `data-tool="notes"` — Notes Organizer
- `data-tool="vision"` — Vision AI (Image Analysis)

These cards currently do **nothing** when clicked. This phase wires them to the backend.

## Reference Files (READ THESE FIRST)
- `d:\sg\frontend\index.html` — Read lines 737-783 for the AI Tools screen structure. Read lines 785-822 for the bottom nav.
- `d:\sg\frontend\app.js` — Read the FULL file. Understand the existing screen navigation logic (look for `data-target`, `screen.active` class toggling), the existing chat send logic, and the server URL construction (`server-ip`, `server-port`).
- `d:\sg\frontend\style.css` — Read to understand existing design tokens (CSS variables on `:root`). Key colors: `--cyan`, `--bg-card`, `--border-glow`, `--text-primary`, etc. Fonts: `--font-display` (Orbitron), `--font-body` (Rajdhani), `--font-mono` (Share Tech Mono).
- `d:\sg\backend\routers\tools.py` — Read to see the exact API contract for each tool endpoint.

## Goal
When a user taps a tool card, a **modal/overlay** opens with:
1. A title (e.g. "Code Generator")
2. A textarea for input
3. A "Submit" / "Generate" button
4. A results area that displays the AI response
5. A close/back button

For the Vision AI card specifically, it needs a **file upload input** instead of a textarea.

The "Chatbot" card should navigate the user to the existing Chat screen (`screen-chat`).

## What to do

### 1. Modify `d:\sg\frontend\index.html`
Add a single **reusable tool modal** somewhere before `</body>` and before `<script src="app.js">`:

```html
<!-- ========== TOOL MODAL (Shared by all tools) ========== -->
<div class="tool-modal-overlay" id="tool-modal" style="display:none;">
    <div class="tool-modal">
        <div class="tool-modal-header">
            <h3 class="tool-modal-title" id="tool-modal-title">Tool</h3>
            <button class="tool-modal-close" id="tool-modal-close"><i class="fas fa-times"></i></button>
        </div>
        <div class="tool-modal-body">
            <!-- Text input (for codegen, summarizer, resume, notes) -->
            <textarea class="tool-modal-input" id="tool-modal-input" placeholder="Enter your text..." rows="6"></textarea>
            <!-- File input (for vision) -->
            <div class="tool-modal-file-area" id="tool-modal-file-area" style="display:none;">
                <label for="tool-modal-file" class="tool-file-label">
                    <i class="fas fa-cloud-arrow-up"></i>
                    <span>Upload Image</span>
                </label>
                <input type="file" id="tool-modal-file" accept="image/*" style="display:none;">
                <span class="tool-file-name" id="tool-file-name"></span>
            </div>
            <!-- Optional prompt for vision -->
            <input type="text" class="tool-modal-prompt" id="tool-modal-prompt" placeholder="Ask a question about the image..." style="display:none;">
            <button class="tool-modal-submit" id="tool-modal-submit">
                <i class="fas fa-bolt"></i> Generate
            </button>
        </div>
        <div class="tool-modal-result" id="tool-modal-result" style="display:none;">
            <div class="tool-result-label">RESULT</div>
            <pre class="tool-result-text" id="tool-result-text"></pre>
        </div>
    </div>
</div>
```

### 2. Modify `d:\sg\frontend\style.css`
Add styles for the tool modal at the END of the file. Use the existing design tokens. The modal should:
- Have a full-screen dark overlay (`rgba(0,0,0,0.85)` backdrop)
- Center a card with `var(--bg-card)` background, `var(--border-glow)` border, `var(--radius)` border radius
- Use `var(--font-display)` for the title, `var(--font-body)` for text
- The submit button should match the existing `chat-send-btn` gradient style (`var(--cyan)` to `var(--blue)`)
- The result area should have a monospace font (`var(--font-mono)`) with `var(--cyan-subtle)` background
- The file upload label should have a dashed border with `var(--cyan-dim)` color
- Add smooth fade-in animation for the overlay

### 3. Modify `d:\sg\frontend\app.js`
Add JavaScript at the END of the file to:

**A. Handle tool card clicks:**
```javascript
document.querySelectorAll('.tool-card').forEach(card => {
    card.addEventListener('click', () => {
        const tool = card.dataset.tool;
        if (tool === 'chatbot') {
            // Navigate to chat screen (use existing screen switching logic)
            return;
        }
        openToolModal(tool);
    });
});
```

**B. `openToolModal(toolName)` function:**
- Set the modal title based on toolName (e.g. "codegen" → "Code Generator")
- Show/hide the textarea vs file input based on whether it's "vision" or not
- Show/hide the vision prompt input for "vision"
- Clear previous results
- Display the modal (`style.display = 'flex'`)

**C. Handle submit button click:**
- Get the server URL from existing `server-ip` and `server-port` inputs
- For text tools (codegen, summarizer, resume, notes): `POST /api/tools/{toolName}` with `{"input_data": textareaValue}`
- For vision: `POST /api/vision` with `FormData` containing the file, plus optional `?prompt=` query param
- Show a loading state on the button
- Display the result in `tool-result-text`

**D. Handle close button:**
- Hide the modal, clear inputs and results

## API Contracts (backend already built)
| Tool | Endpoint | Method | Body | Response |
|------|----------|--------|------|----------|
| codegen | `/api/tools/codegen` | POST | `{"input_data": "..."}` | `{"result": "..."}` |
| summarizer | `/api/tools/summarizer` | POST | `{"input_data": "..."}` | `{"result": "..."}` |
| resume | `/api/tools/resume` | POST | `{"input_data": "..."}` | `{"result": "..."}` |
| notes | `/api/tools/notes` | POST | `{"input_data": "..."}` | `{"result": "..."}` |
| vision | `/api/vision` | POST | `multipart/form-data (file)` | `{"success": true, "description": "..."}` |

## Critical Rules
- DO NOT modify any backend files
- Use the server URL from `document.getElementById('server-ip').value` and `document.getElementById('server-port').value` (already used by existing code for `/api/command`)
- Match the existing futuristic dark UI style exactly — use CSS variables, not hardcoded colors
- The modal must work on mobile (max-width: 480px viewport)
- Handle errors gracefully — show error text in the result area if the API call fails

## Verify
1. Open the frontend, login, go to the AI Tools screen (bottom nav "Tools" tab)
2. Click "Code Generator" → modal opens with textarea → type "Python fibonacci" → click Generate → result appears
3. Click "Vision AI" → modal opens with file upload → pick an image → click Generate → description appears
4. Click "Chatbot" → navigates to the Chat screen (no modal)
5. Close button dismisses the modal cleanly
6. All existing screens (Home, Chat, Automation, System, Settings, Admin) still work normally
