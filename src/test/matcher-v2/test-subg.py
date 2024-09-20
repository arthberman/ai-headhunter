# %%
from langgraph.graph import END, START, StateGraph
from langgraph.constants import Send

# %%
import operator
from typing import Annotated, Dict, List

from pydantic import BaseModel, Field


class MainGraphState(BaseModel):
    criterion: Annotated[List[str], operator.add]
    title: str
    criteria: List[Dict[str, str]] = Field(
        default_factory=lambda: [
            {"id": "1", "description": "Criterion 1", "context": "Context 1"},
            {"id": "2", "description": "Criterion 2", "context": "Context 2"},
            {"id": "3", "description": "Criterion 3", "context": "Context 3"},
        ]
    )

    model_config = {"arbitrary_types_allowed": True}


class SubGraphState(BaseModel):
    main_state: MainGraphState
    criterion_description: str
    criterion_context: str
    criterion_id: str


# %%
def node_1(state: SubGraphState) -> SubGraphState:
    return state


def node_2(state: SubGraphState) -> MainGraphState:
    return {"criterion": [state.criterion_description]}


def get_subgraph():
    # Define a new graph
    workflow = StateGraph(SubGraphState, input=SubGraphState, output=MainGraphState)

    # Define the nodes
    workflow.add_node("node_1", node_1)
    workflow.add_node("node_2", node_2)

    # Set the entrypoint as `init_agent`
    workflow.add_edge(START, "node_1")
    workflow.add_edge("node_1", "node_2")
    workflow.add_edge("node_2", END)

    # Compile the graph
    graph = workflow.compile()
    return graph


# %%
def continue_to_subgraph(state: MainGraphState):
    print(state)
    return [
        Send(
            "subgraph",
            {
                "main_state": state,
                "criterion_description": c["description"],
                "criterion_context": c["context"],
                "criterion_id": c["id"],
            },
        )
        for c in state.criteria
    ]


# %%
def basic_node(state: MainGraphState):
    return state


def get_main_graph():
    workflow = StateGraph(MainGraphState, input=MainGraphState, output=MainGraphState)

    workflow.add_node("basic_node", basic_node)
    workflow.add_node("subgraph", get_subgraph())

    workflow.add_edge(START, "basic_node")
    workflow.add_conditional_edges("basic_node", continue_to_subgraph, ["subgraph"])
    workflow.add_edge("subgraph", END)

    return workflow.compile()


# %%
graph = get_main_graph()
graph.invoke({"title": "test"})

# %%
