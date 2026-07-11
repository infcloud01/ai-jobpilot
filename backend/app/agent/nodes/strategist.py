# backend/app/agent/nodes/strategist.py
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from app.agent.state import JobHuntState

# Step 1: Tune the schema to explicitly demand deep, technical project blueprints
class StrategistOutput(BaseModel):
    """Schema forcing the LLM to output deep, multi-sentence project milestones."""
    roadmap_suggestions: List[str] = Field(
        description=(
            "A sequential list of exactly 4 to 5 deep, highly specific technical career milestones. "
            "CRITICAL: Each milestone must be a detailed 2 to 3 sentence architectural project idea or "
            "tactical objective grounded in the provided resume and target jobs. Avoid generic, short "
            "one-liners like 'Learn Docker' or 'Practice Python'. Instead, give an explicit blueprint."
        )
    )

def strategist_node(state: JobHuntState) -> Dict[str, Any]:
    print("\n🎯 --- ENTERING STEP 3: STRATEGIST NODE (ROADMAP LAYER) ---")
    
    gap_report = state.get("active_gap_analysis")
    resume_context = state.get("resume_text", "")
    target_role = state.get("query", "Target Role")
    job_feed = state.get("raw_job_postings", [])
    
    if not gap_report:
        print("[STRATEGIST] Warning: No active gap profile context detected. Skipping roadmap compilation.")
        return {"roadmap_suggestions": []}
        
    # Bump temperature slightly to 0.7 to unlock deep, contextual engineering advice
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(StrategistOutput)
    
    system_prompt = (
        f"You are a Principal Software Engineer and Elite Technical Career Strategist. Your mission "
        f"is to study a candidate's background, look at their specific target market vacancies for '{target_role}', "
        f"and design a premium, custom 4-to-5 step technical execution roadmap. "
        f"Every milestone step must describe a meaty, production-grade project or system design task that "
        f"simultaneously leverages what they already know while explicitly mastering their core technical gaps."
    )
    
    # Restoring the massive global context footprint the model needs to think critically
    user_prompt = f"""
    Target Career Focus: {target_role}
    
    Candidate's Actual Background / Current Resume:
    ---
    {resume_context}
    ---
    
    Calculated Technical Gaps: {gap_report.critical_gaps}
    Matched Existing Skills Foundation: {gap_report.matched_skills}
    
    Live Market Job Requirements We Are Targeting:
    ---
    {job_feed}
    ---
    """
    
    print("[STRATEGIST] Dispatching full context matrix to structured OpenAI milestone compiler...")
    roadmap_result = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    print(f"[STRATEGIST] Mapping finalized. Created {len(roadmap_result.roadmap_suggestions)} high-IQ action milestones.")
    print("🏁 --- EXITING STRATEGIST NODE: Custom roadmap distributed ---")
    
    return {
        "roadmap_suggestions": roadmap_result.roadmap_suggestions
    }