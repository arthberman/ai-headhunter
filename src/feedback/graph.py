from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feedback.configuration import Configuration
from feedback.nodes.pattern import node_pattern
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

    workflow.add_node("pattern", node_pattern, retry=get_retry_policy())

    workflow.add_edge(START, "context_awareness")
    workflow.add_edge("context_awareness", END)

    graph = workflow.compile()
    graph.name = "FeedbackGraph"
    return graph
