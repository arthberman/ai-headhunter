from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from setup.nodes.enrichment_subgraph.nodes import (
    AgentState,
    call_model,
    init_agent,
    respond,
    should_continue,
)
from setup.nodes.enrichment_subgraph.state import OutputGraphState
from setup.nodes.enrichment_subgraph.tools import get_tools
from utils import get_retry_policy


def get_enrichment_graph():
    """Get the enrichment graph."""
    # Define a new graph
    workflow = StateGraph(AgentState, output=OutputGraphState)

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
    graph.name = "EnrichmentSubGraph"
    return graph
