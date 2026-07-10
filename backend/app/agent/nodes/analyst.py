import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from app.agent.state import JobHuntState, StructuredJob

def analyst_node(state: JobHuntState) -> Dict[str, Any]:
    """
    The analysis layer of AI-JobPilot.
    Processes unstructured text descriptions using OpenAI structured outputs
    to build strict Pydantic profiles of each role.
    """
    print("\n🧠 --- ENTERING STEP 2: ANALYST NODE (STRUCTURED EXTRACTION) ---")
    
    raw_postings = state.get("raw_job_postings", [])
    if not raw_postings:
        print("[ANALYST NODE] No raw job postings found to analyze. Proceeding...")
        return {"analyzed_jobs": []}

    # Verify that the OpenAI API Key is present in the environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY environment variable is missing!")
        # Return fallback mock data to keep the graph pipeline from hard-crashing
        return {"analyzed_jobs": get_fallback_analyzed_jobs()}

    # Initialize the OpenAI model (using the efficient gpt-4o-mini for parsing tasks)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Force the LLM to strictly adhere to our Pydantic schema structure
    structured_llm = llm.with_structured_output(StructuredJob)
    
    analyzed_results: List[StructuredJob] = []
    
    print(f"[ANALYST NODE] Analyzing {len(raw_postings)} job descriptions using OpenAI...")
    
    for idx, raw_job in enumerate(raw_postings, 1):
        print(f" -> Processing job {idx}/{len(raw_postings)}: {raw_job.get('title')} at {raw_job.get('company')}")
        
        # Construct a targeted system prompt instructing the model how to evaluate text
        prompt = f"""
        Analyze the following job posting text and extract the information matching the requested schema.
        
        Company: {raw_job.get('company')}
        Title: {raw_job.get('title')}
        Description:
        {raw_job.get('description')}
        """
        
        try:
            # The structured_llm directly returns a validated StructuredJob Pydantic instance
            structured_data = structured_llm.invoke(prompt)
            analyzed_results.append(structured_data)
        except Exception as e:
            print(f" [WARNING] Failed to parse job {idx} due to API error: {str(e)}")
            continue

    print(f"🏁 --- EXITING ANALYST NODE: Successfully structured {len(analyzed_results)} roles ---")
    
    return {
        "analyzed_jobs": analyzed_results
    }

def get_fallback_analyzed_jobs() -> List[StructuredJob]:
    """Returns a mock StructuredJob list if OpenAI keys are absent during execution."""
    return [
        StructuredJob(
            company="NextGen AI Corp",
            title="Senior AI Infrastructure Engineer",
            required_stack=["Python", "LangGraph", "FastAPI", "Docker", "AWS ECS", "Fargate"],
            preferred_experience=["LangSmith", "GitHub Actions", "Kubernetes", "Triton Inference Server"],
            is_infrastructure_heavy=True
        )
    ]