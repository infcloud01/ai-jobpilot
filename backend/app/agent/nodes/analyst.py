# backend/app/agent/nodes/analyst.py
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from app.agent.state import JobHuntState

# Step 1: Declare the strict structural schema for the Analyst Node
class AnalystOutput(BaseModel):
    """Schema forcing the LLM to output verified, isolated evaluation arrays."""
    match_score: int = Field(
        description="A percentage score from 0 to 100 calculation indicating how well the candidate's resume_text satisfies the requirements seen across raw_job_postings."
    )
    matched_skills: List[str] = Field(
        description="An array of exact core technical skills, programming languages, or architectural frameworks present in both the resume and the target jobs."
    )
    critical_gaps: List[str] = Field(
        description="An array of high-priority technical requirements, platforms, or tools missing from the user's resume but explicitly sought after by the companies."
    )

def analyst_node(state: JobHuntState) -> Dict[str, Any]:
    print("\n🧐 --- ENTERING STEP 2: ANALYST NODE (EVALUATION LAYER) ---")
    
    # Extract runtime state payloads
    resume = state.get("resume_text", "")
    job_feed = state.get("raw_job_postings", [])
    
    # Bind the structural schema constraint directly to the OpenAI model interface
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    structured_llm = llm.with_structured_output(AnalystOutput)
    
    system_prompt = (
        "You are an elite, unbiased technical recruiting platform algorithm. Your mission is to "
        "cross-reference a user's raw resume context against a set of real-world job vacancies. "
        "Isolate exactly what criteria match, what critical tools are totally missing, and "
        "compute an absolute qualification match score based purely on hard technical alignment."
    )
    
    user_prompt = f"""
    Candidate Resume Core Context:
    ---
    {resume}
    ---
    
    Target Job Aggregations & Inbox Leads Data Feed:
    ---
    {job_feed}
    ---
    """
    
    messages = [
        ("system", system_prompt),
        ("user", user_prompt)
    ]
    
    print("[ANALYST] Dispatching live context matrices to structured OpenAI model channel...")
    # The return object is natively verified against the AnalystOutput BaseModel structure
    evaluation_result = structured_llm.invoke(messages)
    
    print(f"[ANALYST] Structural analysis completed. Evaluated Match Score: {evaluation_result.match_score}%")
    print(f"🏁 --- EXITING ANALYST NODE: Generated {len(evaluation_result.critical_gaps)} critical gap items ---")
    
    return {
        "active_gap_analysis": evaluation_result
    }