from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

# Pydantic schemas for enforced structural outputs from the LLM
class StructuredJob(BaseModel):
    company: str = Field(description="Name of the hiring organization")
    title: str = Field(description="The formal job title")
    required_stack: List[str] = Field(description="Hard technical skills, frameworks, and programming languages explicitly required")
    preferred_experience: List[str] = Field(description="Soft requirements, specific architectural paradigms, or nice-to-haves")
    is_infrastructure_heavy: bool = Field(description="True if role focuses on cloud, DevOps, MLOps, or backend systems. False if frontend/wrapper heavy.")

class GapAnalysis(BaseModel):
    match_score: int = Field(description="Alignment rating from 0 to 100 based on resume matching the job stack")
    matched_skills: List[str] = Field(description="Skills the candidate possesses that perfectly align with the job posting")
    critical_gaps: List[str] = Field(description="Essential technical requirements listed in the job that are missing from the resume")

# The master LangGraph state model
class JobHuntState(TypedDict):
    # Appends conversation history dynamically over time
    messages: Annotated[list, add_messages]
    
    # Context anchors
    user_id: str                      # Injected from the validated Google JWT
    query: str
    resume_text: str                  # Plucked from your data layer at runtime
    
    # Pipeline data buckets passed node-to-node
    raw_job_postings: List[Dict[str, Any]]
    analyzed_jobs: List[StructuredJob]
    active_gap_analysis: Optional[GapAnalysis]
    roadmap_suggestions: List[str]