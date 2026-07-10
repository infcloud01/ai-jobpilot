import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from app.agent.state import JobHuntState, GapAnalysis

def matchmaker_node(state: JobHuntState) -> Dict[str, Any]:
    """
    The matrix evaluation layer of AI-JobPilot.
    Compares the user's resume text against the structured job profiles
    to compute an alignment score, highlight matched skills, and isolate critical gaps.
    """
    print("\n⚖️ --- ENTERING STEP 3: MATCHMAKER NODE (RESUME GAP EVALUATION) ---")
    
    resume = state.get("resume_text", "").strip()
    analyzed_jobs = state.get("analyzed_jobs", [])
    
    # Safety guards for empty data inputs
    if not resume:
        print("[MATCHMAKER NODE] Error: No resume text located in the state context.")
        return {"active_gap_analysis": None}
        
    if not analyzed_jobs:
        print("[MATCHMAKER NODE] No structured job profiles available for matching.")
        return {"active_gap_analysis": None}

    if not os.environ.get("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY missing. Loading fallback gap evaluation.")
        return {"active_gap_analysis": get_fallback_gap_analysis()}

    # Focus context on the first target job profile discovered for the demo execution
    target_job = analyzed_jobs[0]
    print(f"[MATCHMAKER NODE] Benchmarking resume against: {target_job.title} at {target_job.company}")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(GapAnalysis)

    # Design a strict prompt forcing semantic evaluation without resume keyword stuffing tricks
    prompt = f"""
    You are an elite corporate technical recruiter scoring a candidate for an AI Engineering role.
    Compare the Candidate Resume against the target Job Profile Requirements.
    
    CRITERIA:
    1. Look for genuine experience matching the required stack.
    2. Calculate a realistic Match Score from 0 to 100 based on strict alignment.
    3. Isolate the skills they possess under 'matched_skills'.
    4. Crucially, find any mandatory core skills or platforms required by the job that are missing from the resume, and list them under 'critical_gaps'.
    
    Candidate Resume:
    \"\"\"{resume}\"\"\"
    
    Target Job Profile:
    - Title: {target_job.title}
    - Company: {target_job.company}
    - Required Stack: {", ".join(target_job.required_stack)}
    - Preferred Experience: {", ".join(target_job.preferred_experience)}
    """

    try:
        # Enforces validation straight back into our Pydantic schema
        gap_report: GapAnalysis = structured_llm.invoke(prompt)
        
        print(f" -> Computed Match Alignment Score: {gap_report.match_score}/100")
        print(f" -> Flagged Critical Gaps: {gap_report.critical_gaps}")
        
        print("🏁 --- EXITING MATCHMAKER NODE: Gap report successfully generated ---")
        return {"active_gap_analysis": gap_report}
        
    except Exception as e:
        print(f"[ERROR] Matchmaker evaluation pipeline failed: {str(e)}")
        return {"active_gap_analysis": None}

def get_fallback_gap_analysis() -> GapAnalysis:
    """Mock GapAnalysis profile fallback layer."""
    return GapAnalysis(
        match_score=75,
        matched_skills=["Python", "LangGraph", "FastAPI", "Docker", "AWS ECS"],
        critical_gaps=["Kubernetes", "Triton Inference Server"]
    )