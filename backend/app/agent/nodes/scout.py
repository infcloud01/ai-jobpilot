# backend/app/agent/nodes/scout.py

from typing import Dict, Any
from app.agent.state import JobHuntState
from app.agent.tools.job_board import fetch_public_job_listings
from app.agent.tools.gmail import fetch_gmail_job_updates 

def scout_node(state: JobHuntState) -> Dict[str, Any]:
    """
    The entry node of the AI-JobPilot assembly line.
    """
    print("\n🚀 --- ENTERING STEP 1: SCOUT NODE (INGESTION LAYER) ---")
    
    # DELETE OR REPLACE THE HARDCODED LINE:
    # search_keywords = "AI Engineer" <-- Old busted line
    
    # NEW DYNAMIC LINE: Extract the user's specific text directly from the state channel
    search_keywords = state.get("query", "AI Engineer") 
    
    user_id = state.get("user_id", "anonymous_user")
    print(f"[SCOUT NODE] Processing live sweep for keywords: '{search_keywords}'")
    
    # Stream 1: Fetch public jobs dynamically!
    public_jobs = fetch_public_job_listings(keywords=search_keywords, max_results=3)
    
    # Stream 2: Fetch personal email leads
    inbox_jobs = fetch_gmail_job_updates()
    
    combined_raw_postings = public_jobs + inbox_jobs
    print(f"🏁 --- EXITING SCOUT NODE: Collected {len(combined_raw_postings)} job footprints ---")
    
    return {
        "raw_job_postings": combined_raw_postings
    }