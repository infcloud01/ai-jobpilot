# backend/test_agent.py
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.agent.graph import job_pilot_graph

def test_pipeline():
    print("🤖 Initializing AI-JobPilot Graph Compilation...")
    
    initial_state = {
        "messages": [],
        "user_id": "google_user_demo_998877",
        "resume_text": "Experienced Python Developer with LangChain and Docker experience.",
        "raw_job_postings": [],
        "analyzed_jobs": [],
        "active_gap_analysis": None,
        "roadmap_suggestions": []
    }
    
    # FIX: Provide a routing thread ID config block so the MemorySaver knows where to store state
    config = {
        "configurable": {
            "thread_id": "local_test_verification_thread"
        }
    }
    
    try:
        print("⚡ Invoking Graph Pipeline with Active Checkpointer Routing...")
        # Pass the config dictionary right here as the second parameter
        final_state = job_pilot_graph.invoke(initial_state, config=config)
        
        print("\n🎉 --- GRAPH COMPLETED EXECUTION SUCCESSFULLY ---")
        print("\nCollected Raw Job Postings Context:")
        print(json.dumps(final_state.get("raw_job_postings", []), indent=2))
        
    except Exception as e:
        print(f"\n❌ Execution Broken: {str(e)}")

if __name__ == "__main__":
    test_pipeline()