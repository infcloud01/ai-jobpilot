import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from app.agent.state import JobHuntState

# A simple Pydantic wrapper to enforce a clean array of strings from OpenAI
class RoadmapOutput(BaseModel):
    suggestions: List[str] = Field(description="Actionable, step-by-step learning items or mini-projects to bridge the gap.")

def strategist_node(state: JobHuntState) -> Dict[str, Any]:
    """
    The advisory layer of AI-JobPilot.
    Reads the identified critical gaps and engineers a targeted, 
    actionable technical roadmap to help the user prepare for the role.
    """
    print("\n🎯 --- ENTERING STEP 4: STRATEGIST NODE (ROADMAP GENERATION) ---")
    
    gap_analysis = state.get("active_gap_analysis")
    
    # Safety check if upstream nodes failed to find gaps
    if not gap_analysis or not gap_analysis.critical_gaps:
        print("[STRATEGIST NODE] No critical gaps identified to build a roadmap for.")
        return {"roadmap_suggestions": ["Your resume perfectly aligns with this role! Focus on standard interview prep."]}

    if not os.environ.get("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY missing. Loading fallback roadmap.")
        return {"roadmap_suggestions": get_fallback_roadmap()}

    print(f"[STRATEGIST NODE] Generating an actionable learning plan for gaps: {gap_analysis.critical_gaps}")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3) # Slightly higher temperature for creative engineering advice
    structured_llm = llm.with_structured_output(RoadmapOutput)

    prompt = f"""
    You are an elite AI Engineering Mentor. The candidate has some technical skill gaps for their target role.
    Generate an actionable, high-impact learning roadmap. For each skill gap, provide a concrete mini-project 
    or configuration task they can build over a weekend to realistically add that skill to their resume.
    
    Critical Skill Gaps:
    {", ".join(gap_analysis.critical_gaps)}
    
    Provide your response as a list of distinct, clear bullet points.
    """

    try:
        roadmap_report: RoadmapOutput = structured_llm.invoke(prompt)
        
        for idx, item in enumerate(roadmap_report.suggestions, 1):
            print(f" Plan Item {idx}: {item[:60]}...")
            
        print("🏁 --- EXITING STRATEGIST NODE: Technical roadmap successfully compiled ---")
        return {"roadmap_suggestions": roadmap_report.suggestions}
        
    except Exception as e:
        print(f"[ERROR] Strategist node failed to generate roadmap: {str(e)}")
        return {"roadmap_suggestions": []}

def get_fallback_roadmap() -> List[str]:
    """Fallback roadmap suggestions layer."""
    return [
        "Spend 48 hours creating a local multi-stage Docker container serving an open-source LLM via Triton Inference Server.",
        "Deploy a basic application on a local single-node Kubernetes cluster (Minikube) to understand Pod networking and volume mounts."
    ]