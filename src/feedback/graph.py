from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feedback.configuration import Configuration
from feedback.nodes.context_awareness import node_context_awareness
from feedback.state import (
    FeedbackGraphState,
    FeedbackInputGraphState,
    FeedbackOutputGraphState,
)
from utils import get_retry_policy


def compile_feedback_graph() -> CompiledGraph:
    """Compile the feedback graph."""
    workflow = StateGraph(
        FeedbackGraphState,
        input=FeedbackInputGraphState,
        output=FeedbackOutputGraphState,
        config_schema=Configuration,
    )

    workflow.add_node(
        "context_awareness", node_context_awareness, retry=get_retry_policy()
    )

    workflow.add_edge(START, "context_awareness")
    workflow.add_edge("context_awareness", END)

    graph = workflow.compile()
    graph.name = "FeedbackGraph"
    return graph
