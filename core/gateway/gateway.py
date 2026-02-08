"""
OpenCngsm MCP Gateway - FastAPI Server
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.orchestrator.orchestrator import CognitiveOrchestrator
from core.auth.jwt_auth import JWTAuth

app = FastAPI(title="OpenCngsm MCP Gateway", version="2.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = CognitiveOrchestrator()
jwt_auth = JWTAuth()

# Request/Response Models
class LoginRequest(BaseModel):
    user_id: str
    secret: str

class MessageRequest(BaseModel):
    message: str
    user_id: str

class MessageResponse(BaseModel):
    response: str
    plan: Optional[Dict[str, Any]] = None
    timestamp: str

# Routes
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    if request.secret == "opencngsm_secret_2024":
        token = jwt_auth.create_token(request.user_id)
        return {"token": token, "user_id": request.user_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "online",
        "gateway": "active",
        "skills": orchestrator.get_available_skills(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Process user message"""
    try:
        result = await orchestrator.process_message(request.message, request.user_id)
        return MessageResponse(
            response=result.get("response", ""),
            plan=result.get("plan"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def get_skills():
    """Get available skills"""
    return {"skills": orchestrator.get_available_skills()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OpenCngsm MCP Gateway",
        "version": "2.0",
        "status": "running"
    }

if __name__ == "__main__":
    print("🚀 Starting OpenCngsm MCP Gateway...")
    print("📡 Backend: http://127.0.0.1:18789")
    print("🌐 Frontend: http://localhost:5173")
    uvicorn.run(app, host="127.0.0.1", port=18789)
