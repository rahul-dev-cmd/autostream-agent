from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import detect_intent, rag_retrieval, lead_collection, handle_greeting

def route_next_step(state: AgentState):
    """
    Determines the next node based on the detected intent.
    """
    intent = state.get("intent")
    
    if intent == "high_intent":
        return "lead_collection"
    elif intent == "inquiry":
        return "rag_retrieval"
    else:
        return "greeting"

# Initialize the state graph
workflow = StateGraph(AgentState)

# Add all required nodes
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("rag_retrieval", rag_retrieval)
workflow.add_node("lead_collection", lead_collection)
workflow.add_node("greeting", handle_greeting)

# The agent always starts by determining what the user wants
workflow.set_entry_point("detect_intent")

# Route the flow based on the intent
workflow.add_conditional_edges(
    "detect_intent",
    route_next_step,
    {
        "rag_retrieval": "rag_retrieval",
        "lead_collection": "lead_collection",
        "greeting": "greeting" 
    }
)

# After these nodes execute, the current graph turn ends
workflow.add_edge("rag_retrieval", END)
workflow.add_edge("lead_collection", END)
workflow.add_edge("greeting", END)

# Initialize the checkpointer for memory retention
memory = MemorySaver()

# Compile the graph with the checkpointer
app = workflow.compile(checkpointer=memory)