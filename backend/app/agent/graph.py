# backend/app/agent/graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver # <-- New Import for state memory
from app.agent.state import JobHuntState
from app.agent.nodes.scout import scout_node
from app.agent.nodes.analyst import analyst_node
from app.agent.nodes.matchmaker import matchmaker_node
from app.agent.nodes.strategist import strategist_node

workflow = StateGraph(JobHuntState)

workflow.add_node("scout", scout_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("matchmaker", matchmaker_node)
workflow.add_node("strategist", strategist_node)

workflow.add_edge(START, "scout")
workflow.add_edge("scout", "analyst")
workflow.add_edge("analyst", "matchmaker")
workflow.add_edge("matchmaker", "strategist")
workflow.add_edge("strategist", END)

# Production Switch: MemorySaver() holds state in-memory during local runtime.
# When ready for AWS, we simply swap this to DynamoDBSaver() from langgraph-checkpoint-aws.
memory_checkpointer = MemorySaver()

# Compile the graph with active state tracking
job_pilot_graph = workflow.compile(checkpointer=memory_checkpointer)