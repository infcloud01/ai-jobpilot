# backend/app/agent/tools/job_board.py
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Automatically look for and load variables defined in the backend/.env file
load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_public_job_listings(keywords: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Queries the live Adzuna REST API for active job openings based on keywords.
    Automatically drops back to safe simulated data vectors if keys are missing.
    """
    # Defensive check: If environment variables are missing, switch to fallback mode
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[JOB BOARD TOOL] Warning: Keys missing from .env. Deploying mock simulation matrix...")
        return get_mock_job_board_data()

    print(f"[JOB BOARD TOOL] Initiating live global query for keywords: '{keywords}'")
    
    # Adzuna regional endpoint targeting the United States market ('us')
    # Syntax: https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
    target_url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    
    query_params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": max_results,
        "what": keywords,
        "content-type": "application/json"
    }

    try:
        response = requests.get(target_url, params=query_params, timeout=10)
        
        if response.status_code != 200:
            print(f"[JOB BOARD TOOL] API returned anomaly code: {response.status_code}. Using fallbacks.")
            return get_mock_job_board_data()
            
        data = response.json()
        results = data.get("results", [])
        
        normalized_postings = []
        for job in results:
            normalized_postings.append({
                "source": "Live Adzuna Aggregator Engine",
                "id": job.get("id", "unknown_id"),
                "company": job.get("company", {}).get("display_name", "Undisclosed Company"),
                "title": job.get("title", "Software Engineer"),
                "location": job.get("location", {}).get("display_name", "Remote / USA"),
                "description": job.get("description", "No description text provided by aggregator resource."),
                "url": job.get("redirect_url", "https://www.adzuna.com"),
                "posted_at": job.get("created", "")
            })
            
        print(f"[JOB BOARD TOOL] Successfully captured {len(normalized_postings)} live marketplace listings.")
        return normalized_postings

    except Exception as e:
        print(f"[JOB BOARD TOOL] Network request connection failure: {str(e)}. Defaulting to sandbox data.")
        return get_mock_job_board_data()


def get_mock_job_board_data() -> List[Dict[str, Any]]:
    """Fallback sample data to keep the LangGraph pipeline alive if network fails or keys are blank."""
    return [
        {
            "source": "Mock Adzuna Data Sandbox",
            "id": "adzuna-mock-001",
            "company": "CloudScale Systems",
            "title": "AI Infrastructure Specialist",
            "location": "San Francisco, CA (Hybrid)",
            "description": "Looking for an engineer to manage high-throughput LLM hosting layers. Core requirements include deep expertise in Kubernetes containerization, Python scripts, Triton Inference Servers, and LangGraph multi-agent systems orchestration architecture.",
            "url": "https://example.com/jobs/1",
            "posted_at": "2026-03-01T00:00:00Z"
        }
    ]