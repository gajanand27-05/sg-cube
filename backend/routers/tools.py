"""
SG CUBE — AI Tools Router
Endpoints for Code Generator, Summarizer, Resume Builder, Notes Organizer.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.llm import ask_ollama, ask_online

tool_router = APIRouter(prefix="/api/tools")


class ToolRequest(BaseModel):
    input_data: str


def safe_llm_call(prompt: str) -> str:
    try:
        return ask_ollama(prompt, "tool_user")
    except Exception:
        return ask_online(prompt, "tool_user")


@tool_router.post("/codegen")
async def codegen(body: ToolRequest):
    prompt = (
        f"Generate production-ready code for: {body.input_data}. Return only the code."
    )
    result = safe_llm_call(prompt)
    return {"result": result}


@tool_router.post("/summarizer")
async def summarizer(body: ToolRequest):
    prompt = (
        f"Summarize the following text accurately in bullet points: {body.input_data}"
    )
    result = safe_llm_call(prompt)
    return {"result": result}


@tool_router.post("/resume")
async def resume(body: ToolRequest):
    prompt = f"Format the following career data into a professional Markdown Resume: {body.input_data}"
    result = safe_llm_call(prompt)
    return {"result": result}


@tool_router.post("/notes")
async def notes(body: ToolRequest):
    prompt = f"Organize the following raw ideas into structured meeting notes: {body.input_data}"
    result = safe_llm_call(prompt)
    return {"result": result}
