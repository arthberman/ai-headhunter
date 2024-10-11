from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from candidate_matcher.analysis.nodes import (
    call_model,
    init_agent,
    respond,
    should_continue,
)
from candidate_matcher.analysis.state import (
    AnalysisMainState,
    MainGraphState,
)
from candidate_matcher.analysis.tools import get_tools
from candidate_matcher.configuration import Configuration
from candidate_matcher.utils import get_retry_policy


def get_analysis_graph():
    """Get the analysis graph."""
    workflow = StateGraph(
        AnalysisMainState,
        input=AnalysisMainState,
        output=MainGraphState,
        config_schema=Configuration,
    )

    # Define the nodes
    workflow.add_node("init_agent", init_agent)
    workflow.add_node("agent", call_model, retry=get_retry_policy())
    workflow.add_node("respond", respond)
    workflow.add_node("tools", ToolNode(get_tools()))

    # Set the entrypoint as `init_agent`
    workflow.add_edge(START, "init_agent")
    workflow.add_edge("init_agent", "agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "respond": "respond",
        },
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("respond", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "AnalysisSubGraph"
    return graph
