from langgraph.graph import END, START, StateGraph

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.nodes import (
    node_assess_open_to_work,
    node_check_hierarchy,
    node_check_redflag_stability,
    node_conclude,
    node_infer_role_trajectory,
    node_synthetize_intent,
)
from utils import get_retry_policy


def get_decision_subgraph():
    """Get the decision subgraph."""
    workflow = StateGraph(
        MainGraphState,
        config_schema=Configuration,
    )

    workflow.add_node(
        "assess_open_to_work", node_assess_open_to_work, retry=get_retry_policy()
    )
    workflow.add_node("check_hierarchy", node_check_hierarchy, retry=get_retry_policy())
    workflow.add_node(
        "check_redflag_stability",
        node_check_redflag_stability,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "synthetize_intent", node_synthetize_intent, retry=get_retry_policy()
    )
    workflow.add_node(
        "infer_role_trajectory", node_infer_role_trajectory, retry=get_retry_policy()
    )
    workflow.add_node("conclude", node_conclude, retry=get_retry_policy())
    workflow.add_edge(START, "assess_open_to_work")
    workflow.add_edge(START, "check_hierarchy")

    workflow.add_edge("check_hierarchy", "synthetize_intent")
    workflow.add_edge("assess_open_to_work", "synthetize_intent")
    workflow.add_edge("synthetize_intent", "check_redflag_stability")
    workflow.add_edge("check_redflag_stability", "infer_role_trajectory")
    workflow.add_edge("infer_role_trajectory", "conclude")
    workflow.add_edge("conclude", END)
    # Compile the graph
    graph = workflow.compile()
    graph.name = "DecisionSubGraph"
    return graph
