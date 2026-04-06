# SG CUBE: Technical Implementation Plan

This document outlines the step-by-step roadmap for developers to build out the features of the SG CUBE AI Assistant based on the current foundation. The objective is to transition from a static hardcoded prototype to a fully dynamic, context-aware Hybrid AI Engine.

## Background Context
Currently, the SG CUBE project has a solid foundation:
- **Frontend**: A futuristic Jarvis-inspired UI built with HTML/CSS/JS, currently using Web Speech API for Speech-to-Text and browser Synthesis for Text-to-Speech.
- **Backend**: A FastAPI server (`server.py`) serving the UI, managing SQLite user databases, and containing a basic regex-pattern matcher for voice commands (`handle_command`).

The following phases outline the steps required for a coder to implement the requested hybrid AI models, context awareness, advanced tools, and vision capabilities.

---

## Proposed Changes

### Phase 1: Backend Architecture Refactoring
**Goal:** Modularize the monolithic `server.py` to prepare for complex AI functionality.
- Split into `ai/llm.py`, `ai/vision.py`, and `utils/tasks.py`.

### Phase 2: Core Chatbot & Context Awareness
**Goal:** Implement conversational memory and plug the AI engine into the frontend.
- Add context memory dictionaries keyed by user IP/Session.

### Phase 3: Implementing Web AI Tools
**Goal:** Hook up the 6 "AI Tools" defined in the frontend (Chatbot, Code Generator, Summarizer, Resume Builder, Notes, Vision AI).
- Create `routers/tools.py` in the backend.
- Write frontend javascript to open specific modals and send fetch requests to these tool routes instead of the base chat route.

### Phase 4: Vision Capabilities Integration
**Goal:** Allow the user to upload or capture images via webcam on the frontend, sent to the backend for analysis.
- Connect `ai/vision.py` using YOLOv8 models.

### Phase 5: Voice Assistant (JARVIS Mode) Upgrades
**Goal:** Ensure voice acts seamlessly alongside the hybrid text engine.
- Either continue expanding Browser Web Speech API or stream WAV files to a backend process running OpenAI's Whisper model.

### Phase 6: System Task Automation
**Goal:** Extend system actions.
- Build extensive commands in `utils/tasks.py`.
