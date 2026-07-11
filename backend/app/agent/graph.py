# backend/app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # <-- ENSURE THIS IS IMPORTED

from app.agent.state import JobHuntState
from app.agent.nodes.scout import scout_node
from app.agent.nodes.analyst import analyst_node
from app.agent.nodes.strategist import strategist_node

# 1. Initialize the in-memory multi-tenant checkpointer instance
memory = MemorySaver()  # <-- THIS WAS MISSING!

# 2. Initialize the State Graph workflow structure
workflow = StateGraph(JobHuntState)

# 3. Register our production structured nodes
workflow.add_node("scout", scout_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("strategist", strategist_node)

# 4. Connect the synchronized operational sequence pipeline
workflow.set_entry_point("scout")
workflow.add_edge("scout", "analyst")
workflow.add_edge("analyst", "strategist")  # Straight bridge, skipping old matchmaker
workflow.add_edge("strategist", END)

# 5. Compile the final runtime graph pinned to our checkpointer memory
job_pilot_graph = workflow.compile(checkpointer=memory)