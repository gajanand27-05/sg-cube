"""
SG CUBE — OS Command Handler
Extracted command pattern matching and OS action execution.
"""

import os
import re
import subprocess
import platform
import psutil
from datetime import datetime


def handle_os_command(text: str) -> dict | None:
    text_lower = text.lower().strip()

    if re.search(
        r"\b(hello|hi|hey|good morning|good evening|good afternoon)\b", text_lower
    ):
        return {
            "response": f"Hello! I'm SG CUBE, your AI assistant. How can I help you?",
            "action": "greeting",
            "success": True,
        }

    if re.search(
        r"\b(system status|check system|status report|how.s the system)\b", text_lower
    ):
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            bat = psutil.sensors_battery()
            return {
                "response": (
                    f"System status report:\n"
                    f"• CPU usage: {cpu}%\n"
                    f"• RAM: {round(mem.used / (1024**3), 1)} GB / {round(mem.total / (1024**3), 1)} GB ({mem.percent}%)\n"
                    f"• Battery: {bat.percent}% {'(Charging)' if bat.power_plugged else '(On Battery)'}"
                    if bat
                    else ""
                ),
                "action": "system_status",
                "success": True,
            }
        except Exception as e:
            return {
                "response": f"Error reading system info: {str(e)}",
                "action": "system_status",
                "success": False,
            }

    if re.search(r"\bopen\s+(chrome|google chrome|browser)\b", text_lower):
        subprocess.Popen(["start", "chrome"], shell=True)
        return {
            "response": "Opening Google Chrome...",
            "action": "open_chrome",
            "success": True,
        }
    if re.search(r"\bopen\s+(vs\s*code|visual studio code|code editor)\b", text_lower):
        subprocess.Popen(["start", "code"], shell=True)
        return {
            "response": "Launching Visual Studio Code...",
            "action": "open_vscode",
            "success": True,
        }
    if re.search(r"\bopen\s+(notepad|text editor)\b", text_lower):
        subprocess.Popen(["start", "notepad"], shell=True)
        return {
            "response": "Opening Notepad...",
            "action": "open_notepad",
            "success": True,
        }
    if re.search(r"\bopen\s+(file\s*manager|explorer|files)\b", text_lower):
        subprocess.Popen(["start", "explorer"], shell=True)
        return {
            "response": "Opening File Explorer...",
            "action": "open_explorer",
            "success": True,
        }
    if re.search(r"\bopen\s+(terminal|cmd|command prompt|powershell)\b", text_lower):
        subprocess.Popen(["start", "cmd"], shell=True)
        return {
            "response": "Opening Terminal...",
            "action": "open_terminal",
            "success": True,
        }

    if re.search(
        r"\b(coding setup|start coding|dev setup|development setup)\b", text_lower
    ):
        steps = []
        try:
            subprocess.Popen(["start", "code"], shell=True)
            steps.append("✓ Launched VS Code")
        except Exception:
            steps.append("✗ Could not launch VS Code")
        try:
            subprocess.Popen(["start", "cmd"], shell=True)
            steps.append("✓ Opened Terminal")
        except Exception:
            steps.append("✗ Could not open Terminal")
        try:
            subprocess.Popen(
                ["start", "chrome", "--auto-open-devtools-for-tabs"], shell=True
            )
            steps.append("✓ Opened Chrome with DevTools")
        except Exception:
            steps.append("✗ Could not open Chrome")
        return {
            "response": "Executing Coding Setup workflow:\n"
            + "\n".join(steps)
            + "\nYour coding environment is ready!",
            "action": "coding_setup",
            "success": True,
        }

    if re.search(r"\b(study mode|focus mode|study time)\b", text_lower):
        steps = []
        for app in ["chrome.exe", "msedge.exe", "discord.exe"]:
            try:
                subprocess.run(["taskkill", "/f", "/im", app], capture_output=True)
                steps.append(f"✓ Closed {app}")
            except Exception:
                pass
        try:
            subprocess.Popen(["start", "notepad"], shell=True)
            steps.append("✓ Opened Notepad for study notes")
        except Exception:
            pass
        if not steps:
            steps.append("✓ No distracting apps found to close")
        steps.append("✓ Focus mode activated")
        return {
            "response": "Study Mode activated:\n" + "\n".join(steps) + "\nGood luck!",
            "action": "study_mode",
            "success": True,
        }

    if re.search(r"\bconfirm shutdown\b", text_lower):
        subprocess.Popen("shutdown /s /t 30", shell=True)
        return {
            "response": "Shutting down in 30 seconds. Run 'shutdown /a' to cancel.",
            "action": "shutdown",
            "success": True,
        }

    if re.search(r"\bconfirm restart\b", text_lower):
        subprocess.Popen("shutdown /r /t 30", shell=True)
        return {
            "response": "Restarting in 30 seconds. Run 'shutdown /a' to cancel.",
            "action": "restart",
            "success": True,
        }

    if re.search(r"\bcancel shutdown\b", text_lower):
        subprocess.Popen("shutdown /a", shell=True)
        return {
            "response": "Shutdown cancelled.",
            "action": "cancel_shutdown",
            "success": True,
        }

    if re.search(r"\b(shutdown|shut down|power off|turn off)\b", text_lower):
        return {
            "response": 'Shutdown command received. Are you sure you want to shut down? Send "confirm shutdown" to proceed.',
            "action": "shutdown_confirm",
            "success": True,
        }
    if re.search(r"\b(restart|reboot)\b", text_lower):
        return {
            "response": 'Restart command received. Are you sure you want to restart? Send "confirm restart" to proceed.',
            "action": "restart_confirm",
            "success": True,
        }

    if re.search(r"\b(what time|current time|time now)\b", text_lower):
        now = datetime.now()
        return {
            "response": f"The current time is {now.strftime('%I:%M %p')}, {now.strftime('%A, %B %d, %Y')}.",
            "action": "time",
            "success": True,
        }
    if re.search(r"\b(what date|today.s date|what day)\b", text_lower):
        now = datetime.now()
        return {
            "response": f"Today is {now.strftime('%A, %B %d, %Y')}.",
            "action": "date",
            "success": True,
        }

    if re.search(
        r"\b(who are you|what are you|your name|introduce yourself)\b", text_lower
    ):
        return {
            "response": (
                "I am SG CUBE — Smart General Contextual Unified Brain Engine. "
                "I'm your personal AI assistant designed to help you control your system, "
                "automate tasks, and provide intelligent responses. "
                "Think of me as your very own Jarvis!"
            ),
            "action": "identity",
            "success": True,
        }

    if re.search(r"\b(help|what can you do|commands|capabilities)\b", text_lower):
        return {
            "response": (
                "Here's what I can do:\n"
                "• Check system status (CPU, RAM, Battery)\n"
                "• Open applications (Chrome, VS Code, Terminal)\n"
                "• Start workflows (Coding Setup, Study Mode)\n"
                "• Tell you the time and date\n"
                "• Shutdown or restart your system\n"
                "• Answer general questions\n"
                "Just speak or type your command!"
            ),
            "action": "help",
            "success": True,
        }

    return None
