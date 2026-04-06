"""
SG CUBE — Backend Server (FastAPI)
FastAPI server providing API endpoints for the SG CUBE AI assistant.
Serves the frontend and handles voice commands.
"""

import os
import platform
import psutil
import sqlite3
import hashlib
import random
import smtplib
import sys
import subprocess
from email.message import EmailMessage
from datetime import datetime
from contextlib import contextmanager

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Module Path Setup ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
DB_PATH = os.path.join(BASE_DIR, 'users.db')
sys.path.insert(0, BASE_DIR)

from ai.llm import generate_smart_response, get_ollama_model, set_ollama_model, load_context_from_db
from utils.tasks import handle_os_command
from routers.tools import tool_router
from ai.vision import analyze_image
import requests as http_requests

# ── API Keys ──
API_KEY = os.getenv('API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ── FastAPI App ──
app = FastAPI(
    title="SG CUBE API",
    description="Smart General Contextual Unified Brain Engine",
    version="2.0.0"
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  Database
# ============================================================

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            method TEXT,
            ip TEXT,
            status_code INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute("SELECT id FROM users WHERE username='admin'")
        if not c.fetchone():
            admin_hash = hashlib.sha256('admin'.encode()).hexdigest()
            c.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      ('admin', 'admin@sgcube.local', admin_hash, 'admin'))
        conn.commit()


init_db()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def log_request(endpoint: str, method: str, ip: str, status_code: int):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO request_logs (endpoint, method, ip, status_code) VALUES (?, ?, ?, ?)",
                      (endpoint, method, ip, status_code))
            conn.commit()
    except Exception:
        pass


# ============================================================
#  Pydantic Request Models
# ============================================================

class CommandRequest(BaseModel):
    text: str

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=4)
    role: Optional[str] = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class ToggleUserRequest(BaseModel):
    user_id: int

class SettingsRequest(BaseModel):
    key: str
    value: str


# ============================================================
#  API Endpoints
# ============================================================

@app.get("/api/health")
async def health_check():
    """Connection test endpoint — returns server status."""
    return {
        "status": "online",
        "name": "SG CUBE",
        "version": "2.0.0",
        "framework": "FastAPI",
        "platform": platform.system(),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/command")
async def process_command(body: CommandRequest, request: Request):
    """Receive a voice command (transcribed text) and return an AI response."""
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty command received.")
    result = handle_os_command(text)
    if result is None:
        result = generate_smart_response(text, user_id=request.client.host, db_path=DB_PATH)
    return result


@app.post("/api/register")
async def handle_register(body: RegisterRequest, request: Request):
    """Register a new user account."""
    username = body.username.strip()
    email = body.email.strip().lower()
    password = body.password
    role = body.role if body.role in ('user', 'admin') else 'user'

    pass_hash = hash_password(password)

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (username,))
            if c.fetchone():
                return JSONResponse(status_code=400, content={"success": False, "message": "Username already taken"})
            c.execute("SELECT id FROM users WHERE email=?", (email,))
            if c.fetchone():
                return JSONResponse(status_code=400, content={"success": False, "message": "Email already registered"})
            c.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      (username, email, pass_hash, role))
            conn.commit()
        log_request('/api/register', 'POST', request.client.host, 200)
        return {"success": True, "message": "Registration successful", "role": role}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.post("/api/login")
async def handle_login(body: LoginRequest, request: Request):
    """Authenticate a user."""
    username = body.username.strip()
    pass_hash = hash_password(body.password)

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT password_hash, role, is_active, username FROM users WHERE username=?", (username,))
            res = c.fetchone()
            if not res:
                log_request('/api/login', 'POST', request.client.host, 401)
                return JSONResponse(status_code=401, content={"success": False, "message": "Invalid username or password"})
            if res['password_hash'] != pass_hash:
                log_request('/api/login', 'POST', request.client.host, 401)
                return JSONResponse(status_code=401, content={"success": False, "message": "Invalid username or password"})
            if not res['is_active']:
                return JSONResponse(status_code=403, content={"success": False, "message": "Account is blocked. Contact admin."})
            log_request('/api/login', 'POST', request.client.host, 200)
        return {"success": True, "message": "Login successful", "role": res['role'], "username": res['username']}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


# ============================================================
#  Admin API Endpoints
# ============================================================

@app.get("/api/admin/stats")
async def admin_stats():
    """Dashboard statistics."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
            total_admins = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM request_logs")
            total_requests = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM request_logs WHERE status_code >= 400")
            total_errors = c.fetchone()[0]
        return {
            "success": True,
            "total_users": total_users,
            "total_admins": total_admins,
            "total_requests": total_requests,
            "total_errors": total_errors
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/admin/users")
async def admin_users():
    """List all registered users."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, is_active, created_at FROM users ORDER BY id")
            rows = c.fetchall()
        users = [dict(r) for r in rows]
        return {"success": True, "users": users}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.post("/api/admin/toggle-user")
async def admin_toggle_user(body: ToggleUserRequest):
    """Block or unblock a user."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT is_active, username FROM users WHERE id=?", (body.user_id,))
            res = c.fetchone()
            if not res:
                return JSONResponse(status_code=404, content={"success": False, "message": "User not found"})
            if res['username'] == 'admin':
                return JSONResponse(status_code=403, content={"success": False, "message": "Cannot block the admin account"})
            new_status = 0 if res['is_active'] else 1
            c.execute("UPDATE users SET is_active=? WHERE id=?", (new_status, body.user_id))
            conn.commit()
        return {"success": True, "is_active": new_status}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/admin/logs")
async def admin_logs():
    """Recent request logs."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT endpoint, method, ip, status_code, timestamp FROM request_logs ORDER BY id DESC LIMIT 100")
            rows = c.fetchall()
        logs = [{"endpoint": r['endpoint'], "method": r['method'], "ip": r['ip'],
                 "status": r['status_code'], "timestamp": r['timestamp']} for r in rows]
        return {"success": True, "logs": logs}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/admin/settings")
async def admin_get_settings():
    """Read app settings."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT key, value FROM app_settings")
            rows = c.fetchall()
        settings = {r['key']: r['value'] for r in rows}
        return {"success": True, "settings": settings}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.post("/api/admin/settings")
async def admin_set_settings(body: SettingsRequest):
    """Write an app setting."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
                      (body.key, body.value))
            conn.commit()
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/system")
async def system_info():
    """Return real system information."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        disk_c = psutil.disk_usage('C:\\') if platform.system() == 'Windows' else None

        info = {
            "cpu": round(cpu_percent, 1),
            "ram_used": round(memory.used / (1024**3), 1),
            "ram_total": round(memory.total / (1024**3), 1),
            "ram_percent": memory.percent,
            "battery": battery.percent if battery else None,
            "battery_plugged": battery.power_plugged if battery else None,
            "disk_c_used": round(disk_c.used / (1024**3)) if disk_c else None,
            "disk_c_total": round(disk_c.total / (1024**3)) if disk_c else None,
            "platform": platform.system(),
            "hostname": platform.node(),
        }
        return {"success": True, **info}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ============================================================
#  Static File Serving (Frontend — unchanged UI)
# ============================================================

@app.get("/")
async def serve_index():
    """Serve the main SG CUBE UI."""
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))




@app.post("/api/vision")
async def process_vision(file: UploadFile = File(...), prompt: str = "Describe this image in detail"):
    """Upload an image and receive an AI-powered text description."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file received.")
    description = analyze_image(image_bytes, prompt=prompt)
    return {"success": True, "description": description}




# ============================================================
#  Ollama Management Endpoints
# ============================================================

@app.get("/api/ollama/status")
async def ollama_status():
    """Check if Ollama is running and return current model."""
    try:
        resp = http_requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"online": True, "models": models, "current_model": get_ollama_model()}
        return {"online": False, "models": [], "current_model": get_ollama_model()}
    except Exception:
        return {"online": False, "models": [], "current_model": get_ollama_model()}


@app.get("/api/ollama/models")
async def ollama_models():
    """List all models pulled in Ollama."""
    try:
        resp = http_requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        resp.raise_for_status()
        models = resp.json().get("models", [])
        return {"success": True, "models": [{"name": m["name"], "size": m.get("size", 0)} for m in models]}
    except Exception:
        return {"success": False, "models": [], "message": "Ollama is not running"}


@app.post("/api/ollama/model")
async def set_model(body: dict):
    """Change the active Ollama model."""
    model_name = body.get("model", "").strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="Model name required")
    set_ollama_model(model_name)
    return {"success": True, "current_model": model_name}




# ============================================================
#  Chat History Endpoints
# ============================================================

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
        messages = [{"role": r["role"], "message": r["message"], "timestamp": r["timestamp"]} for r in reversed(rows)]
        return {"success": True, "messages": messages}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


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



@app.post("/api/system/action")
async def system_action(body: dict):
    """Execute a system quick action."""
    action = body.get("action", "").strip().lower()

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

    if action == "run_script":
        return {"success": True, "response": "Run Script — Coming soon"}

    return JSONResponse(status_code=400, content={"success": False, "response": f"Unknown action: {action}"})

app.include_router(tool_router)

# Mount static files AFTER all API routes so /api/* routes take priority
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")


# ============================================================
#  Server Startup
# ============================================================

if __name__ == '__main__':
    import uvicorn
    print('=' * 50)
    print('  SG CUBE — Backend Server (FastAPI)')
    print('  Smart General Contextual Unified Brain Engine')
    print('=' * 50)
    print(f'  Platform  : {platform.system()} {platform.release()}')
    print(f'  Python    : {platform.python_version()}')
    print(f'  Framework : FastAPI + Uvicorn')
    print(f'  Server    : http://localhost:5000')
    print(f'  API Docs  : http://localhost:5000/docs')
    print(f'  Health    : http://localhost:5000/api/health')
    print('=' * 50)
    print()

    uvicorn.run("server:app", host="0.0.0.0", port=5000)
