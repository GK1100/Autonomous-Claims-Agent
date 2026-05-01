from langgraph.graph import StateGraph, START, END
from typing import Literal
from src.graph.state import ClaimState
from src.graph.nodes import (
    ingestion_node,
    extraction_node,
    validation_node,
    decision_node,
    audit_node
)

# ──────────────────────────────────────────────
# Routing Logic (Controlled Autonomy)
# ──────────────────────────────────────────────
def validation_router(state: ClaimState) -> Literal["extraction", "decision"]:
    """
    Decides whether to loop back to extraction or proceed to decision.
    """
    # If there are recoverable fields missing, and we haven't hit the retry limit
    if state.get("missing_fields_to_retry") and state.get("extraction_attempts", 0) < 3:
        return "extraction"
    
    # Otherwise, move forward (even if degraded, decision node will handle it)
    return "decision"

# ──────────────────────────────────────────────
# Build the Graph
# ──────────────────────────────────────────────
def build_claim_graph():
    workflow = StateGraph(ClaimState)

    # Add Nodes
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("extraction", extraction_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("audit", audit_node)

    # Define Edges
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "extraction")
    workflow.add_edge("extraction", "validation")
    
    # Conditional edge from Validation (Feedback Loop)
    workflow.add_conditional_edges(
        "validation",
        validation_router,
        {
            "extraction": "extraction",
            "decision": "decision"
        }
    )
    
    workflow.add_edge("decision", "audit")
    workflow.add_edge("audit", END)

    # Compile the graph
    app = workflow.compile()
    return app
