"""
FastAPI Server for Northstar Homes AI Conversational Agent.
Provides REST endpoints for Chat, Live Function Calling, Lead Analytics Extraction, and Static Web UI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
import uvicorn
import logging

from backend.config import settings
from backend.agent import agent_orchestrator, get_openai_client
from backend.analytics import generate_analytics_from_transcript

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real Estate AI Sales Agent for Northstar Homes (Northstar One, Sector 79, Gurugram)"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Request / Response Schemas
class ChatRequest(BaseModel):
    session_id: str = Field(default="default-session", description="Unique session identifier")
    message: str = Field(..., description="Customer message")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_executed: bool
    tools: List[Dict[str, Any]] = []

class SessionActionRequest(BaseModel):
    session_id: str = Field(default="default-session")

@app.get("/")
async def serve_index():
    """Serves the web client interface."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Northstar Homes AI Agent API is running.", "docs": "/docs"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """Processes customer messages and returns AI dialogue with tool execution metadata."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    result = agent_orchestrator.process_message(
        session_id=payload.session_id,
        user_message=payload.message
    )
    
    return ChatResponse(
        session_id=payload.session_id,
        response=result["response"],
        tool_executed=result.get("tool_executed", False),
        tools=result.get("tools", [])
    )

@app.post("/api/end-session")
async def end_session_endpoint(payload: SessionActionRequest):
    """
    Terminates conversation and generates structured Lead Analytics (CRM intelligence)
    from the full transcript.
    """
    history = agent_orchestrator.get_session_history(payload.session_id)
    client = get_openai_client()
    analytics_data = generate_analytics_from_transcript(history, client=client)
    return {
        "session_id": payload.session_id,
        "status": "completed",
        "analytics": analytics_data
    }

@app.post("/api/reset")
async def reset_endpoint(payload: SessionActionRequest):
    """Resets the conversation context for a clean session."""
    agent_orchestrator.reset_session(payload.session_id)
    return {"session_id": payload.session_id, "status": "reset_successful"}

@app.get("/api/scenarios")
async def get_test_scenarios():
    """Returns standard evaluation scenarios for one-click testing in UI."""
    return [
        {
            "id": "1",
            "title": "Hinglish 3 BHK Inquiry",
            "tag": "Multilingual",
            "message": "Namaste, mujhe Sector 79 project ke bare mein janna hai, 3 BHK pricing kya hai?"
        },
        {
            "id": "2",
            "title": "Price Objection",
            "tag": "Objection",
            "message": "1.75 Crore is too expensive for Sector 79, can you give me 15% discount?"
        },
        {
            "id": "3",
            "title": "Site Visit Booking (Success)",
            "tag": "Tool / Booking",
            "message": "Can I schedule a site visit for this Saturday at 11:00 AM for 3 BHK?"
        },
        {
            "id": "4",
            "title": "Booking Collision (Sunday 4 PM)",
            "tag": "Failure Recovery",
            "message": "I want to visit the site this Sunday at 4:00 PM."
        },
        {
            "id": "5",
            "title": "Busy / Call Later",
            "tag": "Cadence",
            "message": "I am in an important client meeting right now, please call me tomorrow at 4 PM."
        },
        {
            "id": "6",
            "title": "DND / Stop Communication",
            "tag": "Opt-Out",
            "message": "I am not interested in Gurugram properties. Please do not call me again."
        },
        {
            "id": "7",
            "title": "Human Escalation (Legal Docs)",
            "tag": "Escalation",
            "message": "I want to speak with your senior legal manager regarding the RERA approval papers."
        }
    ]

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=True)
