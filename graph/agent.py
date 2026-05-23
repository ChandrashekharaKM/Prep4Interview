"""
graph/agent.py
Builds and compiles the LangGraph state machine for HR-Copilot.

Graph flow:
    START → classify → [clarify branch OR act] → review_gate → [approve/edit/reject] → audit → END
"""

from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph.nodes import classify_node, act_node, memory_node, audit_node


# ---------------------------------------------------------------------------
# Conditional edge: after classify
# ---------------------------------------------------------------------------

def route_after_classify(state: AgentState) -> str:
    if state.get("clarification_needed"):
        return "needs_clarification"
    if state.get("error"):
        return "error"
    return "act"


# ---------------------------------------------------------------------------
# Conditional edge: after review gate (set externally by the UI)
# ---------------------------------------------------------------------------

def route_after_review(state: AgentState) -> str:
    decision = state.get("review_decision", "pending")
    if decision == "approved":
        return "finalize"
    if decision == "edited":
        return "finalize"
    if decision == "rejected":
        return "rejected"
    # Still pending — this path shouldn't be reached in normal flow
    return "finalize"


# ---------------------------------------------------------------------------
# Inline nodes for terminal states
# ---------------------------------------------------------------------------

def clarification_node(state: AgentState) -> dict:
    """Terminal node: returns the clarification question as draft_output."""
    return {"draft_output": state.get("clarification_question",
                                      "Could you please clarify your request?")}


def error_node(state: AgentState) -> dict:
    """Terminal node: surfaces error as draft_output."""
    return {"draft_output": f"⚠️ An error occurred: {state.get('error', 'Unknown error')}"}


def reject_node(state: AgentState) -> dict:
    """Terminal node: acknowledged rejection."""
    return {"draft_output": "Draft rejected and discarded. No action taken."}


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Add nodes
    g.add_node("classify", classify_node)
    g.add_node("act", act_node)
    g.add_node("memory", memory_node)
    g.add_node("audit", audit_node)
    g.add_node("needs_clarification", clarification_node)
    g.add_node("error_handler", error_node)
    g.add_node("rejected", reject_node)

    # Entry point
    g.set_entry_point("classify")

    # Edges from classify
    g.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "act": "act",
            "needs_clarification": "needs_clarification",
            "error": "error_handler",
        },
    )

    # After act → memory → audit → END
    g.add_edge("act", "memory")
    g.add_edge("memory", "audit")
    g.add_edge("audit", END)

    # Terminal paths
    g.add_edge("needs_clarification", END)
    g.add_edge("error_handler", END)
    g.add_edge("rejected", END)

    return g.compile()


# Singleton compiled graph
hr_graph = build_graph()
