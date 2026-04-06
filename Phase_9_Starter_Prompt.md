# 🚀 SG CUBE — Phase 9: System Task Automation Expansion (FINAL PHASE)

## Context
You are working on the SG CUBE project (`d:\sg\`). Phases 1–8 are complete. This is the FINAL phase.

**Current problems:**
1. `tasks.py` "Coding Setup" returns text saying "✓ Launching VS Code" but **doesn't actually open VS Code**
2. `tasks.py` "Study Mode" returns text saying "✓ Blocking distracting websites" but **doesn't actually block anything**
3. `tasks.py` "Shutdown" only asks for confirmation but **doesn't handle "confirm shutdown"**
4. System screen's 6 Quick Action buttons (File Manager, Terminal, Task Manager, Run Script, Control Panel, Network) **do nothing when clicked**
5. Automation screen's 5 Workflow items (Launch Dev Server, Start Database, Deploy, Security Scan, Backup) **do nothing when clicked**

## Reference Files (READ THESE FIRST)
- `d:\sg\backend\utils\tasks.py` — Read full file (175 lines). This is the main file you'll modify. Note lines 87-114: "Coding Setup" and "Study Mode" return text but don't execute anything.
- `d:\sg\backend\server.py` — Read to see the `/api/command` pipeline and where to add new endpoints.
- `d:\sg\frontend\index.html` — Read lines 239-320 for Automation screen (Quick Commands + Workflows). Read lines 390-420 for System screen Quick Actions.
- `d:\sg\frontend\app.js` — Read the `setupAutomation()` function. Note: automation cards already call `sendToBackend(label)` which hits `/api/command` and routes through `tasks.py`.

## Goal
Make automation commands actually execute real OS operations on Windows. Add a dedicated `/api/system/action` endpoint for system quick actions.

## What to do

### 1. Modify `d:\sg\backend\utils\tasks.py`
Replace the text-only responses with real `subprocess` calls. Add `import subprocess` at the top.

**A. Replace "Coding Setup" (lines 87-101) with real execution:**
```python
if re.search(r'\b(coding setup|start coding|dev setup|development setup)\b', text_lower):
    steps = []
    try:
        subprocess.Popen(['code'], shell=True)
        steps.append("✓ Launched VS Code")
    except: steps.append("✗ Could not launch VS Code")
    try:
        subprocess.Popen(['start', 'cmd'], shell=True)
        steps.append("✓ Opened Terminal")
    except: steps.append("✗ Could not open Terminal")
    try:
        subprocess.Popen(['start', 'chrome', '--auto-open-devtools-for-tabs'], shell=True)
        steps.append("✓ Opened Chrome with DevTools")
    except: steps.append("✗ Could not open Chrome")
    return {
        "response": "Executing Coding Setup workflow:\n" + "\n".join(steps) + "\nYour coding environment is ready!",
        "action": "coding_setup",
        "success": True,
    }
```

**B. Replace "Study Mode" (lines 103-114) with real execution:**
```python
if re.search(r'\b(study mode|focus mode|study time)\b', text_lower):
    steps = []
    # Close distracting apps
    for app in ['chrome.exe', 'msedge.exe', 'discord.exe']:
        try:
            subprocess.run(['taskkill', '/f', '/im', app], capture_output=True)
            steps.append(f"✓ Closed {app}")
        except: pass
    # Open Notepad for study notes
    try:
        subprocess.Popen(['notepad'], shell=True)
        steps.append("✓ Opened Notepad for study notes")
    except: pass
    if not steps:
        steps.append("✓ No distracting apps found to close")
    steps.append("✓ Focus mode activated")
    return {
        "response": "Study Mode activated:\n" + "\n".join(steps) + "\nGood luck!",
        "action": "study_mode",
        "success": True,
    }
```

**C. Add "confirm shutdown" and "confirm restart" handlers:**
```python
if re.search(r'\bconfirm shutdown\b', text_lower):
    os.system('shutdown /s /t 30')
    return {
        "response": "Shutting down in 30 seconds. Run 'shutdown /a' to cancel.",
        "action": "shutdown",
        "success": True,
    }

if re.search(r'\bconfirm restart\b', text_lower):
    os.system('shutdown /r /t 30')
    return {
        "response": "Restarting in 30 seconds. Run 'shutdown /a' to cancel.",
        "action": "restart",
        "success": True,
    }

if re.search(r'\bcancel shutdown\b', text_lower):
    os.system('shutdown /a')
    return {
        "response": "Shutdown cancelled.",
        "action": "cancel_shutdown",
        "success": True,
    }
```
Place these BEFORE the existing shutdown/restart confirm handlers.

**D. Also replace the existing `os.system("start ...")` calls with `subprocess.Popen()` for consistency (open chrome, vs code, notepad, explorer, terminal).**

### 2. Modify `d:\sg\backend\server.py` — Add system action endpoint

Add a new endpoint for the System screen's Quick Action buttons:

```python
@app.post("/api/system/action")
async def system_action(body: dict):
    """Execute a system quick action."""
    action = body.get("action", "").strip().lower()
    
    import subprocess
    
    actions = {
        "file_manager": ("start explorer", "Opened File Explorer"),
        "terminal": ("start cmd", "Opened Command Prompt"),
        "task_manager": ("start taskmgr", "Opened Task Manager"),
        "control_panel": ("start control", "Opened Control Panel"),
        "network": ("start ms-settings:network", "Opened Network Settings"),
    }
    
    if action in actions:
        cmd, msg = actions[action]
        try:
            subprocess.Popen(cmd, shell=True)
            return {"success": True, "response": msg}
        except Exception as e:
            return {"success": False, "response": f"Error: {str(e)}"}
    
    return JSONResponse(status_code=400, content={"success": False, "response": f"Unknown action: {action}"})
```

### 3. Modify `d:\sg\frontend\index.html`

**A. Add `data-action` attributes to the System Quick Action buttons (lines 393-418):**
```html
<button class="sys-action-btn" data-action="file_manager">
    <i class="fas fa-folder-open"></i>
    <span>File Manager</span>
</button>
<button class="sys-action-btn" data-action="terminal">
    <i class="fas fa-terminal"></i>
    <span>Terminal</span>
</button>
<button class="sys-action-btn" data-action="task_manager">
    <i class="fas fa-display"></i>
    <span>Task Manager</span>
</button>
<button class="sys-action-btn" data-action="run_script">
    <i class="fas fa-scroll"></i>
    <span>Run Script</span>
</button>
<button class="sys-action-btn" data-action="control_panel">
    <i class="fas fa-sliders"></i>
    <span>Control Panel</span>
</button>
<button class="sys-action-btn" data-action="network">
    <i class="fas fa-wifi"></i>
    <span>Network</span>
</button>
```

**B. Add `data-workflow` attributes to the Workflow items (lines 277-317):**
```html
<button class="auto-list-item" data-workflow="dev_server">...</button>
<button class="auto-list-item" data-workflow="database">...</button>
<button class="auto-list-item" data-workflow="deploy">...</button>
<button class="auto-list-item" data-workflow="security">...</button>
<button class="auto-list-item" data-workflow="backup">...</button>
```

### 4. Modify `d:\sg\frontend\app.js`

**A. Add System Quick Action click handlers:**
```javascript
document.querySelectorAll('.sys-action-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const action = btn.dataset.action;
        if (!action) return;
        
        const url = getServerUrl();
        try {
            const res = await fetch(`${url}/api/system/action`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: action })
            });
            const data = await res.json();
            showToast(data.success ? 'fa-check-circle' : 'fa-exclamation-triangle', data.response);
        } catch(e) {
            showToast('fa-exclamation-triangle', 'Failed to execute action');
        }
    });
});
```

**B. The Workflow buttons already work via `sendToBackend()` in `setupAutomation()` — no JS changes needed for those.** The existing automation cards already call `sendToBackend(label)` which routes through `/api/command` → `tasks.py`. Just make sure the label text matches the regex patterns.

## Critical Rules
- ALL OS commands must use `subprocess.Popen()` with `shell=True` (not `os.system()`) for non-blocking execution
- Shutdown/restart must have a 30-second delay (`/t 30`) so the user can cancel
- DO NOT break any existing endpoints
- Handle errors gracefully — if an app can't be opened, report it but don't crash
- The "Run Script" quick action can show a toast saying "Coming soon" for now

## Verify
1. `python server.py` starts without errors
2. Automation → "Open Chrome" → Chrome actually opens
3. Automation → "Coding Setup" → VS Code, Terminal, and Chrome all open
4. Automation → "Study Mode" → Distracting apps close, Notepad opens
5. Chat → "confirm shutdown" → system schedules shutdown in 30s, then "cancel shutdown" cancels it
6. System → "File Manager" button → Explorer opens
7. System → "Terminal" button → CMD opens
8. System → "Task Manager" button → Task Manager opens
9. System → "Control Panel" button → Control Panel opens
10. All other endpoints still work
