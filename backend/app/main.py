import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from app.auth import verify_google_token

app = FastAPI(title="AI-JobPilot Core API", version="1.0.0")

# Allow communication from your web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REQUEST/RESPONSE SCHEMAS ---
class AgentQueryRequest(BaseModel):
    query: str

class JobMatchResponse(BaseModel):
    company: str
    title: str
    match_score: int
    critical_gaps: List[str]

# --- ENDPOINTS ---

@app.get("/api/health")
def health_check():
    """Unprotected monitoring endpoint for AWS ALB/ECS target group health verifications."""
    return {"status": "healthy", "environment": os.environ.get("ENVIRONMENT", "development")}


@app.get("/api/user/profile")
def get_user_profile(user: dict = Depends(verify_google_token)):
    """
    Protected identity validation endpoint. Returns the verified token payload.
    Demonstrates data isolation by capturing the injected 'user' context.
    """
    return {
        "message": "Authentication successful",
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"]
    }


@app.post("/api/agent/run", response_model=dict)
async def run_job_pilot_agent(request: AgentQueryRequest, user: dict = Depends(verify_google_token)):
    """
    Protected orchestration route. This is where your LangGraph Engine gets executed.
    Every request passes the user's isolated unique Google ID straight down to the state graph.
    """
    user_id = user["user_id"]
    
    try:
        # Stub execution layer: This is where we will invoke job_pilot_graph.invoke()
        # passing the user_id as the partition configuration anchor
        return {
            "status": "success",
            "msg": f"Agent initialized for user sequence verification loop.",
            "user_context_processed": user_id,
            "query_received": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Execution Failure: {str(e)}")
