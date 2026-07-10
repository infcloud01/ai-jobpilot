# backend/app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Core engine and authorization dependencies
from app.auth import verify_google_token
from app.agent.graph import job_pilot_graph 

app = FastAPI(title="AI-JobPilot Core API", version="1.0.0")

# Register global application cross-origin security rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- APPLICATION ROUTING ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "environment": os.environ.get("ENVIRONMENT", "development")}


@app.post("/api/agent/run")
async def run_job_pilot_agent(
    query: str = Form(...),                        # Ingest key text form fields
    resume_file: UploadFile = File(...),            # Stream raw binary multi-part file payloads
    user: dict = Depends(verify_google_token)    # Toggle this dependency when testing with active frontend auth keys
):
    """
    Secured Form Ingestion Entrypoint.
    Streams an uploaded document, decodes the structural string values, 
    and hooks the content context layer directly into the multi-node LangGraph checkpointer.
    """
    # Hardcoded fallback key for isolated developer testing environments
    user_id = "test_local_user_123"
    
    try:
        print(f"[API GATEWAY] Processing streaming form upload for file: {resume_file.filename}")
        
        # Read file chunks out of raw buffer stream memory
        file_bytes = await resume_file.read()
        
        # Convert incoming binary representations back into a manageable string block
        uploaded_resume_text = file_bytes.decode("utf-8", errors="ignore")
        
        # Defensive input checking
        if not uploaded_resume_text.strip():
            raise HTTPException(status_code=400, detail="The provided file payload contains no text context data.")

        # Seed the structural core requirements parameter dictionary fields
        initial_state = {
            "messages": [],
            "user_id": user_id,
            "query": query,
            "resume_text": uploaded_resume_text, # Injected raw file data
            "raw_job_postings": [],
            "analyzed_jobs": [],
            "active_gap_analysis": None,
            "roadmap_suggestions": []
        }
        
        # Sandboxed multi-tenant checkpointer boundary configs
        config = {
            "configurable": {
                "thread_id": user_id 
            }
        }
        
        print(f"[API GATEWAY] Invoking LangGraph runtime thread sequence for user ID: {user_id}")
        final_state = job_pilot_graph.invoke(initial_state, config=config)
        gap_report = final_state.get("active_gap_analysis")
        
        # Return cleanly parsed, marshaled parameters back onto the active frontend display channel
        return {
            "status": "success",
            "user_id": user_id,
            "metrics": {
                "match_score": gap_report.match_score if gap_report else 0,
                "matched_skills": gap_report.matched_skills if gap_report else [],
                "critical_gaps": gap_report.critical_gaps if gap_report else []
            },
            "action_plan": final_state.get("roadmap_suggestions", [])
        }
        
    except Exception as e:
        print(f"[API ERROR] File stream conversion processing broke down: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Processing Failure: {str(e)}")