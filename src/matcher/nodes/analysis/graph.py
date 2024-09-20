from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from matcher.nodes.analysis.nodes import (
    init_agent,
    call_model,
    respond,
    should_continue,
)
from matcher.nodes.analysis.tools import get_tools
from matcher.nodes.analysis.state import (
    AnalysisMainState,
    MainGraphState,
)


def get_analysis_graph():
    # Define a new graph
    workflow = StateGraph(
        AnalysisMainState, input=AnalysisMainState, output=MainGraphState
    )

    # Define the nodes
    workflow.add_node("init_agent", init_agent)
    workflow.add_node("agent", call_model)
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
    return graph
